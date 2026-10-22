# feature: version_specific
# summary: BaseException.add_note (PEP 678) and notes on propagated exceptions
# requires: >=3.11


def enrich(fn):
    try:
        fn()
    except Exception as e:
        e.add_note('while calling ' + fn.__name__)
        raise


def broken():
    raise LookupError('base problem')


def observe():
    try:
        enrich(broken)
    except LookupError as e:
        notes = e.__notes__
    e2 = ValueError('with notes')
    e2.add_note('first')
    e2.add_note('second')
    return [notes, e2.__notes__, str(e2)]
