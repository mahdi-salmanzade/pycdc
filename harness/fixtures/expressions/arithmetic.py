# feature: expressions
# summary: binary, unary and augmented operators, numeric edge cases, reflected and in-place dunders
import operator


class Vec:
    def __init__(self, *xs):
        self.xs = list(xs)

    def __repr__(self):
        return 'Vec%r' % (tuple(self.xs),)

    def __add__(self, other):
        print('add', self, other)
        return Vec(*map(operator.add, self.xs, other.xs))

    def __radd__(self, other):
        print('radd', self, other)
        return Vec(*map(operator.add, [other] * len(self.xs), self.xs))

    def __iadd__(self, other):
        print('iadd', self, other)
        self.xs = list(map(operator.add, self.xs, [other] * len(self.xs)))
        return self

    def __matmul__(self, other):
        return sum(map(operator.mul, self.xs, other.xs))

    def __neg__(self):
        return Vec(*map(operator.neg, self.xs))

    def __invert__(self):
        return 'inverted'


def observe():
    a, b = 17, -5
    ints = [a + b, a - b, a * b, a / b, a // b, a % b, -a // b, -a % b, a ** 2, 2 ** -1,
            a & b, a | b, a ^ b, ~a, a << 3, a >> 2, -a, +a, not a, divmod(a, b)]
    floats = [7.5 // 2, 7.5 % 2, -7.5 // 2, 1e300 * 10, -0.0, 0.1 + 0.2, 2 ** 0.5]
    big = [2 ** 100 + 1, (2 ** 64) // 3, -(10 ** 30) % 7]
    cplx = [(1 + 2j) * (3 - 4j), abs(3 + 4j), (1j) ** 2]
    prec = [2 + 3 * 4 ** 2, (2 + 3) * 4, -2 ** 2, (-2) ** 2, 2 ** 3 ** 2, 10 - 3 - 2,
            100 // 7 * 3, a - (b - 1), a * (b + 1), -(a + b), ~-a, not not a]
    x = 5
    x += 3
    x -= 1
    x *= 4
    x //= 3
    x %= 7
    x **= 3
    x <<= 1
    x >>= 2
    x |= 64
    x &= 0x7F
    x ^= 5
    y = 9
    y /= 2
    mm = Vec(1, 2)
    mm @= Vec(3, 4)
    v = Vec(1, 2)
    w = v
    v += 10
    r = 3 + Vec(1, 2)
    s = Vec(1, 1) + Vec(2, 3)
    return {'ints': ints, 'floats': floats, 'big': big, 'cplx': cplx, 'prec': prec, 'x': x,
            'alias': (w is v, v.xs), 'y': y, 'mm_inplace': mm, 'r': r.xs, 's': s.xs, 'mm': Vec(1, 2) @ Vec(3, 4),
            'neg': (-Vec(1, -2)).xs, 'inv': ~Vec()}
