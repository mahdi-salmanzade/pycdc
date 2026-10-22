# feature: closures
# summary: closures created inside comprehensions, comprehensions reading enclosing locals and class scope


def lambdas_in_comprehension():
    fs = [lambda: i for i in range(3)]
    gs = [lambda i=i: i for i in range(3)]
    return [f() for f in fs], [g() for g in gs]


def comprehension_reads_enclosing(factor):
    offset = 100
    return [x * factor + offset for x in range(3)], {k: factor for k in 'ab'}


def nested_closure_in_genexp():
    base = 5
    gen = (lambda y: y + base + x for x in range(2))
    funcs = list(gen)
    base = 50
    return [f(1) for f in funcs]


class Scope:
    items = [1, 2, 3]
    factor = 10
    doubled = [x * 2 for x in items]
    try:
        scaled = [x * factor for x in items]
    except NameError as e:
        scaled = 'NameError'


def observe():
    return [lambdas_in_comprehension(), comprehension_reads_enclosing(2),
            nested_closure_in_genexp(), Scope.doubled, Scope.scaled]
