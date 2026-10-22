# feature: generators
# summary: GeneratorExit handling, try/finally in generators, exhausted generators, lazy pipelines


def resource(name):
    print('open', name)
    try:
        yield 'first ' + name
        yield 'second ' + name
    except GeneratorExit:
        print('generator exit', name)
        raise
    finally:
        print('close', name)


def pipeline(source):
    for item in source:
        if item % 2:
            print('filter pass', item)
            yield item * item


def numbers(n):
    i = 0
    while i < n:
        print('produce', i)
        yield i
        i += 1


def lingering():
    try:
        yield 'lingering'
    finally:
        print('lingering finalized')


def leave_cycle():
    holder = {'gen': lingering()}
    holder['self'] = holder
    return next(holder['gen'])


def observe():
    out = [leave_cycle()]
    r = resource('a')
    out.append(next(r))
    r.close()
    r2 = resource('b')
    out.extend(r2)
    out.append(list(r2))
    for value in resource('c'):
        out.append(value)
        break
    p = pipeline(numbers(6))
    out.append(next(p))
    out.append(list(p))
    return out
