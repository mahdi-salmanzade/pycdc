# Decoding fixture (Part 4): constants of every marshal type the compiler
# emits.  Compiled, disassembled and decompiled only; never executed.

floats = (0.1, 2.0, -0.0, 0.0, 1e300, 5e-324, 1.7976931348623157e308, 1e16, 1e15,
          123456789.123456789, 1 / 3, 2.5e-10, 1e999, -1e999, 1e999 - 1e999)
complexes = (2j, -2j, 1 + 2j, 1 - 2j, -1 + 0j, 0j, -0j, 1e999j, -(1.5 + 0j),
             -0.0 + 1j, 0.1 + 0.2j, 1e300 + 1e-300j)
ints = (0, -1, 255, 256, 65535, 65536, 2 ** 31, -2 ** 31, 2 ** 63, 2 ** 100, -2 ** 100,
        10 ** 50)
raw = (b'', b'\x00\x01\x02\x7f\x80\xfe\xff', b"quote ' and \" both", b'back\\slash',
       b'\t\n\r\x0b\x0c')
texts = ('', 'plain', "it's", 'say "hi"', 'both \' and "', 'back\\slash',
         'tab\tnl\ncr\r', '\x00\x1f\x7f\x80\x9f', 'é', 'naïve café', 'Ελληνικά', '中文',
         '\U0001f600 astral', '\ud800', '\udfff', 'a\ud83db', '\u2028\u2029', 'x' * 300)
invisible = ('\u202e', '\u2066x\u2069', 'zero\u200bwidth', '\ufeff', 'soft\xadhyphen', '\u061c',
             '\x85', '\U000e0001')
nested = ((1, (2, (3, ('deep',)))), ((), ((),)), (None, True, False, ...))
singletons = (None, True, False, ...)


def membership(value):
    return value in {1, 2.5, 'a', (1, 2), b'b', None}, value in frozenset()


def non_ascii_names(obj):
    café = obj.naïve
    return café, obj.Ελληνικά


def slices(seq):
    return (seq[1:2], seq[::-1], seq[None:1:2], seq['a':], seq[1:2, 3],
            seq[:-1], seq[2**40:])
