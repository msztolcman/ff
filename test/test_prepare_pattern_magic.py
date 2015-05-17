#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import itertools

from test_manager import *
from ff import pattern


class MockArgParse(object):
    def __init__(self):
        self.fuzzy = False
        self.ignorecase = False
        self.invert_match = False
        self.path_search = False
        self.pattern = ''
        self.regex_dotall = False
        self.regex_multiline = False
        self.regexp = False


class TestMagicPatternInitial(unittest.TestCase):
    def test_empty(self):
        cfg = MockArgParse()
        cfg.pattern = r''

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, r'')
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)

    def test_empty2(self):
        cfg = MockArgParse()
        pat = r'//'
        cfg.pattern = pat

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, r'')
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)

    def test_pattern_simple_no_mode_modifiers(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = '/' + pat + '/'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)

    def test_pattern_regexp_no_mode_modifiers(self):
        cfg = MockArgParse()
        pat = r'^asd$'
        cfg.pattern = '/' + pat + '/'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)


class TestMagicPatternMode(unittest.TestCase):
    def test_mode_p(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = r'p/' + pat + r'/'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)

    def test_mode_f(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = r'f/' + pat + r'/'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)
        self.assertTrue(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)

    def test_mode_g(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = r'g/' + pat + r'/'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertTrue(cfg.regexp)

    def test_mode_unknown_mode(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = r'z/' + pat + r'/'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertTrue(result.startswith('Unknown mode in pattern:'))
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)

    def test_mode_invalid_mode(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = r'pg/' + pat + r'/'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertTrue(result.startswith('Incorrect mode:'))
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)


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
            pat = r'asd'
            cfg.pattern = r'/' + pat + r'/' + modifier

            result = pattern._prepare_pattern__magic(cfg)

            self.assertIsNone(result)

            self.assertFalse(cfg.fuzzy)
            self.assertEqual(cfg.pattern, pat)
            self.assertFalse(cfg.regexp)

            for option_name in modifier_to_option.values():
                value = getattr(cfg, option_name)

                if option_name == selected_option_name:
                    self.assertTrue(value)
                else:
                    self.assertFalse(value)

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
            pat = r'asd'
            cfg.pattern = r'/' + pat + r'/' + ''.join(modifiers)

            result = pattern._prepare_pattern__magic(cfg)

            self.assertIsNone(result)

            self.assertFalse(cfg.fuzzy)
            self.assertEqual(cfg.pattern, pat)
            self.assertFalse(cfg.regexp)

            for modifier, option_name in modifier_to_option.items():
                value = getattr(cfg, option_name)
                if modifier in modifiers:
                    self.assertTrue(value)
                else:
                    self.assertFalse(value)

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
            pat = r'asd'
            cfg.pattern = r'/' + pat + r'/' + modifier * 2

            result = pattern._prepare_pattern__magic(cfg)

            self.assertTrue(result.startswith('Incorrect modifiers in pattern:'))

            self.assertFalse(cfg.fuzzy)
            self.assertEqual(cfg.pattern, pat)
            self.assertFalse(cfg.regexp)

            for option_name in modifier_to_option.values():
                value = getattr(cfg, option_name)
                self.assertFalse(value)

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
            pat = r'asd'
            cfg.pattern = r'/' + pat + r'/' + ''.join(modifiers)

            result = pattern._prepare_pattern__magic(cfg)

            self.assertIsNone(result)

            self.assertFalse(cfg.fuzzy)
            self.assertEqual(cfg.pattern, pat)
            self.assertFalse(cfg.regexp)

            for modifier, option_name in modifier_to_option.items():
                value = getattr(cfg, option_name)
                if modifier in modifiers:
                    self.assertTrue(value)
                else:
                    self.assertFalse(value)

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
            pat = r'asd'
            cfg.pattern = r'/' + pat + r'/' + ''.join(modifiers)

            result = pattern._prepare_pattern__magic(cfg)

            self.assertIsNone(result)

            self.assertFalse(cfg.fuzzy)
            self.assertEqual(cfg.pattern, pat)
            self.assertFalse(cfg.regexp)

            for modifier, option_name in modifier_to_option.items():
                value = getattr(cfg, option_name)
                if modifier in modifiers:
                    self.assertTrue(value)
                else:
                    self.assertFalse(value)

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
            pat = r'asd'
            cfg.pattern = r'/' + pat + r'/' + ''.join(modifiers)

            result = pattern._prepare_pattern__magic(cfg)

            self.assertIsNone(result)

            self.assertFalse(cfg.fuzzy)
            self.assertEqual(cfg.pattern, pat)
            self.assertFalse(cfg.regexp)

            for modifier, option_name in modifier_to_option.items():
                value = getattr(cfg, option_name)
                if modifier in modifiers:
                    self.assertTrue(value)
                else:
                    self.assertFalse(value)

    def test_modifier_ignored(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = r'/' + pat + r'/v'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertIsNone(result)

        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)

    def test_modifier_invalid(self):
        cfg = MockArgParse()
        pat = r'asd'
        cfg.pattern = r'/' + pat + r'/z'

        result = pattern._prepare_pattern__magic(cfg)

        self.assertRegexpMatches(result, r'^Unknown modifier in pattern:')

        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.ignorecase)
        self.assertFalse(cfg.invert_match)
        self.assertFalse(cfg.path_search)
        self.assertEqual(cfg.pattern, pat)
        self.assertFalse(cfg.regex_dotall)
        self.assertFalse(cfg.regex_multiline)
        self.assertFalse(cfg.regexp)


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

            pat = 'a'
            cfg.pattern = delim_open + pat + delim_close

            result = pattern._prepare_pattern__magic(cfg)

            if delim_close in delim_closed and delim_closed[delim_close] == delim_open:
                self.assertIsNone(result)
            else:
                self.assertRegexpMatches(result, r'^Inappropriate delimiters:', str(result))

    def test_matching_delims(self):
        delims = { '}': '{', '>': '<', ']': '[', ')': '(' }
        for delim_close, delim_open in delims.items():
            cfg = MockArgParse()

            pat = 'a'
            cfg.pattern = delim_open + pat + delim_close

            result = pattern._prepare_pattern__magic(cfg)

            self.assertIsNone(result)

    def test_same_delims(self):
        delims = '/!@#%|?+'
        for delim in delims:
            cfg = MockArgParse()

            pat = 'a'
            cfg.pattern = delim + pat + delim

            result = pattern._prepare_pattern__magic(cfg)

            self.assertIsNone(result)

    def test_same_delims_unpaired(self):
        delims = { '!': '<', '>': '[', ']': '(', ')': '{' }
        for delim_close, delim_open in delims.items():
            cfg = MockArgParse()

            pat = 'a'
            cfg.pattern = delim_open + pat + delim_close

            result = pattern._prepare_pattern__magic(cfg)

            self.assertRegexpMatches(result, r'^Inappropriate delimiters:')


if __name__ == '__main__':
    unittest.main()
