# feature: functions
# summary: global and nonlocal declarations, module state mutated from functions

counter = 0
log = []


def bump(n=1):
    global counter
    counter += n
    log.append(counter)


def define_late():
    global late_name
    late_name = 'defined by function'


def outer():
    x = 'outer'
    calls = 0

    def inner():
        nonlocal x, calls
        calls += 1
        x = x + '!'
        return x

    def reader():
        return (x, calls)
    inner()
    inner()
    return reader()


def shadow():
    counter = 'local'
    return counter


def observe():
    bump()
    bump(5)
    define_late()
    return [counter, log, late_name, outer(), shadow(), counter]
