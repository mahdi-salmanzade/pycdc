# feature: exceptions
# summary: optional-import idioms: try/except ImportError at module level and inside functions

try:
    import does_not_exist_pycdc_fixture
except ImportError as e:
    does_not_exist_pycdc_fixture = None
    import_error = type(e).__name__

try:
    from json import no_such_name
except ImportError:
    no_such_name = 'fallback'
else:
    no_such_name = 'unexpected'

try:
    import json as fast_json
except ImportError:
    fast_json = None


def optional(name):
    try:
        module = __import__(name)
    except ModuleNotFoundError as e:
        return 'missing ' + e.name
    else:
        return 'found ' + module.__name__


def observe():
    return [does_not_exist_pycdc_fixture, import_error, no_such_name, fast_json.__name__,
            optional('keyword'), optional('no_such_module_pycdc')]
