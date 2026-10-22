# feature: branches
# summary: and/or/not return operands, short-circuit side effects, chained comparisons evaluate once


class Truth:
    def __init__(self, name, value):
        self.name, self.value = name, value

    def __bool__(self):
        print('bool', self.name)
        return self.value

    def __repr__(self):
        return 'T(%s)' % self.name


def v(name, value):
    print('eval', name)
    return value


def observe():
    out = []
    out.append(v('a', 0) and v('b', 1))
    out.append(v('a', 2) and v('b', 0))
    out.append(v('a', 0) or v('b', '') or v('c', 'x'))
    out.append(v('a', 0) or v('b', 0) and v('c', 3))
    out.append((v('a', 1) or v('b', 2)) and v('c', 3))
    out.append(not v('a', []))
    out.append(not (v('a', 1) and v('b', 0)))
    t, f = Truth('t', True), Truth('f', False)
    out.append(t and f)
    out.append(f or t)
    out.append(not t)
    out.append(f and t)
    out.append(t or f)
    out.append(bool(f or f or t))
    x = 5
    out.append(x > 3 and x < 10 or x == 100)
    out.append(x > 3 and (x < 4 or x == 5))
    out.append(None or [] or {} or 0 or '')
    out.append(1 and 'yes' or 'no')
    out.append(0 and 'yes' or 'no')
    out.append(v('a', 1) < v('b', 2) < v('c', 3))
    out.append(v('a', 1) < v('b', 0) < v('c', 3))
    out.append(v('a', 1) == v('b', 1) != v('c', 2) <= v('d', 2))
    out.append(1 < 2 > 1 >= 1 <= 5)
    out.append(v('lo', 0) <= x < v('hi', 10))
    return out
