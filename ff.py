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

__version__ = '0.1'

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
        self.interactive_exec = False
        self.invert_match = False
        self.display = True
        self.delim = "\n";
        self.help = False
        self.vcs = False
        self.shell_exec = False

        for key in kw:
            setattr(self, key, kw[key])

def ask(question, replies, default):
    replies = [ reply.lower() for reply in replies ]
    choices = ','.join(replies)
    choices = choices.replace(default.lower(), default.upper())
    question += ' (' + choices + ') '
    while True:
        reply = raw_input(question).lower()
        if reply in replies:
            return reply

def parse_input_args(args):
    cfg = Config()

    opts_short = 'gp:m:s:ildBEhx:v0'
    opts_long  = ('regexp', 'pattern=', 'mode=', 'source=', 'ignorecase', 'regex-multiline', 'regex-dotall',
                'begin', 'end', 'prefix', 'help', 'exec=', 'invert-match', 'print0', 'no-display', 'verbose-exec', 'interactive-exec',
                 'vcs', 'shell-exec')
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
            cfg.execute = a
        elif  o == '--verbose-exec':
            cfg.verbose_exec = True
        elif o in ('-v', '--invert-match'):
            cfg.invert_match = True
        elif o == '--interactive-exec':
            cfg.interactive_exec = True
        elif o == '--no-display':
            cfg.display = False
        elif o in ('-0', '--print0'):
            cfg.delim = chr(0)
        elif o == '--vcs':
            cfg.vcs = True
        elif o == '--shell-exec':
            cfg.shell_exec = True
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

    if cfg.shell_exec:
        cfg.execute = [cfg.execute]
    elif cfg.execute:
        cfg.execute = shlex.split(cfg.execute)

    return cfg

def _prepare_execute__vars(m):
    if len(m.group(1)) % 2 == 0:
        return os.environ.get(m.group(2), '')
    else:
        return m.group(0)

def prepare_execute(exe, path, dirname, basename, expand_vars=True):
    exe = copy.copy(exe)
    rxp_var = re.compile(r'(\\*)\$([_a-zA-Z0-9]+)')
    for i, elem in enumerate(exe):
        exe[i] = exe[i].replace('{path}', path)
        exe[i] = exe[i].replace('{dirname}', dirname)
        exe[i] = exe[i].replace('{basename}', basename)
        if expand_vars:
            exe[i] = rxp_var.sub(_prepare_execute__vars, exe[i])

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
            pattern = r'\A' + pattern

        if not cfg.fnmatch_end:
            pattern = re.sub(r'\\Z (?: \( [^)]+ \) )? $', '', pattern, flags=re.VERBOSE)


    pattern = re.compile(pattern, flags)
    return pattern

def process_item(cfg, path):
    m = cfg.pattern.search(os.path.basename(path))
    if (not cfg.invert_match and m) or (cfg.invert_match and not m):
        if cfg.display:
            prefix = ''
            if cfg.prefix:
                prefix = 'd: ' if os.path.isdir(path) else 'f: '
            print(prefix, path, sep='', end=cfg.delim)
        if cfg.execute:
            exe = prepare_execute(cfg.execute, path, os.path.dirname(path), os.path.basename(path), not cfg.shell_exec)
            if cfg.verbose_exec:
                print(' '.join(exe))
            if not cfg.interactive_exec or ask('Execute command on %s?' % path, 'yn', 'n') == 'y':
                subprocess.call(exe, shell=cfg.shell_exec)

def main():
    try:
        config = parse_input_args(sys.argv[1:])
    except getopt.error as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    if config.help:
        print('''%s
    [-0|--print0] split results by binary zero instead of new line (useful to work with xargs)
    [-i|--ignorecase]
    *[-s|--source source] - optional, see: pattern below
    *[-p|--pattern]
    [-g|--regexp] - treat pattern as regular expression (uses Python regexp engine)
    [-l|--regex-multiline]
    [-d|--regex-dotall]
    [-B|--begin] - match pattern to begin of item name (ignored in regexp mode)
    [-E|--end] - match pattern to end of item name (ignored in regexp mode)
    [-v|--invert-match]
    [-m|--mode] - one of: 'all' (default), 'dirs', 'files'
    [-x|--exec] - execute some command on every found item. In command, placeholders: {path}, {dirname}, {basename} are replaced with correct value
    [--prefix=PREFIX] - add prefix 'd: ' (directory) or 'f: ' (file) to every found item
    [--no-display] - don't display element (useful with --exec argument)
    [--verbose-exec] - show command before execute it
    [--interactive-exec] - ask before execute command on every item
    [--shell-exec] - execute command from --exec argument in shell (with shell expansion etc)
    [--vcs] - do not skip VCS directories (.git, .svn etc)
    [-h|--help]
    pattern - pattern to search
    [source1 .. sourceN] - optional source (if missing, use current directory)''' % os.path.basename(sys.argv[0]))
        sys.exit()

    config.pattern = prepare_pattern(config)

    rxp_vcs = re.compile('(?:^|/)(?:\.git|\.svn|\.CVS|\.hg|_MTN|CVS|RCS|SCCS|_darcs|_sgbak)(?:$|/)')

    for source in config.source:
        for root, dirs, files in os.walk(source):
            if config.mode in ('dirs', 'all'):
                if config.vcs or not rxp_vcs.search(root):
                    process_item(config, root)

            if config.mode in ('files', 'all'):
                for file_ in files:
                    path = os.path.join(root, file_)
                    if config.vcs or not rxp_vcs.search(path):
                        process_item(config, path)

if __name__ == '__main__':
    main()
