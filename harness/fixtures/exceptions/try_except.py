# feature: exceptions
# summary: try/except/else/finally, handler order, tuple handlers, bare except, 'as' name unbinding
import sys


def attempt(action):
    log = []
    try:
        log.append('try')
        action()
        log.append('after action')
    except ZeroDivisionError:
        log.append('zero')
    except (KeyError, IndexError) as e:
        log.append('lookup %s %r' % (type(e).__name__, e.args))
    except Exception as e:
        log.append('other ' + type(e).__name__)
        print('handler for', type(e).__name__, file=sys.stderr)
    else:
        log.append('else')
    finally:
        log.append('finally')
    return log


def bare(action):
    try:
        action()
    except:
        return 'bare caught %s' % sys.exc_info()[0].__name__
    return 'no exception'


def name_unbound():
    try:
        raise ValueError('v')
    except ValueError as err:
        msg = str(err)
    try:
        err
    except NameError:
        return msg, 'err unbound'
    return msg, 'err still bound'


def exception_in_else():
    try:
        pass
    except ValueError:
        return 'handler'
    else:
        try:
            raise KeyError('from else')
        except KeyError as e:
            return 'caught ' + repr(e)


def observe():
    return [attempt(lambda: 1 / 0), attempt(lambda: {}['k']), attempt(lambda: [][1]),
            attempt(lambda: int('x')), attempt(lambda: None), bare(lambda: 1 / 0),
            bare(lambda: 0), name_unbound(), exception_in_else(), sys.exc_info()]
