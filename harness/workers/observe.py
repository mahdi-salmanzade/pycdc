"""Harness worker: execute one fixture and record its observable behavior.

usage: observe.py --pyc FILE --out OUT.json
       observe.py --source FILE --optimize N --filename NAME --out OUT.json

The code object (marshal-loaded from the .pyc, or compiled from source at the
given optimization level) is executed in a fresh module named "fixture".  If
the module defines a callable observe(), it is then called with no arguments.

Recorded (and compared by the harness):
  env       interpreter version, sys.flags.optimize, a hash() probe
            (integrity check: reference and candidate must agree)
  module    ordered stdout/stderr transcript of module execution, and its
            outcome: returned, or the raised exception
  globals   description of every non-dunder module global after execution
  observe   transcript and outcome (return value or exception) of observe()
  finalize  transcript of an explicit gc.collect() after observe()
            (automatic GC is disabled while the fixture runs, so cyclic
            garbage is finalized only here)
  process   the worker's own stdout/stderr, i.e. anything printed at
            interpreter exit (atexit handlers, late finalizers)
Exceptions are described by type, str(), args, __cause__, __context__,
__suppress_context__, __notes__ and ExceptionGroup members.  Values are
described structurally (see describe()).  The default-repr address
" at 0x..." is normalized; nothing else is.

Not recorded (outside the observation contract): tracebacks and line numbers,
code-object attributes, source text, warning locations, object identities
and addresses, timing.
"""

import argparse
import builtins
import gc
import importlib.util
import inspect
import io
import json
import marshal
import re
import sys
import types
import warnings

_dumps = json.dumps
_open = open
_ADDR = re.compile(r' at 0x[0-9A-Fa-f]+')
_BaseExceptionGroup = getattr(builtins, 'BaseExceptionGroup', None)
MAX_DEPTH = 6
MAX_ITEMS = 200
SCALARS = (type(None), bool, int, float, complex, str, bytes, type(Ellipsis),
           type(NotImplemented))
# Class-dict entries created implicitly by type() or carrying line numbers;
# every other entry, dunder methods included, is part of a class description.
IMPLICIT_CLASS_ATTRS = frozenset(('__module__', '__dict__', '__weakref__', '__firstlineno__'))


def norm(text):
    return _ADDR.sub(' at 0x?', text)


def type_name(t):
    mod = getattr(t, '__module__', None)
    qual = getattr(t, '__qualname__', None) or getattr(t, '__name__', '?')
    return qual if mod in (None, 'builtins') else '%s.%s' % (mod, qual)


def safe(fn, *args):
    try:
        return fn(*args)
    except BaseException as e:
        return '<%s raised %s>' % (getattr(fn, '__name__', 'call'), type(e).__name__)


def is_dunder(name):
    return name.startswith('__') and name.endswith('__')


def signature_text(func):
    """Parameter list with defaults, without annotations (annotations are
    evaluated lazily from 3.14 and could run fixture code; fixtures observe
    annotations explicitly when they matter)."""
    try:
        if sys.version_info >= (3, 14):
            import annotationlib
            sig = inspect.signature(func, annotation_format=annotationlib.Format.STRING)
        else:
            sig = inspect.signature(func)
        params = [p.replace(annotation=inspect.Parameter.empty)
                  for p in sig.parameters.values()]
        sig = sig.replace(parameters=params, return_annotation=inspect.Signature.empty)
        return norm(str(sig))
    except BaseException as e:
        return '<no signature: %s>' % type(e).__name__


def describe(obj, depth=0, active=None):
    t = type(obj)
    if t in SCALARS:
        return ['v', repr(obj)]
    if depth >= MAX_DEPTH:
        return ['max-depth', type_name(t)]
    if active is None:
        active = set()
    if id(obj) in active:
        return ['cycle', type_name(t)]
    active.add(id(obj))
    try:
        return _describe(obj, t, depth, active)
    finally:
        active.discard(id(obj))


def _describe(obj, t, depth, active):
    def d(x):
        return describe(x, depth + 1, active)

    if t is list or t is tuple:
        items = list(obj)
        return [t.__name__, [d(x) for x in items[:MAX_ITEMS]], len(items)]
    if t is dict:
        items = list(obj.items())
        return ['dict', [[d(k), d(v)] for k, v in items[:MAX_ITEMS]], len(items)]
    if t is set or t is frozenset:
        members = sorted(_dumps(d(x), sort_keys=True) for x in obj)
        return [t.__name__, members[:MAX_ITEMS], len(members)]
    if isinstance(obj, BaseException):
        return ['exception', describe_exc(obj, depth + 1)]
    if isinstance(obj, type):
        attrs = sorted((k, v) for k, v in vars(obj).items() if k not in IMPLICIT_CLASS_ATTRS)
        return ['class', type_name(obj), [type_name(b) for b in obj.__bases__],
                type_name(type(obj)), [[k, d(v)] for k, v in attrs]]
    if isinstance(obj, types.FunctionType):
        return ['function', obj.__qualname__, signature_text(obj)]
    if isinstance(obj, types.MethodType):
        return ['method', getattr(obj.__func__, '__qualname__', '?'),
                type_name(type(obj.__self__))]
    if isinstance(obj, (types.BuiltinFunctionType, types.BuiltinMethodType)):
        return ['builtin', getattr(obj, '__qualname__', '?')]
    if isinstance(obj, (staticmethod, classmethod)):
        return [t.__name__, d(obj.__func__)]
    if isinstance(obj, property):
        return ['property', d(obj.fget), d(obj.fset), d(obj.fdel)]
    if isinstance(obj, types.GeneratorType):
        return ['generator', obj.__qualname__]
    if isinstance(obj, types.CoroutineType):
        return ['coroutine', obj.__qualname__]
    if isinstance(obj, types.AsyncGeneratorType):
        return ['async_generator', obj.__qualname__]
    if isinstance(obj, types.ModuleType):
        return ['module', obj.__name__]
    return ['object', type_name(t), norm(safe(repr, obj))]


