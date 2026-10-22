# feature: version_specific
# summary: PEP 649/749 deferred evaluation of annotations, forward references, annotationlib formats
# requires: >=3.14
import annotationlib


def note(label, value):
    print('evaluated', label)
    return value


def f(x: Later, y: note('y', int)) -> note('ret', str):
    return x


class Later:
    field: Later
    count: note('count', int) = 0


def observe():
    print('before access')
    fwd = annotationlib.get_annotations(f, format=annotationlib.Format.STRING)
    values = f.__annotations__
    cls = Later.__annotations__
    return [fwd, {k: getattr(v, '__name__', v) for k, v in values.items()},
            {k: getattr(v, '__name__', v) for k, v in cls.items()}]
