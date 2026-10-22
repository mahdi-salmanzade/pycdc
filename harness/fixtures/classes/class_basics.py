# feature: classes
# summary: attributes, __init__, inheritance, diamond MRO, class vs instance attributes, properties


class Animal:
    kind = 'animal'
    count = 0

    def __init__(self, name, sound='...'):
        self.name = name
        self.sound = sound
        Animal.count += 1

    def speak(self):
        return '%s says %s' % (self.name, self.sound)


class Dog(Animal):
    kind = 'dog'

    def __init__(self, name):
        super().__init__(name, 'woof')
        self.tricks = []

    def add_trick(self, trick):
        self.tricks.append(trick)
        return self


class A:
    def who(self):
        return ['A']


class B(A):
    def who(self):
        return ['B'] + super().who()


class C(A):
    def who(self):
        return ['C'] + super().who()


class D(B, C):
    def who(self):
        return ['D'] + super().who()


class Temperature:
    def __init__(self):
        self._c = 0

    @property
    def celsius(self):
        return self._c

    @celsius.setter
    def celsius(self, value):
        print('set celsius', value)
        self._c = value

    @celsius.deleter
    def celsius(self):
        print('delete celsius')
        self._c = None

    fahrenheit = property(lambda self: self._c * 9 / 5 + 32)


class Empty:
    pass


def observe():
    d = Dog('rex').add_trick('sit').add_trick('roll')
    a = Animal('cat', 'meow')
    a.kind = 'instance override'
    t = Temperature()
    t.celsius = 100
    f = t.fahrenheit
    del t.celsius
    return [d.speak(), d.tricks, d.kind, a.kind, Animal.kind, Animal.count, D().who(),
            list(map(lambda k: k.__name__, D.__mro__)), f, t.celsius, isinstance(d, Animal),
            type(Empty()).__name__, Empty.__bases__]
