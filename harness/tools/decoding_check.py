#!/usr/bin/env python3
"""Part 4 decoding checks: pycdas against the matching CPython.

  dis        For every .pyc of a difftest run, compare pycdas's output with
             the reference decoding of the same interpreter
             (workers/dis_dump.py), at the semantic level: code-object
             fields, names, local and cell names, constants, every
             instruction (offset, opcode, raw operand and what the operand
             means: jump target, name, constant, local, comparison) and the
             exception table.  Formatting is not compared.

Every pycdas run and every reference run happens inside the harness sandbox
(harness/sandbox.py).  The .pyc files are only loaded, never executed.

  headers    Rewrite every .pyc with the checked-hash and unchecked-hash
             headers py_compile writes (workers/pyc_variants.py) and require
             pycdas and pycdc to behave identically on all three forms.

  formats    Crafted inputs pycdc cannot decode (empty, truncated headers,
             unknown and future magic, unknown marshal type codes, text, a
             directory, a missing file, -c -v with an unsupported version):
             each must exit nonzero with a message on stderr, and must not
             look like a successful listing.

  malformed  Deterministic truncations and seeded byte mutations of every
             .pyc: pycdas and pycdc must never crash, hang or hit the output
             limit.  Exit status 0 is allowed (a mutation can leave a valid
             file).  Failing inputs are kept under --workdir.

  generate   Write the generated decoding inputs (operands too wide for one
             EXTENDED_ARG prefix) to a directory (the decoding-generated
             suite).

usage: decoding_check.py dis --workroot build/difftest [--suites features]
           [--versions 3.13,3.14] [--pycdas build/release/pycdas]
           --out DIS.json [--summary DIS.md]
       decoding_check.py headers|malformed --workroot W [--suites S] --out OUT.json
       decoding_check.py formats --workroot W --out OUT.json
       decoding_check.py generate --out DIR
"""

import argparse
import ast
import collections
import glob
import hashlib
import json
import math
import os
import re
import shutil
import sys
import time

TOOLS = os.path.dirname(os.path.realpath(__file__))
HARNESS = os.path.dirname(TOOLS)
REPO = os.path.dirname(HARNESS)
sys.path.insert(0, HARNESS)
import difftest  # noqa: E402
import sandbox  # noqa: E402

TIMEOUT = 60
MAX_EXAMPLES = 8


# ------------------------------------------------------------ pycdas parsing

INSTR = re.compile(r'^(\d+)\s+(\S+)\s*(.*?)\s*$')
OPERAND = [
    ('none', re.compile(r'^$')),
    ('target', re.compile(r'^(-?\d+) \(to (-?\d+)\)$')),
    ('invalid', re.compile(r'^(-?\d+) <INVALID>$')),
    ('paren', re.compile(r'^(-?\d+) \((.*)\)$')),
    ('colon', re.compile(r'^(-?\d+): (.*)$')),
    ('plain', re.compile(r'^(-?\d+)$')),
]
EXC = re.compile(r'^(\d+) to (\d+) -> (\d+) \[(\d+)\]\s*(lasti)?\s*$')
FIELDS = {
    'File Name': 'filename', 'Object Name': 'name', 'Qualified Name': 'qualname',
    'Arg Count': 'argcount', 'Pos Only Arg Count': 'posonlyargcount',
    'KW Only Arg Count': 'kwonlyargcount', 'Locals': 'nlocals', 'Stack Size': 'stacksize',
    'Flags': 'flags',
}
SECTIONS = {'[Names]': 'names', '[Var Names]': 'varnames', '[Locals+Names]': 'localsplus',
            '[Free Vars]': 'freevars', '[Cell Vars]': 'cellvars', '[Constants]': 'consts',
            '[Disassembly]': 'instructions', '[Exception Table]': 'exception_table'}
OPENERS = {'(': ('tuple', ')'), '[': ('list', ']'), '{': ('set', '}'),
           'frozenset({': ('frozenset', '})'), 'slice(': ('slice', ')')}


class ParseError(Exception):
    pass


def depth(line):
    n = len(line) - len(line.lstrip(' '))
    return n // 4


def parse_object(lines, i, level):
    """Parse one output_object() item that starts at lines[i] (indent level).
    Returns (normalized value, next index)."""
    text = lines[i][level * 4:]
    if text == '[Code]':
        return parse_code(lines, i + 1, level + 1)
    if text in OPENERS:
        kind, closer = OPENERS[text]
        items, i = [], i + 1
        while i < len(lines) and not (depth(lines[i]) == level and
                                      lines[i][level * 4:] == closer):
            if depth(lines[i]) <= level:
                raise ParseError('unterminated %s at line %d' % (kind, i + 1))
            value, i = parse_object(lines, i, level + 1)
            items.append(value)
        if i >= len(lines):
            raise ParseError('unterminated %s' % kind)
        if kind == 'frozenset':
            items = sorted(items, key=lambda x: json.dumps(x, sort_keys=True))
        return [kind, items], i + 1
    return scalar(text), i + 1


