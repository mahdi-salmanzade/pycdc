# feature: expressions
# summary: constants of every type, container displays, starred displays, escapes and folding

INTS = (0, 1, -1, 255, 0o17, 0x1F, 0b101, 10 ** 20, -(2 ** 63), 1_000_000)
FLOATS = (0.0, -0.0, 1.5, 1e-10, 1e308, float('inf'), -float('inf'), 3.14159)
STRS = ('', 'a', "it's", 'tab\tnew\nline', '\x00\x7f', 'é中', r'raw\d', 'a' 'b' 'c',
        '''triple
quoted''', 'quote"inside')
BYTES = (b'', b'abc', b'\x00\xff', rb'\d', bytes(3))
MISC = (None, True, False, ..., 1j, 2 + 3j, NotImplemented)
FOLDED = (2 * 3 + 1, 'ab' * 3, (1, 2) + (3,), -(-5), not 0, 1 << 10, ('x',) * 2)


def observe():
    a = [1, 2]
    b = (3, 4)
    d = {'k': 1}
    displays = {
        'list': [1, [2, [3, []]], ()],
        'tuple': (1,), 'empty_tuple': (), 'nested': ((1, 2), [3, {4: 5}]),
        'set': sorted({3, 1, 2, 1}), 'frozen': sorted(frozenset('hello')),
        'dict': {'b': 1, 'a': 2, 1: 'one', (1, 2): 'tuple', None: 0},
        'star_list': [*a, *b, 5, *'xy'], 'star_tuple': (*a, 0, *b),
        'star_set': sorted({*a, *b, 2}), 'merge': {**d, 'z': 0, **{'k': 9}},
        'dict_order': list({'z': 1, 'a': 2, 'm': 3}),
        'big_list': list(range(40))[::7],
        'const_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'const_set': sorted({'p', 'q', 'r', 's', 't'}),
    }
    return [INTS, FLOATS, STRS, BYTES, MISC, FOLDED, displays]
