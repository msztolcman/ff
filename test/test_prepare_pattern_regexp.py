#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from test_manager import *
from ff import pattern


class MockArgParse(object):
    def __init__(self):
        self.ignorecase = False
        self.pattern = ''
        self.regex_dotall = False
        self.regex_multiline = False

class TestPatternCompileRegexp(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        pat = r''

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pat)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_regex_dotall(self):
        cfg = MockArgParse()
        pat = r''
        cfg.regex_dotall = True

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(result.pattern, pat)

        self.assertFalse(cfg.ignorecase)
        self.assertTrue(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_regex_multiline(self):
        cfg = MockArgParse()
        pat = r''
        cfg.regex_multiline = True

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE)
        self.assertEqual(result.pattern, pat)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertTrue(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        pat = r''
        cfg.ignorecase = True

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.IGNORECASE)
        self.assertEqual(result.pattern, pat)

        self.assertTrue(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

    def test_simple_pattern(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pat)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pat)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_regexp_and_regex_dotall(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = pat
        cfg.regex_dotall = True

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(result.pattern, pat)

        self.assertFalse(cfg.ignorecase)
        self.assertTrue(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

    def test_full_options(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = pat
        cfg.ignorecase = True
        cfg.regex_dotall = True
        cfg.regex_multiline = True

        result = pattern._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, pat)

        self.assertTrue(cfg.ignorecase)
        self.assertTrue(cfg.regex_dotall)
        self.assertTrue(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pat)

if __name__ == '__main__':
    unittest.main()