def parse_code(lines, i, level):
    code = {'consts': [], 'names': [], 'instructions': [], 'exception_table': []}
    section = None
    while i < len(lines) and depth(lines[i]) >= level:
        line = lines[i]
        text = line[level * 4:]
        if depth(line) == level:
            if text in SECTIONS:
                section = SECTIONS[text]
                code.setdefault(section, [])
                i += 1
                continue
            key, sep, value = text.partition(': ')
            if sep and key in FIELDS:
                field = FIELDS[key]
                if field == 'flags':
                    code[field] = int(value.split()[0], 16)
                elif field in ('filename', 'name', 'qualname'):
                    code[field] = value
                else:
                    code[field] = int(value)
                section = None
                i += 1
                continue
            raise ParseError('unexpected line %d: %r' % (i + 1, line))
        if section is None:
            raise ParseError('content outside a section at line %d' % (i + 1))
        inner = line[(level + 1) * 4:]
        if section == 'instructions':
            code['instructions'].append(parse_instruction(inner))
            i += 1
        elif section == 'exception_table':
            m = EXC.match(inner)
            if not m:
                raise ParseError('bad exception table line %d: %r' % (i + 1, line))
            code['exception_table'].append([int(m.group(1)), int(m.group(2)),
                                            int(m.group(3)), int(m.group(4)),
                                            bool(m.group(5))])
            i += 1
        else:
            value, i = parse_object(lines, i, level + 1)
            code[section].append(value)
    return ['code', code], i


def parse_instruction(text):
    m = INSTR.match(text)
    if not m:
        raise ParseError('bad instruction line: %r' % text)
    ins = {'offset': int(m.group(1)), 'opname': m.group(2), 'arg': None, 'operand': None}
    rest = m.group(3)
    for kind, pat in OPERAND:
        om = pat.match(rest)
        if om:
            if kind != 'none':
                ins['arg'] = int(om.group(1))
            if kind in ('target', 'paren', 'colon'):
                ins['operand'] = [kind, om.group(2)]
            elif kind == 'invalid':
                ins['operand'] = ['invalid', None]
            return ins
    ins['operand'] = ['unparsed', rest]
    return ins


def scalar(text):
    """Normalize a constant as pycdas prints it (output_object or print_const)
    to the representation workers/dis_dump.py uses; ['text', ...] if it is
    not a Python literal at all."""
    if text.startswith('<CODE> '):
        return ['codename', text[len('<CODE> '):]]
    try:
        node = ast.parse(text, mode='eval').body
    except SyntaxError:
        return ['text', text]
    try:
        return literal(node)
    except ValueError:
        return ['text', text]


def literal(node):
    if isinstance(node, ast.Constant):
        return pyvalue(node.value)
    if isinstance(node, ast.Tuple):
        return ['tuple', [literal(e) for e in node.elts]]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = ast.literal_eval(node)
        return pyvalue(value)
    if isinstance(node, ast.BinOp):
        return pyvalue(ast.literal_eval(node))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        name, args = node.func.id, node.args
        if name == 'frozenset' and len(args) == 1 and isinstance(args[0], ast.Set):
            items = [literal(e) for e in args[0].elts]
            return ['frozenset', sorted(items, key=lambda x: json.dumps(x, sort_keys=True))]
        if name == 'frozenset' and not args:
            return ['frozenset', []]
        if name == 'slice' and len(args) == 3:
            return ['slice', [literal(a) for a in args]]
        if name == 'float' and len(args) == 1 and isinstance(args[0], ast.Constant):
            return pyvalue(float(args[0].value))
        if name == 'complex' and len(args) == 2:
            parts = [literal(a) for a in args]
            if all(p[0] == 'float' for p in parts):
                return pyvalue(complex(float(parts[0][1]), float(parts[1][1])))
    raise ValueError('not a literal')


def pyvalue(value):
    if value is None or value is Ellipsis or isinstance(value, bool):
        return ['const', repr(value)]
    if isinstance(value, int):
        return ['int', str(value)]
    if isinstance(value, float):
        return ['float', repr(value)]
    if isinstance(value, complex):
        return ['complex', repr(value.real), repr(value.imag)]
    if isinstance(value, str):
        return ['str', value]
    if isinstance(value, bytes):
        return ['bytes', value.hex()]
    raise ValueError('unsupported literal')


def parse_pycdas(text):
    lines = [l for l in text.split('\n') if l.strip()]
    if not lines or not re.match(r'^.* \(Python \d+\.\d+.*\)$', lines[0]):
        raise ParseError('missing header line')
    if len(lines) < 2 or lines[1] != '[Code]':
        raise ParseError('no code object')
    value, i = parse_code(lines, 2, 1)
    if i != len(lines):
        raise ParseError('trailing output at line %d' % (i + 1))
    return value[1]


# ---------------------------------------------------------------- comparing

def const_equal(ref, got):
    """ref from dis_dump, got from scalar()/parse_object()."""
    if ref[0] == 'code':
        if got[0] == 'code':
            return True                      # compared separately, recursively
        return got[0] == 'codename' and got[1] == ref[1]['name']
    if ref[0] in ('tuple', 'frozenset', 'slice'):
        if got[0] != ref[0] or len(got[1]) != len(ref[1]):
            return False
        if ref[0] == 'frozenset':
            return sorted(json.dumps(x, sort_keys=True) for x in ref[1]) == \
                sorted(json.dumps(x, sort_keys=True) for x in got[1]) or \
                all(any(const_equal(r, g) for g in got[1]) for r in ref[1])
        return all(const_equal(r, g) for r, g in zip(ref[1], got[1]))
    if ref[0] == 'float' and got[0] == 'float':
        return same_float(float(ref[1]), float(got[1]))
    if ref[0] == 'complex' and got[0] == 'complex':
        return (same_float(float(ref[1]), float(got[1]))
                and same_float(float(ref[2]), float(got[2])))
    return ref == got


