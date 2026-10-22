# feature: classes
# summary: statements in class bodies, nested classes and qualnames, private name mangling, type() classes


class Config:
    options = {}
    key = 'a'
    options[key] = key.upper()
    mode = 'multi'
    del key
    temp = 'remove me'
    del temp

    class Inner:
        class Deeper:
            pass

    def method(self):
        class Local:
            pass
        return Local.__qualname__


class Private:
    __secret = 'hidden'

    def __init__(self):
        self.__value = 42
        self._single = 1

    def reveal(self):
        return (self.__secret, self.__value, self.__helper())

    def __helper(self):
        return 'helper'

    def nested(self):
        def inner():
            return self.__value
        return inner()


Dynamic = type('Dynamic', (Config,), {'extra': 1, 'go': lambda self: 'go'})


def observe():
    p = Private()
    return [Config.options, Config.mode, hasattr(Config, 'key'), hasattr(Config, 'temp'),
            Config.Inner.Deeper.__qualname__, Config().method(), p.reveal(), p.nested(),
            sorted(vars(p)), '_Private__secret' in vars(Private),
            Dynamic().go(), Dynamic.extra, Dynamic.mode]
