# feature: exceptions
# summary: context manager enter/exit order, exception info to __exit__, suppression, multiple items


class CM:
    def __init__(self, name, suppress=False):
        self.name, self.suppress = name, suppress

    def __enter__(self):
        print('enter', self.name)
        return self.name.upper()

    def __exit__(self, exc_type, exc, tb):
        print('exit', self.name, exc_type.__name__ if exc_type else None, exc)
        return self.suppress


def basic():
    with CM('a') as value:
        print('body', value)
    return value


def multiple():
    with CM('outer') as o, CM('inner') as i:
        print('body', o, i)


def nested_suppress():
    with CM('suppressing', suppress=True):
        with CM('plain'):
            raise ValueError('swallowed')
        print('not reached')
    return 'after suppression'


def propagate():
    try:
        with CM('propagating'):
            raise KeyError('k')
    except KeyError as e:
        return 'caught ' + repr(e)


def return_inside():
    with CM('ret'):
        return 'returned from with'


def loop_inside():
    out = []
    for i in range(3):
        with CM('loop%d' % i):
            if i == 1:
                continue
            if i == 2:
                break
            out.append(i)
    return out


def no_as_and_tuple_target():
    with CM('x'):
        pass
    with CM('t') as (first, *rest):
        pass
    return first, rest


def observe():
    return [basic(), multiple(), nested_suppress(), propagate(), return_inside(), loop_inside(),
            no_as_and_tuple_target()]
