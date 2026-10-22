# feature: functions
# summary: module, class, function and method docstrings (stripped at -OO in the compiled program)
"""Module docstring for the fixture."""


def documented(x):
    """Return x doubled.

    Second paragraph.
    """
    return x * 2


def not_a_docstring():
    x = 1
    """This string is an expression statement, not a docstring."""
    return x


class Doc:
    """Class docstring."""

    def method(self):
        """Method docstring."""
        return 'm'

    def empty(self):
        """Only a docstring."""


def observe():
    import sys
    mod = sys.modules[__name__]
    return [mod.__doc__, documented.__doc__, documented(2), not_a_docstring.__doc__,
            Doc.__doc__, Doc.method.__doc__, Doc().empty(), Doc.empty.__doc__]
