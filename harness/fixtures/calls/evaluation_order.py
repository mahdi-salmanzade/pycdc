# feature: calls
# summary: evaluation order of callee, arguments, keyword arguments, star-args and chained calls


def v(name, value=None):
    print('eval', name)
    return value


def make(label):
    print('make', label)

    def inner(*args, **kwargs):
        print('call', label, args, sorted(kwargs))
        return lambda *a: (label, a)
    return inner


class Obj:
    def method(self, *args):
        print('method', args)
        return self


def observe():
    make('f')(v('a', 1), v('b', 2))
    make('g')(v('p', 1), k=v('kw', 2), *v('star', [3]), **v('dstar', {'z': 4}))
    r = make('h')(v('x', 0))(v('y', 1))
    o = Obj()
    v('obj', o).method(v('m1', 1)).method(v('m2', 2))
    d = {'f': make('dict')}
    d[v('key', 'f')](v('arg', 9))
    nested = max(v('n1', 3), min(v('n2', 5), v('n3', 4)), key=v('key-fn', None))
    print(v('print-arg', 'done'), sep=v('sep', '-'))
    return [r, nested]
