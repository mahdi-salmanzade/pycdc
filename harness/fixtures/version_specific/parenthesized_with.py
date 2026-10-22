# feature: version_specific
# summary: parenthesized multi-item with statements (officially 3.10+ grammar)
# requires: >=3.10


class CM:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print('enter', self.name)
        return self.name

    def __exit__(self, *exc):
        print('exit', self.name)
        return False


def observe():
    with (
        CM('a') as a,
        CM('b') as b,
        CM('c'),
    ):
        print('body', a, b)
    with (CM('single')):
        pass
    return [a, b]
