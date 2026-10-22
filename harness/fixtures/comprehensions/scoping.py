# feature: comprehensions
# summary: comprehension variables do not leak, outer names shadowed, nested comprehension scoping

x = 'module x'


def no_leak():
    y = 'outer y'
    squares = [y for y in range(3)]
    return y, squares


def shadow_outer():
    x = 'local x'
    result = [x for x in 'ab']
    return x, result, [x for _ in range(2)]


def nested_refs():
    rows = [[1, 2], [3, 4]]
    return [[cell * len(row) for cell in row] for row in rows]


def dict_comp_scope():
    keys = ['a', 'b']
    k = 'kept'
    d = {k: i for i, k in enumerate(keys)}
    return k, d


def observe():
    return [no_leak(), shadow_outer(), nested_refs(), dict_comp_scope(), [x for _ in (1,)]]
