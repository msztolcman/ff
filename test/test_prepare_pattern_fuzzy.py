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
        self.fnmatch_begin = False
        self.fnmatch_end = False
        self.ignorecase = False
        self.pattern = ''

class TestPatternCompileFuzzy(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        pattern = r''

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_fnmatch_begin(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.fnmatch_begin = True

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\A')

        self.assertTrue(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_fnmatch_end(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.fnmatch_end = True

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\Z')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.ignorecase = True

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, r'')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertTrue(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

    def test_simple_pattern(self):
        cfg = MockArgParse()
        pattern = r'asd'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'.*a.*s.*d')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        pattern = r'^asd$'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'.*\^.*a.*s.*d.*\$')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_regexp_and_fnmatch_begin(self):
        cfg = MockArgParse()
        pattern = r'^asd$'
        cfg.pattern = pattern
        cfg.fnmatch_begin = True

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\A.*\^.*a.*s.*d.*\$')

        self.assertTrue(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

    def test_full_options(self):
        cfg = MockArgParse()
        pattern = r'^asd$'
        cfg.pattern = pattern
        cfg.fnmatch_begin = True
        cfg.fnmatch_end = True
        cfg.ignorecase = True

        result = ff._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, r'\A.*\^.*a.*s.*d.*\$\Z')

        self.assertTrue(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertTrue(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pattern)

if __name__ == '__main__':
    unittest.main()
