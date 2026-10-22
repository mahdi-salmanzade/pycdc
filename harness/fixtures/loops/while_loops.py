# feature: loops
# summary: while/else, break, continue, while True with return, zero iterations, side-effecting conditions


def cond(state):
    state['checks'] += 1
    print('check', state['n'])
    return state['n'] > 0


def countdown(n):
    state = {'n': n, 'checks': 0}
    seen = []
    while cond(state):
        state['n'] -= 1
        if state['n'] == 2:
            continue
        seen.append(state['n'])
    else:
        seen.append('else')
    return seen, state['checks']


def first_square_above(limit):
    n = 0
    while True:
        n += 1
        if n * n > limit:
            return n


def with_break(items):
    i = 0
    while i < len(items):
        if items[i] is None:
            break
        i += 1
    else:
        return 'complete'
    return 'broke at %d' % i


def observe():
    n = 0
    while n:
        n = 'never'
    nested = []
    a = 0
    while a < 3:
        b = 0
        while b < a:
            nested.append((a, b))
            b += 1
        a += 1
    return [countdown(4), countdown(0), first_square_above(50), with_break([1, 2]),
            with_break([1, None, 3]), n, nested]
