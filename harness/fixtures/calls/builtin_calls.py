# feature: calls
# summary: builtins with key functions, map/filter/zip, nested calls, getattr chains


def observe():
    words = ['pear', 'Apple', 'fig', 'banana']
    out = [
        sorted(words),
        sorted(words, key=str.lower),
        sorted(words, key=lambda w: (len(w), w), reverse=True),
        list(map(len, words)),
        list(filter(lambda w: 'a' in w, words)),
        list(zip(words, range(10), 'xyz')),
        sum(map(len, words)),
        any(map(lambda w: w.startswith('f'), words)),
        all(map(lambda w: len(w) > 2, words)),
        dict(zip('abc', range(3))),
        list(enumerate(words, start=1)),
        max(words, key=len), min(3, 1, 2), abs(-4), round(2.675, 2), round(7.5),
        isinstance(1, (int, str)), issubclass(bool, int), callable(len),
        getattr(getattr(words, 'copy')(), '__len__')(),
        list(reversed(range(3))), divmod(-7, 2), pow(2, 10, 1000), hash(()) == hash(()),
        int('ff', 16), float('1.5'), str(b'x', 'ascii'), repr('q'), ascii('é'), chr(65), ord('a'),
    ]
    return out
