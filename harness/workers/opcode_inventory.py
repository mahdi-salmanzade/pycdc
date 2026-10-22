"""Harness worker: report this interpreter's opcode table and the raw opcodes
used by the given .pyc files.

usage: opcode_inventory.py OUT.json [PYC ...]

Only marshal-loads the files and walks co_code / co_consts; never executes
them.  Prints nothing; writes one JSON object to OUT.json.
"""

import dis
import importlib.util
import json
import marshal
import sys
import types


def cache_entries():
    raw = getattr(dis, '_inline_cache_entries', None)
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return {dis.opname[k] if isinstance(k, int) else k: v for k, v in raw.items() if v}
    return {dis.opname[i]: n for i, n in enumerate(raw) if n}


def walk(code, counts):
    raw = code.co_code
    for i in range(0, len(raw), 2):
        name = dis.opname[raw[i]]
        counts[name] = counts.get(name, 0) + 1
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            walk(const, counts)


def main():
    out = sys.argv[1]
    counts = {}
    files = 0
    for path in sys.argv[2:]:
        with open(path, 'rb') as f:
            data = f.read()
        if data[:4] != importlib.util.MAGIC_NUMBER:
            continue
        walk(marshal.loads(data[16:]), counts)
        files += 1
    res = {
        'version': '%d.%d.%d' % sys.version_info[:3],
        'opmap': {name: num for name, num in dis.opmap.items() if num < 256},
        'hasarg': sorted(dis.opname[i] for i in dis.hasarg) if hasattr(dis, 'hasarg') else [],
        'have_argument': dis.HAVE_ARGUMENT,
        'cache_entries': cache_entries(),
        'corpus_files': files,
        'corpus_counts': counts,
    }
    with open(out, 'w') as f:
        json.dump(res, f, sort_keys=True)


if __name__ == '__main__':
    main()
