# -*- coding: utf-8 -*-

"""
    Process input
"""

from __future__ import print_function, unicode_literals, division

import copy
import os, os.path
import subprocess
import sys
import unicodedata

from ff.plugin import FFPluginError
from ff.utils import ask, disp


_IS_VCS__NAMES = {'.git': 1, '.svn': 1, 'CVS': 1, '.hg': 1, '_MTN': 1, 'RCS': 1, 'SCCS': 1, '_darcs': 1, '_sgbak': 1}


def prepare_execute(exe, path, dirname, basename):
    """ Replace keywords and env variables in 'exe' with values.
        Recognized keywords:
        {path} - full file path
        {dirname} - parent directory for file
        {basename} - filename without path
    """

    exe = copy.copy(exe)
    for i, elem in enumerate(exe):
        elem = elem.replace('{path}', path)
        elem = elem.replace('{dirname}', dirname)
        elem = elem.replace('{basename}', basename)
        exe[i] = elem

    return exe


# pylint: disable=too-many-branches
def process_item(cfg, path):
    """ Test path for matching with pattern, print it if so, and execute command if given.
    """

    if cfg.path_search:
        is_name_match = cfg.pattern.search(path)
    else:
        is_name_match = cfg.pattern.search(os.path.basename(path))

    to_show = False
    if not cfg.invert_match and is_name_match:
        to_show = True
    elif cfg.invert_match and not is_name_match:
        to_show = True

    if not to_show:
        return

    if cfg.tests:
        for test in cfg.tests:
            try:
                to_show = test.run(path)
            except FFPluginError as ex:
                disp('Plugin "%s" error: %s' % (test.name, ex), file=sys.stderr)
                sys.exit(1)
            else:
                if not to_show:
                    return

    if cfg.display:
        if not cfg.prefix:
            prefix = ''
        elif os.path.isdir(path):
            prefix = 'd: '
        else:
            prefix = 'f: '

        disp(prefix, path, sep='', end=cfg.delim)

    if cfg.execute:
        exe = prepare_execute(cfg.execute, path, os.path.dirname(path), os.path.basename(path))
        if cfg.verbose_exec:
            disp(*exe)
        if not cfg.interactive_exec or ask('Execute command on %s?' % path, 'yn', 'n') == 'y':
            subprocess.call(exe, shell=cfg.shell_exec)


def is_path_excluded(excluded_paths, path):
    """ Check that path is excluded from processing

        Excluded paths shouldn't end with `os.sep`.
    """

    path = path.rstrip(os.sep)
    path = unicodedata.normalize('NFKC', path)
    for ex_path in excluded_paths:
        if path == ex_path or ex_path + os.sep in path:
            return True
    return False


def _is_not_vcs(item):
    """ Check if `item` is VCS
    """
    return item not in _IS_VCS__NAMES


def process_source(src, cfg):
    """ Process single source: search for items and call process_item on them.
    """

    src_len = len(src)
    for root, dirs, files in os.walk(src):
        ## limit search depth to cfg.depth
        if -1 < cfg.depth < len(root[src_len:].split('/')):
            dirs[:] = []
            continue

        root = unicodedata.normalize('NFKC', root)
        if is_path_excluded(cfg.excluded_paths, root):
            continue

        ## remove vcs directories from traversing
        if not cfg.vcs:
            dirs[:] = filter(_is_not_vcs, dirs)

        if cfg.mode in ('dirs', 'all') and root != src:
            process_item(cfg, root)

        if cfg.mode in ('files', 'all'):
            for file_ in files:
                file_ = unicodedata.normalize('NFKC', file_)
                path = os.path.join(root, file_)
                if is_path_excluded(cfg.excluded_paths, path):
                    continue

                process_item(cfg, path)
