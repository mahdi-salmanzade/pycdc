# feature: closures
# summary: counters with nonlocal, shared cells, late binding vs early binding via defaults


def counter(start=0):
    count = start

    def inc(step=1):
        nonlocal count
        count += step
        return count

    def get():
        return count
    return inc, get


def late_binding():
    i = 0
    f0 = lambda: i
    i = 1
    f1 = lambda: i
    i = 2
    return f0(), f1()


def early_binding():
    i = 0
    f0 = lambda i=i: i
    i = 1
    f1 = lambda i=i: i
    i = 2
    return f0(), f1()


def cell_after_creation():
    def show():
        return value
    value = 'assigned after def'
    first = show()
    value = 'reassigned'
    return first, show()


def delete_cell():
    cell = 'temporary'

    def peek():
        return cell
    first = peek()
    del cell
    return first, len(peek.__closure__)


def param_capture(x):
    def inner():
        return x * 2
    x += 1
    return inner


def observe():
    inc, get = counter(10)
    inc()
    inc(5)
    inc2, get2 = counter()
    inc2()
    return [get(), get2(), late_binding(), early_binding(), cell_after_creation(),
            param_capture(3)(), inc.__closure__ is not None, len(get.__closure__),
            delete_cell()]
