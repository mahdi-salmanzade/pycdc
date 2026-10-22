# feature: branches
# summary: user-defined __bool__/__len__ call counts in if, while, not, and/or, ternary and assert


class Counted:
    calls = 0

    def __init__(self, values):
        self.values = list(values)

    def __bool__(self):
        Counted.calls += 1
        print('bool ->', bool(self.values))
        return bool(self.values)


class Sized:
    def __init__(self, n):
        self.n = n

    def __len__(self):
        print('len ->', self.n)
        return self.n


def observe():
    c = Counted([1, 2])
    out = []
    if c:
        out.append('if')
    if not c:
        out.append('not')
    else:
        out.append('else')
    while c:
        c.values.pop()
    out.append('x' if Counted([]) else 'y')
    out.append(Counted([1]) and 'and')
    out.append(Counted([]) or 'or')
    if Sized(0) or Sized(2):
        out.append('sized')
    out.append(bool(Sized(3)))
    out.append(Counted.calls)
    return out
