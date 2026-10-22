# feature: branches
# summary: early returns, implicit None, multiple return points, recursion and mutual recursion


def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)


def fib(n, memo={}):
    if n in memo:
        return memo[n]
    result = n if n < 2 else fib(n - 1) + fib(n - 2)
    memo[n] = result
    return result


def is_even(n):
    return True if n == 0 else is_odd(n - 1)


def is_odd(n):
    return False if n == 0 else is_even(n - 1)


def find(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i
        if item is None:
            print('stop at None')
            return -2
    print('not found')


def nothing():
    x = 1


def multi(x):
    if x > 0:
        if x > 10:
            return 'big'
        return 'small'
    elif x < 0:
        return
    return 'zero', x


def observe():
    return [fact(10), fib(40), is_even(10), is_odd(7), find([1, 2, 3], 2),
            find([1, None, 3], 3), find([], 1), nothing(), multi(50), multi(5), multi(-1),
            multi(0)]
