#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os.path
import textwrap

from error import PluginError

def _test_greater(a, b): return a > b
def _test_lesser(a, b): return a < b
def _test_equal(a, b): return a == b
_tests = {
    '>': _test_greater,
    '<': _test_lesser,
    '=': _test_equal
}

_multi = {
    'b': 1,
    'k': 1024,
    'm': 1024**2,
    'g': 1024**3,
}

_cache = {}

def _action(name, argument, path):
    global _tests, _multi, _cache

    if not argument:
        raise PluginError('missing size')

    if argument[0] in ('<', '>', '='):
        test = _tests[argument[0]]
        size = argument[1:]
    else:
        test = _tests['=']
        size = argument

    if size[-1] in 'bkmgBKMG':
        size = int(size[:-1]) * _multi[size[-1].lower()]
    else:
        size = int(size)

    path = os.path.realpath(path)
    if path not in _cache:
        _cache[path] = os.path.getsize(path)
    return test(_cache[path], size)

def plugin_action(name, argument, path):
    try:
        return _action(name, argument, path)
    except PluginError:
        raise
    except:
        import sys
        e = sys.exc_info()[1]
        raise PluginError(e.message)

plugin_descr = 'Filter files by their size.'
plugin_help = '''Size must be given as argument, and must follow pattern:

    operator size multiplier

(without spaces).

Operator (can be omitted) is one of:

    > - file size must be bigger then argument
    < - file size must be lower then argument
    = - must be exactly as argument

Multiplier (can be omitted) is one of:
    b - do not multiply
    k - multiply size with 1024
    m - multiply size with 1024 * 1024
    g - multiply size with 1024 * 1024 * 1024'''.strip()
