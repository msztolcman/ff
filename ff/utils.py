# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import sys


IS_PY2 = sys.version_info[0] < 3


def ask(question, replies, default=None):
    """ Ask question and repeat it, until answer will not be one of 'replies',
        or nothing (then default value will be used).
        Question should not contain possible answers, it's built based on
        'replies'.
        'replies' is iterable with one letter possible answers.
        'default' can be empty.
    """
    replies = set(reply.lower() for reply in replies)
    if default:
        default = default.lower()
        replies.add(default)

    choices = ','.join(sorted(replies))
    if default:
        choices = choices.replace(default, default.upper())

    question += ' (' + choices + ') '
    while True:
        try:
            reply = raw_input(question).lower()
        except NameError:
            # pylint: disable-msg=bad-builtin
            reply = input(question).lower()

        if reply == '':
            if default:
                return default
        elif reply in replies:
            return reply


def u(string):
    """ Wrapper to decode string into unicode.
        Converts only when `string` is type of `str`, and in python2.
        Thanks to this there is possible single codebase between PY2 and PY3.
    """
    if IS_PY2:
        if type(string) is str:
            return string.decode('utf-8')
    else:
        if type(string) is bytes:
            return str(string)

    return string


def disp(*args, **kwargs):
    """ Print data in safe way.

        First, try to encode whole data to utf-8. If printing fails, try to encode to
        sys.stdout.encoding or sys.getdefaultencoding(). In last step, encode to 'ascii'
        with replacing unconvertable characters.
    """
    try:
        if IS_PY2:
            data = [part.encode('utf-8') for part in args]
        else:
            data = args
        print(*data, sep=kwargs.get('sep'), end=kwargs.get('end'), file=kwargs.get('file'))
    except UnicodeEncodeError:
        try:
            data = [part.encode(sys.stdout.encoding or sys.getdefaultencoding()) for part in args]
            print(*data, sep=kwargs.get('sep'), end=kwargs.get('end'), file=kwargs.get('file'))
        except UnicodeEncodeError:
            data = [part.encode('ascii', 'replace') for part in args]
            print(*data, sep=kwargs.get('sep'), end=kwargs.get('end'), file=kwargs.get('file'))
