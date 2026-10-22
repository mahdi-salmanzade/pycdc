# feature: expressions
# summary: f-strings (conversions, format specs, nested specs, = specifier, nesting, concatenation)


class R:
    def __repr__(self):
        return 'R<é>'

    def __str__(self):
        return 'str-of-R'

    def __format__(self, spec):
        return 'fmt(%s)' % spec


def observe():
    name, n, pi, width = 'world', 42, 3.14159265, 8
    r = R()
    return [
        f'hello {name}',
        f'{n:>{width}}|{n:<6}|{n:^7}|{n:08.3f}|{n:x}|{n:#o}|{n:,}|{n:+d}',
        f'{pi:.2f} {pi:e} {pi:10.4} {pi!r}',
        f'{r} {r!r} {r!s} {r!a} {r:spec} {r:{width}x}',
        f'{name=} {n = } {pi=:.1f} {r=!s}',
        f'{"quoted"} {name.upper()} {[1, 2][n % 2]} {n * 2 + 1} {{literal}}',
        f'{name!r:>12}',
        f'{f"{n}"!r}',
        f'',
        f'{n}' f'{name}' 'plain',
    ]
