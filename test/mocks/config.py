# -*- coding: utf-8 -*-

from ff import scanner

class ConfigMock:
    def __init__(self):
        self.source = []

        self.depth = -1
        self.excluded_paths = []
        self.vcs = False
        self.mode = scanner.MODE_ALL
        self.pattern = None
        self.path_search = False
        self.invert_match = False
        self.tests = []
