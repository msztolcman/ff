#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from pprint import pprint, pformat

from test_manager import *

unittest = import_unittest()

import ff

class MockArgParse(object):
    def __init__(self):
        self.ignorecase = False
        self.pattern = ''
        self.regex_dotall = False
        self.regex_multiline = False

class TestPatternCompileRegexp(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        pattern = r''

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_regex_dotall(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.regex_dotall = True

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(result.pattern, pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertTrue(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_regex_multiline(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.regex_multiline = True

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE)
        self.assertEqual(result.pattern, pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertTrue(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.ignorecase = True

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.IGNORECASE)
        self.assertEqual(result.pattern, pattern)

        self.assertTrue(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

    def test_simple_pattern(self):
        cfg = MockArgParse()
        pattern = r'asd'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        pattern = r'^asd$'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_regexp_and_regex_dotall(self):
        cfg = MockArgParse()
        pattern = r'^asd$'
        cfg.pattern = pattern
        cfg.regex_dotall = True

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.DOTALL)
        self.assertEqual(result.pattern, pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertTrue(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

    def test_full_options(self):
        cfg = MockArgParse()
        pattern = r'^asd$'
        cfg.pattern = pattern
        cfg.ignorecase = True
        cfg.regex_dotall = True
        cfg.regex_multiline = True

        result = ff._prepare_pattern__compile_regexp(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, pattern)

        self.assertTrue(cfg.ignorecase)
        self.assertTrue(cfg.regex_dotall)
        self.assertTrue(cfg.regex_multiline)
        self.assertEqual(cfg.pattern, pattern)

if __name__ == '__main__':
    unittest.main()
