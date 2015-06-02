#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import os.path

from test_manager import *

from ff import cli
from ff.plugin import FFPlugins
from ff.utils import u, normalize, IS_PY2


class TestDetectPluginsPaths(unittest.TestCase):
    def __init__(self, *a, **b):
        super(TestDetectPluginsPaths, self).__init__(*a, **b)

        plugins_path = os.path.dirname(os.path.abspath(__file__))
        plugins_path = os.path.join(plugins_path, '..', 'ff_plugins')
        paths = {
            os.path.abspath(plugins_path),
            os.path.expanduser('~/.ff/plugins'),
        }
        self.default_paths = paths

    def setUp(self):
        FFPlugins._paths.clear()

    def test_empty(self):
        paths = []
        cli.detect_plugins_paths(paths)

        expected = self.default_paths
        self.assertEquals(FFPlugins._paths, expected)

    def test_single(self):
        paths = ['/tmp']
        cli.detect_plugins_paths(paths)

        expected = self.default_paths.copy()
        for path in paths:
            expected.add(path)
        self.assertEquals(FFPlugins._paths, expected)

    def test_multi(self):
        paths = ['/tmp', '/etc', '/qwe']
        cli.detect_plugins_paths(paths)

        expected = self.default_paths.copy()
        for path in paths:
            expected.add(path)
        self.assertEquals(FFPlugins._paths, expected)

    def test_home_dir(self):
        paths = ['~/tmp', '/etc']
        cli.detect_plugins_paths(paths)

        expected = self.default_paths.copy()
        for path in paths:
            expected.add(os.path.expanduser(path))
        self.assertEquals(FFPlugins._paths, expected)

    def test_unicode(self):
        if not IS_PY2:
            paths = ['/GÖS_från', '/förstår_pas']
        else:
            paths = ['/GÖS_från'.encode('utf-8'), '/förstår_pas'.encode('utf-8')]
        cli.detect_plugins_paths(paths)

        expected = self.default_paths.copy()
        for path in paths:
            path = u(path)
            path = normalize(path)
            expected.add(path)
        self.assertEquals(FFPlugins._paths, expected)


if __name__ == '__main__':
    unittest.main()
