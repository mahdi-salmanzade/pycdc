# feature: version_specific
# summary: ExceptionGroup and except* (PEP 654): splitting, re-raising unhandled parts, nesting
# requires: >=3.11


def handle(group):
    log = []
    try:
        raise group
    except* ValueError as eg:
        log.append(('value', sorted(str(e) for e in eg.exceptions)))
    except* (KeyError, IndexError) as eg:
        log.append(('lookup', len(eg.exceptions)))
    return log


def partial():
    result = None
    try:
        try:
            raise ExceptionGroup('mixed', [ValueError('v'), TypeError('t')])
        except* ValueError:
            print('handled ValueError part')
    except* TypeError as rest:
        result = ('remaining', [type(e).__name__ for e in rest.exceptions])
    return result


def naked_exception():
    result = None
    try:
        raise KeyError('naked')
    except* KeyError as eg:
        result = (type(eg).__name__, [repr(e) for e in eg.exceptions])
    return result


def observe():
    out = [handle(ExceptionGroup('g', [ValueError('a'), KeyError('b'), ValueError('c')])),
           handle(ExceptionGroup('nested', [ExceptionGroup('inner', [IndexError(1)])])),
           partial(), naked_exception()]
    eg = ExceptionGroup('split me', [ValueError(1), TypeError(2)])
    match, rest = eg.split(ValueError)
    out.append((str(match), str(rest)))
    print(out)
    raise ExceptionGroup('escapes observe', [RuntimeError('r'), ValueError('v')])
