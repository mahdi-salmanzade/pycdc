# feature: expressions
# summary: indexing, slicing with steps, slice assignment/deletion, slice objects passed to __getitem__


class Probe:
    def __getitem__(self, key):
        return ('get', repr(key))

    def __setitem__(self, key, value):
        print('set', repr(key), value)

    def __delitem__(self, key):
        print('del', repr(key))


def observe():
    s = list(range(10))
    reads = [s[0], s[-1], s[2:5], s[:3], s[7:], s[::2], s[::-1], s[-3:-1], s[1:8:3],
             s[:], s[100:], 'hello'[1:-1], (1, 2, 3)[::-2]]
    t = list(range(6))
    t[1:3] = ['a', 'b', 'c']
    t[::2] = [0, 0, 0, 0][:len(t[::2])]
    del t[-1]
    del t[:1]
    u = list(range(8))
    del u[::3]
    m = [[1, 2], [3, 4]]
    m[1][0] = 'x'
    m[0][-1] += 10
    p = Probe()
    probes = [p[1], p[1:2], p[::3], p[1, 2], p[1:2, ::-1], p[...], p['k']]
    p[0] = 'a'
    p[1:5:2] = 'b'
    p[:, 1] = 'c'
    del p[2:]
    del p[0, 0]
    d = {'a': {'b': [1, 2, {'c': 'deep'}]}}
    d['a']['b'][2]['c'] += '!'
    i = 1
    return [reads, t, u, m, probes, d, s[i + 1], s[i:i + 3]]
