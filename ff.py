#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import copy
import getopt
import os, os.path
import re
import shlex
import subprocess
import sys

from pprint import pprint, pformat

try:
    opts_short = 'gp:m:s:ildBEhx:v'
    opts_long  = ('regexp', 'pattern=', 'mode=', 'source=', 'ignorecase', 'regex-multiline', 'regex-dotall',
                  'begin', 'end', 'prefix', 'help', 'exec', 'invert-match', 'no-display', 'verbose-exec')
    opts, args = getopt.gnu_getopt(sys.argv[1:], opts_short, opts_long)
    del opts_short
    del opts_long
except getopt.error as e:
    print(e)
    sys.exit(1)

class Config:
    def __init__(self):
        self.regexp = False
        self.pattern = None
        self.mode = 'all'
        self.source = None
        self.ignorecase = True
        self.regex_multiline = False
        self.regex_dotall = False
        self.fnmatch_begin = False
        self.fnmatch_end = False
        self.prefix = False
        self.execute = None
        self.verbose_exec = False
        self.invert_match = False
        self.display = True
config = Config()

def ff_execute_prepare(exe, path, dirname, basename):
    exe = copy.copy(exe)
    for i, elem in enumerate(exe):
        exe[i] = exe[i].replace('{path}', path)
        exe[i] = exe[i].replace('{dirname}', dirname)
        exe[i] = exe[i].replace('{basename}', basename)

    return exe

for o, a in opts:
    if o in ('-g', '--regexp'):
        config.regexp = True
    elif o in ('-p', '--pattern'):
        config.pattern = a
    elif o in ('-m', '--mode'):
        if a not in ('files', 'dirs', 'all'):
            print('Mode must be one of: "files", "dirs", "all".')
            sys.exit(1)

        config.mode = a
    elif o in ('-s', '--source'):
        if not os.path.isdir(a):
            print('Source %s doesn\'t exists or is not a directory' % a)

        if config.source is None:
            config.source = [a]
        else:
            config.source.append(a)
    elif o in ('-i', '--ignorecase'):
        config.ignorecase = True
    elif o in ('-l', '--regex-multiline'):
        config.regex_multiline = True
    elif o in ('-d', '--regex-dotall'):
        config.regex_dotall = True
    elif o in ('-B', '--begin'):
        config.fnmatch_begin = True
    elif o in ('-E', '--end'):
        config.fnmatch_end = True
    elif o == '--prefix':
        config.prefix = True
    elif o in ('-x', '--exec'):
        config.execute = shlex.split(a)
    elif  o in ('--verbose-exec'):
        config.verbose_exec = True
    elif o in ('-v', '--invert-match'):
        config.invert_match = True
    elif o in ('--no-display'):
        config.display = False
    elif o in ('-h', '--help'):
        print('''%s pattern
    [-i|--ignorecase]
    *[-s|--source source]
    [-l|--regex-multiline]
    [-d|--regex-dotall]
    [-B|--begin]
    [-E|--end]
    [-v|--invert-match]
    [--prefix=PREFIX]
    pattern
    [source1 .. sourceN]''' % os.path.basename(sys.argv[0]))
        sys.exit()

if config.pattern is None:
    if args:
        config.pattern = args.pop(0)
    else:
        print('Pattern is missing')
        sys.exit(1)

if config.source is None:
    if args:
        config.source = args
    else:
        config.source = ['.']

if config.regexp:
    flags = 0
    if config.ignorecase:
        flags = flags | re.IGNORECASE
    if config.regex_dotall:
        flags = flags | re.DOTALL
    if config.regex_multiline:
        flags = flags | re.MULTILINE
    config.pattern = re.compile(config.pattern, flags)
else:
    import fnmatch

    flags = 0
    if config.ignorecase:
        flags = flags | re.IGNORECASE

    config.pattern = fnmatch.translate(config.pattern)
    if config.fnmatch_begin:
        config.pattern = '^' + config.pattern
    if config.fnmatch_end:
        config.pattern = config.pattern + '$'

    config.pattern = re.sub(r'\\Z (?: \( [^)]+ \) )? $', '', config.pattern, flags=re.VERBOSE)
    config.pattern = re.compile(config.pattern, flags)

for source in config.source:
    for root, dirs, files in os.walk(source):
        if config.mode in ('dirs', 'all'):
            prefix = 'd: ' if config.prefix else ''
            m = config.pattern.search(os.path.basename(root))
            if (not config.invert_match and m) or (config.invert_match and not m):
                if config.display:
                    print(prefix, root, sep='')
                if config.execute:
                    exe = ff_execute_prepare(config.execute, root, os.path.dirname(root), os.path.basename(root))
                    if config.verbose_exec:
                        print(exe)
                    subprocess.call(exe)

        if config.mode in ('files', 'all'):
            prefix = 'f: ' if config.prefix else ''
            for file_ in files:
                m = config.pattern.search(file_)
                if (not config.invert_match and m) or (config.invert_match and not m):
                    path = os.path.join(root, file_)
                    if config.display:
                        print(prefix, path, sep='')
                    if config.execute:
                        exe = ff_execute_prepare(config.execute, path, root, file_)
                        if config.verbose_exec:
                            print(exe)
                        subprocess.call(exe)
