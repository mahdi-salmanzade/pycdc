# feature: branches
# summary: match with sequence, star, mapping (**rest), class (positional/keyword) and nested patterns
# requires: >=3.10


class Point:
    __match_args__ = ('x', 'y')

    def __init__(self, x, y):
        self.x, self.y = x, y


class Circle:
    def __init__(self, center, r):
        self.center, self.r = center, r


def describe(obj):
    match obj:
        case []:
            return 'empty list'
        case [x]:
            return 'one: %r' % (x,)
        case [1, *rest]:
            return 'starts with 1, rest %r' % (rest,)
        case (a, b, *_, z) if a == z:
            return 'bookends %r %r' % (a, b)
        case {'type': 'user', 'name': str(name), **extra}:
            return 'user %s extra %r' % (name, sorted(extra))
        case {'type': t}:
            return 'typed ' + t
        case Point(0, 0):
            return 'origin'
        case Point(x, y=0):
            return 'on x axis at %r' % x
        case Point(x=px, y=py) if px == py:
            return 'diagonal %r' % px
        case Circle(center=Point(x, y), r=r) if r > 10:
            return 'big circle at %r,%r' % (x, y)
        case Circle():
            return 'circle'
        case [Point(), *points]:
            return 'points list of %d' % (len(points) + 1)
        case _:
            return 'unknown'


def observe():
    cases = [[], [5], [1, 2, 3], (7, 8, 9, 7), {'type': 'user', 'name': 'ann', 'age': 3},
             {'type': 'admin'}, Point(0, 0), Point(4, 0), Point(3, 3), Point(1, 2),
             Circle(Point(1, 2), 20), Circle(Point(0, 0), 1), [Point(1, 1), Point(2, 2)],
             'string', {'type': 5}]
    out = []
    for c in cases:
        try:
            out.append(describe(c))
        except TypeError as e:
            out.append('TypeError: %s' % e)
    return out
