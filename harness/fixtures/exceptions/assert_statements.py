# feature: exceptions
# summary: assert with/without message (removed from the compiled program at -O and -OO)


def checked(x):
    assert x > 0
    assert isinstance(x, int), 'need int, got %r' % (x,)
    return x * 2


def observe():
    out = []
    for value in (3, -1, 2.5):
        try:
            out.append(checked(value))
        except AssertionError as e:
            out.append(('AssertionError', e.args))
    out.append(__debug__)
    return out
