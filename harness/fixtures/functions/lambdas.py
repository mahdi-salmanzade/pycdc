# feature: functions
# summary: lambdas with defaults, varargs, keyword-only args, nesting, immediate calls

add = lambda a, b=1: a + b
variadic = lambda *a, **k: (a, sorted(k.items()))
kwonly = lambda x, *, y=2: x * y
compose = lambda f, g: lambda x: f(g(x))
const = lambda: 'const'


def observe():
    inc = compose(add, lambda x: x * 10)
    return [
        add(1), add(1, 5), variadic(1, 2, z=3), kwonly(3), kwonly(3, y=4),
        inc(2), const(), (lambda: 'iife')(), (lambda x, y: (y, x))(1, 2),
        sorted([(1, 'b'), (2, 'a')], key=lambda p: p[1]),
        list(map(lambda n: (lambda n=n: n * n)(), range(4))),
        (lambda *args: len(args))(*range(5)),
        (lambda a, /, b, *, c: (a, b, c))(1, b=2, c=3),
        add.__name__, inc.__qualname__,
    ]
