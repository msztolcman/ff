#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

from test_manager import *

from ff.config import strip_quotes


class TestStripQuotes(unittest.TestCase):
    def test_single_quotes(self):
        value = ''' 'asd' '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' asd '''.strip())

    def test_single_quotes_doubled(self):
        value = ''' ''asd'' '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' 'asd' '''.strip())

    def test_double_quotes(self):
        value = ''' "asd" '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' asd '''.strip())

    def test_double_quotes_doubled(self):
        value = ''' ""asd"" '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' "asd" '''.strip())

    def test_mixed_quotes(self):
        value = ''' 'asd" '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' 'asd" '''.strip())

        value = ''' "asd' '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' "asd' '''.strip())

    def test_one_side_quotes(self):
        value = ''' 'asd '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' 'asd '''.strip())

        value = ''' asd' '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' asd' '''.strip())

        value = ''' "asd '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' "asd '''.strip())

        value = ''' asd" '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' asd" '''.strip())

    def test_unquoted(self):
        value = ''' asd '''.strip()
        ret = strip_quotes(value)

        self.assertEqual(ret, ''' asd '''.strip())


if __name__ == '__main__':
    unittest.main()