def same_float(a, b):
    """Equal including the sign of zero; any NaN equals any NaN."""
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    return a == b and math.copysign(1, a) == math.copysign(1, b)


def short(v, n=120):
    s = json.dumps(v, sort_keys=True) if not isinstance(v, str) else v
    return s if len(s) <= n else s[:n] + '…'


def compare_operand(ref, got, opname):
    """Returns a category name for a mismatch, or None."""
    meaning = ref['meaning']
    if meaning is None:
        return None
    kind, value = meaning
    operand = got['operand']
    if operand is None:
        return 'operand_missing'
    okind, text = operand
    if kind == 'target':
        if okind != 'target':
            return 'target_missing'
        return None if int(text) == value else 'jump_target'
    if kind == 'name':
        if okind != 'colon':
            return 'name_missing'
        if text.startswith('NULL + '):
            text = text[len('NULL + '):]
        return None if text == value else 'name'
    if kind == 'local':
        if okind != 'colon':
            return 'local_missing'
        return None if text == value else 'local'
    if kind == 'locals':
        if okind != 'colon':
            return 'local_missing'
        return None if [t.strip() for t in text.split(',')] == value else 'local'
    if kind == 'compare':
        if okind != 'paren':
            return 'compare_missing'
        return None if text == value else 'compare'
    if kind == 'const':
        if okind != 'colon':
            return 'const_missing'
        return None if const_equal(value, scalar(text)) else 'const'
    return None


def compare_code(ref, got, path, problems):
    def bad(category, detail):
        problems.append({'category': category, 'path': path, 'detail': detail})

    for field in ('filename', 'name', 'qualname', 'argcount', 'posonlyargcount',
                  'kwonlyargcount', 'stacksize', 'flags'):
        if ref.get(field) is None:
            continue
        if got.get(field) != ref[field]:
            bad('field:' + field, 'reference %s, pycdas %s' % (short(ref[field]),
                                                                short(got.get(field))))
    if ref.get('localsplus') is None and got.get('nlocals') != ref['nlocals']:
        bad('field:nlocals', 'reference %s, pycdas %s' % (ref['nlocals'], got.get('nlocals')))

    def names(ref_list, got_list, category):
        got_names = [g[1] if g and g[0] == 'str' else short(g) for g in got_list]
        if got_names != ref_list:
            bad(category, 'reference %s, pycdas %s' % (short(ref_list), short(got_names)))

    names(ref['names'], got.get('names', []), 'names')
    if ref.get('localsplus') is not None:
        names(ref['localsplus'], got.get('localsplus', []), 'localsplus')
    else:
        names(ref['varnames'], got.get('varnames', []), 'varnames')
        names(ref['freevars'], got.get('freevars', []), 'freevars')
        names(ref['cellvars'], got.get('cellvars', []), 'cellvars')

    rconsts, gconsts = ref['consts'], got.get('consts', [])
    if len(rconsts) != len(gconsts):
        bad('consts', 'reference %d constants, pycdas %d' % (len(rconsts), len(gconsts)))
    for i, (rc, gc) in enumerate(zip(rconsts, gconsts)):
        if rc[0] == 'code':
            if gc[0] != 'code':
                bad('consts', 'constant %d: reference code object, pycdas %s' % (i, short(gc)))
            else:
                compare_code(rc[1], gc[1], path + [i], problems)
        elif not const_equal(rc, gc):
            bad('consts', 'constant %d: reference %s, pycdas %s' % (i, short(rc), short(gc)))

    rins = {x['offset']: x for x in ref['instructions']}
    gins = {x['offset']: x for x in got.get('instructions', [])}
    for off in sorted(set(rins) - set(gins)):
        bad('instr_missing', 'offset %d %s' % (off, rins[off]['opname']))
    for off in sorted(set(gins) - set(rins)):
        bad('instr_extra', 'offset %d %s %s' % (off, gins[off]['opname'],
                                                 short(gins[off]['operand'])))
    for off in sorted(set(rins) & set(gins)):
        r, g = rins[off], gins[off]
        if r['opname'] != g['opname']:
            bad('opname', 'offset %d: reference %s, pycdas %s' % (off, r['opname'], g['opname']))
            continue
        if g['operand'] and g['operand'][0] in ('invalid', 'unparsed'):
            bad('operand_' + g['operand'][0], 'offset %d %s: %s' % (off, r['opname'],
                                                                   short(g['operand'])))
            continue
        if r['arg'] != g['arg']:
            bad('arg', 'offset %d %s: reference %s, pycdas %s' % (off, r['opname'], r['arg'],
                                                                g['arg']))
            continue
        cat = compare_operand(r, g, r['opname'])
        if cat:
            bad(cat, 'offset %d %s %s: reference %s, pycdas %s' % (
                off, r['opname'], r['arg'], short(r['meaning'][1]), short(g['operand'])))

    if ref.get('exception_table') is not None:
        if got.get('exception_table', []) != ref['exception_table']:
            bad('exception_table', 'reference %s, pycdas %s' % (
                short(ref['exception_table']), short(got.get('exception_table'))))


# ---------------------------------------------------------------- running

