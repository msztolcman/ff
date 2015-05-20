#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import itertools

from test_manager import *
from test_helpers import MockArgParse
from ff import pattern


class TestMagicPatternInitial(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        cfg.pattern = r''

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, r'')

        expected = {}
        self.assertDictEqual(expected, opts)

    def test_empty2(self):
        cfg = MockArgParse()
        cfg.pattern = r'//'

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, r'')

        expected = {}
        self.assertDictEqual(expected, opts)

    def test_pattern_simple_no_mode_modifiers(self):
        cfg = MockArgParse()
        cfg.pattern = r'/asd/'

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, r'asd')

        expected = {}
        self.assertDictEqual(expected, opts)

    def test_pattern_regexp_no_mode_modifiers(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = '/' + pat + '/'

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, r'^asd$')

        expected = {}
        self.assertDictEqual(expected, opts)


class TestMagicPatternMode(unittest.TestCase):
    def test_mode_p(self):
        cfg = MockArgParse()
        cfg.pattern = r'p/asd/'

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, 'asd')

        expected = {}
        self.assertDictEqual(expected, opts)

    def test_mode_f(self):
        cfg = MockArgParse()
        cfg.pattern = r'f/asd/'

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, 'asd')

        expected = {
            'fuzzy': True,
        }
        self.assertDictEqual(expected, opts)

    def test_mode_g(self):
        cfg = MockArgParse()
        cfg.pattern = r'g/asd/'

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, 'asd')

        expected = {
            'regexp': True,
        }
        self.assertDictEqual(expected, opts)

    def test_mode_unknown_mode(self):
        cfg = MockArgParse()
        cfg.pattern = r'z/asd/'

        with self.assertRaisesRegexp(pattern.PatternError, r'^Unknown mode in pattern:'):
            pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

    def test_mode_invalid_mode(self):
        cfg = MockArgParse()
        cfg.pattern = r'pg/asd/'

        with self.assertRaisesRegexp(pattern.PatternError, r'^Incorrect mode:'):
            pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)


