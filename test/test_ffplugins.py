#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import functools
import glob
import sys

import os
import os.path


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from test_manager import *

from ff import plugin


def clear_ffplugins_paths(f):
    @functools.wraps(f)
    def _(*a, **b):
        try:
            f(*a, **b)
        finally:
            plugin.FFPlugins._paths = set()
    return _

def clear_sys_path(f):
    @functools.wraps(f)
    def _(*a, **b):
        old_sys_path = sys.path
        sys.path = []
        try:
            f(*a, **b)
        finally:
            sys.path = old_sys_path
    return _

TEST_MOD3_DESCR = 'short descr'
TEST_MOD3_HELP = 'some help'

class TestFFPlugins(unittest.TestCase):
    def setUp(self):
        sys.path.append(PLAYGROUND_PATH)

        with open(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'), 'w') as fh:
            pass

        with open(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod2_action.py'), 'w') as fh:
            fh.write("plugin_action = lambda name, arg, path: path.upper()\n")

        with open(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod3_action_descr_help.py'), 'w') as fh:
            fh.write("plugin_action = lambda name, arg, path: path.upper()\n")
            fh.write("PLUGIN_DESCR = \"" + TEST_MOD3_DESCR + "short descr\"\n")
            fh.write("PLUGIN_HELP = \"" + TEST_MOD3_HELP + "\"\n")

        with open(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod4_action_descr_help_callable.py'), 'w') as fh:
            fh.write("plugin_action = lambda name, arg, path: name.upper() + '!' + arg.lower() + '!' + path.upper()\n")
            fh.write("PLUGIN_DESCR = lambda name: \"short descr for \" + name\n")
            fh.write("PLUGIN_HELP = lambda name: \"some help for \" + name\n")

    def tearDown(self):
        sys.path.remove(PLAYGROUND_PATH)

        for file_ in ('ffplugin_test_mod1_empty.py', 'ffplugin_test_mod2_action.py',
                      'ffplugin_test_mod3_action_descr_help.py', 'ffplugin_test_mod4_action_descr_help_callable.py'):
            path = os.path.join(PLAYGROUND_PATH, file_)
            if os.path.exists(path):
                os.unlink(path)

        for file_ in glob.glob(os.path.join(PLAYGROUND_PATH, '*.pyc')):
            os.unlink(file_)

    def test_init(self):
        p = plugin.FFPlugins()
        self.assertIsInstance(p, plugin.FFPlugins)
        self.assertIsInstance(p, list)

    @clear_ffplugins_paths
    def test_paths(self):
        self.assertTrue(hasattr(plugin.FFPlugins, '_paths'))
        self.assertIsInstance(plugin.FFPlugins._paths, set, 'FFPlugins._paths should be of type: set()')
        self.assertFalse(plugin.FFPlugins._paths, 'There should be no paths at start')

        ## PLAYGROUND_PATH should not be in FFPlugins._paths yet...
        self.assertNotIn(PLAYGROUND_PATH, plugin.FFPlugins._paths)

        cur = sys.path.count(PLAYGROUND_PATH)
        plugin.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertEqual(sys.path.count(PLAYGROUND_PATH), cur + 1)

        ## and now should be
        self.assertIn(PLAYGROUND_PATH, plugin.FFPlugins._paths)

    @clear_ffplugins_paths
    @clear_sys_path
    def test_find_all_plugins_names(self):
        plugin.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        ret = plugin.FFPlugins._find_all_plugins('test')
        expected = ['mod1_empty', 'mod2_action', 'mod3_action_descr_help', 'mod4_action_descr_help_callable']
        self.assertTrue(ret == expected, 'Incorrect set of loaded modules')

    @clear_ffplugins_paths
    @clear_sys_path
    def test_find_all(self):
        plugin.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        self.assertRaises(AttributeError, lambda: plugin.FFPlugins.find_all('test'))

        ## remove invalid plugin
        os.unlink(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'))

        plugins = plugin.FFPlugins.find_all('test')

        self.assertIsInstance(plugins, plugin.FFPlugins)
        self.assertTrue(len(plugins), 3)
        for plug in plugins:
            self.assertIsInstance(plug, plugin.FFPlugin)

    @clear_ffplugins_paths
    @clear_sys_path
    def test_find(self):
        plugin.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        self.assertRaises(ImportError, lambda: plugin.FFPlugins.find(['non_existant'], 'test'))

        plugins = plugin.FFPlugins.find(['mod2_action'], 'test')

        self.assertIsInstance(plugins, plugin.FFPlugins)
        self.assertTrue(len(plugins), 1)
        for plug in plugins:
            self.assertIsInstance(plug, plugin.FFPlugin)

    @clear_ffplugins_paths
    @clear_sys_path
    def test_print_list(self):
        plugin.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        ## remove invalid plugin
        os.unlink(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'))

        p = plugin.FFPlugins.find_all('test')
        self.assertIsInstance(p, plugin.FFPlugins)

        self.assertEqual(len(p), 3)

        old_stdout = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout

        p.print_list()

        sys.stdout = old_stdout

        data = stdout.getvalue().strip().split("\n")

        self.assertEqual(len(data), 3, "Incorrect len of read data: %s (%s)" % (len(data), data))
        self.assertRegexpMatches(data[0], r'^ff plugin: mod2')
        self.assertRegexpMatches(data[1], r'^ff plugin: mod3')
        self.assertRegexpMatches(data[2], r'^ff plugin: mod4')

    @clear_ffplugins_paths
    @clear_sys_path
    def test_print_help(self):
        plugin.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        ## remove invalid plugin
        os.unlink(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'))

        p = plugin.FFPlugins.find(['mod2_action', 'mod3_action_descr_help'], 'test')
        self.assertIsInstance(p, plugin.FFPlugins)

        self.assertEqual(len(p), 2)

        old_stdout = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout

        p.print_help()

        sys.stdout = old_stdout

        data = stdout.getvalue()

        self.assertIn(TEST_MOD3_DESCR, data)
        self.assertIn(TEST_MOD3_HELP, data)

if __name__ == '__main__':
    unittest.main()
