# feature: async
# summary: async def, await on custom awaitables, return values and exceptions driven by a manual loop


class Suspend:
    def __init__(self, label):
        self.label = label

    def __await__(self):
        print('suspend', self.label)
        resumed = yield self.label
        print('resumed', self.label, 'with', resumed)
        return 'value-' + self.label


async def leaf(label):
    result = await Suspend(label)
    return result.upper()


async def failing():
    await Suspend('before-fail')
    raise ValueError('async failure')


async def composite():
    a = await leaf('a')
    b = await leaf('b')
    try:
        await failing()
    except ValueError as e:
        handled = str(e)
    return [a, b, handled]


def run(coro):
    trace = []
    value = None
    while True:
        try:
            yielded = coro.send(value)
        except StopIteration as e:
            return trace, e.value
        trace.append(yielded)
        value = 'sent-%d' % len(trace)


def observe():
    c = leaf('unused')
    c.close()
    return [run(composite()), run(leaf('solo'))]