class TestMagicPatternModifier(unittest.TestCase):
    def test_modifiers_single(self):
        modifier_to_option = {
            'i': 'ignorecase',
            'm': 'regex_multiline',
            's': 'regex_dotall',
            'r': 'invert_match',
            'q': 'path_search'
        }

        for modifier, selected_option_name in modifier_to_option.items():
            cfg = MockArgParse()
            cfg.pattern = r'/asd/' + modifier

            parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

            self.assertEqual(parsed_pat, r'asd')

            expected = {
                selected_option_name: True,
            }
            self.assertDictEqual(expected, opts)

    def test_modifiers_two_together_no_repeats(self):
        modifier_to_option = {
            'i': 'ignorecase',
            'm': 'regex_multiline',
            's': 'regex_dotall',
            'r': 'invert_match',
            'q': 'path_search'
        }

        for modifiers in itertools.permutations(modifier_to_option.keys(), 2):
            cfg = MockArgParse()
            cfg.pattern = r'/asd/' + ''.join(modifiers)

            parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

            self.assertEqual(parsed_pat, 'asd')

            expected = {modifier_to_option[modifier]: True for modifier in modifiers}
            self.assertDictEqual(expected, opts)

    def test_modifiers_two_together_repeats(self):
        modifier_to_option = {
            'i': 'ignorecase',
            'm': 'regex_multiline',
            's': 'regex_dotall',
            'r': 'invert_match',
            'q': 'path_search'
        }

        for modifier in modifier_to_option.keys():
            cfg = MockArgParse()
            cfg.pattern = r'/asd/' + modifier * 2

            with self.assertRaisesRegexp(pattern.PatternError, r'^Incorrect modifiers in pattern:'):
                pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

    def test_modifiers_three_together_no_repeats(self):
        modifier_to_option = {
            'i': 'ignorecase',
            'm': 'regex_multiline',
            's': 'regex_dotall',
            'r': 'invert_match',
            'q': 'path_search'
        }

        for modifiers in itertools.permutations(modifier_to_option.keys(), 3):
            cfg = MockArgParse()
            cfg.pattern = r'/asd/' + ''.join(modifiers)

            parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

            self.assertEqual(parsed_pat, 'asd')

            expected = {modifier_to_option[modifier]: True for modifier in modifiers}
            self.assertDictEqual(expected, opts)

    def test_modifiers_four_together_no_repeats(self):
        modifier_to_option = {
            'i': 'ignorecase',
            'm': 'regex_multiline',
            's': 'regex_dotall',
            'r': 'invert_match',
            'q': 'path_search'
        }

        for modifiers in itertools.permutations(modifier_to_option.keys(), 4):
            cfg = MockArgParse()
            cfg.pattern = r'/asd/' + ''.join(modifiers)

            parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

            self.assertEqual(parsed_pat, 'asd')

            expected = {modifier_to_option[modifier]: True for modifier in modifiers}
            self.assertDictEqual(expected, opts)

    def test_modifiers_five_together_no_repeats(self):
        modifier_to_option = {
            'i': 'ignorecase',
            'm': 'regex_multiline',
            's': 'regex_dotall',
            'r': 'invert_match',
            'q': 'path_search'
        }

        for modifiers in itertools.permutations(modifier_to_option.keys(), 5):
            cfg = MockArgParse()
            cfg.pattern = r'/asd/' + ''.join(modifiers)

            parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

            self.assertEqual(parsed_pat, 'asd')

            expected = {modifier_to_option[modifier]: True for modifier in modifiers}
            self.assertDictEqual(expected, opts)

    def test_modifier_ignored(self):
        cfg = MockArgParse()
        cfg.pattern = r'/asd/v'

        parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

        self.assertEqual(parsed_pat, 'asd')

        expected = {}
        self.assertDictEqual(expected, opts)

    def test_modifier_invalid(self):
        cfg = MockArgParse()
        cfg.pattern = r'/asd/z'

        with self.assertRaisesRegexp(pattern.PatternError, r'^Unknown modifier in pattern:'):
            pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)


class TestMagicPatternDelims(unittest.TestCase):
    def test_delims(self):
        delim_closed = {
            ## match same
            '/': '/', '!': '!', '@': '@', '#': '#', '%': '%', '|': '|', '?': '?', '+': '+',
            ## match pair
            '}': '{', ']': '[', ')': '(', '>': '<'
        }

        delims = set(delim_closed.keys()) | set(delim_closed.values())

        for delim_close, delim_open in itertools.product(delims, repeat=2):
            cfg = MockArgParse()

            cfg.pattern = delim_open + 'a' + delim_close

            if delim_close in delim_closed and delim_closed[delim_close] == delim_open:
                parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)
                self.assertEqual(parsed_pat, 'a')
            else:
                with self.assertRaisesRegexp(pattern.PatternError, r'^Inappropriate delimiters:'):
                    pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

    def test_matching_delims(self):
        delims = { '}': '{', '>': '<', ']': '[', ')': '(' }
        for delim_close, delim_open in delims.items():
            cfg = MockArgParse()

            cfg.pattern = delim_open + 'a' + delim_close

            parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

            self.assertEqual(parsed_pat, 'a')

    def test_same_delims(self):
        delims = '/!@#%|?+'
        for delim in delims:
            cfg = MockArgParse()

            cfg.pattern = delim + 'a' + delim

            parsed_pat, opts = pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)

            self.assertEqual(parsed_pat, 'a')

    def test_same_delims_unpaired(self):
        delims = { '!': '<', '>': '[', ']': '(', ')': '{' }
        for delim_close, delim_open in delims.items():
            cfg = MockArgParse()

            cfg.pattern = delim_open + 'a' + delim_close

            with self.assertRaises(pattern.PatternError):
                pattern._prepare_pattern__decompile_magic_pattern(cfg.pattern)


if __name__ == '__main__':
    unittest.main()
