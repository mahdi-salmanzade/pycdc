# feature: version_specific
# summary: PEP 750 template string literals (t-strings)
# requires: >=3.14


def render(template):
    parts = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        else:
            parts.append('[%s=%r conv=%s spec=%s]' % (item.expression, item.value,
                                                       item.conversion, item.format_spec))
    return ''.join(parts)


def observe():
    name, n = 'world', 42
    t = t'hello {name} and {n!r:>5} {n + 1}'
    empty = t''
    return [type(t).__name__, t.strings, [i.value for i in t.interpolations], render(t),
            empty.strings, render(t'{name=}'), render(t'a' t'{n}')]
