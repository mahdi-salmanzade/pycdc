# feature: exceptions
# summary: try/except inside loops with continue/break/return, exceptions escaping loops


def parse_all(items):
    out = []
    for item in items:
        try:
            value = int(item)
        except ValueError:
            out.append('bad:' + item)
            continue
        except TypeError:
            out.append('type error')
            break
        else:
            out.append(value)
        finally:
            print('processed', item)
    return out


def retry(attempts):
    n = 0
    while True:
        n += 1
        try:
            if n < attempts:
                raise ConnectionError('try %d' % n)
            return 'succeeded after %d' % n
        except ConnectionError as e:
            print('retrying after', e)
            if n >= 5:
                return 'gave up'


def escaping():
    total = 0
    try:
        for i in range(10):
            total += 10 // (3 - i)
    except ZeroDivisionError:
        return 'escaped at total %d' % total


def observe():
    return [parse_all(['1', 'x', '3']), parse_all(['5', None, '7']), retry(3), retry(9),
            escaping()]