class Context(object):
    """Interpreters, sandbox, binaries and the cases a check runs on."""

    def __init__(self, args, need_cases=True):
        self.interps = difftest.resolve_interpreters()
        self.mode = sandbox.default_mode()
        if self.mode is None:
            sys.exit('no sandbox available on this platform')
        self.workroot = os.path.realpath(args.workroot) if getattr(args, 'workroot', None) else None
        self.versions = args.versions.split(',') if getattr(args, 'versions', None) else None
        self.pycdas = os.path.realpath(args.pycdas)
        self.pycdc = os.path.realpath(args.pycdc)
        self.out_dir = os.path.realpath(args.workdir)
        self.jobs = args.jobs
        self.cases = []
        if need_cases:
            self.cases = discover(self.workroot, args.suites.split(','), self.versions)
            if not self.cases:
                sys.exit('no .pyc files found under %s' % self.workroot)
        allow = {REPO, self.out_dir, os.path.dirname(self.pycdas), os.path.dirname(self.pycdc)}
        if self.workroot:
            allow.add(self.workroot)
        for e in self.interps.values():
            if e.get('path'):
                allow.add(os.path.dirname(os.path.dirname(os.path.realpath(e['path']))))
        self.read_allow = sorted(allow)

    def meta(self, start):
        return {
            'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'command': [os.path.relpath(sys.argv[0], REPO)] + sys.argv[1:],
            'pycdas': {'path': self.pycdas, 'sha256': sha256(self.pycdas)},
            'pycdc': {'path': self.pycdc, 'sha256': sha256(self.pycdc)},
            'source_head': difftest.git(REPO, 'rev-parse', 'HEAD'),
            'harness_dirty': (difftest.git(REPO, 'status', '--porcelain', '--', 'harness')
                              or '').splitlines(),
            'decompiler_source_dirty': (difftest.git(
                REPO, 'status', '--porcelain', '--', '*.cpp', '*.h', '*.inl', 'CMakeLists.txt',
                ':(exclude)harness') or '').splitlines(),
            'interpreters': {m: {'pinned': e['pinned'], 'status': e['status']}
                             for m, e in self.interps.items()},
            'workroot': self.workroot,
            'wall_seconds': round(time.monotonic() - start, 1),
        }


def discover(workroot, suites, versions):
    found = []
    for suite in suites:
        for pyc in sorted(glob.glob(os.path.join(workroot, suite, '*', '*-O*', 'fixture.pyc'))):
            case_dir = os.path.dirname(pyc)
            ver, _, opt = os.path.basename(case_dir).partition('-O')
            if versions and ver not in versions:
                continue
            fid = os.path.basename(os.path.dirname(case_dir)).replace('__', '/')
            found.append({'suite': suite, 'fixture': fid, 'version': ver, 'opt': int(opt),
                          'pyc': os.path.realpath(pyc)})
    return found


def case_key(c):
    return (c['suite'], c['fixture'], difftest.version_tuple(c['version']), c['opt'])


def case_dir(root, c):
    return os.path.join(root, c['suite'], c['fixture'].replace('/', '__'),
                        '%s-O%d' % (c['version'], c['opt']))


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_report(path, data):
    with open(path, 'w') as f:
        f.write(difftest.scrub_paths(json.dumps(data, indent=1, sort_keys=True)) + '\n')


def run_tool(job, binary, argv, wd, tag, timeout=TIMEOUT):
    """Run pycdas or pycdc in the sandbox; returns a small outcome record.
    The input path (the last argument) is replaced by <input> in stderr."""
    os.makedirs(wd, exist_ok=True)
    r = sandbox.run([binary] + argv, wd, job['mode'], timeout, read_allow=job['read_allow'],
                    tag=tag)
    return {'returncode': r.returncode, 'timed_out': r.timed_out,
            'signal': r.signal_name() if r.signal else None,
            'stdout_sha256': sha256(os.path.join(wd, tag + '.stdout')),
            'stdout_head': r.stdout[:400].decode('utf-8', 'replace'),
            'stderr': r.stderr[:600].decode('utf-8', 'replace').replace(argv[-1], '<input>')}


def outcome(res):
    if res['timed_out']:
        return 'timeout'
    if res['signal'] == 'SIGXFSZ':
        return 'output_limit'
    if res['signal']:
        return 'crash'
    return 'exit0' if res['returncode'] == 0 else 'error'


# --------------------------------------------------------------------- dis

def run_pycdas(job):
    wd = job['workdir']
    os.makedirs(wd, exist_ok=True)
    r = sandbox.run([job['pycdas'], job['pyc']], wd, job['mode'], TIMEOUT,
                    read_allow=job['read_allow'], tag='pycdas')
    res = {'workdir': wd, 'returncode': r.returncode, 'timed_out': r.timed_out,
           'signal': r.signal_name() if r.signal else None,
           'stderr': r.stderr.decode('utf-8', 'replace')[:2000]}
    if r.timed_out or r.signal or r.returncode != 0:
        res['status'] = 'pycdas_failed'
        return res
    try:
        # The full listing: Result.stdout is truncated for large outputs.
        with open(os.path.join(wd, 'pycdas.stdout'), 'rb') as f:
            res['parsed'] = parse_pycdas(f.read().decode('utf-8', 'replace'))
        res['status'] = 'parsed'
    except ParseError as e:
        res['status'] = 'unparsable'
        res['error'] = str(e)
    return res


