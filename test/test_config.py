#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import os
import os.path
import tempfile
import textwrap

from ff.config import Config, ConfigError
from ff import scanner
from ff import utils

from test_manager import *


_validators = {}


def register_validator(*names):
    def inner(func):
        for name in names:
            _validators[name] = func
        return func
    return inner


@register_validator('mode')
def validate_mode(val):
    return val in (scanner.MODE_ALL, scanner.MODE_DIRS, scanner.MODE_FILES)


@register_validator('ignorecase', 'smartcase', 'print0',
    'regexp', 'fuzzy', 'path_search', 'prefix', 'colorize',
    'include_vcs',)
def validate_boolean(val):
    return val in (True, False, 1, 0, 'on', 'off', 'yes', 'no', 'true', 'false', 'True', 'False')


@register_validator('depth')
def validate_depth(val):
    return isinstance(val, int)


@register_validator('prefix_files', 'prefix_dirs')
def validate_prefix_for_mode(val):
    if not utils.IS_PY2:
        return isinstance(val, str)
    else:
        return isinstance(val, (str, unicode))


@register_validator('excluded_paths', 'plugins_paths')
def validate_paths_sections(val):
    if not utils.IS_PY2:
        return isinstance(val, (list, tuple)) and all(isinstance(path, str) for path in val)
    else:
        return isinstance(val, (list, tuple)) and all(isinstance(path, (str, unicode)) for path in val)


def validate(field, val):
    return _validators[field](val)


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.properties = (
            'ignorecase', 'smartcase', 'print0', 'depth', 'mode',
            'regexp', 'fuzzy', 'path_search', 'prefix', 'prefix_dirs',
            'prefix_files', 'colorize', 'include_vcs', 'excluded_paths',
            'plugins_paths'
        )

    def test_read_non_existent_file(self):
        cfg = Config.parse_config(['/a/w/e'])

        self.assertTrue(cfg)
        self.assertIsInstance(cfg, Config)

        for property in self.properties:
            validate(property, getattr(cfg, property))

    def test_read_existent_file(self):
        cfg = Config.parse_config([os.path.join(PROJECT_ROOT, 'ff.rc')])

        self.assertTrue(cfg)
        self.assertIsInstance(cfg, Config)

        for property in self.properties:
            validate(property, getattr(cfg, property))

    def test_read_incorrect_file(self):
        tmp = tempfile.NamedTemporaryFile(prefix='ff_', delete=False)
        data = textwrap.dedent('''\
        asdassa
        ''')
        try:
            tmp.write(data.encode('utf-8'))
            tmp.close()

            with self.assertRaises(ConfigError):
                Config.parse_config([tmp.name])
        finally:
            os.unlink(tmp.name)

    def test_read_file_without_ff_section(self):
        tmp = tempfile.NamedTemporaryFile(prefix='ff_', delete=False)
        data = textwrap.dedent('''\
        [asd]
        ''')
        try:
            tmp.write(data.encode('utf-8'))
            tmp.close()

            with self.assertRaises(ConfigError):
                Config.parse_config([tmp.name])
        finally:
            os.unlink(tmp.name)

    def test_read_file_with_incorrect_data(self):
        data = '''\
        [ff]
        aa
        '''
        tmp = tempfile.NamedTemporaryFile(prefix='ff_', delete=False)
        data = textwrap.dedent(data)
        try:
            tmp.write(data.encode('utf-8'))
            tmp.close()

            with self.assertRaises(ConfigError):
                Config.parse_config([tmp.name])
        finally:
            os.unlink(tmp.name)

    def test_simple(self):
        cfg = Config.parse_config([os.path.join(PROJECT_ROOT, 'ff.rc')])

        for property in self.properties:
            validate(property, getattr(cfg, property))

        self.assertTrue(cfg.ignorecase)
        self.assertFalse(cfg.smartcase)
        self.assertFalse(cfg.print0)
        self.assertEqual(cfg.depth, 2)
        self.assertEqual(cfg.mode, 'all')
        self.assertFalse(cfg.regexp)
        self.assertFalse(cfg.fuzzy)
        self.assertFalse(cfg.path_search)
        self.assertFalse(cfg.prefix)
        self.assertEqual(cfg.prefix_dirs, 'dr: ')
        self.assertEqual(cfg.prefix_files, 'fl: ')
        self.assertTrue(cfg.colorize)
        self.assertTrue(cfg.include_vcs)
        self.assertEqual(cfg.excluded_paths, ['data', 'test', '/var/log'])
        self.assertEqual(cfg.plugins_paths, ['c'])


if __name__ == '__main__':
    unittest.main()
