# feature: loops
# summary: custom iterators, StopIteration, iter(callable, sentinel), iteration side-effect order


class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        print('iter called')
        return self

    def __next__(self):
        if self.n <= 0:
            print('stop')
            raise StopIteration
        self.n -= 1
        print('next ->', self.n + 1)
        return self.n + 1


def observe():
    out = list(Countdown(3))
    for y in Countdown(2):
        out.append(y * 10)
    data = iter([5, 6, 0, 7])
    out.append(list(iter(lambda: next(data), 0)))
    it = iter('ab')
    out.append(next(it))
    out.append(next(it))
    out.append(next(it, 'default'))
    try:
        next(it)
    except StopIteration:
        out.append('StopIteration')
    out.append(list(range(10, 0, -3)))
    out.append(list(zip(*[(1, 'a'), (2, 'b')])))
    return out
