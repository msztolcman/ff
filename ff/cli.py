# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import argparse
import itertools
import os
import shlex
import sys
import textwrap
import unicodedata

import ff
from ff.pattern import prepare_pattern
from ff.plugin import FFPlugins, FFPlugin
from ff.utils import disp, u


# pylint: disable-msg=too-many-branches, too-many-statements
def parse_input_args(args):
    """ Parse input 'arguments' and return parsed.
    """

    args_description = 'Easily search and process files.'
    args_epilog = textwrap.dedent('''
        Pattern, provided as positional argument (not with --pattern) can be provided
        in special form (called: magic pattern). It allows to more "nerdish"
        (or "perlish" :) ) way to control `ff` behavior.

        The general pattern for magic pattern is:

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
                's' (--regex-dotall), 'v' (not used currently), 'r' (--invert-match)
                'q' (--path-search)

        There is also ability to extend capabilities of `ff` by plugins. Plugins are
        run with switch --test and then plugin name with optional plugin argument:

            --test plugin_name:plugin_arg

        There can be used more then one plugin at once.

        Authors:
            Marcin Sztolcman <marcin@urzenia.net> // http://urzenia.net

        HomePage:
            http://mysz.github.io/ff/
    ''').strip()

    # pylint: disable-msg=invalid-name
    p = argparse.ArgumentParser(description=args_description, epilog=args_epilog,
                                formatter_class=argparse.RawDescriptionHelpFormatter)

    p.add_argument('--print0', '-0', action='store_true', default=False,
                   help='split results by binary zero instead of new line (useful to work with xargs)')
    p.add_argument('--ignorecase', '-i', '--ignore-case', action='store_true', default=False,
                   help='ignore case when match pattern to paths')
    p.add_argument('--source', '-s', action='append', type=str, default=[],
                   help='optional, see: source above')
    p.add_argument('--pattern', '-p', type=str,
                   help='optional, see: pattern above')
    p.add_argument('--regexp', '-g', action='store_true', default=False,
                   help='treat pattern as regular expression (uses Python regexp engine)')
    p.add_argument('--fuzzy', '-f', action='store_true', default=False,
                   help='pattern defines only set and order of characters used in filename')
    p.add_argument('--depth', '-D', type=int, default=-1, help='how deep we should search (default: -1, means infinite)')
    p.add_argument('--path-search', '-q', action='store_true', default=False,
                   help='search in full path, instead of bare name of item')
    p.add_argument('--regex-multiline', '-l', action='store_true', default=False,
                   help='modify meta characters: "^" and "$" behaviour when pattern is regular expression. '
                   'See: http://docs.python.org/2/library/re.html#re.MULTILINE')
    p.add_argument('--regex-dotall', '-d', action='store_true', default=False,
                   help='modify meta character: "." behaviour when pattern is regular expression. '
                   'See: http://docs.python.org/2/library/re.html#re.DOTALL')
    p.add_argument('--begin', '-B', dest='fnmatch_begin', action='store_true', default=False,
                   help='match pattern to begin of item name (ignored in regexp mode)')
    p.add_argument('--end', '-E', dest='fnmatch_end', action='store_true', default=False,
                   help='match pattern to end of item name (ignored in regexp mode)')
    p.add_argument('--invert-match', '-v', '-r', action='store_true', default=False,
                   help='find objects that do *not* match pattern')
    p.add_argument('--mode', '-m', default='all', help='allow to choose to search for "files" only, "dirs", or "all"')
    p.add_argument('--exec', '-x', metavar='COMMAND', dest='execute', type=str,
                   help='execute some command on every found item. In command, placeholders: {path}, '
                   '{dirname}, {basename} are replaced with correct value')
    p.add_argument('--prefix', action='store_true', default=False,
                   help='add prefix "d: " (directory) or "f: " (file) to every found item')
    p.add_argument('--no-display', dest='display', action='store_false', default=True,
                   help='don\'t display element (useful with --exec argument)')
    p.add_argument('--verbose-exec', action='store_true', default=False,
                   help='show command before execute it')
    p.add_argument('--interactive-exec', action='store_true', default=False,
                   help='ask before execute command on every item')
    p.add_argument('--shell-exec', action='store_true', default=False,
                   help='execute command from --exec argument in shell (with shell expansion etc)')
    p.add_argument('--vcs', action='store_true', default=False, help='do not skip VCS directories (.git, .svn etc)')
    p.add_argument('--exclude-path', '-c', metavar='EXCLUDED_PATH', dest='excluded_paths', action='append', type=str, default=[],
                   help='skip given paths from scanning')
    p.add_argument('--test', '-t', dest='tests', action='append', default=[],
                   help='additional tests, available by plugins (see annotations below or --help-test-plugins)')
    p.add_argument('--plugins-path', type=str,
                   help='additional path where to search plugins (see annotations below)')
    p.add_argument('--version', action='version', version="%s %s\n%s" % (os.path.basename(sys.argv[0]), ff.__version__, args_description))
    p.add_argument('--help-test-plugins', metavar='TEST_NAME[,TEST2_NAME]', nargs='?', action='append', default=[],
                   help='display help for installed test plugins')
    p.add_argument('anon_pattern', metavar='pattern', type=str, nargs='?',
                   help='pattern to search')
    p.add_argument('anon_sources', metavar='sources', type=str, nargs='*',
                   help='optional source (if missing, use current directory)')

    args = p.parse_args(args)
    del args_description, args_epilog

    # where to search for plugins
    if args.plugins_path:
        try:
            plugins_path = u(args.plugins_path)
        except UnicodeDecodeError as ex:
            disp('ERROR: ', args.plugins_path, ': ', ex, sep='', file=sys.stderr)
            sys.exit(1)
        else:
            plugins_path = os.path.expanduser(plugins_path)
            FFPlugins.path_add(plugins_path)

    FFPlugins.path_add(os.path.expanduser('~/.ff/plugins'))
    FFPlugins.path_add(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ff_plugins'))

    # show info about testing plugins
    if args.help_test_plugins:
        # None means: show me the list of plugins
        if None in args.help_test_plugins:
            plugins = FFPlugins.find_all('test')
            plugins.print_list()

        else:
            # plugins names can be separated with comma
            args.help_test_plugins = itertools.chain(*[ plugin.split(',') for plugin in args.help_test_plugins])

            try:
                plugins = FFPlugins.find(args.help_test_plugins, 'test')
            except ImportError as ex:
                disp('ERROR: Unknown plugin: %s' % ex.message, file=sys.stderr)
                sys.exit(1)
            plugins.print_help()

        sys.exit()

    # find all requested test plugins
    plugins = FFPlugins()
    for plugin in args.tests:
        if ':' in plugin:
            plugin_name, plugin_argument = plugin.split(':', 1)
        else:
            plugin_name, plugin_argument = plugin, None

        try:
            plugins.append(FFPlugin(plugin_name, 'test', argument=plugin_argument))
        except ImportError:
            disp('ERROR: unknown plugin: %s' % plugin_name, file=sys.stderr)
            sys.exit(1)
        except AttributeError:
            disp('ERROR: broken plugin: %s' % plugin_name, file=sys.stderr)
            sys.exit(1)
    args.tests = plugins

    # mode
    if args.mode in ('file', 'f'):
        args.mode = 'files'
    elif args.mode in ('dir', 'd'):
        args.mode = 'dirs'
    elif args.mode not in ('all', 'files', 'dirs'):
        p.error("argument -m/--mode: invalid choice: '%s' (choose from 'files', 'dirs', 'all')" % args.mode)

    # prepare pattern
    err_msg = prepare_pattern(args)
    if err_msg:
        raise p.error(err_msg)

    # prepare sources
    args.source += args.anon_sources
    if not args.source:
        args.source.append('.')

    for i, src in enumerate(args.source):
        try:
            src = u(src)
        except UnicodeDecodeError as ex:
            disp('ERROR: ', src, ': ', ex, sep='', file=sys.stderr)
            sys.exit()

        if not os.path.isdir(src):
            p.error('Source %s doesn\'t exists or is not a directory' % src)
        src = os.path.abspath(src)
        args.source[i] = unicodedata.normalize('NFKC', src)

    # prepare exec
    if args.shell_exec:
        args.execute = [u(args.execute)]
    elif args.execute:
        args.execute = [ u(part) for part in shlex.split(args.execute) ]

    # prepare excluded paths
    for i, ex_path in enumerate(args.excluded_paths):
        ex_path = u(ex_path)
        ex_path = unicodedata.normalize('NFKC', ex_path)
        args.excluded_paths[i] = os.path.abspath(ex_path).rstrip(os.sep)

    if args.print0:
        args.delim = chr(0)
    else:
        args.delim = "\n"

    return args
