#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Plugin script for `ff` (http://msztolcman.github.io/ff/).
"""

from __future__ import print_function, unicode_literals

import os.path

def _test_greater(arg1, arg2):
    """ Test for being greater then.
    """
    return arg1 > arg2

def _test_less(arg1, arg2):
    """ Test for being less then.
    """
    return arg1 < arg2

def _test_equal(arg1, arg2):
    """ Test for being equal.
    """
    return arg1 == arg2

_TESTS = {
    '>': _test_greater,
    '<': _test_less,
    '=': _test_equal
}

_MULTI = {
    'b': 1,
    'k': 1024,
    'm': 1024**2,
    'g': 1024**3,
}

# pylint: disable=invalid-name
_cache = {}

def _action(__, argument, path):
    """ Test given path for being it's size match specified criteria.

        `__` - not used
        `argument` - data passed by user. It's syntax is: [<>=]?[0-9]+[bkgm]?
        `path` - path to tested file
    """

    if not argument:
        # pylint: disable=undefined-variable
        raise FFPluginError('missing size')

    if argument[0] in ('<', '>', '='):
        test = _TESTS[argument[0]]
        size = argument[1:]
    else:
        test = _TESTS['=']
        size = argument

    if size[-1] in 'bkmgBKMG':
        size = int(size[:-1]) * _MULTI[size[-1].lower()]
    else:
        size = int(size)

    path = os.path.realpath(path)
    if path not in _cache:
        _cache[path] = os.path.getsize(path)
    return test(_cache[path], size)

def plugin_action(name, argument, path):
    """ Action used by `ff`. Wrapper for `_action`.
    """
    try:
        return _action(name, argument, path)
    # pylint: disable=undefined-variable
    except FFPluginError:
        raise
    except:
        import sys
        ex = sys.exc_info()[1]
        # pylint: disable=undefined-variable
        raise FFPluginError(ex.message)

PLUGIN_DESCR = 'Filter files by their size.'
PLUGIN_HELP = '''Size must be given as argument, and must follow pattern (without spaces):

    operator size multiplier

Operator (can be omitted) is one of: >, <, = (default)
Multiplier (can be omitted) is one of: b (default), k (multiply by 1024),
m (multiply by 1024*1024) or g (multiply by 1024*1024*1024)'''.strip()
