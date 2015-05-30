#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import os
import unicodedata

from mocks.config import ConfigMock
from test_manager import *

from ff import scanner
from ff.utils import u, normalize


class TestIsPathExcluded(unittest.TestCase):
    def setUp(self):
        cfg = ConfigMock()
        self.scanner = scanner.Scanner(cfg)

    def _set_excluded_paths(self, paths):
        ex_paths = []
        for path in paths:
            path = u(path)
            path = normalize(path)
            path = path.rstrip(os.sep)
            ex_paths.append(path)

        self.scanner.excluded_paths = ex_paths

    def test_simple_is_excluded(self):
        excluded_paths = ['a', 's', 'd']
        self._set_excluded_paths(excluded_paths)

        test_paths = {'a': True, 's': True, 'd': True}
        for path in sorted(test_paths.keys()):
            path = normalize(path)
            self.assertEqual(self.scanner._is_path_excluded(path), test_paths[path],
                'Path "%s" should%s be excluded (excluded: %s)' % (
                    path, '' if test_paths[path] else ' not', self.scanner.excluded_paths))

    def test_simple_is_not_excluded(self):
        excluded_paths = ['a', 's', 'd']
        self._set_excluded_paths(excluded_paths)

        test_paths = {'q': False, 'w': False, 'e': False}
        for path in sorted(test_paths.keys()):
            path = normalize(path)
            self.assertEqual(self.scanner._is_path_excluded(path), test_paths[path],
                 'Path "%s" should%s be excluded (excluded: %s)' % (
                     path, '' if test_paths[path] else ' not', self.scanner.excluded_paths))

    def test_dir_in_longer_paths(self):
        excluded_paths = ['/etc']
        self._set_excluded_paths(excluded_paths)

        test_paths = {'/var/run/apache.pid': False, '/var': False, '/var/': False, '/etc/passwd': True, '/etc': True }
        for path in sorted(test_paths.keys()):
            path = normalize(path)
            self.assertEqual(self.scanner._is_path_excluded(path), test_paths[path],
                 'Path "%s" should%s be excluded (excluded: %s)' % (
                     path, '' if test_paths[path] else ' not', self.scanner.excluded_paths))

    def test_unicode_normalized_is_excluded(self):
        excluded_paths = ['/etc/pas_ążśź_GÖS_end']
        self._set_excluded_paths(excluded_paths)
        test_paths = {excluded_paths[0]: True}

        for path in sorted(test_paths.keys()):
            path = normalize(path)
            self.assertEqual(self.scanner._is_path_excluded(path), test_paths[path],
                 'Path "%s" should%s be excluded (excluded: %s)' % (
                     path, '' if test_paths[path] else ' not', self.scanner.excluded_paths))

    def test_unicode_denormalized_is_excluded(self):
        excluded_paths = ['/etc/pas_ążśź_GÖS_end']
        self._set_excluded_paths(excluded_paths)

        test_paths = {
            unicodedata.normalize(norm, path): True
                for path in excluded_paths
                for norm in ('NFKC', 'NFC', 'NFKD', 'NFD')
        }

        for path in sorted(test_paths.keys()):
            path = normalize(path)
            self.assertEqual(self.scanner._is_path_excluded(path), test_paths[path],
                 'Path "%s" should%s be excluded (excluded: %s)' % (
                     path, '' if test_paths[path] else ' not', self.scanner.excluded_paths))


if __name__ == '__main__':
    unittest.main()
