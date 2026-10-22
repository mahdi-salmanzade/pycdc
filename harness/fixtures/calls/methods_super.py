# feature: calls
# summary: bound methods, classmethod/staticmethod, zero-arg and explicit super(), method calls on literals


class Base:
    tag = 'base'

    def greet(self, who):
        return 'Base.greet(%s, %s)' % (type(self).__name__, who)

    @classmethod
    def make(cls, *args):
        return (cls.__name__, cls.tag, args)

    @staticmethod
    def util(x):
        return x * 3


class Child(Base):
    tag = 'child'

    def greet(self, who):
        return 'Child>' + super().greet(who)

    @classmethod
    def make(cls, *args):
        return ('Child.make',) + super().make(*args)


class Grand(Child):
    def greet(self, who):
        return 'Grand>' + super(Child, self).greet(who) + '|' + super().greet(who)


def observe():
    g = Grand()
    bound = g.greet
    return [
        Base().greet('x'), Child().greet('y'), g.greet('z'), bound('w'),
        Base.make(1), Child.make(2, 3), Grand.make(), g.make(4), Base.util(5), g.util(6),
        Base.greet(g, 'unbound'), 'a,b'.split(','), ', '.join(['x', 'y']), (1).__add__(2),
        [3, 1, 2].copy(), {'k': 1}.get('k'), b'ab'.hex(), 1.5.is_integer(),
    ]
