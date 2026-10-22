# feature: comprehensions
# summary: list/set/dict comprehensions with filters, nested fors, nested comprehensions, conditionals


def observe():
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    words = ['alpha', 'beta', 'gamma']
    return [
        [x * 2 for x in data],
        [x for x in data if x > 2 if x % 2],
        [(x, y) for x in range(3) for y in range(x)],
        [[c for c in w if c != 'a'] for w in words],
        sorted({x % 3 for x in data}),
        {w: len(w) for w in words},
        {k: v for k, v in zip('abc', range(3)) if v},
        [x if x % 2 else -x for x in range(5)],
        [y for x in [[1, 2], [3]] for y in x],
        [[i * j for j in range(3)] for i in range(3)],
        {(i, j): i + j for i in range(2) for j in range(2)},
        [w.upper() for w in words if 'm' in w or w.startswith('b')],
        [i for i in range(20) if i % 3 == 0 and i % 2 == 0],
    ]
