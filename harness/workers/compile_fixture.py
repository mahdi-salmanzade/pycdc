"""Harness worker: compile one source file to .pyc with this interpreter.

usage: compile_fixture.py SOURCE OUT_PYC OPTIMIZE DFILE

Compiles only; never executes the source.  The source mtime is pinned so the
timestamp-based .pyc header (the default, most common on-disk form) is
deterministic.  Prints one JSON object on stdout.
"""

import importlib.util
import json
import os
import py_compile
import sys

FIXED_MTIME = 1700000000


def main():
    src, out, optimize, dfile = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    os.utime(src, (FIXED_MTIME, FIXED_MTIME))
    res = {
        'version': '%d.%d.%d' % sys.version_info[:3],
        'magic': int.from_bytes(importlib.util.MAGIC_NUMBER[:2], 'little'),
    }
    try:
        py_compile.compile(src, cfile=out, dfile=dfile, doraise=True, optimize=optimize,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        res['ok'] = True
    except py_compile.PyCompileError as e:
        res['ok'] = False
        res['error'] = e.exc_type_name
        res['message'] = str(e.exc_value)[:500]
    print(json.dumps(res))


if __name__ == '__main__':
    main()
