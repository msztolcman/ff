#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals


class MockArgParse(object):
    def __init__(self):
        self.ignorecase = False
        self.pattern = ''
        self.regex_dotall = False
        self.regex_multiline = False
        self.fuzzy = False
        self.invert_match = False
        self.path_search = False
        self.regexp = False
        self.fnmatch_begin = False
        self.fnmatch_end = False


def get_opts(cfg):
    opts = {
        'fnmatch_begin': cfg.fnmatch_begin,
        'fnmatch_end': cfg.fnmatch_end,
        'ignorecase': cfg.ignorecase,
        'regex_dotall': cfg.regex_dotall,
        'regex_multiline': cfg.regex_multiline,
    }
    return opts


def apply_opts(cfg, opts):
    for opt, val in opts.items():
        setattr(cfg, opt, val)
