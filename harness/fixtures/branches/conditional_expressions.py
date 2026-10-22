# feature: branches
# summary: conditional expressions, nested and with side effects, in lambdas and call arguments


def v(name, value):
    print('eval', name)
    return value


def classify(n):
    return 'neg' if n < 0 else 'zero' if n == 0 else 'small' if n < 10 else 'big'


def observe():
    out = list(map(classify, (-3, 0, 4, 40)))
    out.append(v('yes', 1) if v('cond', True) else v('no', 2))
    out.append(v('yes', 1) if v('cond', 0) else v('no', 2))
    out.append((v('a', 'A') if v('c1', 0) else v('b', 'B')) + (v('x', 'X') if v('c2', 1) else 'Y'))
    f = lambda x: x * 2 if x else -1
    out.append([f(0), f(3)])
    out.append(str(1 if len(out) > 3 else 0))
    out.append(max(1, 2) if min(1, 2) == 1 else None)
    x = 7
    out.append(('odd' if x % 2 else 'even', 'big' if x > 5 and x < 100 else 'other'))
    out.append(list(map(lambda y: y if y % 2 else -y, range(5))))
    return out
