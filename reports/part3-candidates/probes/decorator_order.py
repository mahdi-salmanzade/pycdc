def deco(arg):
    return lambda fn: fn

@deco(print('a'))
def f(x=print('b')):
    return x
