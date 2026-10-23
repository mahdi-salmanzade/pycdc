def h(f):
    try:
        f()
    except ValueError:
        x = 1
        return x
    return 0
