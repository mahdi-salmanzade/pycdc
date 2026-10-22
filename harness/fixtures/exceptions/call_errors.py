# feature: exceptions
# summary: argument-binding errors raised by calls (missing, duplicate, positional-only, keyword types)


def f(a, b=2, *args, c, d=4, **kw):
    return [a, b, args, c, d]


def posonly(x, y=1, /, z=2, *, w=3):
    return (x, y, z, w)


def collect(*args, **kwargs):
    return (args, kwargs)


def observe():
    errors = []
    calls = (lambda: f(1), lambda: f(1, 2, c=3, a=1), lambda: posonly(x=1),
             lambda: posonly(1, 2, 3, 4), lambda: collect(**{1: 2}), lambda: f(c=1),
             lambda: posonly(1, w=2, q=3), lambda: len(1, 2))
    for call in calls:
        try:
            call()
        except TypeError as e:
            errors.append(str(e))
    return errors
