#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from test_helpers import get_opts, MockArgParse
from test_manager import *

from ff import pattern


RE_TYPE = type(re.compile(''))


class TestPatternCompileRegexp(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, '')

    def test_empty_pattern_regex_dotall(self):
        cfg = MockArgParse()
        cfg.regex_dotall = True

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, '')

    def test_empty_pattern_regex_multiline(self):
        cfg = MockArgParse()
        cfg.regex_multiline = True

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE)
        self.assertEqual(parsed_pat.pattern, '')

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        cfg.ignorecase = True

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.IGNORECASE)
        self.assertEqual(parsed_pat.pattern, '')

    def test_simple_pattern(self):
        cfg = MockArgParse()
        cfg.pattern = r'asd'

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'asd')

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        cfg.pattern = r'^asd$'

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'^asd$')

    def test_pattern_with_regexp_and_regex_dotall(self):
        cfg = MockArgParse()
        cfg.pattern = r'^asd$'
        cfg.regex_dotall = True

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(parsed_pat.pattern, r'^asd$')

    def test_full_options(self):
        cfg = MockArgParse()
        cfg.pattern = r'^asd$'
        cfg.ignorecase = True
        cfg.regex_dotall = True
        cfg.regex_multiline = True

        parsed_pat = pattern._prepare_pattern__compile_regexp(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(parsed_pat.pattern, r'^asd$')


if __name__ == '__main__':
    unittest.main()
