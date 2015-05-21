# -*- coding: utf-8 -*-

"""
    Prepare and compile pattern
"""

from __future__ import print_function, unicode_literals, division

import re
import unicodedata

from ff.utils import u


_DELIM_CLOSED = {
    ## match same
    '/': '/', '!': '!', '@': '@', '#': '#', '%': '%', '|': '|', '?': '?', '+': '+',
    ## match pair
    '}': '{', ']': '[', ')': '(', '>': '<'
}

class PatternError(Exception):
    pass


# pylint: disable=too-many-branches
def _prepare_pattern__decompile_magic_pattern(pattern):
    """ Parse pattern and try to recognize it is magic pattern.
        If so, parse magic pattern and set options for argparse
        result as in magic pattern is set.
    """

    rxp_pattern = re.compile(r'''
        ^
        (?P<mode>           [a-z0-9]+            )?
        (?P<delim_open>     [{}[\]()<>/!@#%|?+]  )
        (?P<pattern>        .*                   )
        (?P<delim_close>    [{}[\]()<>/!@#%|?+]  )
        (?P<modifier>       [a-z0-9]+            )?
        $
    ''', re.UNICODE | re.VERBOSE)

    match = rxp_pattern.match(pattern)
    if not match:
        return pattern, {}

    pattern_parts = match.groupdict()

    if pattern_parts['delim_close'] not in _DELIM_CLOSED or \
            _DELIM_CLOSED[pattern_parts['delim_close']] != pattern_parts['delim_open']:
        raise PatternError('Inappropriate delimiters: %(delim_open)s %(delim_close)s' % pattern_parts)

    pat = pattern_parts['pattern']
    opts = {}

    # pylint: disable=superfluous-parens
    for item in (pattern_parts['modifier'] or ''):
        if len(set(pattern_parts['modifier'])) != len(pattern_parts['modifier']):
            raise PatternError('Incorrect modifiers in pattern: %s. Allowed modifiers: i, m, s, v, r.' % item)

        # pylint: disable=multiple-statements
        if item == 'i': opts['ignorecase'] = True
        elif item == 'm': opts['regex_multiline'] = True
        elif item == 's': opts['regex_dotall'] = True
        elif item == 'v': pass
        elif item == 'r': opts['invert_match'] = True
        elif item == 'q': opts['path_search'] = True
        else:
            raise PatternError('Unknown modifier in pattern: %s. Allowed modifiers: i, m, s, v, r.' % item)

    if pattern_parts['mode'] is not None:
        if len(pattern_parts['mode']) > 1:
            raise PatternError('Incorrect mode: %s. Allowed modes: p, g, f.' % pattern_parts['mode'])

        # pylint: disable=multiple-statements
        if pattern_parts['mode'] == 'g': opts['regexp'] = True
        elif pattern_parts['mode'] == 'p': pass
        elif pattern_parts['mode'] == 'f': opts['fuzzy'] = True
        else:
            raise PatternError('Unknown mode in pattern: %s. Allowed modes: p, g, f.' % pattern_parts['mode'])

    return pat, opts


def _prepare_pattern__compile_fuzzy(pattern, opts):
    """ Compile pattern to compiled regular expression using fuzzy syntax.

        fuzzy syntax mean that we search for name where are all given characters
        in given order, but there can be anything between them.
    """

    pat = ''
    if opts['fnmatch_begin']:
        pat += r'\A'
    for char in pattern:
        pat += '.*' + re.escape(char)
    if opts['fnmatch_end']:
        pat += r'\Z'

    flags = re.UNICODE | re.DOTALL | re.MULTILINE
    if opts['ignorecase']:
        flags = flags | re.IGNORECASE

    return re.compile(pat, flags)


def _prepare_pattern__compile_regexp(pattern, opts):
    """ Compile pattern to compiled regular expression using regexp syntax.

        We found that pattern is regular expression, and just pass there
        flags from arguments.
    """

    flags = re.UNICODE
    if opts['ignorecase']:
        flags = flags | re.IGNORECASE
    if opts['regex_dotall']:
        flags = flags | re.DOTALL
    if opts['regex_multiline']:
        flags = flags | re.MULTILINE

    return re.compile(pattern, flags)


def _prepare_pattern__compile_fnmatch(pattern, opts):
    """ Compile pattern to compiled regular expression using fnmatch syntax.

        See: http://docs.python.org/library/fnmatch.html
    """
    import fnmatch

    flags = re.UNICODE
    if opts['ignorecase']:
        flags = flags | re.IGNORECASE

    pat = fnmatch.translate(pattern)
    if opts['fnmatch_begin']:
        pat = r'\A' + pat

    ## our behaviour is in the opposite to fnmatch: by default *do not* match end of string
    if not opts['fnmatch_end']:
        pat = re.sub(r'\\Z (?: \( [^)]+ \) )? $', '', pat, flags=re.UNICODE | re.VERBOSE)

    return re.compile(pat, flags)


def prepare_pattern(cfg):
    """ Prepare pattern from input args to use.

        If work in regex mode, there pattern is only compiled with flags. In normal mode,
        pattern is converted to regex, and then compiled. Recognize also fuzzy mode.

        Returns always compiled regexp, ready to use.
    """

    cfg.pattern = u(cfg.pattern)
    cfg.pattern = unicodedata.normalize('NFKC', cfg.pattern)

    if cfg.magic_pattern:
        cfg.pattern, opts = _prepare_pattern__decompile_magic_pattern(cfg.pattern)
        for opt, val in opts.items():
            setattr(cfg, opt, val)

    opts = {
        'fnmatch_begin': cfg.fnmatch_begin,
        'fnmatch_end': cfg.fnmatch_end,
        'ignorecase': cfg.ignorecase,
        'regex_dotall': cfg.regex_dotall,
        'regex_multiline': cfg.regex_multiline,
    }

    if cfg.fuzzy:
        cfg.pattern = _prepare_pattern__compile_fuzzy(cfg.pattern, opts)
    elif cfg.regexp:
        cfg.pattern = _prepare_pattern__compile_regexp(cfg.pattern, opts)
    else:
        cfg.pattern = _prepare_pattern__compile_fnmatch(cfg.pattern, opts)
