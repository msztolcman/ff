#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from test_manager import *

from ff import pattern


class MockArgParse(object):
    def __init__(self):
        self.ignorecase = False
        self.fnmatch_begin = False
        self.fnmatch_end = False
        self.pattern = ''

class TestPatternCompileFnmatch(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        pat = r''

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, pat)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_fnmatch_begin(self):
        cfg = MockArgParse()
        pat = r''
        cfg.fnmatch_begin = True

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'\A')

        self.assertFalse(cfg.ignorecase)
        self.assertTrue(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_fnmatch_end(self):
        cfg = MockArgParse()
        pat = r''
        cfg.fnmatch_end = True

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.DOTALL | re.MULTILINE)
        self.assertTrue(re.match(r'\\Z (?: \( \? [a-z]+ \) )?$', result.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % result.pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        pat = r''
        cfg.ignorecase = True

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.IGNORECASE)
        self.assertEqual(result.pattern, r'')

        self.assertTrue(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_simple_pattern(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'asd')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'\^asd\$')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_wildcard_single(self):
        cfg = MockArgParse()
        pat = r'asd?asd'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'asd.asd')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_wildcard_multi(self):
        cfg = MockArgParse()
        pat = r'asd*asd'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE)
        self.assertEqual(result.pattern, r'asd.*asd')

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_wildcard_multi_and_fnmatch_end(self):
        cfg = MockArgParse()
        pat = r'asd*asd'
        cfg.pattern = pat
        cfg.fnmatch_end = True

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertTrue(re.match(r'^ asd \. \* asd \\Z ( \( \?[a-z]+ \) )? $', result.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % result.pattern)

        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

    def test_full_options(self):
        cfg = MockArgParse()
        pat = r'asd*asd'
        cfg.pattern = pat
        cfg.fnmatch_begin = True
        cfg.fnmatch_end = True
        cfg.ignorecase = True

        result = pattern._prepare_pattern__compile_fnmatch(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertTrue(re.match(r'^ \\A asd \. \* asd \\Z ( \( \?[a-z]+ \) )? $', result.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % result.pattern)

        self.assertTrue(cfg.ignorecase)
        self.assertTrue(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertEqual(cfg.pattern, pat)

if __name__ == '__main__':
    unittest.main()
