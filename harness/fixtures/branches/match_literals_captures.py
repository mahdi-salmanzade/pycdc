# feature: branches
# summary: match statement with literal, capture, wildcard, value, or/as patterns and guards
# requires: >=3.10
import enum


class Color(enum.Enum):
    RED = 'red'
    GREEN = 'green'


def classify(value):
    match value:
        case 0:
            return 'zero'
        case 1 | 2 | 3:
            return 'small'
        case None:
            return 'none'
        case True:
            return 'true'
        case 'hello' | 'hi' as greeting:
            return 'greeting:' + greeting
        case Color.RED:
            return 'red enum'
        case int(n) if n < 0:
            return 'negative %d' % n
        case float() | complex():
            return 'non-int number'
        case str() as s if len(s) > 5:
            return 'long string'
        case other:
            return 'other:%r' % (other,)


def no_match(x):
    result = 'before'
    match x:
        case 1:
            result = 'one'
    return result


def observe():
    return [classify(v) for v in (0, 2, None, True, 'hi', Color.RED, Color.GREEN, -4, 1.5,
                                  'abcdefg', 'abc', 99)] + [no_match(1), no_match(2)]
