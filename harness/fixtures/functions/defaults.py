# feature: functions
# summary: default values evaluated once at definition time, mutable default persistence, kw-only defaults


def v(name, value):
    print('default', name)
    return value


def accumulate(item, bucket=[]):
    bucket.append(item)
    return bucket


def configured(a, b=v('b', 10), *, c=v('c', 'C'), d=v('d', None)):
    return (a, b, c, d)


SCALE = 3


def scaled(x, factor=SCALE * 2):
    return x * factor


SCALE = 100


def observe():
    print('observe starts')
    r1 = accumulate(1)
    r2 = accumulate(2)
    r3 = accumulate(3, [])
    return [r1 is r2, r2, r3, configured(1), configured(1, 2, c=3, d=4), scaled(2),
            accumulate.__defaults__ is not None, configured.__kwdefaults__]
