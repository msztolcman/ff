# -*- coding: utf-8 -*-

"""
    Scan sources and validate them.
"""

from __future__ import print_function, unicode_literals, division

import os, os.path

from ff.utils import normalize


MODE_ALL = 'all'
MODE_FILES = 'files'
MODE_DIRS = 'dirs'
VCS_NAMES = {
    '.git': 1, '.svn': 1, 'CVS': 1, '.hg': 1,
    '_MTN': 1, 'RCS': 1, 'SCCS': 1, '_darcs': 1,
    '_sgbak': 1
}

class Scanner(object):
    def __init__(self, cfg):
        self.sources = cfg.source

        self.depth = cfg.depth
        self.excluded_paths = cfg.excluded_paths
        self.include_vcs = cfg.vcs
        self.mode = cfg.mode
        self.pattern = cfg.pattern
        self.path_search = cfg.path_search
        self.invert_match = cfg.invert_match
        self.tests = cfg.tests

    def _is_path_excluded(self, path):
        """
        Check that path is excluded from processing

        Excluded paths shouldn't end with `os.sep`.
        """

        path = path.rstrip(os.sep)
        return any(
            path == ex_path or ex_path + os.sep in path
                for ex_path in self.excluded_paths
        )

    def _is_not_vcs(self, item):
        """ Check if `item` is VCS
        """
        return item not in VCS_NAMES

    def _walk(self, path):
        src_len = len(path)
        for root, dirs, files in os.walk(path):
            ## limit search depth to cfg.depth
            if -1 < self.depth < len(root[src_len:].split('/')):
                dirs[:] = []
                continue

            root = normalize(root)
            if self._is_path_excluded(root):
                continue

            ## remove vcs directories from traversing
            if not self.include_vcs:
                dirs[:] = filter(self._is_not_vcs, dirs)

            if self.mode in (MODE_DIRS, MODE_ALL) and root != path:
                yield root

            if self.mode in (MODE_FILES, MODE_ALL):
                for file_ in files:
                    file_ = normalize(file_)
                    path = os.path.join(root, file_)
                    if self._is_path_excluded(path):
                        continue

                    yield path

    def _scan_source(self, path):
        for item in self._walk(path):
            if self.path_search:
                is_name_match = self.pattern.pattern.search(item)
            else:
                is_name_match = self.pattern.pattern.search(os.path.basename(item))

            to_show = False
            if not self.invert_match and is_name_match:
                to_show = True
            elif self.invert_match and not is_name_match:
                to_show = True

            if not to_show:
                continue

            if self.tests:
                for test in self.tests:
                    # TODO: test should have passed to_show argument to decide to fail or not (usualy: yes)
                    to_show = test.run(item)

            if not to_show:
                continue

            yield item

    def __iter__(self):
        for source in self.sources:
            for path in self._scan_source(source):
                yield path
