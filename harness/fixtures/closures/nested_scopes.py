# feature: closures
# summary: three-level nesting, free variables passing through intermediate scopes, shadowing

x = 'global x'


def level1():
    a = 'a1'
    x = 'level1 x'

    def level2():
        b = 'b2'

        def level3():
            return (a, b, x)
        return level3

    def shadow():
        a = 'shadowed'

        def inner():
            return a
        return inner()

    def rebind():
        nonlocal a
        a = 'rebound'
    l3 = level2()
    before = l3()
    rebind()
    return before, l3(), shadow()


def uses_global():
    def inner():
        return x
    return inner()


def make_adder(n):
    return lambda y: n + y


def observe():
    adders = list(map(make_adder, range(3)))
    return [level1(), uses_global(), adders[0](10), adders[2](10)]
