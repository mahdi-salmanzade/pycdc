# Decoding fixture (Part 4, Python 3.14+): template strings and deferred
# annotations.  Compiled, disassembled and decompiled only.


def render(name, width):
    return t'hello {name!r:>{width}} and {name=}'


class Annotated:
    field: UndefinedLater
    other: int = 3

    def method(self, x: AlsoUndefined) -> 'str':
        return x
