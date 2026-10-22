# feature: expressions
# summary: single comparisons, in/not in, is/is not, rich comparisons returning non-bool values


def v(name, value):
    print('eval', name)
    return value


class Weird:
    def __init__(self, n):
        self.n = n

    def __lt__(self, other):
        print('lt', self.n, other.n)
        return 'lt-result'

    def __eq__(self, other):
        print('eq', self.n, getattr(other, 'n', other))
        return self.n == getattr(other, 'n', other)

    __hash__ = None


def observe():
    xs = [1, 2, 3]
    return [
        v('a', 1) < v('b', 2), v('a', 2) <= v('b', 2), v('a', 3) > v('b', 2),
        v('a', 1) >= v('b', 2), v('a', 1) == v('b', 1.0), v('a', 'x') != v('b', 'y'),
        2 in xs, 4 not in xs, 'b' in 'abc', 'k' in {'k': 1}, None in [None],
        xs is xs, xs is not None, None is None, [] is not [],
        Weird(1) < Weird(2), Weird(1) == Weird(1), Weird(1) != Weird(2),
        (1, 2) < (1, 3), [3] > [2, 9], 'abc' < 'abd', sorted([3, 1, 2]) == [1, 2, 3],
    ]
