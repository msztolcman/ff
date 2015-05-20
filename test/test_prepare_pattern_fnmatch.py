#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import re

from test_helpers import get_opts, MockArgParse
from test_manager import *

from ff import pattern


RE_TYPE = type(re.compile(''))


class TestPatternCompileFnmatch(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'')

    def test_empty_pattern_fnmatch_begin(self):
        cfg = MockArgParse()
        cfg.fnmatch_begin = True

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'\A')

    def test_empty_pattern_fnmatch_end(self):
        cfg = MockArgParse()
        cfg.fnmatch_end = True

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.DOTALL | re.MULTILINE)
        self.assertTrue(re.match(r'\\Z (?: \( \? [a-z]+ \) )?$', parsed_pat.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % parsed_pat.pattern)

    def test_empty_pattern_ignorecase(self):
        cfg = MockArgParse()
        cfg.ignorecase = True

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.IGNORECASE)
        self.assertEqual(parsed_pat.pattern, r'')

    def test_simple_pattern(self):
        cfg = MockArgParse()
        cfg.pattern = r'asd'

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'asd')

    def test_pattern_with_regexp(self):
        cfg = MockArgParse()
        cfg.pattern = r'^asd$'

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'\^asd\$')

    def test_pattern_with_wildcard_single(self):
        cfg = MockArgParse()
        cfg.pattern = r'asd?asd'

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'asd.asd')

    def test_pattern_with_wildcard_multi(self):
        cfg = MockArgParse()
        cfg.pattern = r'asd*asd'

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE)
        self.assertEqual(parsed_pat.pattern, r'asd.*asd')

    def test_pattern_with_wildcard_multi_and_fnmatch_end(self):
        cfg = MockArgParse()
        cfg.pattern = r'asd*asd'
        cfg.fnmatch_end = True

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL)
        self.assertTrue(re.match(r'^ asd \. \* asd \\Z ( \( \?[a-z]+ \) )? $', parsed_pat.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % parsed_pat.pattern)

    def test_full_options(self):
        cfg = MockArgParse()
        cfg.pattern = r'asd*asd'
        cfg.fnmatch_begin = True
        cfg.fnmatch_end = True
        cfg.ignorecase = True

        parsed_pat = pattern._prepare_pattern__compile_fnmatch(cfg.pattern, get_opts(cfg))

        self.assertIsInstance(parsed_pat, RE_TYPE)

        self.assertEqual(parsed_pat.flags, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertTrue(re.match(r'^ \\A asd \. \* asd \\Z ( \( \?[a-z]+ \) )? $', parsed_pat.pattern, re.VERBOSE), 'Pattern doesn\'t match: %s' % parsed_pat.pattern)


if __name__ == '__main__':
    unittest.main()
