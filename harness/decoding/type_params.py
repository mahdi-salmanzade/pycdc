# Decoding fixture (Part 4, Python 3.12+): type parameters and aliases, which
# add annotation scopes and intrinsics.  Compiled, disassembled and
# decompiled only.


type Alias[T] = list[T]


def first[T: (int, str), *Ts, **P](items: list[T]) -> T:
    return items[0]


class Box[T]:
    def get(self) -> T:
        return self.value

    nested = f"{'a' + f'{1 + 2!r:>{3}}'}"