def reference(minor, entry, pycs, workdir, mode, read_allow):
    os.makedirs(workdir, exist_ok=True)
    out = os.path.join(workdir, 'reference-%s.json' % minor)
    argv = [entry['path'], '-I', '-B', os.path.join(HARNESS, 'workers', 'dis_dump.py'), out]
    results = {}
    # Batches of at most ~1 MB of .pyc keep each dump below the sandbox's
    # output-size limit; a larger file goes in a batch of its own.
    batches, batch, size = [], [], 0
    for pyc in pycs:
        n = os.path.getsize(pyc)
        if batch and size + n > 1 << 20:
            batches.append(batch)
            batch, size = [], 0
        batch.append(pyc)
        size += n
    if batch:
        batches.append(batch)
    for batch in batches:
        r = sandbox.run(argv + batch, workdir, mode, 600, read_allow=read_allow,
                        env_extra=difftest.PY_ENV, tag='reference-' + minor)
        if r.returncode != 0:
            sys.exit('reference dump failed for %s: %s' % (minor, r.stderr.decode()[-800:]))
        with open(out) as f:
            results.update(json.load(f)['files'])
    return results


def cmd_dis(args):
    ctx = Context(args)
    out_dir = os.path.join(ctx.out_dir, 'dis')
    refs = {}
    by_version = collections.defaultdict(list)
    for c in ctx.cases:
        by_version[c['version']].append(c['pyc'])
    for minor, pycs in sorted(by_version.items()):
        entry = ctx.interps.get(minor)
        if not entry or entry['status'] != 'ok':
            sys.exit('interpreter %s unavailable' % minor)
        refs.update(reference(minor, entry, pycs, os.path.join(out_dir, 'reference'), ctx.mode,
                              ctx.read_allow))

    jobs = [dict(c, pycdas=ctx.pycdas, workdir=case_dir(out_dir, c), mode=ctx.mode,
                 read_allow=ctx.read_allow) for c in ctx.cases]
    start = time.monotonic()
    # execute() returns results in completion order; each carries its workdir.
    results = {res['workdir']: res for res in difftest.execute(run_pycdas, jobs, ctx.jobs)}

    report_cases = []
    for job in jobs:
        res = results[job['workdir']]
        ref = refs.get(job['pyc'], {'error': 'no reference'})
        case = {k: job[k] for k in ('suite', 'fixture', 'version', 'opt')}
        case['pyc_sha256'] = sha256(job['pyc'])
        if 'error' in ref:
            case.update(status='reference_failed', detail=ref['error'])
        elif res['status'] != 'parsed':
            case.update(status=res['status'], detail=res.get('error') or res['stderr'][:300]
                        or 'exit %s signal %s' % (res['returncode'], res['signal']))
        else:
            problems = []
            compare_code(ref['code'], res['parsed'], [], problems)
            counts = collections.Counter(p['category'] for p in problems)
            case.update(status='match' if not problems else 'mismatch',
                        categories=dict(counts),
                        examples=problems[:MAX_EXAMPLES])
        report_cases.append(case)

    data = {'schema': 1, 'kind': 'decoding-dis', 'meta': ctx.meta(start),
            'cases': sorted(report_cases, key=case_key)}
    write_report(args.out, data)
    summary = render_dis(data)
    if args.summary:
        with open(args.summary, 'w') as f:
            f.write(difftest.scrub_paths(summary))
    sys.stdout.write(difftest.scrub_paths(summary.split('\n## Examples')[0]))
    return 0 if all(c['status'] == 'match' for c in report_cases) else 1