def describe_exc(exc, depth=0):
    out = {
        'type': type_name(type(exc)),
        'str': norm(safe(str, exc)),
        'args': describe(exc.args, depth + 1),
        'suppress_context': bool(exc.__suppress_context__),
    }
    if depth < 4:
        if exc.__cause__ is not None:
            out['cause'] = describe_exc(exc.__cause__, depth + 1)
        if exc.__context__ is not None:
            out['context'] = describe_exc(exc.__context__, depth + 1)
    notes = getattr(exc, '__notes__', None)
    if notes is not None:
        out['notes'] = describe(notes, depth + 1)
    if _BaseExceptionGroup is not None and isinstance(exc, _BaseExceptionGroup):
        out['group'] = [describe_exc(e, depth + 1) for e in exc.exceptions]
    return out


class _Tee(io.TextIOBase):
    def __init__(self, stream, log):
        self._stream = stream
        self._log = log

    @property
    def encoding(self):
        return 'utf-8'

    def writable(self):
        return True

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError('write() argument must be str, not %s' % type(s).__name__)
        self._log.append((self._stream, s))
        return len(s)

    def flush(self):
        pass


def _merge(log):
    out = []
    for stream, text in log:
        if out and out[-1][0] == stream:
            out[-1][1] += text
        else:
            out.append([stream, text])
    return [[s, norm(t)] for s, t in out if t]


def run_captured(fn, described=False):
    log = []
    saved = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = _Tee('out', log), _Tee('err', log)
    try:
        try:
            value = fn()
            outcome = {'returned': value if described else describe(value)}
        except BaseException as e:
            outcome = {'raised': describe_exc(e)}
    finally:
        sys.stdout, sys.stderr = saved
    outcome['transcript'] = _merge(log)
    return outcome


def _formatwarning(message, category, filename, lineno, line=None):
    return '%s: %s\n' % (category.__name__, message)


def load_code(args):
    if args.pyc:
        with _open(args.pyc, 'rb') as f:
            data = f.read()
        if data[:4] != importlib.util.MAGIC_NUMBER:
            raise SystemExit('observe: .pyc magic does not match this interpreter')
        return marshal.loads(data[16:])
    with _open(args.source, 'rb') as f:
        data = f.read()
    # Compile-time warnings (e.g. SyntaxWarning) belong to the source text, not to
    # runtime behavior; the reference .pyc emits none, so they are not observed here.
    # The syntax stage records them separately.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return compile(data, args.filename, 'exec', dont_inherit=True,
                       optimize=args.optimize)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pyc')
    ap.add_argument('--source')
    ap.add_argument('--optimize', type=int, default=0)
    ap.add_argument('--filename', default='fixture.py')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    code = load_code(args)
    warnings.formatwarning = _formatwarning
    warnings.simplefilter('always')
    # Automatic cyclic GC would run finalizers at allocation-dependent points;
    # cycles are collected only by the explicit gc.collect() in "finalize".
    gc.disable()

    mod = types.ModuleType('fixture')
    ns = mod.__dict__
    ns['__file__'] = 'fixture.py'
    ns['__builtins__'] = builtins
    sys.modules['fixture'] = mod

    obs = {'env': {'version': '%d.%d.%d' % sys.version_info[:3],
                   'optimize': sys.flags.optimize,
                   'hash_probe': hash('pycdc-harness')}}
    obs['module'] = run_captured(lambda: exec(code, ns))
    obs['globals'] = run_captured(
        lambda: [[k, describe(ns[k])] for k in sorted(ns) if not is_dunder(k)],
        described=True)
    entry = ns.get('observe')
    obs['observe'] = run_captured(entry) if callable(entry) else None
    obs['finalize'] = run_captured(lambda: (gc.collect(), None)[1])

    with _open(args.out, 'w', encoding='utf-8') as f:
        f.write(_dumps(obs, sort_keys=True, ensure_ascii=True))


if __name__ == '__main__':
    main()
