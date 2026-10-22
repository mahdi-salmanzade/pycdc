# feature: calls
# summary: positional, keyword, defaults, keyword-only, positional-only, *args/**kwargs; a binding error


def f(a, b=2, *args, c, d=4, **kw):
    return [a, b, args, c, d, sorted(kw.items())]


def posonly(x, y=1, /, z=2, *, w=3):
    return (x, y, z, w)


def collect(*args, **kwargs):
    return (args, kwargs)


def observe():
    print([
        f(1, c=3),
        f(1, 5, 6, 7, c=3, e=9),
        f(a=0, c=0, d=0, b=0, z=1),
        posonly(10),
        posonly(10, 20, 30, w=40),
        posonly(10, z=5),
        collect(),
        collect(1, 'two', k=3, j=4),
        collect(*[1, 2], *(3,), **{'x': 1}, y=2),
        posonly(*(1, 2), **{'z': 3}),
    ])
    return posonly(x=1)
