#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import glob
import os, os.path
import sys
import re
import types

from pprint import pprint, pformat

from test_manager import *

import ff

class TestFFPlugin(unittest.TestCase):
    def setUp(self):
        sys.path.append(PLAYGROUND_PATH)

        with open(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod1_empty.py'), 'w') as fh:
            pass

        with open(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod2_action.py'), 'w') as fh:
            fh.write("plugin_action = lambda name, arg, path: path.upper()\n")

        with open(os.path.join(PLAYGROUND_PATH, 'ffplugin_test_mod3_action_descr_help.py'), 'w') as fh:
            fh.write("plugin_action = lambda name, arg, path: path.upper()\n")
            fh.write("PLUGIN_DESCR = \"short descr\"\n")
            fh.write("PLUGIN_HELP = \"some help\"\n")

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

    def test_import_success(self):
        _mod = ff.FFPlugin._import('test', 'mod4_action_descr_help_callable')
        self.assertTrue(type(_mod) is types.ModuleType)
        self.assertTrue(hasattr(_mod, 'plugin_action'))
        self.assertTrue(hasattr(_mod, 'PLUGIN_DESCR'))
        self.assertTrue(hasattr(_mod, 'PLUGIN_HELP'))
        self.assertTrue(hasattr(_mod, 'FFPluginError'))
        self.assertTrue(_mod.FFPluginError is ff.FFPluginError)

    def test_import_non_existant(self):
        self.assertRaises(ImportError, lambda: ff.FFPlugin._import('test', 'mod_non_existent'))

    def test_init_empty(self):
        self.assertRaises(TypeError, lambda: ff.FFPlugin())
        self.assertRaises(AttributeError, lambda: ff.FFPlugin('mod1_empty', 'test'))

    def test_init_action(self):
        p = ff.FFPlugin('mod2_action', 'test')
        self.assertIsInstance(p, ff.FFPlugin)
        self.assertEqual(p.name, 'mod2_action')
        self.assertEqual(p.type, 'test')
        self.assertIsInstance(p.action, types.FunctionType)
        path = 'asd'
        self.assertEqual(p.action('mod2_action', '', path), path.upper())
        self.assertEqual(p.descr, '')
        self.assertEqual(p.help, '')
        self.assertIsNone(p.argument)

    def test_init_descr_help(self):
        p = ff.FFPlugin('mod3_action_descr_help', 'test')
        self.assertIsInstance(p, ff.FFPlugin)
        self.assertEqual(p.name, 'mod3_action_descr_help')
        self.assertEqual(p.type, 'test')
        self.assertIsInstance(p.action, types.FunctionType)
        path = 'asd'
        self.assertEqual(p.action('mod3_action_descr_help', '', path), path.upper())
        self.assertEqual(p.descr, 'short descr')
        self.assertEqual(p.help, 'some help')
        self.assertIsNone(p.argument)

    def test_init_descr_help_callable(self):
        p = ff.FFPlugin('mod4_action_descr_help_callable', 'test')
        self.assertIsInstance(p, ff.FFPlugin)
        self.assertEqual(p.name, 'mod4_action_descr_help_callable')
        self.assertEqual(p.type, 'test')
        self.assertIsInstance(p.action, types.FunctionType)
        path = 'asd'
        self.assertEqual(p.action('mod4_action_descr_help_callable', '', path), 'mod4_action_descr_help_callable'.upper() + '!!' + path.upper())
        self.assertEqual(p.descr, 'short descr for mod4_action_descr_help_callable')
        self.assertEqual(p.help, 'some help for mod4_action_descr_help_callable')
        self.assertIsNone(p.argument)

    def test_run(self):
        path = 'asd'
        arg = 'ARG'

        p = ff.FFPlugin('mod4_action_descr_help_callable', 'test', argument=arg)
        self.assertIsInstance(p, ff.FFPlugin)

        result = 'mod4_action_descr_help_callable'.upper() + '!' + arg.lower() + '!' + path.upper()
        self.assertEqual(p.run(path), result)

if __name__ == '__main__':
    unittest.main()
