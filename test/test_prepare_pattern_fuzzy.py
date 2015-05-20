#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from test_helpers import get_opts, MockArgParse
from test_manager import *

from ff import pattern


RE_TYPE = type(re.compile(''))


class TestPatternCompileFuzzy(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'')

    def test_empty_pattern_fnmatch_begin(self):
        cfg = MockArgParse()
        cfg.fnmatch_begin = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\A')

    def test_empty_pattern_fnmatch_end(self):
        cfg = MockArgParse()
        cfg.fnmatch_end = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\Z')

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        cfg.ignorecase = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, r'')

    def test_simple_pattern(self):
        cfg = MockArgParse()
        cfg.pattern = r'asd'

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'.*a.*s.*d')

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        cfg.pattern = r'^asd$'

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'.*\^.*a.*s.*d.*\$')

    def test_pattern_with_regexp_and_fnmatch_begin(self):
        cfg = MockArgParse()
        cfg.pattern = r'^asd$'
        cfg.fnmatch_begin = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\A.*\^.*a.*s.*d.*\$')

    def test_full_options(self):
        cfg = MockArgParse()
        cfg.pattern = r'^asd$'
        cfg.fnmatch_begin = True
        cfg.fnmatch_end = True
        cfg.ignorecase = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(result, RE_TYPE)

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, r'\A.*\^.*a.*s.*d.*\$\Z')


if __name__ == '__main__':
    unittest.main()
