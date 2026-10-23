"""Harness worker: dump the reference decoding of .pyc files, as this
interpreter's marshal and dis modules see them.

usage: dis_dump.py OUT.json PYC [PYC ...]

Only reads the header and marshal-loads the code object; never executes it.
For every code object (recursively, in co_consts order) it records the
fields pycdas prints, the constants in a normalized form, every instruction
with its operand resolved to what the operand means (jump target offset,
name, constant, local or cell name, comparison operator), and the exception
table.  EXTENDED_ARG prefixes are folded into the instruction they extend,
whose offset is that of its first prefix, and inline CACHE units are
omitted; pycdas prints instructions the same way.  Writes one JSON object.
"""

import dis
import importlib.util
import json
import marshal
import sys
import types

V = sys.version_info[:2]
HAS = {name: set(getattr(dis, name, ())) for name in (
    'hasjrel', 'hasjabs', 'hasname', 'hasconst', 'haslocal', 'hasfree', 'hascompare')}
EXTENDED_ARG = dis.opmap['EXTENDED_ARG']


def norm_const(value):
    if isinstance(value, types.CodeType):
        return ['code', dump_code(value)]
    if isinstance(value, tuple):
        return ['tuple', [norm_const(v) for v in value]]
    if isinstance(value, frozenset):
        items = [norm_const(v) for v in value]
        return ['frozenset', sorted(items, key=lambda x: json.dumps(x, sort_keys=True))]
    if isinstance(value, slice):
        return ['slice', [norm_const(value.start), norm_const(value.stop),
                          norm_const(value.step)]]
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
    return ['other', type(value).__name__, repr(value)]


def localsplus(code):
    if V < (3, 11):
        return None
    names, i = [], 0
    while True:
        try:
            names.append(code._varname_from_oparg(i))
        except (IndexError, ValueError):
            return names
        i += 1


def meaning(code, ins):
    """The operand's meaning in a form pycdas can be compared with, or None
    when only the raw operand is defined."""
    op = ins.opcode
    if op in HAS['hasjrel'] or op in HAS['hasjabs']:
        return ['target', ins.argval]
    if op in HAS['hasconst']:
        # dis itself resolves only some of these (3.11 leaves KW_NAMES unknown)
        return ['const', norm_const(code.co_consts[ins.arg])]
    if op in HAS['hasname']:
        return ['name', ins.argval]
    if op in HAS['haslocal'] or op in HAS['hasfree']:
        if isinstance(ins.argval, tuple):          # LOAD_FAST_LOAD_FAST and friends
            return ['locals', list(ins.argval)]
        return ['local', ins.argval]
    if op in HAS['hascompare']:
        return ['compare', ins.argval]
    return None


def instructions(code):
    out, prefix_start = [], None
    for ins in dis.get_instructions(code):
        if ins.opcode == EXTENDED_ARG:
            if prefix_start is None:
                prefix_start = ins.offset
            continue
        if ins.opname == 'CACHE':
            continue
        start = getattr(ins, 'start_offset', None)
        if start is None:
            start = prefix_start if prefix_start is not None else ins.offset
        prefix_start = None
        out.append({'offset': start, 'opname': ins.opname, 'arg': ins.arg,
                    'meaning': meaning(code, ins) if ins.arg is not None else None})
    return out


def exception_table(code):
    if V < (3, 11):
        return None
    return [[e.start, e.end, e.target, e.depth, bool(e.lasti)]
            for e in dis._parse_exception_table(code)]


def dump_code(code):
    return {
        'filename': code.co_filename,
        'name': code.co_name,
        'qualname': getattr(code, 'co_qualname', None),
        'argcount': code.co_argcount,
        'posonlyargcount': code.co_posonlyargcount,
        'kwonlyargcount': code.co_kwonlyargcount,
        'nlocals': code.co_nlocals,
        'stacksize': code.co_stacksize,
        'flags': code.co_flags,
        'names': list(code.co_names),
        'varnames': list(code.co_varnames),
        'localsplus': localsplus(code),
        'freevars': list(code.co_freevars),
        'cellvars': list(code.co_cellvars),
        'consts': [norm_const(c) for c in code.co_consts],
        'instructions': instructions(code),
        'exception_table': exception_table(code),
    }


def main():
    out = {'version': '%d.%d.%d' % sys.version_info[:3], 'files': {}}
    for path in sys.argv[2:]:
        with open(path, 'rb') as f:
            data = f.read()
        if data[:4] != importlib.util.MAGIC_NUMBER:
            out['files'][path] = {'error': 'magic does not match this interpreter'}
            continue
        try:
            out['files'][path] = {'code': dump_code(marshal.loads(data[16:]))}
        except Exception as e:  # noqa: BLE001 - reported, never fatal
            out['files'][path] = {'error': '%s: %s' % (type(e).__name__, e)}
    with open(sys.argv[1], 'w') as f:
        json.dump(out, f, sort_keys=True)


if __name__ == '__main__':
    main()
