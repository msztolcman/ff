#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

from pprint import pprint, pformat

from test_manager import *

import ff

class TestIsVcs(unittest.TestCase):
    def test_correct(self):
        for item in ff._IS_VCS__NAMES.keys():
            result = ff._is_vcs(item)
            self.assertTrue(result)

    def test_incorrect(self):
        for item in ('a', 'sada', 'faewwf3', 32, '', None, True, False):
            result = ff._is_vcs(item)
            self.assertFalse(result)

    def test_correct_with_strange_case(self):
        for item in ff._IS_VCS__NAMES.keys():
            result = ff._is_vcs(item.swapcase())
            self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
