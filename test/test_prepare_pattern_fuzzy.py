#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from test_manager import *

from ff import pattern


class MockArgParse(object):
    def __init__(self):
        self.fnmatch_begin = False
        self.fnmatch_end = False
        self.ignorecase = False
        self.pattern = ''

class TestPatternCompileFuzzy(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        pat = r''

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_fnmatch_begin(self):
        cfg = MockArgParse()
        pat = r''
        cfg.fnmatch_begin = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\A')

        self.assertTrue(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_fnmatch_end(self):
        cfg = MockArgParse()
        pat = r''
        cfg.fnmatch_end = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\Z')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        pat = r''
        cfg.ignorecase = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, r'')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertTrue(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

    def test_simple_pattern(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'.*a.*s.*d')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = pat

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'.*\^.*a.*s.*d.*\$')

        self.assertFalse(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

    def test_pattern_with_regexp_and_fnmatch_begin(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = pat
        cfg.fnmatch_begin = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertEqual(result.pattern, r'\A.*\^.*a.*s.*d.*\$')

        self.assertTrue(cfg.fnmatch_begin)
        self.assertFalse(cfg.fnmatch_end)
        self.assertFalse(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

    def test_full_options(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = pat
        cfg.fnmatch_begin = True
        cfg.fnmatch_end = True
        cfg.ignorecase = True

        result = pattern._prepare_pattern__compile_fuzzy(cfg)

        expected_type = re.compile('')
        self.assertIsInstance(result, type(expected_type))

        self.assertEqual(result.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertEqual(result.pattern, r'\A.*\^.*a.*s.*d.*\$\Z')

        self.assertTrue(cfg.fnmatch_begin)
        self.assertTrue(cfg.fnmatch_end)
        self.assertTrue(cfg.ignorecase)
        self.assertEqual(cfg.pattern, pat)

if __name__ == '__main__':
    unittest.main()
