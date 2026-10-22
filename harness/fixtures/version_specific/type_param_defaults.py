# feature: version_specific
# summary: PEP 696 defaults for type parameters
# requires: >=3.13


class Container[T = int, *Ts = *tuple[str, ...], **P = [float]]:
    pass


def func[X = str](x: X) -> X:
    return x


type Mapping[K = str, V = list[K]] = dict[K, V]


def observe():
    return [[(p.__name__, repr(p.__default__)) for p in Container.__type_params__],
            [(p.__name__, repr(p.__default__)) for p in func.__type_params__],
            [(p.__name__, p.has_default()) for p in Mapping.__type_params__], func(3)]
