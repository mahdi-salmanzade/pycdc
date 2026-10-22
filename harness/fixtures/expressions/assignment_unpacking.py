# feature: expressions
# summary: tuple/starred/nested unpacking, chained assignment aliasing, swaps, subscript augmented order


def v(name, value):
    print('eval', name)
    return value


class Store(dict):
    def __getitem__(self, k):
        print('getitem', k)
        return dict.__getitem__(self, k)

    def __setitem__(self, k, val):
        print('setitem', k, val)
        dict.__setitem__(self, k, val)


def observe():
    a, b = 1, 2
    a, b = b, a
    x, *rest = [1, 2, 3, 4]
    *init, last = 'abcd'
    first, *mid, end = range(5)
    (p, q), [r, (s, t)] = (1, 2), [3, (4, 5)]
    m = n = []
    m.append(1)
    i = j = k = 0
    i += 1
    lst = [0, 0, 0]
    idx = 0
    idx, lst[idx] = 2, 'set'
    store = Store(k=1)
    v('target', store)[v('key', 'k')] += v('value', 10)
    one, = [99]
    [c1, c2] = 'xy'
    g1, g2, g3 = map(lambda z: v(str(z), z), range(3))
    obj = type('O', (), {})()
    obj.a, obj.b = v('rhs1', 'A'), v('rhs2', 'B')
    lst[0], lst[1] = lst[1], lst[0]
    return [a, b, x, rest, init, last, first, mid, end, p, q, r, s, t, m is n, m, i, j, k,
            lst, idx, dict(store), one, c1, c2, g1, g2, g3, obj.a, obj.b]
