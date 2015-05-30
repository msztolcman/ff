#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import os, os.path
import sys

__all__ = ['PROJECT_ROOT', 'TEST_ROOT', 'PLAYGROUND_PATH', 'IS_PY2', 'unittest']

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
TEST_ROOT = os.path.join(PROJECT_ROOT, 'test')
PLAYGROUND_PATH = os.path.join(TEST_ROOT, 'playground')
IS_PY2 = sys.version_info[0] < 3

if IS_PY2 and sys.version_info[1] < 7:
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
        class Fail(unittest.TestCase):
            def test_fail(self):
                self.fail('Need unittest2 module for python older then 2.7!')
else:
    import unittest
