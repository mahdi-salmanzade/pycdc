# feature: imports
# summary: import forms with aliases, dotted names, parenthesized from-imports, imports inside functions
import os
import os.path
import collections.abc as cabc
import json, string as strmod
import xml.dom.minidom
from math import sqrt
from math import floor as fl, ceil
from itertools import (
    chain,
    islice as take,
)
from os.path import join as pjoin
from collections import abc


def lazy():
    import textwrap
    from functools import reduce as fold
    import email.utils as eu
    return textwrap.dedent('  x').strip(), fold(lambda a, b: a + b, [1, 2, 3]), eu.__name__


def observe():
    return [os.path.basename('/a/b.txt'), os.__name__, cabc.__name__, cabc.Sequence.__name__,
            json.dumps([1]), strmod.digits, xml.__name__, xml.dom.minidom.__name__, sqrt(16),
            fl(2.7), ceil(2.1), list(chain([1], [2])), list(take(range(10), 3)),
            pjoin('a', 'b'), abc.__name__, lazy(), __import__('keyword').iskeyword('if')]
