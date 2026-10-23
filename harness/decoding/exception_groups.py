# Decoding fixture (Part 4, Python 3.11+): except* and deeply nested
# exception-table ranges.  Compiled, disassembled and decompiled only.


def groups(f):
    try:
        f()
    except* ValueError as e:
        g = e
    except* (TypeError, KeyError):
        g = None
    try:
        try:
            try:
                f()
            finally:
                f()
        except BaseException:
            f()
    finally:
        f()
    return g
