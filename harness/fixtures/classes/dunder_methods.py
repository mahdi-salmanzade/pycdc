# feature: classes
# summary: container/iteration/call/comparison/hash dunders, NotImplemented fallback, __bool__ via __len__


class Bag:
    def __init__(self, *items):
        self.items = list(items)

    def __repr__(self):
        return 'Bag(%s)' % ', '.join(map(repr, self.items))

    def __len__(self):
        print('len called')
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

    def __setitem__(self, i, v):
        self.items[i] = v

    def __delitem__(self, i):
        del self.items[i]

    def __contains__(self, x):
        print('contains', x)
        return x in self.items

    def __iter__(self):
        return iter(reversed(self.items))

    def __call__(self, *a):
        return ('called', a)

    def __eq__(self, other):
        if not isinstance(other, Bag):
            return NotImplemented
        return self.items == other.items

    def __hash__(self):
        return hash(tuple(self.items))

    def __lt__(self, other):
        return len(self.items) < len(other.items)

    def __add__(self, other):
        if isinstance(other, Bag):
            return Bag(*(self.items + other.items))
        return NotImplemented


class Seq:
    def __getitem__(self, i):
        if i >= 3:
            raise IndexError(i)
        return i * 10


def observe():
    b = Bag(1, 2, 3)
    b[0] = 'one'
    del b[1]
    out = [repr(b), len(b), bool(Bag()), 3 in b, 9 in b, list(b), b('x', 'y'),
           b == Bag('one', 3), b != Bag(), b == 'other', hash(b) == hash(Bag('one', 3)),
           sorted([Bag(1, 2), Bag(), Bag(1)]), list(Seq()), 20 in Seq(), b + Bag(4)]
    try:
        b + 1
    except TypeError as e:
        out.append(str(e))
    if Bag(1):
        out.append('truthy')
    return out
