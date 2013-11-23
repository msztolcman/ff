#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

from pprint import pprint, pformat

from test_manager import *

import ff


class TestIsNotVcs(unittest.TestCase):
    def test_positives(self):
        for item in ff._IS_VCS__NAMES.keys():
            result = ff._is_not_vcs(item)
            self.assertFalse(result)

    def test_negatives(self):
        for item in ('a', 'sada', 'faewwf3', 32, '', None, True, False):
            result = ff._is_not_vcs(item)
            self.assertTrue(result)

    def test_positives_with_strange_case(self):
        for item in ff._IS_VCS__NAMES.keys():
            result = ff._is_not_vcs(item.swapcase())
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
