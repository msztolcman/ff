#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from pprint import pprint, pformat

from test_config import *

unittest = import_unittest()

import ff

class MockArgParse(object):
    def __init__(self):
        self.ignorecase = False
        self.fnmatch_begin = False
        self.fnmatch_end = False
        self.pattern = ''

class TestPatternCompileFnmatch(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        pattern = r''

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_fnmatch_begin(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.fnmatch_begin = True

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'\A')

        self.assertFalse(cfg.ignorecase)
        self.assertTrue(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_fnmatch_end(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.fnmatch_end = True

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.DOTALL | re.MULTILINE)
        self.assertTrue(re.match(r'\\Z (?: \( \? [a-z]+ \) )?$', result.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % result.pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        pattern = r''
        cfg.ignorecase = True

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.IGNORECASE)
        self.assertEqual(result.pattern, r'')

        self.assertTrue(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_simple_pattern(self):
        cfg = MockArgParse()
        pattern = r'asd'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'asd')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        pattern = r'^asd$'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'\^asd\$')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_wildcard_single(self):
        cfg = MockArgParse()
        pattern = r'asd?asd'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'asd.asd')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_wildcard_multi(self):
        cfg = MockArgParse()
        pattern = r'asd*asd'
        cfg.pattern = pattern

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'asd.*asd')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_pattern_with_wildcard_multi_and_fnmatch_end(self):
        cfg = MockArgParse()
        pattern = r'asd*asd'
        cfg.pattern = pattern
        cfg.fnmatch_end = True

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertTrue(re.match(r'^ asd \. \* asd \\Z ( \( \?[a-z]+ \) )? $', result.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % result.pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

    def test_full_options(self):
        cfg = MockArgParse()
        pattern = r'asd*asd'
        cfg.pattern = pattern
        cfg.fnmatch_begin = True
        cfg.fnmatch_end = True
        cfg.ignorecase = True

        result = ff._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertTrue(re.match(r'^ \\A asd \. \* asd \\Z ( \( \?[a-z]+ \) )? $', result.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % result.pattern)

        self.assertTrue(cfg.ignorecase)
        self.assertTrue(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pattern)

if __name__ == '__main__':
    unittest.main()
