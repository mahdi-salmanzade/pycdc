# feature: expressions
# summary: del of names, attributes, subscripts and slices; reading a deleted local raises UnboundLocalError

COUNTER = 3
del COUNTER
TEMP = 'module temp'


class Obj:
    pass


def read_deleted():
    x = 10
    del x
    return x


def observe():
    d = {'a': 1, 'b': 2, 'c': 3}
    del d['b']
    lst = list(range(6))
    del lst[1], lst[2]
    del lst[-2:]
    o = Obj()
    o.attr = 1
    o.other = 2
    del o.attr
    a = b = 5
    del a, b
    global TEMP
    del TEMP
    print([d, lst, sorted(vars(o)), 'COUNTER' in globals(), 'TEMP' in globals()])
    return read_deleted()
