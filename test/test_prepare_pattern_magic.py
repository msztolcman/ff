#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import itertools

from test_manager import *
from ff import pattern


class TestMagicPatternInitial(unittest.TestCase):
    def test_empty(self):
        pat = pattern.Pattern()
        pat.pattern = ''
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, r'')
        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertFalse(pat.regexp)
        self.assertFalse(pat.fuzzy)

    def test_empty2(self):
        pat = pattern.Pattern()
        pat.pattern = r'//'
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, r'')
        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertFalse(pat.regexp)
        self.assertFalse(pat.fuzzy)

    def test_pattern_simple_no_mode_modifiers(self):
        pat = pattern.Pattern()
        pat.pattern = r'/asd/'
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, r'asd')
        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertFalse(pat.regexp)
        self.assertFalse(pat.fuzzy)

    def test_pattern_regexp_no_mode_modifiers(self):
        pat = pattern.Pattern()
        pat.pattern = r'/^asd$/'
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, r'^asd$')
        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertFalse(pat.regexp)
        self.assertFalse(pat.fuzzy)


class TestMagicPatternMode(unittest.TestCase):
    def test_mode_p(self):
        pat = pattern.Pattern()
        pat.pattern = r'p/asd/'
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, r'asd')
        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertFalse(pat.regexp)
        self.assertFalse(pat.fuzzy)

    def test_mode_f(self):
        pat = pattern.Pattern()
        pat.pattern = r'f/asd/'
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, r'asd')
        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertFalse(pat.regexp)
        self.assertTrue(pat.fuzzy)

    def test_mode_g(self):
        pat = pattern.Pattern()
        pat.pattern = r'g/asd/'
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, r'asd')
        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertTrue(pat.regexp)
        self.assertFalse(pat.fuzzy)

    def test_mode_unknown_mode(self):
        pat = pattern.Pattern()
        pat.pattern = r'z/asd/'

        with self.assertRaisesRegexp(pattern.PatternError, r'^Unknown mode in pattern:'):
            pat._prepare_pattern__decompile_magic_pattern()

    def test_mode_invalid_mode(self):
        pat = pattern.Pattern()
        pat.pattern = r'pg/asd/'

        with self.assertRaisesRegexp(pattern.PatternError, r'^Incorrect mode:'):
            pat._prepare_pattern__decompile_magic_pattern()


