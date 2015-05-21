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

_MODIFIERS = {
    'i': 'ignorecase',
    'm': 'regex_multiline',
    's': 'regex_dotall',
    'v': None,
    'r': 'invert_match',
}

_VALID_MODIFIERS = sorted(_MODIFIERS.keys())

_MODES = {
    'g': 'regexp',
    'p': None,
    'f': 'fuzzy',
}

_VALID_MODES = sorted(_MODES.keys())


class PatternError(Exception):
    """
        Pattern error exception
    """
    pass


def prepare_pattern(cfg):
    """
    Parse and compile pattern
    :param cfg:
    :return: Pattern
    """
    pat = Pattern()

    opts_list = ('fnmatch_begin', 'fnmatch_end', 'ignorecase', 'regex_dotall', 'regex_multiline',
    'invert_match', 'regexp', 'fuzzy', 'magic_pattern', 'pattern')

    for opt in opts_list:
        setattr(pat, opt, getattr(cfg, opt))

    pat.compile()

    opts = {}
    for opt in opts_list:
        opts[opt] = getattr(pat, opt)

    return pat.pattern, opts


# pylint: disable=too-many-instance-attributes
class Pattern(object):
    """ Representation of pattern to search
    """
    STATUS_NEW = 1
    STATUS_IN_PROGRESS = 2
    STATUS_COMPLETED = 3

    def __init__(self):
        self._pattern = ''
        self._fnmatch_begin = False
        self._fnmatch_end = False
        self._ignorecase = False
        self._regex_dotall = False
        self._regex_multiline = False
        self._invert_match = False
        self._regexp = False
        self._fuzzy = False
        self._magic_pattern = False
        self._compilation_status = self.STATUS_NEW

    def compile(self):
        """ Compile pattern using data set to this
            :return:
        """
        self._compilation_status = self.STATUS_IN_PROGRESS

        if self.magic_pattern:
            self._prepare_pattern__decompile_magic_pattern()

        if self.fuzzy:
            self.pattern = self._prepare_pattern__compile_fuzzy()
        elif self.regexp:
            self.pattern = self._prepare_pattern__compile_regexp()
        else:
            self.pattern = self._prepare_pattern__compile_fnmatch()

        self._compilation_status = self.STATUS_COMPLETED

    def _prepare_pattern__decompile_magic_pattern(self):
        """ Parse pattern and try to recognize it is magic pattern.
            If so, parse magic pattern and set options for argparse
            result as in magic pattern is set.
            :return:
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

        match = rxp_pattern.match(self.pattern)
        if not match:
            return {}

        pattern_parts = match.groupdict()

        if pattern_parts['delim_close'] not in _DELIM_CLOSED or \
                        _DELIM_CLOSED[pattern_parts['delim_close']] != pattern_parts['delim_open']:
            raise PatternError('Inappropriate delimiters: %(delim_open)s %(delim_close)s' % pattern_parts)

        self.pattern = pattern_parts['pattern']

        # pylint: disable=superfluous-parens
        for item in (pattern_parts['modifier'] or ''):
            if len(set(pattern_parts['modifier'])) != len(pattern_parts['modifier']):
                raise PatternError('Incorrect modifiers in pattern: %s. Allowed modifiers: %s.' %
                                   (item, ', '.join(_VALID_MODIFIERS)))

            try:
                if _MODIFIERS[item]:
                    setattr(self, _MODIFIERS[item], True)
            except KeyError:
                raise PatternError('Unknown modifier in pattern: %s. Allowed modifiers: %s.' %
                                   (item, ', '.join(_VALID_MODIFIERS)))

        if pattern_parts['mode'] is not None:
            if len(pattern_parts['mode']) > 1:
                raise PatternError('Incorrect mode: %s. Allowed modes: %s.' %
                                   (pattern_parts['mode'], ', '.join(_VALID_MODES)))

            try:
                if _MODES[pattern_parts['mode']]:
                    setattr(self, _MODES[pattern_parts['mode']], True)
            except KeyError:
                raise PatternError('Unknown mode in pattern: %s. Allowed modes: %s.' %
                                   (pattern_parts['mode'], ', '.join(_VALID_MODES)))

    def _prepare_pattern__compile_fuzzy(self):
        """ Compile pattern to compiled regular expression using fuzzy syntax.

            fuzzy syntax mean that we search for name where are all given characters
            in given order, but there can be anything between them.

            :return: compiled regular expression
        """

        pat = ''
        if self.fnmatch_begin:
            pat += r'\A'
        for char in self.pattern:
            pat += '.*' + re.escape(char)
        if self.fnmatch_end:
            pat += r'\Z'

        flags = re.UNICODE | re.DOTALL | re.MULTILINE
        if self.ignorecase:
            flags = flags | re.IGNORECASE

        return re.compile(pat, flags)

    def _prepare_pattern__compile_regexp(self):
        """ Compile pattern to compiled regular expression using regexp syntax.

            We found that pattern is regular expression, and just pass there
            flags from arguments.

            :return: compiled regular expression
        """

        flags = re.UNICODE
        if self.ignorecase:
            flags = flags | re.IGNORECASE
        if self.regex_dotall:
            flags = flags | re.DOTALL
        if self.regex_multiline:
            flags = flags | re.MULTILINE

        return re.compile(self.pattern, flags)

    def _prepare_pattern__compile_fnmatch(self):
        """ Compile pattern to compiled regular expression using fnmatch syntax.

            See: http://docs.python.org/library/fnmatch.html

            :return: compiled regular expression
        """
        import fnmatch

        flags = re.UNICODE
        if self.ignorecase:
            flags = flags | re.IGNORECASE

        pat = fnmatch.translate(self.pattern)
        if self.fnmatch_begin:
            pat = r'\A' + pat

        ## our behaviour is in the opposite to fnmatch: by default *do not* match end of string
        if not self.fnmatch_end:
            pat = re.sub(r'\\Z (?: \( [^)]+ \) )? $', '', pat, flags=re.UNICODE | re.VERBOSE)

        return re.compile(pat, flags)

    @property
    def pattern(self):
        """ Getter for pattern property
            :return:
        """
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        """ Setter for pattern property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_NEW:
            self._pattern = u(value)
            self._pattern = unicodedata.normalize('NFKC', self._pattern)
        elif self._compilation_status == self.STATUS_IN_PROGRESS:
            self._pattern = value
        else:
            raise PatternError('Pattern instance cannot be modified after compiling')

    @property
    def fnmatch_begin(self):
        """ Getter for fnmatch_begin property
            :return:
        """
        return self._fnmatch_begin

    @fnmatch_begin.setter
    def fnmatch_begin(self, value):
        """ Setter for fnmatch_begin property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._fnmatch_begin = bool(value)

    @property
    def fnmatch_end(self):
        """ Getter for fnmatch_end property
            :return:
        """
        return self._fnmatch_end

    @fnmatch_end.setter
    def fnmatch_end(self, value):
        """ Setter for fnmatch_end property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._fnmatch_end = bool(value)

    @property
    def ignorecase(self):
        """ Getter for ignorecase property
            :return:
        """
        return self._ignorecase

    @ignorecase.setter
    def ignorecase(self, value):
        """ Setter for ignorecase property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._ignorecase = bool(value)

    @property
    def regex_dotall(self):
        """ Getter for regex_dotall property
            :return:
        """
        return self._regex_dotall

    @regex_dotall.setter
    def regex_dotall(self, value):
        """ Setter for regex_dotall property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._regex_dotall = bool(value)

    @property
    def regex_multiline(self):
        """ Getter for regex_multiline property
            :return:
        """
        return self._regex_multiline

    @regex_multiline.setter
    def regex_multiline(self, value):
        """ Setter for regex_multiline property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._regex_multiline = bool(value)

    @property
    def invert_match(self):
        """ Getter for invert_match property
            :return:
        """
        return self._invert_match

    @invert_match.setter
    def invert_match(self, value):
        """ Setter for invert_match property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._invert_match = bool(value)

    @property
    def regexp(self):
        """ Getter for regexp property
            :return:
        """
        return self._regexp

    @regexp.setter
    def regexp(self, value):
        """ Setter for regexp property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._regexp = bool(value)

    @property
    def fuzzy(self):
        """ Getter for fuzzy property
            :return:
        """
        return self._fuzzy

    @fuzzy.setter
    def fuzzy(self, value):
        """ Setter for fuzzy property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._fuzzy = bool(value)

    @property
    def magic_pattern(self):
        """ Getter for magic_pattern property
            :return:
        """
        return self._magic_pattern

    @magic_pattern.setter
    def magic_pattern(self, value):
        """ Setter for magic_pattern property.
            Do not allow to change after call to self.compile
            :param value:
            :return:
        """
        if self._compilation_status == self.STATUS_COMPLETED:
            raise PatternError('Pattern instance cannot be modified after compiling')
        self._magic_pattern = bool(value)
