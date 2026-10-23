def g():
    yield
    x = yield
    yield None
    return x
