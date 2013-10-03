#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import unicodedata

from pprint import pprint, pformat

from test_manager import *

import ff

class TestIsPathExcluded(unittest.TestCase):
    def test_simple_is_excluded(self):
        excluded_paths = ['a', 's', 'd']
        test_paths = {'a': True, 's': True, 'd': True}
        for path in sorted(test_paths.keys()):
            self.assertEqual(ff.is_path_excluded(excluded_paths, path), test_paths[path],
                             'Path "%s" should%s be excluded (excluded: %s)' % (path, '' if test_paths[path] else ' not', excluded_paths))

    def test_simple_is_not_excluded(self):
        excluded_paths = ['a', 's', 'd']
        test_paths = {'q': False, 'w': False, 'e': False}
        for path in sorted(test_paths.keys()):
            self.assertEqual(ff.is_path_excluded(excluded_paths, path), test_paths[path],
                             'Path "%s" should%s be excluded (excluded: %s)' % (path, '' if test_paths[path] else ' not', excluded_paths))

    def test_dir_in_longer_paths(self):
        excluded_paths = ['/etc']
        test_paths = {'/var/run/apache.pid': False, '/var': False, '/var/': False, '/etc/passwd': True, '/etc': True }

        for path in sorted(test_paths.keys()):
            self.assertEqual(ff.is_path_excluded(excluded_paths, path), test_paths[path],
                             'Path "%s" should%s be excluded (excluded: %s)' % (path, '' if test_paths[path] else ' not', excluded_paths))

    def test_unicode_normalized_is_excluded(self):
        excluded_paths = ['/etc/pas_ążśź_GÖS_end']
        test_paths = {excluded_paths[0]: True}

        for path in sorted(test_paths.keys()):
            self.assertEqual(ff.is_path_excluded(excluded_paths, path), test_paths[path],
                             'Path "%s" should%s be excluded (excluded: %s)' % (path, '' if test_paths[path] else ' not', excluded_paths))

    def test_unicode_denormalized_is_excluded(self):
        excluded_paths = ['/etc/pas_ążśź_GÖS_end']
        test_paths = {
            unicodedata.normalize(norm, path): True
                for path in excluded_paths
                for norm in ('NFKC', 'NFC', 'NFKD', 'NFD')}

        for path in sorted(test_paths.keys()):
            self.assertEqual(ff.is_path_excluded(excluded_paths, path), test_paths[path],
                             'Path "%s" should%s be excluded (excluded: %s)' % (path, '' if test_paths[path] else ' not', excluded_paths))

if __name__ == '__main__':
    unittest.main()
