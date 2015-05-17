# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import re
import unicodedata

from ff.utils import u

def _prepare_pattern__magic(args):  ## pylint: disable-msg=too-many-branches
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

    match = rxp_pattern.match(args.pattern)
    if not match:
        return

    pattern_parts = match.groupdict()

    delim_closed = {
        ## match same
        '/': '/', '!': '!', '@': '@', '#': '#', '%': '%', '|': '|', '?': '?', '+': '+',
        ## match pair
        '}': '{', ']': '[', ')': '(', '>': '<'
    }
    if pattern_parts['delim_close'] not in delim_closed or \
            delim_closed[pattern_parts['delim_close']] != pattern_parts['delim_open']:
        return 'Inappropriate delimiters: %(delim_open)s %(delim_close)s' % pattern_parts

    args.pattern = pattern_parts['pattern']

    for item in (pattern_parts['modifier'] or ''):
        if len(set(pattern_parts['modifier'])) != len(pattern_parts['modifier']):
            return 'Incorrect modifiers in pattern: %s. Allowed modifiers: i, m, s, v, r.' % item

        ## pylint: disable-msg=multiple-statements
        if item == 'i': args.ignorecase = True
        elif item == 'm': args.regex_multiline = True
        elif item == 's': args.regex_dotall = True
        elif item == 'v': pass
        elif item == 'r': args.invert_match = True
        elif item == 'q': args.path_search = True
        else:
            return 'Unknown modifier in pattern: %s. Allowed modifiers: i, m, s, v, r.' % item

    if pattern_parts['mode'] is not None:
        if len(pattern_parts['mode']) > 1:
            return 'Incorrect mode: %s. Allowed modes: p, g, f.' % pattern_parts['mode']

        ## pylint: disable-msg=multiple-statements
        if pattern_parts['mode'] == 'g': args.regexp = True
        elif pattern_parts['mode'] == 'p': pass
        elif pattern_parts['mode'] == 'f': args.fuzzy = True
        else:
            return 'Unknown mode in pattern: %s. Allowed modes: p, g, f.' % pattern_parts['mode']


def _prepare_pattern__compile_fuzzy(cfg):
    """ Compile pattern to compiled regular expression using fuzzy syntax.

        fuzzy syntax mean that we search for name where are all given characters
        in given order, but there can be anything between them.
    """

    pattern = ''
    if cfg.fnmatch_begin:
        pattern += r'\A'
    for char in cfg.pattern:
        pattern += '.*' + re.escape(char)
    if cfg.fnmatch_end:
        pattern += r'\Z'

    flags = re.UNICODE | re.DOTALL | re.MULTILINE
    if cfg.ignorecase:
        flags = flags | re.IGNORECASE

    return re.compile(pattern, flags)


def _prepare_pattern__compile_regexp(cfg):  ## pylint: disable-msg=invalid-name
    """ Compile pattern to compiled regular expression using regexp syntax.

        We found that pattern is regular expression, and just pass there
        flags from arguments.
    """

    flags = re.UNICODE
    if cfg.ignorecase:
        flags = flags | re.IGNORECASE
    if cfg.regex_dotall:
        flags = flags | re.DOTALL
    if cfg.regex_multiline:
        flags = flags | re.MULTILINE

    return re.compile(cfg.pattern, flags)


def _prepare_pattern__compile_fnmatch(cfg):  ## pylint: disable-msg=invalid-name
    """ Compile pattern to compiled regular expression using fnmatch syntax.

        See: http://docs.python.org/library/fnmatch.html
    """
    import fnmatch

    flags = re.UNICODE
    if cfg.ignorecase:
        flags = flags | re.IGNORECASE

    pattern = fnmatch.translate(cfg.pattern)
    if cfg.fnmatch_begin:
        pattern = r'\A' + pattern

    ## our behaviour is in the opposite to fnmatch: by default *do not* match end of string
    if not cfg.fnmatch_end:
        pattern = re.sub(r'\\Z (?: \( [^)]+ \) )? $', '', pattern, flags=re.UNICODE | re.VERBOSE)

    return re.compile(pattern, flags)


def prepare_pattern(cfg):
    """ Prepare pattern from input args to use.

        If work in regex mode, there pattern is only compiled with flags. In normal mode,
        pattern is converted to regex, and then compiled. Recognize also fuzzy mode.

        Returns always compiled regexp, ready to use.
    """

    parse_magic_pattern = False
    if cfg.pattern is not None:
        cfg.anon_sources.insert(0, cfg.anon_pattern)
    else:
        parse_magic_pattern = True
        cfg.pattern = cfg.anon_pattern

    if cfg.pattern is None:
        return 'argument -p/--pattern is required'

    cfg.pattern = u(cfg.pattern)
    cfg.pattern = unicodedata.normalize('NFKC', cfg.pattern)

    if parse_magic_pattern:
        err_msg = _prepare_pattern__magic(cfg)
        if err_msg:
            return err_msg

    if cfg.fuzzy:
        cfg.pattern = _prepare_pattern__compile_fuzzy(cfg)
    elif cfg.regexp:
        cfg.pattern = _prepare_pattern__compile_regexp(cfg)
    else:
        cfg.pattern = _prepare_pattern__compile_fnmatch(cfg)
