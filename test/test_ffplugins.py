#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import functools
import glob
import os, os.path
import sys
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import types

from pprint import pprint, pformat

import unittest

from test_config import *

import ff

def clear_ffplugins_paths(f):
    @functools.wraps(f)
    def _(*a, **b):
        try:
            f(*a, **b)
        finally:
            ff.FFPlugins._paths = set()
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

class TestFFPlugin(unittest.TestCase):
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
        p = ff.FFPlugins()
        self.assertIsInstance(p, ff.FFPlugins)
        self.assertIsInstance(p, list)

    @clear_ffplugins_paths
    def test_paths(self):
        self.assertTrue(hasattr(ff.FFPlugins, '_paths'))
        self.assertIsInstance(ff.FFPlugins._paths, set, 'FFPlugins._paths should be of type: set()')
        self.assertFalse(ff.FFPlugins._paths, 'There should be no paths at start')

        ## PLAYGROUND_PATH should not be in FFPlugins._paths yet...
        self.assertNotIn(PLAYGROUND_PATH, ff.FFPlugins._paths)

        cur = sys.path.count(PLAYGROUND_PATH)
        ff.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertEqual(sys.path.count(PLAYGROUND_PATH), cur + 1)

        ## and now should be
        self.assertIn(PLAYGROUND_PATH, ff.FFPlugins._paths)

    @clear_ffplugins_paths
    @clear_sys_path
    def test_find_all_plugins_names(self):
        ff.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        ret = ff.FFPlugins._find_all_plugins('test')
        expected = ['mod1_empty', 'mod2_action', 'mod3_action_descr_help', 'mod4_action_descr_help_callable']
        self.assertTrue(ret == expected, 'Incorrect set of loaded modules')

    @clear_ffplugins_paths
    @clear_sys_path
    def test_find_all(self):
        ff.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        self.assertRaises(AttributeError, lambda: ff.FFPlugins.find_all('test'))

        ## remove invalid plugin
        os.unlink(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'))

        plugins = ff.FFPlugins.find_all('test')

        self.assertIsInstance(plugins, ff.FFPlugins)
        self.assertTrue(len(plugins), 3)
        for plugin in plugins:
            self.assertIsInstance(plugin, ff.FFPlugin)

    @clear_ffplugins_paths
    @clear_sys_path
    def test_find(self):
        ff.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        self.assertRaises(ImportError, lambda: ff.FFPlugins.find(['non_existant'], 'test'))

        plugins = ff.FFPlugins.find(['mod2_action'], 'test')

        self.assertIsInstance(plugins, ff.FFPlugins)
        self.assertTrue(len(plugins), 1)
        for plugin in plugins:
            self.assertIsInstance(plugin, ff.FFPlugin)

    @clear_ffplugins_paths
    @clear_sys_path
    def test_print_list(self):
        ff.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        ## remove invalid plugin
        os.unlink(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'))

        p = ff.FFPlugins.find_all('test')
        self.assertIsInstance(p, ff.FFPlugins)

        self.assertEqual(len(p), 3)

        old_stdout = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout

        p.print_list()

        sys.stdout = old_stdout

        stdout.seek(0)
        data = stdout.readlines()

        self.assertTrue(len(data) == 3)
        self.assertTrue(data[0].startswith('ff plugin: mod2'))
        self.assertTrue(data[1].startswith('ff plugin: mod3'))
        self.assertTrue(data[2].startswith('ff plugin: mod4'))

    @clear_ffplugins_paths
    @clear_sys_path
    def test_print_help(self):
        ff.FFPlugins.path_add(PLAYGROUND_PATH)
        self.assertIn(PLAYGROUND_PATH, sys.path)

        ## remove invalid plugin
        os.unlink(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'))

        p = ff.FFPlugins.find(['mod2_action', 'mod3_action_descr_help'], 'test')
        self.assertIsInstance(p, ff.FFPlugins)

        self.assertEqual(len(p), 2)

        old_stdout = sys.stdout
        stdout = StringIO()
        sys.stdout = stdout

        p.print_help()

        sys.stdout = old_stdout

        stdout.seek(0)
        data = stdout.read()

        self.assertIn(TEST_MOD3_DESCR, data)
        self.assertIn(TEST_MOD3_HELP, data)

if __name__ == '__main__':
    unittest.main()
