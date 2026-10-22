# feature: version_specific
# summary: PEP 758 except clauses listing several types without parentheses
# requires: >=3.14


def catch(exc):
    try:
        raise exc
    except ValueError, TypeError:
        return 'value-or-type'
    except KeyError, IndexError:
        return 'lookup'


def observe():
    return [catch(ValueError()), catch(TypeError()), catch(KeyError()), catch(IndexError())]
