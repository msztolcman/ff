#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

import copy
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

from test_manager import *

import ff

class TestPrepareExecute(unittest.TestCase):
    def test_replace_nothing(self):
        args = dict(
            exe = ['asd qwe zxc'],
            path = '/etc/passwd',
            dirname = '/etc',
            basename = 'passwd'
        )
        exe_copy = copy.deepcopy(args['exe'])

        self.assertEqual(ff.prepare_execute(**args), args['exe'])
        self.assertEqual(args['exe'], exe_copy)

    def test_replace_path(self):
        args = dict(
            exe = ['asd qwe {path} zxc'],
            path = '/etc/passwd',
            dirname = '/etc',
            basename = 'passwd'
        )
        exe_copy = copy.deepcopy(args['exe'])

        result = ff.prepare_execute(**args)
        self.assertEqual(result, [args['exe'][0].replace('{path}', args['path'])])
        self.assertEqual(args['exe'], exe_copy)

    def test_replace_all(self):
        args = dict(
            exe = ['asd {basename} qwe {path} zxc {dirname} poi'],
            path = '/etc/passwd',
            dirname = '/etc',
            basename = 'passwd'
        )
        exe_copy = copy.deepcopy(args['exe'])

        expected = args['exe'][0]
        for key in ('path', 'dirname', 'basename'):
            expected = expected.replace('{' + key + '}', args[key])

        result = ff.prepare_execute(**args)
        self.assertEqual(result, [expected])
        self.assertEqual(args['exe'], exe_copy)

    def test_replace_few_lines(self):
        args = dict(
            exe = [
                'asd {basename} qwe {path} zxc {dirname} poi'
                'qwe {path} asd {dirname} poi {basename} zxc'
            ],
            path = '/etc/passwd',
            dirname = '/etc',
            basename = 'passwd'
        )
        exe_copy = copy.deepcopy(args['exe'])

        expected = []
        for line in args['exe']:
            expected.append(line)
            for key in ('path', 'dirname', 'basename'):
                expected[-1] = expected[-1].replace('{' + key + '}', args[key])

        result = ff.prepare_execute(**args)
        self.assertEqual(ff.prepare_execute(**args), expected)
        self.assertEqual(args['exe'], exe_copy)

    def test_omit_unknown_keyword(self):
        args = dict(
            exe = ['asd {qwe} zxc'],
            path = '/etc/passwd',
            dirname = '/etc',
            basename = 'passwd'
        )
        exe_copy = copy.deepcopy(args['exe'])

        self.assertEqual(ff.prepare_execute(**args), args['exe'])
        self.assertEqual(args['exe'], exe_copy)

if __name__ == '__main__':
    unittest.main()
