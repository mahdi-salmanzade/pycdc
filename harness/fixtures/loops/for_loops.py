# feature: loops
# summary: for/else with and without break, continue, zero iterations, unpacking and attribute targets


class Target:
    pass


def search(items, target):
    for i, item in enumerate(items):
        if item == target:
            print('found at', i)
            break
    else:
        print('not found')
        i = -1
    return i


def observe():
    out = []
    for x in range(10):
        if x % 2:
            continue
        if x > 6:
            break
        out.append(x)
    for _ in []:
        out.append('never')
    else:
        out.append('empty else')
    out.append(search('abc', 'b'))
    out.append(search('abc', 'z'))
    pairs = []
    for k, (a, b) in {'p': (1, 2), 'q': (3, 4)}.items():
        pairs.append((k, a + b))
    t = Target()
    for t.attr in 'xy':
        pass
    d = {}
    for d['key'] in range(3):
        pass
    total = 0
    for i in range(3):
        for j in range(3):
            if j > i:
                break
            total += i * j
        else:
            total += 100
    for first, *rest in [(1, 2, 3), (4,)]:
        out.append((first, rest))
    return [out, pairs, t.attr, d, total]
