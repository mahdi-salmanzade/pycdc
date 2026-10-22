# feature: functions
# summary: function, variable and class annotations with side effects (eager before 3.14, deferred in 3.14)
import sys


def note(label, value):
    print('annotation evaluated:', label)
    return value


def f(a: note('a', int), b: note('b', 'str') = 'x', *args: note('args', tuple),
      k: note('k', float) = 1.0, **kw: note('kw', dict)) -> note('return', list):
    return [a, b, args, k, kw]


module_var: note('module_var', int) = 5
unassigned: note('unassigned', str)


class C:
    attr: note('attr', bytes) = b''
    plain: int

    def method(self, x: 'C') -> None:
        pass


def observe():
    print('observe starts')
    mod = sys.modules[__name__]
    ann = {k: (v.__name__ if isinstance(v, type) else v) for k, v in f.__annotations__.items()}
    mod_ann = {k: getattr(v, '__name__', v) for k, v in mod.__annotations__.items()}
    cls_ann = {k: getattr(v, '__name__', v) for k, v in C.__annotations__.items()}
    return [f(1), ann, mod_ann, cls_ann, C.method.__annotations__, 'unassigned' in dir(mod)]
