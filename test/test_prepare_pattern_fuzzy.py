#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import re

from test_manager import *

from ff import pattern


RE_TYPE = type(re.compile(''))


class TestPatternCompileFuzzy(unittest.TestCase):
    def test_empty(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'()')

    def test_empty_pattern_fnmatch_begin(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.fnmatch_begin = True
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'(\A)')

    def test_empty_pattern_fnmatch_end(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.fnmatch_end = True
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'(\Z)')

    def test_empty_pattern_ignorecase(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.ignorecase = True
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(parsed_pat.pattern, r'()')

    def test_simple_pattern(self):
        pat = pattern.Pattern()
        pat.pattern = r'asd'
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'(.*a.*s.*d)')

    def test_pattern_with_regexp(self):
        pat = pattern.Pattern()
        pat.pattern = r'^asd$'
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'(.*\^.*a.*s.*d.*\$)')

    def test_pattern_with_regexp_and_fnmatch_begin(self):
        pat = pattern.Pattern()
        pat.pattern = r'^asd$'
        pat.fnmatch_begin = True
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'(\A.*\^.*a.*s.*d.*\$)')

    def test_full_options(self):
        pat = pattern.Pattern()
        pat.pattern = r'^asd$'
        pat.fnmatch_begin = True
        pat.fnmatch_end = True
        pat.ignorecase = True
        parsed_pat = pat._prepare_pattern__compile_fuzzy()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(parsed_pat.pattern, r'(\A.*\^.*a.*s.*d.*\$\Z)')


if __name__ == '__main__':
    unittest.main()
