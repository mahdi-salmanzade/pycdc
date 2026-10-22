# feature: functions
# summary: decorator evaluation and application order, factories, stacking, class decorators


def trace(label):
    print('factory', label)

    def deco(fn):
        print('apply', label, fn.__name__)

        def wrapper(*args, **kwargs):
            print('enter', label)
            result = fn(*args, **kwargs)
            print('exit', label)
            return (label, result)
        wrapper.__name__ = fn.__name__
        return wrapper
    return deco


def register(registry):
    def deco(obj):
        registry.append(obj.__name__)
        return obj
    return deco


REGISTRY = []


@trace('outer')
@trace('inner')
def work(x):
    print('work', x)
    return x * 2


@register(REGISTRY)
@register(REGISTRY)
class Thing:
    @property
    def value(self):
        return 'value'

    @staticmethod
    @trace('static')
    def helper():
        return 'helper'


def replace(fn):
    return 'replaced:' + fn.__name__


@replace
def gone():
    pass


def observe():
    return [work(5), REGISTRY, Thing().value, Thing.helper(), gone, work.__name__]
