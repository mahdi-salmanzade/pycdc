# Decoding fixture (Part 4): every family of jump, both directions, loops,
# exception tables of different depths, with blocks and pattern matching.
# Compiled, disassembled and decompiled only; never executed.


def branches(a, b, c):
    if a and b or c:
        x = 1
    elif not a:
        x = 2
    else:
        x = 3
    y = a or b
    z = a and b
    w = (a if b else c) if c is None else c is not None
    while a:
        a -= 1
        if a == 5:
            continue
        if a == 2:
            break
    else:
        x = 4
    for i in range(b):
        if i:
            break
    else:
        x = 5
    assert x, 'message'
    return x, y, z, w


def handlers(f):
    try:
        try:
            f()
        except (ValueError, TypeError) as e:
            raise RuntimeError('wrapped') from e
        except Exception:
            pass
        else:
            return 1
        finally:
            f()
    finally:
        with open(f) as one, open(f) as two:
            return one, two


def matching(value):
    match value:
        case [1, 2, *rest]:
            return rest
        case {'key': v, **others}:
            return v, others
        case int(x) | float(x) if x > 0:
            return x
        case str() as s:
            return s
        case _:
            return None
