# feature: branches
# summary: if/elif/else chains, nesting, empty bodies, side-effecting conditions, compound conditions


def v(name, value):
    print('cond', name)
    return value


def grade(score):
    if score >= 90:
        g = 'A'
    elif score >= 80:
        g = 'B'
    elif score >= 70:
        if score >= 75:
            g = 'C+'
        else:
            g = 'C'
    else:
        g = 'F'
    return g


def compound(a, b, c):
    if a and b or c:
        r = 'first'
    elif not a and (b or not c):
        r = 'second'
    elif a is None:
        pass
        r = 'none'
    else:
        r = 'else'
    if a:
        pass
    else:
        r += '!'
    return r


def side_effects(x):
    out = []
    if v('first', x > 0) and v('second', x > 5):
        out.append('both')
    elif v('third', x == 0):
        out.append('zero')
    if not v('fourth', x):
        out.append('falsy')
    return out


def nested(x, y):
    if x:
        if y:
            return 'x and y'
        else:
            if y is None:
                return 'x, y None'
        return 'x only'
    elif y:
        return 'y only'
    return 'neither'


def observe():
    grades = []
    for s in (95, 85, 77, 72, 10):
        grades.append(grade(s))
    combos = []
    for a in (0, 1, None):
        for b in (0, 1):
            for c in (0, 1):
                combos.append(compound(a, b, c))
    nests = []
    for x in (0, 1):
        for y in (0, 1, None):
            nests.append(nested(x, y))
    return [grades, combos, side_effects(7), side_effects(3), side_effects(0), nests]
