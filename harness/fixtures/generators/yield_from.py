# feature: generators
# summary: yield from delegation, return value of yield from, send/throw passthrough, nested delegation


def inner(label):
    try:
        x = yield label + ':1'
        print('inner received', x)
        y = yield label + ':2'
        print('inner received', y)
    except ValueError as e:
        print('inner caught', e)
        yield label + ':recovered'
    return 'inner result ' + label


def middle():
    r1 = yield from inner('a')
    print('middle got', r1)
    r2 = yield from inner('b')
    return [r1, r2]


def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def observe():
    out = []
    g = middle()
    out.append(next(g))
    out.append(g.send('s1'))
    out.append(g.send('s2'))
    out.append(g.throw(ValueError('thrown into b')))
    try:
        next(g)
    except StopIteration as e:
        out.append(e.value)
    out.append(list(flatten([1, [2, [3, [4]], 5], [[6]]])))
    out.append(list(x for x in flatten([[1, 2], 3])))
    return out