class TestMagicPatternModifier(unittest.TestCase):
    modifier_to_option = {
        'i': 'ignorecase',
        'm': 'regex_multiline',
        's': 'regex_dotall',
        'r': 'invert_match',
    }
    excluded_pattern_fields = ('pattern', 'magic_pattern', 'compilation_status')

    def test_modifiers_single(self):
        for modifier, selected_option_name in self.modifier_to_option.items():
            pat = pattern.Pattern()
            pat.pattern = r'/asd/' + modifier
            pat._prepare_pattern__decompile_magic_pattern()

            self.assertEqual(pat.pattern, r'asd')

            for field in pattern.Pattern.__slots__:
                field = field[1:]
                if field in self.excluded_pattern_fields:
                    continue

                if field == selected_option_name:
                    self.assertTrue(getattr(pat, field))
                else:
                    self.assertFalse(getattr(pat, field))

    def test_modifiers_two_together_no_repeats(self):
        for modifiers in itertools.permutations(self.modifier_to_option.keys(), 2):
            pat = pattern.Pattern()
            pat.pattern = r'/asd/' + ''.join(modifiers)
            pat._prepare_pattern__decompile_magic_pattern()

            self.assertEqual(pat.pattern, 'asd')

            modifiers_name = [self.modifier_to_option[m] for m in modifiers]

            for field in pattern.Pattern.__slots__:
                field = field[1:]
                if field in self.excluded_pattern_fields:
                    continue

                if field in modifiers_name:
                    self.assertTrue(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))
                else:
                    self.assertFalse(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))

    def test_modifiers_two_together_repeats(self):
        for modifier in self.modifier_to_option.keys():
            pat = pattern.Pattern()
            pat.pattern = r'/asd/' + modifier * 2

            with self.assertRaisesRegexp(pattern.PatternError, r'^Incorrect modifiers in pattern:'):
                pat._prepare_pattern__decompile_magic_pattern()

    def test_modifiers_three_together_no_repeats(self):
        for modifiers in itertools.permutations(self.modifier_to_option.keys(), 3):
            pat = pattern.Pattern()
            pat.pattern = r'/asd/' + ''.join(modifiers)
            pat._prepare_pattern__decompile_magic_pattern()

            self.assertEqual(pat.pattern, 'asd')

            modifiers_name = [self.modifier_to_option[m] for m in modifiers]

            for field in pattern.Pattern.__slots__:
                field = field[1:]
                if field in self.excluded_pattern_fields:
                    continue

                if field in modifiers_name:
                    self.assertTrue(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))
                else:
                    self.assertFalse(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))

    def test_modifiers_four_together_no_repeats(self):
        for modifiers in itertools.permutations(self.modifier_to_option.keys(), 4):
            pat = pattern.Pattern()
            pat.pattern = r'/asd/' + ''.join(modifiers)
            pat._prepare_pattern__decompile_magic_pattern()

            self.assertEqual(pat.pattern, 'asd')

            modifiers_name = [self.modifier_to_option[m] for m in modifiers]

            for field in pattern.Pattern.__slots__:
                field = field[1:]
                if field in self.excluded_pattern_fields:
                    continue

                if field in modifiers_name:
                    self.assertTrue(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))
                else:
                    self.assertFalse(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))

    def test_modifiers_five_together_no_repeats(self):
        for modifiers in itertools.permutations(self.modifier_to_option.keys(), 5):
            pat = pattern.Pattern()
            pat.pattern = r'/asd/' + ''.join(modifiers)
            pat._prepare_pattern__decompile_magic_pattern()

            self.assertEqual(pat.pattern, 'asd')

            modifiers_name = [self.modifier_to_option[m] for m in modifiers]

            for field in pattern.Pattern.__slots__:
                field = field[1:]
                if field in self.excluded_pattern_fields:
                    continue

                if field in modifiers_name:
                    self.assertTrue(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))
                else:
                    self.assertFalse(getattr(pat, field), '%s:%s:%s' % (modifiers, field, getattr(pat, field)))

    def test_modifier_ignored(self):
        pat = pattern.Pattern()
        pat.pattern = r'/asd/v'
        pat._prepare_pattern__decompile_magic_pattern()

        self.assertEqual(pat.pattern, 'asd')

        self.assertFalse(pat.fnmatch_begin)
        self.assertFalse(pat.fnmatch_end)
        self.assertFalse(pat.ignorecase)
        self.assertFalse(pat.regex_dotall)
        self.assertFalse(pat.regex_multiline)
        self.assertFalse(pat.invert_match)
        self.assertFalse(pat.regexp)
        self.assertFalse(pat.fuzzy)

    def test_modifier_invalid(self):
        pat = pattern.Pattern()
        pat.pattern = r'/asd/z'

        with self.assertRaisesRegexp(pattern.PatternError, r'^Unknown modifier in pattern:'):
            pat._prepare_pattern__decompile_magic_pattern()


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
            pat = pattern.Pattern()
            pat.pattern = delim_open + 'a' + delim_close

            if delim_close in delim_closed and delim_closed[delim_close] == delim_open:
                pat._prepare_pattern__decompile_magic_pattern()
                self.assertEqual(pat.pattern, 'a')
            else:
                with self.assertRaisesRegexp(pattern.PatternError, r'^Inappropriate delimiters:'):
                    pat._prepare_pattern__decompile_magic_pattern()

    def test_matching_delims(self):
        delims = { '}': '{', '>': '<', ']': '[', ')': '(' }
        for delim_close, delim_open in delims.items():
            pat = pattern.Pattern()
            pat.pattern = delim_open + 'a' + delim_close

            pat._prepare_pattern__decompile_magic_pattern()

            self.assertEqual(pat.pattern, 'a')

    def test_same_delims(self):
        delims = '/!@#%|?+'
        for delim in delims:
            pat = pattern.Pattern()
            pat.pattern = delim + 'a' + delim

            pat._prepare_pattern__decompile_magic_pattern()

            self.assertEqual(pat.pattern, 'a')

    def test_same_delims_unpaired(self):
        delims = { '!': '<', '>': '[', ']': '(', ')': '{' }
        for delim_close, delim_open in delims.items():
            pat = pattern.Pattern()
            pat.pattern = delim_open + 'a' + delim_close

            with self.assertRaises(pattern.PatternError):
                pat._prepare_pattern__decompile_magic_pattern()


if __name__ == '__main__':
    unittest.main()
