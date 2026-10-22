# feature: expressions
# summary: attribute get/set/del, chains, augmented attribute assignment evaluating the target once


class Node:
    def __init__(self, name):
        self.name = name
        self.child = None
        self.count = 0


class Logged:
    def __init__(self):
        object.__setattr__(self, 'log', [])

    def __getattr__(self, name):
        self.log.append('getattr ' + name)
        return 0

    def __setattr__(self, name, value):
        self.log.append('setattr %s=%r' % (name, value))
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        self.log.append('delattr ' + name)
        object.__delattr__(self, name)


def get(obj, label):
    print('get', label)
    return obj


def observe():
    root = Node('root')
    root.child = Node('child')
    root.child.child = Node('grandchild')
    get(root, 'root').child.count += 5
    get(get(root, 'r').child, 'c').child.count -= 2
    names = [root.name, root.child.name, root.child.child.name, root.child.child.count]
    lg = Logged()
    lg.x = 1
    lg.x += 1
    lg.y += 3
    del lg.x
    missing = getattr(root, 'nope', 'default')
    has = (hasattr(root, 'child'), hasattr(root, 'zzz'))
    setattr(root, 'dyn', 42)
    delattr(root, 'dyn')
    return [names, root.child.count, lg.log, missing, has, hasattr(root, 'dyn'),
            (3).bit_length(), 'abc'.upper().lower(), [1, 2].index(2), root.child.child.child]
