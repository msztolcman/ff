#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import argparse
import unicodedata

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
import os.path
import re
import sys

from test_manager import *
from mocks.input_args import InputArgsMock

import ff
from ff.cli import parse_input_args
from ff import pattern
from ff import scanner


class TestParseInputArgs(unittest.TestCase):
    def test_no_args(self):
        cfg = InputArgsMock()

        iargs = []
        with self.assertRaisesRegexp(SystemExit, '2'):
            parse_input_args(iargs, cfg)

    def test_unknown_args(self):
        cfg = InputArgsMock()

        iargs = ['--unknown-and-non-existent-argument']
        with self.assertRaisesRegexp(SystemExit, '2'):
            parse_input_args(iargs, cfg)

    def test_anonymous_pattern_no_sources(self):
        cfg = InputArgsMock()

        iargs = ['a']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.sources, [TEST_ROOT])

    def test_explicit_pattern_no_sources(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.sources, [TEST_ROOT])

    def test_anonymous_pattern_anonymous_sources(self):
        cfg = InputArgsMock()

        iargs = ['a', 'b', 'c']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.pattern.pattern.pattern, '(a)')
        self.assertEqual(args.sources, [os.path.abspath('b'), os.path.abspath('c')])

    def test_explicit_pattern_anonymous_sources(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a', '/etc', '/tmp']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.sources, ['/etc', '/tmp'])

    def test_explicit_pattern_explicit_sources(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a', '--source', '/etc', '--source', '/tmp']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.sources, ['/etc', '/tmp'])

    def test_simple_call_explicit_sources_unicode(self):
        cfg = InputArgsMock()

        sources = (
            '/etc/eee_GÖS_från',
            '/tmp/förstår_pas',
        )

        for norm in ('NFC', 'NFKC', 'NFD', 'NFKD'):
            iargs = ['--pattern', 'a',
                '--source', unicodedata.normalize(norm, sources[0]).encode('utf-8'),
                '--source', unicodedata.normalize(norm, sources[1]).encode('utf-8'),
            ]
            args = parse_input_args(iargs, cfg)

            self.assertIsInstance(args, argparse.Namespace)
            self.assertIsInstance(args.pattern, pattern.Pattern)
            self.assertEqual(args.sources, list(sources))

    def _opt2prop(self, opt):
        tr = {'vcs': 'include_vcs', 'begin': 'fnmatch_begin', 'end': 'fnmatch_end', 'no-display': 'display',
            'no-colorize': 'colorize'}
        ret = tr.get(opt, opt)
        ret = ret.replace('-', '_')
        return ret

    def test_boolean_options(self):
        cfg = InputArgsMock()

        booleans = {
            'print0': False,
            'ignorecase': False,
            'regexp': False,
            'fuzzy': False,
            'path-search': False,
            'regex-multiline': False,
            'regex-dotall': False,
            'begin': False,
            'end': False,
            'invert-match': False,
            'prefix': False,
            'no-display': True,
            'no-colorize': True,
            'verbose-exec': False,
            'interactive-exec': False,
            'shell-exec': False,
            'vcs': False,
        }

        iargs = ['--pattern', 'a']
        args = parse_input_args(iargs, cfg)
        for name, value in booleans.items():
            prop = getattr(args, self._opt2prop(name))
            self.assertEqual(prop, value, '%s should be %s' % (name, value))

        for name, value in booleans.items():
            iargs = ['--pattern', 'a', '--' + name]
            args = parse_input_args(iargs, cfg)

            for test_name, test_value in booleans.items():
                prop = getattr(args, self._opt2prop(test_name))
                if name == test_name:
                    self.assertEqual(prop, not test_value, 'option: %s, so %s should be %s' % (name, test_name, not test_value))
                else:
                    self.assertEqual(prop, test_value, 'option %s, so %s should be %s' % (name, test_name, test_value))

    def test_mode(self):
        cfg = InputArgsMock()

        for mode in (
            scanner.MODE_ALL, scanner.MODE_DIRS, scanner.MODE_FILES,
            scanner.MODE_ALL.lower(), scanner.MODE_DIRS.lower(), scanner.MODE_FILES.lower(),
            scanner.MODE_ALL.upper(), scanner.MODE_DIRS.upper(), scanner.MODE_FILES.upper(),
        ):
            iargs = ['--pattern', 'a', '--mode', mode]
            args = parse_input_args(iargs, cfg)

            self.assertIsInstance(args, argparse.Namespace)
            self.assertIsInstance(args.pattern, pattern.Pattern)
            self.assertEqual(args.mode, mode.lower())

        with self.assertRaisesRegexp(SystemExit, '2'):
            iargs = ['--pattern', 'a', '--mode']
            parse_input_args(iargs, cfg)

    def test_excluded_paths_no_value(self):
        cfg = InputArgsMock()

        with self.assertRaisesRegexp(SystemExit, '2'):
            iargs = ['--pattern', 'a', '--exclude-path']
            parse_input_args(iargs, cfg)

    def test_excluded_paths_single(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a', '--exclude-path', 'a']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.excluded_paths, [os.path.abspath('a')])

    def test_excluded_paths_multi(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a', '--exclude-path', 'a', '--exclude-path', 'b', '--exclude-path', '/etc/pam.d']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.excluded_paths, [
            os.path.abspath('a'),
            os.path.abspath('b'),
            os.path.abspath('/etc/pam.d'),
        ])

    def test_excluded_paths_unicode(self):
        cfg = InputArgsMock()

        sources = (
            '/etc/eee_GÖS_från',  # .encode('utf-8'),
            '/tmp/förstår_pas',  # .encode('utf-8'),
        )

        for norm in ('NFC', 'NFKC', 'NFD', 'NFKD'):
            iargs = ['--pattern', 'a',
                '--exclude-path', unicodedata.normalize(norm, sources[0]).encode('utf-8'),
                '--exclude-path', unicodedata.normalize(norm, sources[1]).encode('utf-8'),
            ]
            args = parse_input_args(iargs, cfg)

            self.assertIsInstance(args, argparse.Namespace)
            self.assertIsInstance(args.pattern, pattern.Pattern)
            self.assertEqual(args.excluded_paths, list(sources))

    def test_depth_empty(self):
        cfg = InputArgsMock()

        iargs = ['a', '--depth']

        with self.assertRaisesRegexp(SystemExit, '2'):
            parse_input_args(iargs, cfg)

    def test_depth_string(self):
        cfg = InputArgsMock()

        iargs = ['a', '--depth', 'q']

        with self.assertRaisesRegexp(SystemExit, '2'):
            parse_input_args(iargs, cfg)

    def test_depth_valid_values(self):
        cfg = InputArgsMock()

        for depth in (0, 1, -1, 3, -3):
            iargs = ['--pattern', 'a', '--depth', str(depth).replace('-', r'\-')]

            args = parse_input_args(iargs, cfg)
            self.assertEquals(args.depth, depth)

    def test_prefix_dirs_files(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a', '--prefix-files', 'hakunamatata:makaka: ']
        args = parse_input_args(iargs, cfg)
        self.assertEqual(args.prefix_files, 'hakunamatata:makaka: ')
        self.assertEqual(args.prefix_dirs, 'd: ')

        iargs = ['--pattern', 'a', '--prefix-dirs', 'hakunamatata:makaka: ']
        args = parse_input_args(iargs, cfg)
        self.assertEqual(args.prefix_files, 'f: ')
        self.assertEqual(args.prefix_dirs, 'hakunamatata:makaka: ')

        iargs = ['--pattern', 'a',
            '--prefix-dirs', 'hakunamatata:makaka: ',
            '--prefix-files', 'hakunamatata:makaka: ']
        args = parse_input_args(iargs, cfg)
        self.assertEqual(args.prefix_files, 'hakunamatata:makaka: ')
        self.assertEqual(args.prefix_dirs, 'hakunamatata:makaka: ')

    def test_exec(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.execute, None)

        with self.assertRaisesRegexp(SystemExit, '2'):
            iargs = ['--pattern', 'a', '--exec']
            parse_input_args(iargs, cfg)

        iargs = ['--pattern', 'a', '--exec', 'wc -l']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.execute, 'wc -l')

    def test_tests(self):
        cfg = InputArgsMock()

        iargs = ['--pattern', 'a']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.tests, [])

        with self.assertRaisesRegexp(SystemExit, '2'):
            iargs = ['--pattern', 'a', '--test']
            parse_input_args(iargs, cfg)

        iargs = ['--pattern', 'a', '--test', 't1:val']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.tests, ['t1:val'])

        iargs = ['--pattern', 'a', '--test', 't1:val', '--test', 't2:val']
        args = parse_input_args(iargs, cfg)

        self.assertIsInstance(args, argparse.Namespace)
        self.assertIsInstance(args.pattern, pattern.Pattern)
        self.assertEqual(args.tests, ['t1:val', 't2:val'])

    def test_version(self):
        cfg = InputArgsMock()

        iargs = ['--version']

        _org_stderr = sys.stderr
        sys.stderr = StringIO()
        with self.assertRaisesRegexp(SystemExit, '0'):
            parse_input_args(iargs, cfg)
        stderr = sys.stderr.getvalue()
        sys.stderr = _org_stderr
        self.assertRegexpMatches(stderr, r'^[\w.]+ %s\n' % re.escape(ff.__version__))

    def test_help(self):
        cfg = InputArgsMock()

        iargs = ['--help']

        _org_stdout = sys.stdout
        sys.stdout = StringIO()
        with self.assertRaisesRegexp(SystemExit, '0'):
            parse_input_args(iargs, cfg)
        stdout = sys.stdout.getvalue()
        sys.stdout = _org_stdout
        self.assertRegexpMatches(stdout, r'(?ms)^usage: .+\bHomePage:\n\s+http://mysz\.github\.io/ff/$')

if __name__ == '__main__':
    unittest.main()

# TODO: modify default values by config
# TODO: help-test-plugins
