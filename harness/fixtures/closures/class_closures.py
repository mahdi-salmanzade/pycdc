# feature: closures
# summary: __class__ cell and zero-arg super, class body names invisible to methods, classes in functions

name = 'module name'


class Base:
    def who(self):
        return 'Base'


class Derived(Base):
    name = 'class attribute name'

    def who(self):
        return 'Derived/' + super().who() + '/' + __class__.__name__

    def which_name(self):
        return name


def class_factory(prefix):
    counter = [0]

    class Made:
        label = prefix + '-label'

        def describe(self):
            counter[0] += 1
            return (prefix, self.label, counter[0])
    return Made


def method_closure():
    class Holder:
        def __init__(self):
            self.items = []

        def adder(self):
            def add(x):
                self.items.append(x)
                return len(self.items)
            return add
    h = Holder()
    add = h.adder()
    add('a')
    add('b')
    return h.items


def observe():
    M = class_factory('p')
    m = M()
    return [Derived().who(), Derived().which_name(), m.describe(), m.describe(), M.__qualname__,
            method_closure()]
