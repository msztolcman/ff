# -*- coding: utf-8 -*-

from ff import scanner

class InputArgsMock:
    def __init__(self):
        self.sources = []

        self.depth = -1
        self.excluded_paths = []
        self.include_vcs = False
        self.mode = scanner.MODE_ALL
        self.pattern = None
        self.path_search = False
        self.invert_match = False
        self.tests = []
