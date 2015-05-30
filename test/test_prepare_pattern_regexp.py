#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import re

from test_manager import *

from ff import pattern


RE_TYPE = type(re.compile(''))


class TestPatternCompileRegexp(unittest.TestCase):
    def test_empty(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, '')

    def test_empty_pattern_regex_dotall(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.regex_dotall = True
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, '')

    def test_empty_pattern_regex_multiline(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.regex_multiline = True
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE)
        self.assertEqual(parsed_pat.pattern, '')

    def test_empty_pattern_ignorecase(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.ignorecase = True
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.IGNORECASE)
        self.assertEqual(parsed_pat.pattern, '')

    def test_simple_pattern(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.pattern = r'asd'
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'asd')

    def test_pattern_with_regexp(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.pattern = r'^asd$'
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'^asd$')

    def test_pattern_with_regexp_and_regex_dotall(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat.pattern = r'^asd$'
        pat.regex_dotall = True
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'^asd$')

    def test_full_options(self):
        pat = pattern.Pattern()
        pat.pattern = r'^asd$'
        pat.ignorecase = True
        pat.regex_dotall = True
        pat.regex_multiline = True
        parsed_pat = pat._prepare_pattern__compile_regexp()

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(parsed_pat.pattern, r'^asd$')


if __name__ == '__main__':
    unittest.main()
