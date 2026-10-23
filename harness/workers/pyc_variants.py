"""Harness worker: write hash-based variants of timestamp-based .pyc files.

usage: pyc_variants.py JOBS.json

JOBS.json is a list of {"source": SRC.py, "pyc": IN.pyc, "checked": OUT.pyc,
"unchecked": OUT.pyc}.  Each output gets the header py_compile writes for
PycInvalidationMode.CHECKED_HASH (flags 0b11) or UNCHECKED_HASH (flags 0b01):
this interpreter's magic, the flags word and importlib.util.source_hash() of
the source, followed by the unchanged marshalled code object.  Nothing is
executed.  Prints one JSON object with the number of files written.
"""

import importlib.util
import json
import sys


def main():
    with open(sys.argv[1]) as f:
        jobs = json.load(f)
    written = 0
    for job in jobs:
        with open(job['pyc'], 'rb') as f:
            data = f.read()
        if data[:4] != importlib.util.MAGIC_NUMBER:
            continue
        with open(job['source'], 'rb') as f:
            digest = importlib.util.source_hash(f.read())
        for key, flags in (('checked', 0b11), ('unchecked', 0b01)):
            with open(job[key], 'wb') as f:
                f.write(importlib.util.MAGIC_NUMBER + flags.to_bytes(4, 'little') + digest
                        + data[16:])
            written += 1
    print(json.dumps({'written': written}))


if __name__ == '__main__':
    main()
