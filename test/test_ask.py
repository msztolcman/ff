#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import

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

from test_config import *

unittest = import_unittest()

import ff

_set_input__prompt = None
def set_input(*a):
    a = list(a)
    def _(prompt):
        global _set_input__prompt
        _set_input__prompt = prompt
        return a.pop(0)
    try:
        raw_input
    except NameError:
        ff.input = _
    else:
        ff.raw_input = _


class TestAsk(unittest.TestCase):
    def test_ask_simple(self):
        question = 'My question'

        set_input('n')
        ret = ff.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'n')

        set_input('y')
        ret = ff.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_one_wrong_answer(self):
        question = 'My question'

        set_input('w', 'y')
        ret = ff.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_uppercase_replies(self):
        question = 'My question'

        set_input('n')
        ret = ff.ask(question, 'YN')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'n')

        set_input('y')
        ret = ff.ask(question, 'YN')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_uppercase_answer(self):
        question = 'My question'

        set_input('N')
        ret = ff.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'n')

        set_input('Y')
        ret = ff.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_default_answer_replied(self):
        question = 'My question'

        set_input('y')
        ret = ff.ask(question, 'yn', 'y')
        self.assertEqual(_set_input__prompt, question + ' (n,Y) ')
        self.assertEqual(ret, 'y')

        set_input('N')
        ret = ff.ask(question, 'YN', 'n')
        self.assertEqual(_set_input__prompt, question + ' (N,y) ')
        self.assertEqual(ret, 'n')

    def test_ask_with_default_answer_no_replied(self):
        question = 'My question'

        set_input('')
        ret = ff.ask(question, 'yn', 'y')
        self.assertEqual(_set_input__prompt, question + ' (n,Y) ')
        self.assertEqual(ret, 'y')

    def test_ask_multiplied_single_answer(self):
        question = 'My question'

        set_input('')
        ret = ff.ask(question, 'yny', 'y')
        self.assertEqual(_set_input__prompt, question + ' (n,Y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_default_value_not_in_answers(self):
        question = 'My question'

        set_input('')
        ret = ff.ask(question, 'yn', 'w')
        self.assertEqual(_set_input__prompt, question + ' (n,W,y) ')
        self.assertEqual(ret, 'w')

if __name__ == '__main__':
    unittest.main()
