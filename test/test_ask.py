#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from test_manager import *

from ff import utils

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
        utils.input = _
    else:
        utils.raw_input = _


class TestAsk(unittest.TestCase):
    def test_ask_simple(self):
        question = 'My question'

        set_input('n')
        ret = utils.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'n')

        set_input('y')
        ret = utils.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_one_wrong_answer(self):
        question = 'My question'

        set_input('w', 'y')
        ret = utils.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_uppercase_replies(self):
        question = 'My question'

        set_input('n')
        ret = utils.ask(question, 'YN')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'n')

        set_input('y')
        ret = utils.ask(question, 'YN')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_uppercase_answer(self):
        question = 'My question'

        set_input('N')
        ret = utils.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'n')

        set_input('Y')
        ret = utils.ask(question, 'yn')
        self.assertEqual(_set_input__prompt, question + ' (n,y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_default_answer_replied(self):
        question = 'My question'

        set_input('y')
        ret = utils.ask(question, 'yn', 'y')
        self.assertEqual(_set_input__prompt, question + ' (n,Y) ')
        self.assertEqual(ret, 'y')

        set_input('N')
        ret = utils.ask(question, 'YN', 'n')
        self.assertEqual(_set_input__prompt, question + ' (N,y) ')
        self.assertEqual(ret, 'n')

    def test_ask_with_default_answer_no_replied(self):
        question = 'My question'

        set_input('')
        ret = utils.ask(question, 'yn', 'y')
        self.assertEqual(_set_input__prompt, question + ' (n,Y) ')
        self.assertEqual(ret, 'y')

    def test_ask_multiplied_single_answer(self):
        question = 'My question'

        set_input('')
        ret = utils.ask(question, 'yny', 'y')
        self.assertEqual(_set_input__prompt, question + ' (n,Y) ')
        self.assertEqual(ret, 'y')

    def test_ask_with_default_value_not_in_answers(self):
        question = 'My question'

        set_input('')
        ret = utils.ask(question, 'yn', 'w')
        self.assertEqual(_set_input__prompt, question + ' (n,W,y) ')
        self.assertEqual(ret, 'w')

if __name__ == '__main__':
    unittest.main()
