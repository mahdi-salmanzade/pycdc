# feature: async
# summary: async generators (asend/athrow/aclose), async comprehensions, await inside comprehensions


async def agen(n):
    try:
        for i in range(n):
            received = yield i
            if received:
                print('agen received', received)
    except KeyError:
        print('agen caught KeyError')
        yield 'recovered'
    finally:
        print('agen finally')


async def double(x):
    return x * 2


async def main():
    out = [x async for x in agen(3)]
    out.append([await double(x) async for x in agen(2) if x])
    out.append({x: await double(x) for x in range(2)})
    g = agen(5)
    out.append(await g.__anext__())
    out.append(await g.asend('hello'))
    out.append(await g.athrow(KeyError('k')))
    await g.aclose()
    return out


def run(coro):
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError('coroutine suspended unexpectedly')


def observe():
    return run(main())
