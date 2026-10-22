# feature: exceptions
# summary: raise forms, explicit/implicit chaining, from None, bare re-raise, custom exception classes


class AppError(Exception):
    def __init__(self, code, msg):
        super().__init__(code, msg)
        self.code = code

    def __str__(self):
        return '[%d] %s' % (self.code, self.args[1])


class NotFound(AppError):
    pass


def explicit_cause():
    try:
        {}['missing']
    except KeyError as e:
        raise NotFound(404, 'no such key') from e


def implicit_context():
    try:
        1 / 0
    except ZeroDivisionError:
        raise ValueError('while handling')


def suppressed():
    try:
        int('x')
    except ValueError:
        raise TypeError('clean') from None


def reraise():
    try:
        raise AppError(500, 'boom')
    except AppError:
        print('logging, then re-raising')
        raise


def raise_class():
    raise KeyError


def capture(fn):
    try:
        fn()
    except Exception as e:
        cause, ctx = e.__cause__, e.__context__
        return [type(e).__name__, str(e), e.args, type(cause).__name__ if cause else None,
                type(ctx).__name__ if ctx else None, e.__suppress_context__,
                getattr(e, 'code', None), isinstance(e, AppError)]


def observe():
    results = []
    for f in (explicit_cause, implicit_context, suppressed, reraise, raise_class):
        results.append(capture(f))
    print(results)
    print('about to raise out of observe')
    try:
        explicit_cause()
    except NotFound as e:
        raise RuntimeError('escaping observe') from e
    return results
