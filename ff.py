#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import argparse
import copy
import os, os.path
import re
import shlex
import subprocess
import sys
import textwrap

from pprint import pprint, pformat

__version__ = '0.3'

def ask(question, replies, default=None):
    """ Ask question and repeat it, until answer will not be one of 'replies',
        or nothing (then default value will be used).
        Question should not contain possible answers, it's built based on
        'replies'.
        'replies' is iterable with one letter possible answers.
        'default' can be empty.
    """
    replies = { reply.lower() for reply in replies }
    if default:
        default = default.lower()
        replies.add(default)

    choices = ','.join(replies)
    if default:
        choices = choices.replace(default, default.upper())

    question += ' (' + choices + ') '
    while True:
        reply = raw_input(question).lower()
        if reply == '':
            if default:
                return default
        elif reply in replies:
            return reply

def _parse_input_args__prepare_anon_pattern(args):
    args.pattern = args.anon_pattern

    if not args.pattern:
        return

    rxp_pattern = re.compile(r'''
        ^
        (?P<mode>           [a-z0-9]        )?
        (?P<delim_open>     [{[(</!@#%|]    )
        (?P<pattern>        .*              )
        (?P<delim_close>    [}\])>/!@#%|]   )
        (?P<modifier>       [a-z0-9]+       )?
        $
    ''', re.VERBOSE)
    match = rxp_pattern.match(args.pattern)
    if match:
        pattern_parts = match.groupdict()

        delim_closed = { '}': '{', ']': '[', ')': '(', '>': '<' }
        if pattern_parts['delim_open'] in '/!@#%|' and pattern_parts['delim_open'] != pattern_parts['delim_close']:
            return 'Invalid pattern'
        elif pattern_parts['delim_open'] in '{[(<' and \
                (pattern_parts['delim_close'] not in delim_closed or \
                 delim_closed[pattern_parts['delim_close']] != pattern_parts['delim_open']):
            return 'Invalid pattern'

        args.pattern = pattern_parts['pattern']

        for item in (pattern_parts['modifier'] or ''):
            if item == 'i': args.ignorecase = True
            elif item == 'm': args.regex_multiline = True
            elif item == 's': args.regex_dotall = True
            elif item == 'v': pass
            elif item == 'r': args.invert_match = True
            elif item == 'q': args.path_search = True
            else:
                return 'Unknown modifier in pattern: %s. Allowed modifiers: i, m, s, v, r,' % item

        for item in (pattern_parts['mode'] or ''):
            if item == 'g': args.regexp = True
            elif item == 'p': pass
            elif item == 'f': args.fuzzy = True
            else:
                return 'Unknown mode in pattern: %s. Allowed modes: p, g, f.' % item

