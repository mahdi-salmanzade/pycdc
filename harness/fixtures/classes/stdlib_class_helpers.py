# feature: classes
# summary: dataclasses, enums, namedtuple and functools.total_ordering used the way real modules use them
import dataclasses
import enum
import functools
from collections import namedtuple


@dataclasses.dataclass(order=True)
class Point:
    x: int
    y: int = 0
    tags: list = dataclasses.field(default_factory=list, compare=False)


@dataclasses.dataclass(frozen=True)
class Frozen:
    name: str


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = enum.auto()


class Flags(enum.IntFlag):
    A = 1
    B = 2


Pair = namedtuple('Pair', 'left right')


@functools.total_ordering
class Version:
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return self.n == other.n

    def __lt__(self, other):
        return self.n < other.n


def observe():
    p = Point(1, 2)
    return [repr(p), p == Point(1, 2, ['x']), sorted([Point(2), Point(1, 5), Point(1)]),
            Frozen('a'), hash(Frozen('a')) == hash(Frozen('a')), list(map(lambda c: c.name, Color)), Color(2), Color.BLUE.value,
            int(Flags.A | Flags.B), Pair(1, 2), Pair(1, 2).right, Version(1) >= Version(1),
            Version(2) > Version(1)]
