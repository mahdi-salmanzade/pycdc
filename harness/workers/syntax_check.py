"""Harness worker: check that recovered source compiles under this interpreter.

usage: syntax_check.py SOURCE OPTIMIZE

Compiles only; never executes the source.  The file is passed to compile() as
bytes so PEP 263 encoding rules apply exactly as for a real source file.
Prints one JSON object on stdout.
"""

import json
import sys
import warnings


def main():
    path, optimize = sys.argv[1], int(sys.argv[2])
    with open(path, 'rb') as f:
        data = f.read()
    res = {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            compile(data, 'recovered.py', 'exec', dont_inherit=True, optimize=optimize)
            res['ok'] = True
        except SyntaxError as e:
            res.update(ok=False, error=type(e).__name__, message=e.msg, lineno=e.lineno,
                       text=(e.text or '').strip()[:300])
        except (ValueError, UnicodeDecodeError, MemoryError, RecursionError) as e:
            res.update(ok=False, error=type(e).__name__, message=str(e)[:300])
    res['warnings'] = sorted(set('%s: %s' % (w.category.__name__, w.message)
                                 for w in caught))[:20]
    print(json.dumps(res))


if __name__ == '__main__':
    main()
