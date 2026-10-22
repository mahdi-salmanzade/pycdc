# feature: async
# summary: async for over custom async iterators, async with, break/else in async for


class Ticker:
    def __init__(self, n):
        self.n = n

    def __aiter__(self):
        print('aiter')
        return self

    async def __anext__(self):
        if self.n <= 0:
            print('anext stop')
            raise StopAsyncIteration
        self.n -= 1
        return self.n


class AsyncCM:
    def __init__(self, name):
        self.name = name

    async def __aenter__(self):
        print('aenter', self.name)
        return self.name

    async def __aexit__(self, et, ev, tb):
        print('aexit', self.name, et.__name__ if et else None)
        return et is KeyError


async def main():
    out = []
    async for t in Ticker(3):
        out.append(t)
    async for t in Ticker(5):
        if t == 3:
            break
        out.append(('b', t))
    else:
        out.append('not reached')
    async for t in Ticker(0):
        out.append('never')
    else:
        out.append('empty else')
    async with AsyncCM('one') as name:
        out.append(name)
    async with AsyncCM('two') as a, AsyncCM('three') as b:
        out.append((a, b))
    async with AsyncCM('suppress'):
        raise KeyError('suppressed')
    return out


def run(coro):
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError('coroutine suspended unexpectedly')


def observe():
    return run(main())