def render_dis(data):
    cases = data['cases']
    versions = sorted({c['version'] for c in cases}, key=difftest.version_tuple)
    out = ['# pycdas versus dis', '',
           'Generated by `harness/tools/decoding_check.py dis`. pycdas `%s`, source `%s`.'
           % (data['meta']['pycdas']['sha256'][:16], (data['meta']['source_head'] or '?')[:12]),
           '', '| suite | version | files | match | mismatch | pycdas failed | unparsable | '
           'reference failed |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for suite in sorted({c['suite'] for c in cases}):
        for v in versions:
            cs = [c for c in cases if c['suite'] == suite and c['version'] == v]
            if not cs:
                continue
            st = collections.Counter(c['status'] for c in cs)
            out.append('| %s | %s | %d | %d | %d | %d | %d | %d |' % (
                suite, v, len(cs), st['match'], st['mismatch'], st['pycdas_failed'],
                st['unparsable'], st['reference_failed']))
    out += ['', '## Mismatch categories (files affected / occurrences)', '',
            '| category | ' + ' | '.join(versions) + ' |', '|' + ' --- |' * (len(versions) + 1)]
    cats = sorted({k for c in cases for k in c.get('categories', {})})
    for cat in cats:
        row = []
        for v in versions:
            cs = [c for c in cases if c['version'] == v and cat in c.get('categories', {})]
            row.append('%d / %d' % (len(cs), sum(c['categories'][cat] for c in cs)) if cs else '')
        out.append('| %s | %s |' % (cat, ' | '.join(row)))
    if not cats:
        out.append('| none | ' + ' | '.join('' for _ in versions) + ' |')
    out += ['', '## Examples', '']
    seen = collections.Counter()
    for c in cases:
        for p in c.get('examples', []):
            key = (c['version'], p['category'])
            if seen[key] >= 3:
                continue
            seen[key] += 1
            out.append('- %s `%s` %s -O%d, code %s: **%s** %s' % (
                c['suite'], c['fixture'], c['version'], c['opt'], p['path'] or '<module>',
                p['category'], p['detail']))
        if c['status'] not in ('match', 'mismatch'):
            key = (c['version'], c['status'])
            if seen[key] < 3:
                seen[key] += 1
                out.append('- %s `%s` %s -O%d: **%s** %s' % (
                    c['suite'], c['fixture'], c['version'], c['opt'], c['status'],
                    short(c.get('detail', ''), 300)))
    if not seen:
        out.append('- none')
    return '\n'.join(out) + '\n'


# ----------------------------------------------------------------- headers

def run_header_case(job):
    """pycdas and pycdc output for the timestamp .pyc and its two hash-based
    variants, which must be identical (they share the marshalled code)."""
    res = {'key': job['key'], 'runs': {}}
    for variant, pyc in job['variants'].items():
        wd = os.path.join(job['workdir'], variant)
        for tool, binary in (('pycdas', job['pycdas']), ('pycdc', job['pycdc'])):
            res['runs']['%s/%s' % (variant, tool)] = run_tool(job, binary, [pyc], wd, tool)
    return res


def cmd_headers(args):
    ctx = Context(args)
    start = time.monotonic()
    out_dir = os.path.join(ctx.out_dir, 'headers')
    by_version = collections.defaultdict(list)
    jobs = []
    for c in ctx.cases:
        wd = case_dir(out_dir, c)
        variants = {'timestamp': c['pyc']}
        spec = {'source': os.path.join(os.path.dirname(c['pyc']), 'fixture.py'), 'pyc': c['pyc']}
        for kind in ('checked', 'unchecked'):
            path = os.path.join(wd, kind + '-hash', 'fixture.pyc')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            spec[kind] = path
            variants[kind + '-hash'] = path
        by_version[c['version']].append(spec)
        jobs.append(dict(c, key=case_key(c), variants=variants, workdir=wd, pycdas=ctx.pycdas,
                         pycdc=ctx.pycdc, mode=ctx.mode, read_allow=ctx.read_allow))
    for minor, specs in sorted(by_version.items()):
        entry = ctx.interps[minor]
        jobs_file = os.path.join(out_dir, 'variants-%s.json' % minor)
        with open(jobs_file, 'w') as f:
            json.dump(specs, f)
        r = sandbox.run([entry['path'], '-I', '-B',
                         os.path.join(HARNESS, 'workers', 'pyc_variants.py'), jobs_file],
                        out_dir, ctx.mode, 300, read_allow=ctx.read_allow,
                        env_extra=difftest.PY_ENV, tag='variants-' + minor)
        if r.returncode != 0:
            sys.exit('writing hash-based variants failed for %s: %s' % (
                minor, r.stderr.decode()[-800:]))
    results = {tuple(r['key']): r for r in difftest.execute(run_header_case, jobs, ctx.jobs)}
    report = []
    for job in jobs:
        runs = results[job['key']]['runs']
        case = {k: job[k] for k in ('suite', 'fixture', 'version', 'opt')}
        problems = []
        for tool in ('pycdas', 'pycdc'):
            base = runs['timestamp/' + tool]
            for variant in ('checked-hash', 'unchecked-hash'):
                other = runs['%s/%s' % (variant, tool)]
                if outcome(other) != outcome(base):
                    problems.append('%s %s: outcome %s, timestamp .pyc %s' % (
                        variant, tool, outcome(other), outcome(base)))
                elif outcome(base) not in ('crash', 'timeout', 'output_limit'):
                    # A crash's partial output and signal vary between runs.
                    for field in ('returncode', 'stdout_sha256', 'stderr'):
                        if other[field] != base[field]:
                            problems.append('%s %s: %s differs from the timestamp .pyc '
                                            '(%s vs %s)' % (variant, tool, field,
                                                            short(other[field], 80),
                                                            short(base[field], 80)))
            # Decoding must work: pycdas must succeed on every variant.  A pycdc
            # crash is a decompile-stage result, reported by `difftest.py run`.
            if tool == 'pycdas' and outcome(base) != 'exit0':
                problems.append('pycdas on the timestamp .pyc: %s' % outcome(base))
        case['pycdc_outcome'] = outcome(runs['timestamp/pycdc'])
        case['status'] = 'identical' if not problems else 'differs'
        if problems:
            case['problems'] = problems[:MAX_EXAMPLES]
        report.append(case)
    data = {'schema': 1, 'kind': 'decoding-headers', 'meta': ctx.meta(start),
            'cases': sorted(report, key=case_key)}
    write_report(args.out, data)
    st = collections.Counter(c['status'] for c in report)
    print('headers: %d cases, %d identical, %d differ' % (len(report), st['identical'],
                                                          st['differs']))
    for c in report:
        if c['status'] != 'identical':
            print('  %s %s %s -O%d: %s' % (c['suite'], c['fixture'], c['version'], c['opt'],
                                           c['problems'][0]))
    return 0 if st['differs'] == 0 else 1


# ----------------------------------------------------------------- formats

def format_inputs(ctx, inputs_dir):
    """Inputs pycdc cannot decode, each with the command-line options to use.
    Every one must fail with a message and a nonzero exit."""
    os.makedirs(inputs_dir, exist_ok=True)
    samples = {}
    for minor in ('3.13', '3.14'):
        found = sorted(glob.glob(os.path.join(ctx.workroot, 'features', '*',
                                              '%s-O0' % minor, 'fixture.pyc')))
        if not found:
            sys.exit('formats: no %s feature .pyc under %s' % (minor, ctx.workroot))
        with open(found[0], 'rb') as f:
            samples[minor] = f.read()
    cases = {
        'empty': (b'', []),
        'one_byte': (b'\r', []),
        'text_file': (b"print('hello')\n", []),
        'unknown_magic': (b'\x00\x00\r\n' + b'\x00' * 12 + b'N', []),
        'future_magic_3700': ((3700).to_bytes(2, 'little') + b'\r\n' + samples['3.14'][4:], []),
    }
    for minor, data in sorted(samples.items()):
        tag = minor.replace('.', '')
        cases['magic_only_%s' % tag] = (data[:4], [])
        cases['truncated_header_%s' % tag] = (data[:8], [])
        cases['header_only_%s' % tag] = (data[:16], [])
        cases['unknown_type_code_%s' % tag] = (data[:16] + b'?' + data[17:], [])
        cases['marshalled_unsupported_%s' % tag] = (data[16:], ['-c', '-v', minor])
    paths = {}
    for name, (data, opts) in sorted(cases.items()):
        path = os.path.join(inputs_dir, name + '.pyc')
        with open(path, 'wb') as f:
            f.write(data)
        paths[name] = (path, opts)
    paths['directory'] = (os.path.join(inputs_dir, 'a_directory.pyc'), [])
    os.makedirs(paths['directory'][0], exist_ok=True)
    paths['missing_file'] = (os.path.join(inputs_dir, 'does_not_exist.pyc'), [])
    return paths


def run_format_case(job):
    res = {'name': job['name'], 'runs': {}}
    for tool, binary in (('pycdas', job['pycdas']), ('pycdc', job['pycdc'])):
        res['runs'][tool] = run_tool(job, binary, job['opts'] + [job['path']],
                                     os.path.join(job['workdir'], tool), tool)
    return res


def cmd_formats(args):
    ctx = Context(args, need_cases=False)
    start = time.monotonic()
    out_dir = os.path.join(ctx.out_dir, 'formats')
    inputs = format_inputs(ctx, os.path.join(out_dir, 'inputs'))
    jobs = [dict(name=name, path=path, opts=opts, workdir=os.path.join(out_dir, 'runs', name),
                 pycdas=ctx.pycdas, pycdc=ctx.pycdc, mode=ctx.mode, read_allow=ctx.read_allow)
            for name, (path, opts) in sorted(inputs.items())]
    results = {r['name']: r for r in difftest.execute(run_format_case, jobs, ctx.jobs)}
    report = []
    for name in sorted(results):
        for tool, res in sorted(results[name]['runs'].items()):
            problems = []
            kind = outcome(res)
            if kind != 'error':
                problems.append('expected a clean nonzero exit, got %s (exit %s)'
                                % (kind, res['returncode']))
            if not res['stderr'].strip():
                problems.append('no message on stderr')
            if '(Python -1.-1)' in res['stdout_head'] or '<NULL>' in res['stdout_head']:
                problems.append('stdout looks like a successful listing: %r'
                                % res['stdout_head'][:120])
            report.append({'input': name, 'tool': tool, 'options': inputs[name][1],
                           'returncode': res['returncode'], 'outcome': kind,
                           'stderr': res['stderr'][:200],
                           'status': 'fails_clearly' if not problems else 'unclear',
                           'problems': problems})
    data = {'schema': 1, 'kind': 'decoding-formats', 'meta': ctx.meta(start), 'cases': report}
    write_report(args.out, data)
    bad = [c for c in report if c['status'] != 'fails_clearly']
    print('formats: %d runs, %d fail clearly, %d do not' % (len(report), len(report) - len(bad),
                                                            len(bad)))
    for c in report:
        print('  %-30s %-6s exit %-4s %s' % (c['input'], c['tool'], c['returncode'],
                                            c['stderr'].strip().split('\n')[-1][:70]
                                            if not c['problems'] else '; '.join(c['problems'])))
    return 0 if not bad else 1


# --------------------------------------------------------------- malformed

def malformed_variants(data, seed, mutations):
    """Deterministic truncations and byte mutations of one .pyc."""
    import random
    n = len(data)
    cuts = sorted({k for k in range(0, 24)} | {n * k // 16 for k in range(1, 16)} |
                  {n - 2, n - 1})
    variants = [('truncate:%d' % k, data[:k]) for k in cuts if 0 <= k < n]
    rng = random.Random(seed)
    for m in range(mutations):
        buf = bytearray(data)
        changes = []
        for _ in range(rng.randint(1, 4)):
            pos = rng.randrange(16, n) if n > 16 else rng.randrange(n)
            val = rng.randrange(256)
            buf[pos] = val
            changes.append('%d=%02x' % (pos, val))
        variants.append(('mutate:%s' % ','.join(changes), bytes(buf)))
    return variants


def run_malformed_case(job):
    with open(job['pyc'], 'rb') as f:
        data = f.read()
    tally = collections.Counter()
    bad = []
    seed = '%s:%s:%s:%s:%d' % (job['seed'], job['suite'], job['fixture'], job['version'],
                               job['opt'])
    for i, (desc, blob) in enumerate(malformed_variants(data, seed, job['mutations'])):
        wd = os.path.join(job['workdir'], str(i))
        os.makedirs(wd, exist_ok=True)
        path = os.path.join(wd, 'input.pyc')
        with open(path, 'wb') as f:
            f.write(blob)
        for tool, binary in (('pycdas', job['pycdas']), ('pycdc', job['pycdc'])):
            res = run_tool(job, binary, [path], wd, tool, timeout=job['timeout'])
            kind = outcome(res)
            tally['%s:%s' % (tool, kind)] += 1
            if kind in ('crash', 'timeout', 'output_limit'):
                bad.append({'tool': tool, 'variant': desc, 'outcome': kind,
                            'signal': res['signal'], 'stderr': res['stderr'][-200:]})
        if not bad or bad[-1]['variant'] != desc:
            shutil.rmtree(wd, ignore_errors=True)   # keep only failing inputs
    return {'key': job['key'], 'tally': dict(tally), 'bad': bad}


def cmd_malformed(args):
    ctx = Context(args)
    start = time.monotonic()
    out_dir = os.path.join(ctx.out_dir, 'malformed')
    jobs = [dict(c, key=case_key(c), workdir=case_dir(out_dir, c), pycdas=ctx.pycdas,
                 pycdc=ctx.pycdc, mode=ctx.mode, read_allow=ctx.read_allow, seed=args.seed,
                 mutations=args.mutations, timeout=args.timeout) for c in ctx.cases]
    results = {tuple(r['key']): r for r in difftest.execute(run_malformed_case, jobs, ctx.jobs)}
    report, totals = [], collections.Counter()
    for job in jobs:
        r = results[job['key']]
        totals.update(r['tally'])
        case = {k: job[k] for k in ('suite', 'fixture', 'version', 'opt')}
        case.update(tally=r['tally'], failures=r['bad'],
                    status='safe' if not r['bad'] else 'unsafe')
        report.append(case)
    data = {'schema': 1, 'kind': 'decoding-malformed', 'meta': ctx.meta(start),
            'parameters': {'seed': args.seed, 'mutations': args.mutations,
                           'timeout': args.timeout},
            'totals': dict(totals), 'cases': sorted(report, key=case_key)}
    write_report(args.out, data)
    unsafe = [c for c in report if c['status'] != 'safe']
    print('malformed: %d source files, %d derived inputs per tool' % (
        len(report), sum(v for k, v in totals.items() if k.startswith('pycdas:'))))
    for k in sorted(totals):
        print('  %-24s %d' % (k, totals[k]))
    for c in unsafe[:40]:
        for b in c['failures'][:3]:
            print('  UNSAFE %s %s %s -O%d %s %s: %s %s' % (
                c['suite'], c['fixture'], c['version'], c['opt'], b['tool'], b['variant'][:60],
                b['outcome'], b['signal'] or ''))
    return 0 if not unsafe else 1


# ---------------------------------------------------------------- generate

WIDE_HEADER = '''# Generated by harness/tools/decoding_check.py generate (Part 4).
# Operands that need two EXTENDED_ARG prefixes: more than 65536 names and
# constants, and forward and backward jumps over more than 65536 code units.
# Compiled, disassembled and decompiled only; never executed.
'''


def cmd_generate(args):
    os.makedirs(args.out, exist_ok=True)
    lines = [WIDE_HEADER, 'FLAG = 0', 'if FLAG:']
    lines += ['    v%05d = %d' % (i, 100000 + i) for i in range(70000)]
    lines += ['while FLAG:', '    FLAG = FLAG - 1']
    lines += ['    u%05d = %d' % (i, 200000 + i) for i in range(35000)]
    with open(os.path.join(args.out, 'wide_operands.py'), 'w') as f:
        f.write('\n'.join(lines) + '\n')

    params = ', '.join('a%d' % i for i in range(300))
    body = ['# Generated by harness/tools/decoding_check.py generate (Part 4).',
            '# Locals, arguments and tuple sizes above 255 (one EXTENDED_ARG prefix).',
            '# Compiled, disassembled and decompiled only; never executed.', '',
            'def many(%s):' % params,
            '    total = ' + ' + '.join('a%d' % i for i in range(300)),
            '    return total, (%s)' % params, '',
            'def call_many(f):',
            '    return f(%s)' % ', '.join(str(i) for i in range(300))]
    with open(os.path.join(args.out, 'wide_locals.py'), 'w') as f:
        f.write('\n'.join(body) + '\n')
    print('wrote %s' % args.out)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('generate')
    p.add_argument('--out', required=True)
    p.set_defaults(fn=cmd_generate)

    def common(p, cases=True):
        if cases:
            p.add_argument('--suites', default='features')
            p.add_argument('--versions')
        p.add_argument('--workroot', required=True, help='a difftest run --workroot')
        p.add_argument('--pycdas', default=os.path.join(REPO, 'build', 'release', 'pycdas'))
        p.add_argument('--pycdc', default=os.path.join(REPO, 'build', 'release', 'pycdc'))
        p.add_argument('--workdir', default=os.path.join(REPO, 'build', 'decoding'))
        p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
        p.add_argument('--out', required=True)

    p = sub.add_parser('dis')
    common(p)
    p.add_argument('--summary')
    p.set_defaults(fn=cmd_dis)
    p = sub.add_parser('headers')
    common(p)
    p.set_defaults(fn=cmd_headers)
    p = sub.add_parser('formats')
    common(p, cases=False)
    p.set_defaults(fn=cmd_formats)
    p = sub.add_parser('malformed')
    common(p)
    p.add_argument('--seed', default='part4')
    p.add_argument('--mutations', type=int, default=16)
    p.add_argument('--timeout', type=int, default=10)
    p.set_defaults(fn=cmd_malformed)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
