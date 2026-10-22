# feature: comprehensions
# summary: generator expression laziness, eager first iterable, short-circuiting consumers


def source(label, items):
    print('source', label)
    for i in items:
        print('produce', label, i)
        yield i


def observe():
    g = (x * 10 for x in source('a', [1, 2, 3]))
    print('genexp created')
    first = next(g)
    rest = list(g)
    found = any(x > 1 for x in source('b', [0, 2, 5]))
    every = all(x < 3 for x in source('c', [1, 5, 2]))
    total = sum(x for x in range(5) if x % 2)
    nested = list((a, b) for a in source('outer', [1, 2]) for b in source('inner', 'x'))
    pairs = dict((k, v) for k, v in [('p', 1), ('q', 2)])
    joined = ''.join(str(i) for i in range(4))
    return [first, rest, found, every, total, nested, pairs, joined]
