#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

from mocks.config import ConfigMock
from test_manager import *

from ff import scanner


class TestIsNotVcs(unittest.TestCase):
    def setUp(self):
        cfg = ConfigMock()
        self.scanner = scanner.Scanner(cfg)

    def test_positives(self):
        for item in scanner.VCS_NAMES.keys():
            result = self.scanner._is_not_vcs(item)
            self.assertFalse(result)

    def test_negatives(self):
        for item in ('a', 'sada', 'faewwf3', 32, '', None, True, False):
            result = self.scanner._is_not_vcs(item)
            self.assertTrue(result)

    def test_positives_with_strange_case(self):
        for item in scanner.VCS_NAMES.keys():
            result = self.scanner._is_not_vcs(item.swapcase())
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