def parse_input_args(args):
    """ Parse input 'args' and return parsed.
    """

    args_description = 'Easily search and process files by names.'
    args_epilog = textwrap.dedent('''
        Pattern, provided as positional argument (not with --pattern) can be provided
        in special form. It allows to more "nerdish" (or "perlish" :) ) way to control
        `ff` behavior.

        The general pattern for pattern ( ;) ) is:
        mode/pattern/modifier

        where:
            mode - is one of 'p' (--pattern), 'g' - (--regexp) or 'f' (--fuzzy)
            / - is delimiter:
                * one of: '/', '!', '@', '#', '%', '|', and then start and end
                    delimiter must be the same
                * one of: '{', '[', '(', '<', and the end delimiter must be the
                    closing one (ex. '}' if start is '{')
            pattern - any pattern, processed in a way specified with 'mode'
            modifier - one of: 'i' (--ignore-case), 'm' (--regex-multiline),
                's' (--regex_dotall), 'v' (not used currently), 'r' (--invert-match)
                'q' (--path-search)

        Author:
            Marcin Sztolcman <marcin@urzenia.net> // http://urzenia.net

        HomePage:
            https://github.com/mysz/ff/
    ''').strip()
    p = argparse.ArgumentParser(description=args_description, epilog=args_epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

    p.add_argument('-0', '--print0', action='store_true', default=False, help='split results by binary zero instead of new line (useful to work with xargs)')
    p.add_argument('-i', '--ignorecase', '--ignore-case', action='store_true', default=False, help='')
    p.add_argument('-s', '--source', action='append', type=str, default=[], help='optional, see: source above')
    p.add_argument('-p', '--pattern', type=str, help='optional, see: pattern above')
    p.add_argument('-g', '--regexp', action='store_true', default=False, help='treat pattern as regular expression (uses Python regexp engine)')
    p.add_argument('-f', '--fuzzy', action='store_true', default=False, help='pattern defines only set and order of characters used in filename')
    p.add_argument('-q', '--path-search', action='store_true', default=False, help='search in full path, instead of bare name of item')
    p.add_argument('-l', '--regex-multiline', action='store_true', default=False, help='')
    p.add_argument('-d', '--regex-dotall', action='store_true', default=False, help='')
    p.add_argument('-B', '--begin', dest='fnmatch_begin', action='store_true', default=False, help='match pattern to begin of item name (ignored in regexp mode)')
    p.add_argument('-E', '--end', dest='fnmatch_end', action='store_true', default=False, help='match pattern to end of item name (ignored in regexp mode)')
    p.add_argument('-v', '-r', '--invert-match', action='store_true', default=False, help='')
    p.add_argument('-m', '--mode', choices=('all', 'files', 'dirs'), default='all', help='')
    p.add_argument('-x', '--exec', metavar='COMMAND', dest='execute', type=str, help='execute some command on every found item. In command, placeholders: {path}, {dirname}, {basename} are replaced with correct value')
    p.add_argument('--prefix', action='store_true', default=False, help='add prefix "d: " (directory) or "f: " (file) to every found item')
    p.add_argument('--no-display', dest='display', action='store_false', default=True, help='don\'t display element (useful with --exec argument)')
    p.add_argument('--verbose-exec', action='store_true', default=False, help='show command before execute it')
    p.add_argument('--interactive-exec', action='store_true', default=False, help='ask before execute command on every item')
    p.add_argument('--shell-exec', action='store_true', default=False, help='execute command from --exec argument in shell (with shell expansion etc)')
    p.add_argument('--vcs', action='store_true', default=False, help='do not skip VCS directories (.git, .svn etc)')
    p.add_argument('-c', '--exclude-path', metavar='EXCLUDED_PATH', dest='excluded_paths', action='append', type=str, default=[], help='skip given paths from scanning')
    p.add_argument('anon_pattern', metavar='pattern', type=str, nargs='?', help='pattern to search')
    p.add_argument('anon_sources', metavar='sources', type=str, nargs='*', help='optional source (if missing, use current directory)')

    args = p.parse_args()

    if args.pattern is None:
        err = _parse_input_args__prepare_anon_pattern(args)
        if err:
            p.error(err)
    elif args.anon_pattern:
        args.anon_sources.insert(0, args.anon_pattern)

    if args.pattern is None:
        raise p.error('argument -p/--pattern is required')

    args.source += args.anon_sources;
    if not args.source:
        args.source.append('.')

    for i, src in enumerate(args.source):
        if not os.path.isdir(src):
            p.error('Source %s doesn\'t exists or is not a directory' % src)
        args.source[i] = os.path.abspath(src)

    if args.shell_exec:
        args.execute = [args.execute]
    elif args.execute:
        args.execute = shlex.split(args.execute)

    for i, exc in enumerate(args.excluded_paths):
        args.excluded_paths[i] = os.path.abspath(exc).rstrip('/')

    if args.print0:
        args.delim = chr(0)
    else:
        args.delim = "\n"

    return args

def _prepare_execute__vars(m):
    """ Helper method for prepare_execute, used in replacement of regular expression.
        Returns environment variable if found, and quantity of escape characters ('\')
        is even.
    """
    if len(m.group(1)) % 2 == 0:
        return os.environ.get(m.group(2), '')
    else:
        return m.group(0)

def prepare_execute(exe, path, dirname, basename, expand_vars=True):
    """ Replace keywords and env variables in 'exe' with values.
        Recognized keywords:
        {path} - full file path
        {dirname} - parent directory for file
        {basename} - filename without path
    """

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
    """ Prepare pattern from input args to use.

        If work in regex mode, there pattern is only compiled with flags. In normal mode,
        pattern is converted to regex, and then compiled. Recognize also fuzzy mode.

        Returns always compiled regexp, ready to use.
    """
    pattern = cfg.pattern
    flags = 0

    if cfg.fuzzy:
        new_pattern = ''
        if cfg.fnmatch_begin:
            new_pattern += '^'
        for char in pattern:
            new_pattern += '.*' + re.escape(char)
        if cfg.fnmatch_end:
            new_pattern += '$'

        flags = flags | re.DOTALL | re.MULTILINE
        if cfg.ignorecase:
            flags = flags | re.IGNORECASE

        pattern = new_pattern

    elif cfg.regexp:
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
    """ Test path for matching with pattern, print it if so, and execute command if given.
    """
    m = cfg.pattern.search(os.path.basename(path))
    to_show = False
    if not cfg.invert_match and m:
        to_show = True
    elif cfg.invert_match and not m:
        to_show = True

    if not to_show:
        return

    if cfg.display:
        if not cfg.prefix:
            prefix = ''
        elif os.path.isdir(path):
            prefix = 'd: '
        else:
            prefix = 'f: '
        print(prefix, path, sep='', end=cfg.delim)

    if cfg.execute:
        exe = prepare_execute(cfg.execute, path, os.path.dirname(path), os.path.basename(path), not cfg.shell_exec)
        if cfg.verbose_exec:
            print(' '.join(exe))
        if not cfg.interactive_exec or ask('Execute command on %s?' % path, 'yn', 'n') == 'y':
            subprocess.call(exe, shell=cfg.shell_exec)

def is_path_excluded(excluded_paths, path):
    path = path.rstrip('/')
    for exc in excluded_paths:
        if path == exc or exc + '/' in path:
            return True
    return False

def main():
    try:
        config = parse_input_args(sys.argv[1:])
    except argparse.ArgumentError:
        print(e, file=sys.stderr)
        sys.exit(1)

    config.pattern = prepare_pattern(config)

    rxp_vcs = re.compile('(?:^|/)(?:\.git|\.svn|\.CVS|\.hg|_MTN|CVS|RCS|SCCS|_darcs|_sgbak)(?:$|/)')

    try:
        for source in config.source:
            for root, dirs, files in os.walk(source):
                try:
                    root = root.decode('utf-8')
                except UnicodeDecodeError as e:
                    print(root, ': ', e, sep='', file=sys.stderr)
                    continue

                if is_path_excluded(config.excluded_paths, root):
                    continue

                if config.mode in ('dirs', 'all'):
                    if config.vcs or not rxp_vcs.search(root):
                        process_item(config, root)

                if config.mode in ('files', 'all'):
                    for file_ in files:
                        try:
                            file_ = file_.decode('utf-8')
                        except UnicodeDecodeError as e:
                            ## do not change to os.path.join, will break if are some strange characters in file_
                            print(root, os.sep, file_, ': ', e, sep='', file=sys.stderr)
                            continue

                        path = os.path.join(root, file_)
                        if is_path_excluded(config.excluded_paths, path):
                            continue
                        if config.vcs or not rxp_vcs.search(path):
                            process_item(config, path)
    except KeyboardInterrupt:
        print('Interrupted by CTRL-C, aborting', file=sys.stderr)

if __name__ == '__main__':
    main()
