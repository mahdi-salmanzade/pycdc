# feature: expressions
# summary: str.format and printf-style % formatting, string concatenation and repetition


class R:
    def __repr__(self):
        return 'R<é>'

    def __str__(self):
        return 'str-of-R'

    def __format__(self, spec):
        return 'fmt(%s)' % spec


def observe():
    name, n, pi, r = 'world', 42, 3.14159265, R()
    return [
        'hello ' + name + '!' * 3,
        '{} {:>5} {name} {0}'.format('a', 'b', name='kw'),
        '{0!r} {0!s} {0:spec} {1:08.3f} {1:x} {1:#o} {1:,} {1:+d}'.format(r, n),
        '{:.2f} {:e} {:10.4}'.format(pi, pi, pi),
        '%s %r %5.2f %-4d| %x %%' % ('s', 'r', pi, n, 255),
        '%(a)s-%(b)s' % {'a': 1, 'b': 2},
        '%c%c' % (72, 'i'),
        format(n, '>8'), format(r, 'xyz'), str(r), repr(r), ascii(r),
        ' '.join(['x', 'y']) * 2, 'abc'[::-1] + 'def'[1],
    ]
