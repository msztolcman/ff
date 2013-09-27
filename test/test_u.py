#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import codecs
import os, os.path
import sys
import re
from pprint import pprint, pformat

from test_manager import *

unittest = import_unittest()

import ff

if PY2:
    type_bytes = str
    type_unicode = unicode
else:
    type_bytes = bytes
    type_unicode = str

class TestUFunction(unittest.TestCase):
    def test_ascii_bytes(self):
        in_ = b"asd"
        self.assertEqual(type(in_), type_bytes)
        out = ff.u(in_)
        self.assertEqual(type(out), type_unicode)

    def test_ascii_unicode(self):
        in_ = u"asd"
        self.assertEqual(type(in_), type_unicode)
        out = ff.u(in_)
        self.assertEqual(type(out), type_unicode)

    def test_utf8_bytes(self):
        in_ = b"asdG\xc3\x96Sasd"

        self.assertEqual(type(in_), type_bytes)
        out = ff.u(in_)
        self.assertEqual(type(out), type_unicode)

    def test_utf8_unicode(self):
        in_ = u"asd"
        self.assertEqual(type(in_), type_unicode)
        out = ff.u(in_)
        self.assertEqual(type(out), type_unicode)

if __name__ == '__main__':
    unittest.main()
