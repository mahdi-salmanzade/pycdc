# feature: classes
# summary: metaclass __prepare__/__new__/__init__ ordering, class keywords, __init_subclass__, __set_name__


class Meta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kw):
        print('prepare', name, sorted(kw))
        return {'injected': 'by prepare'}

    def __new__(mcs, name, bases, ns, **kw):
        print('meta new', name, sorted(filter(lambda k: not k.startswith('__'), ns)))
        cls = super().__new__(mcs, name, bases, ns)
        cls.options = kw
        return cls

    def __init__(cls, name, bases, ns, **kw):
        print('meta init', name)
        super().__init__(name, bases, ns)


class Field:
    def __set_name__(self, owner, name):
        print('set_name', owner.__name__, name)
        self.name = name

    def __get__(self, obj, objtype=None):
        return 'field:' + self.name


class Base(metaclass=Meta, flavor='plain'):
    print('Base body runs')
    x = Field()


class Plugin:
    registry = []

    def __init_subclass__(cls, key=None, **kwargs):
        print('init_subclass', cls.__name__, key)
        super().__init_subclass__(**kwargs)
        Plugin.registry.append((cls.__name__, key))


class First(Plugin, key='first'):
    pass


class Second(First):
    y = Field()


class Child(Base, extra=1):
    print('Child body runs')


def observe():
    return [Base.options, Child.options, Base.injected, Base().x, Second().y,
            Plugin.registry, type(Child).__name__]
