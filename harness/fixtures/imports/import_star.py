# feature: imports
# summary: star import populates module globals (observed through the globals snapshot)
from keyword import *


def observe():
    return [iskeyword('def'), 'class' in kwlist, sorted(filter(lambda n: 'keyword' in n, globals()))]
