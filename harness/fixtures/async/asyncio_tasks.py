# feature: async
# summary: asyncio.run with gather, tasks and deterministic interleaving via sleep(0)
import asyncio


async def worker(name, steps, log):
    for i in range(steps):
        log.append('%s step %d' % (name, i))
        await asyncio.sleep(0)
    return name * steps


async def main():
    log = []
    results = await asyncio.gather(worker('a', 2, log), worker('b', 3, log))
    task = asyncio.ensure_future(worker('c', 1, log))
    done = await task
    try:
        await asyncio.wait_for(asyncio.sleep(0, result='slept'), timeout=5)
    except asyncio.TimeoutError:
        pass
    return [results, done, log]


def observe():
    return asyncio.run(main())
