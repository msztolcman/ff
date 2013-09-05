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

class Config:
    def __init__(self, **kw):
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
        self.help = False

        for key in kw:
            setattr(self, key, kw[key])

def parse_input_args(args):
    cfg = Config()

    opts_short = 'gp:m:s:ildBEhx:v'
    opts_long  = ('regexp', 'pattern=', 'mode=', 'source=', 'ignorecase', 'regex-multiline', 'regex-dotall',
                'begin', 'end', 'prefix', 'help', 'exec=', 'invert-match', 'no-display', 'verbose-exec')
    opts, args = getopt.gnu_getopt(args, opts_short, opts_long)

    for o, a in opts:
        if o in ('-g', '--regexp'):
            cfg.regexp = True
        elif o in ('-p', '--pattern'):
            cfg.pattern = a
        elif o in ('-m', '--mode'):
            if a not in ('files', 'dirs', 'all'):
                raise getopt.error('Mode must be one of: "files", "dirs", "all".')

            cfg.mode = a
        elif o in ('-s', '--source'):
            if not os.path.isdir(a):
                raise getopt.error('Source "%s" doesn\'t exists or is not a directory' % a)

            try:
                cfg.source.append(a)
            except AttributeError:
                cfg.source = [a]
        elif o in ('-i', '--ignorecase'):
            cfg.ignorecase = True
        elif o in ('-l', '--regex-multiline'):
            cfg.regex_multiline = True
        elif o in ('-d', '--regex-dotall'):
            cfg.regex_dotall = True
        elif o in ('-B', '--begin'):
            cfg.fnmatch_begin = True
        elif o in ('-E', '--end'):
            cfg.fnmatch_end = True
        elif o == '--prefix':
            cfg.prefix = True
        elif o in ('-x', '--exec'):
            cfg.execute = shlex.split(a)
        elif  o in ('--verbose-exec'):
            cfg.verbose_exec = True
        elif o in ('-v', '--invert-match'):
            cfg.invert_match = True
        elif o in ('--no-display'):
            cfg.display = False
        elif o in ('-h', '--help'):
            return Config(help=True)

    if cfg.pattern is None:
        if args:
            cfg.pattern = args.pop(0)
        else:
            raise getopt.error('Pattern is missing')

    if cfg.source is None:
        if args:
            cfg.source = args
        else:
            cfg.source = ['.']

    for i, src in enumerate(cfg.source):
        cfg.source[i] = os.path.abspath(src)

    return cfg

def prepare_execute(exe, path, dirname, basename):
    exe = copy.copy(exe)
    for i, elem in enumerate(exe):
        exe[i] = exe[i].replace('{path}', path)
        exe[i] = exe[i].replace('{dirname}', dirname)
        exe[i] = exe[i].replace('{basename}', basename)

    return exe

def prepare_pattern(cfg):
    pattern = cfg.pattern
    flags = 0

    if cfg.regexp:
        if cfg.ignorecase:
            flags = flags | re.IGNORECASE
        if cfg.regex_dotall:
            flags = flags | re.DOTALL
        if cfg.regex_multiline:
            flags = flags | re.MULTILINE
    else:
        import fnmatch

        if cfg.ignorecase:
            flags = flags | re.IGNORECASE

        pattern = fnmatch.translate(pattern)
        if cfg.fnmatch_begin:
            pattern = '^' + pattern
        if cfg.fnmatch_end:
            pattern = pattern + '$'

        pattern = re.sub(r'\\Z (?: \( [^)]+ \) )? $', '', pattern, flags=re.VERBOSE)

    pattern = re.compile(pattern, flags)
    return pattern

def process_item(config, path):
    m = config.pattern.search(os.path.basename(path))
    if (not config.invert_match and m) or (config.invert_match and not m):
        if config.display:
            prefix = ''
            if config.prefix:
                prefix = 'd: ' if os.path.isdir(path) else 'f: '
            print(prefix, path, sep='')
        if config.execute:
            exe = prepare_execute(config.execute, path, os.path.dirname(path), os.path.basename(path))
            if config.verbose_exec:
                print(' '.join(exe))
            subprocess.call(exe)

def main():
    try:
        config = parse_input_args(sys.argv[1:])
    except getopt.error as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    if config.help:
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

    config.pattern = prepare_pattern(config)

    for source in config.source:
        for root, dirs, files in os.walk(source):
            if config.mode in ('dirs', 'all'):
                process_item(config, root)

            if config.mode in ('files', 'all'):
                for file_ in files:
                    process_item(config, os.path.join(root, file_))

if __name__ == '__main__':
    main()
