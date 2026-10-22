# feature: loops
# summary: loops, conditionals and try statements executed inside class bodies


class Config:
    options = {}
    for key in ('a', 'b', 'c'):
        if key == 'b':
            continue
        options[key] = key.upper()
    else:
        loop_done = True
    if len(options) > 1:
        mode = 'multi'
    elif options:
        mode = 'single'
    else:
        mode = 'none'
    del key
    try:
        limit = int('x')
    except ValueError:
        limit = -1
    n = 0
    while n < 3:
        n += 1


def observe():
    return [Config.options, Config.loop_done, Config.mode, Config.limit, Config.n,
            hasattr(Config, 'key')]
