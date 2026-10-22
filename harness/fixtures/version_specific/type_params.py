# feature: version_specific
# summary: PEP 695 type parameters on functions/classes and the type statement
# requires: >=3.12


def first[T](items: list[T]) -> T:
    return items[0]


def bounded[N: (int, float), S: str, *Ts, **P](x: N) -> N:
    return x


class Box[T]:
    def __init__(self, item: T):
        self.item = item

    def get[U](self, default: U) -> T | U:
        return self.item if self.item is not None else default


class Outer:
    target = int
    type Inner = list[target]

    def method[T](self, x: target) -> T:
        return x


type Pair[K] = tuple[K, K]
type Alias = list[int]


def describe_params(obj):
    out = []
    for p in obj.__type_params__:
        out.append((type(p).__name__, p.__name__, getattr(p, '__bound__', None),
                    getattr(p, '__constraints__', None)))
    return out


def observe():
    return [first([7, 8]), Box('x').get(1), Box(None).get('d'), describe_params(first),
            describe_params(bounded), describe_params(Box), describe_params(Box.get),
            repr(Outer.Inner.__value__), Outer().method(5), Pair.__name__, [p.__name__ for p in Pair.__type_params__], Alias.__value__,
            repr(Pair[int].__value__) if hasattr(Pair[int], '__value__') else str(Pair[int])]
