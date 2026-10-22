# feature: version_specific
# summary: starred expressions inside subscripts (PEP 646 grammar)
# requires: >=3.11


class Recorder:
    def __getitem__(self, key):
        return key

    def __class_getitem__(cls, key):
        return ('class', key)


def observe():
    r = Recorder()
    rest = (2, 3)
    return [r[*rest], r[1, *rest], r[*rest, 4], Recorder[*rest], r[*'ab', *[0]]]
