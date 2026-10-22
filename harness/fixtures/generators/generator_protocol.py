# feature: generators
# summary: yield, send, throw, close, return values via StopIteration, finally on close, yield expressions


def echo():
    print('started')
    received = None
    try:
        while True:
            received = yield received
            print('got', received)
            if received == 'stop':
                return 'stopped cleanly'
    except KeyError as e:
        print('caught thrown', e)
        yield 'recovered'
    finally:
        print('echo finally')


def counter(n):
    for i in range(n):
        yield i
    return 'done %d' % n


def accumulate():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value
    return total


def observe():
    out = []
    g = echo()
    out.append(next(g))
    out.append(g.send('hello'))
    out.append(g.send('again'))
    try:
        g.send('stop')
    except StopIteration as e:
        out.append(('stop', e.value))
    g2 = echo()
    next(g2)
    out.append(g2.throw(KeyError('boom')))
    g2.close()
    g3 = echo()
    next(g3)
    g3.close()
    out.append(list(counter(3)))
    c = counter(1)
    out.append(next(c))
    try:
        next(c)
    except StopIteration as e:
        out.append(e.value)
    acc = accumulate()
    next(acc)
    for v in (5, 10, 20):
        out.append(acc.send(v))
    try:
        acc.send(None)
    except StopIteration as e:
        out.append(('total', e.value))
    unstarted = echo()
    unstarted.close()
    return out
