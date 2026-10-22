# feature: exceptions
# summary: finally on return/break/continue/exception, nested finally order, finally overriding results


def ret_in_try():
    try:
        print('try')
        return 'from try'
    finally:
        print('finally runs before return')


def finally_overrides_exception():
    try:
        raise ValueError('lost')
    finally:
        return 'finally wins'


def loop_with_finally():
    out = []
    for i in range(5):
        try:
            if i == 1:
                continue
            if i == 3:
                break
            out.append(i)
        finally:
            out.append('f%d' % i)
    return out


def nested():
    out = []
    try:
        try:
            out.append('inner try')
            raise KeyError('k')
        finally:
            out.append('inner finally')
    except KeyError:
        out.append('outer except')
    finally:
        out.append('outer finally')
    return out


def reraise_after_finally():
    try:
        try:
            1 / 0
        finally:
            print('cleanup before propagation')
    except ZeroDivisionError as e:
        return 'propagated ' + type(e).__name__


def try_except_finally_return(x):
    try:
        if x:
            raise RuntimeError('x')
        return 'normal'
    except RuntimeError:
        return 'handled'
    finally:
        print('finally for', x)


def observe():
    return [ret_in_try(), finally_overrides_exception(), loop_with_finally(), nested(),
            reraise_after_finally(), try_except_finally_return(0),
            try_except_finally_return(1)]
