# Decoding fixture (Part 4): nested code objects, cells and free variables,
# argument kinds, generators and coroutines.  Compiled, disassembled and
# decompiled only; never executed.
import functools


def outer(a, /, b=1, *args, c, d=2, **kwargs):
    total = a + b

    def middle(x):
        nonlocal total
        total += x

        def inner():
            return total + x + c
        return inner

    class Local:
        value = total

        def method(self):
            return __class__, super().__repr__(), self.value

    return middle, Local, lambda y=d: y + len(args) + len(kwargs)


def class_scope(prefix):
    class Scoped:
        name = prefix
        names = [prefix + str(i) for i in range(3)]
    return Scoped


def generator(n):
    received = yield n
    yield from range(received or 0)
    return n


async def coroutine(source, lock):
    async with lock:
        async for item in source:
            await item
    result = [x async for x in source]
    return result


@functools.lru_cache(maxsize=None)
def decorated(x: int, *, y: 'str' = 'y') -> 'tuple':
    return x, y


comprehensions = ([x for x in range(3)], {x: x for x in range(3)},
                  {x for x in range(3)}, list(x for x in range(3)))
