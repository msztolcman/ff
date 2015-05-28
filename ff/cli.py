# -*- coding: utf-8 -*-

"""
    Parse and prepare CLI arguments
"""

from __future__ import print_function, unicode_literals, division

import argparse
import copy
import itertools
import os, os.path
import shlex
import subprocess
import sys
import tmcolors
import textwrap

import ff
from ff import pattern
from ff.plugin import FFPlugins, FFPlugin, InvalidPluginsPath, FFPluginError
from ff import scanner
from ff.utils import disp, err, u, ask, normalize


# pylint: disable=too-many-statements,too-many-branches
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

        There is also ability to extend capabilities of `ff` by plugins. Plugins are
        run with switch --test and then plugin name with optional plugin argument:

            --test plugin_name:plugin_arg

        There can be used more then one plugin at once.

        Authors:
            Marcin Sztolcman <marcin@urzenia.net> // http://urzenia.net

        HomePage:
            http://mysz.github.io/ff/
    ''').strip()

    # pylint: disable=invalid-name
    p = argparse.ArgumentParser(description=args_description, epilog=args_epilog,
                                formatter_class=argparse.RawDescriptionHelpFormatter)

    p.add_argument('--print0', '-0', action='store_true', default=False,
       help='split results by binary zero instead of new line (useful to work with xargs)')
    p.add_argument('--ignorecase', '-i', '--ignore-case', action='store_true', default=False,
       help='ignore case when match pattern to paths')
    p.add_argument('--source', '-s', dest='sources', metavar='source', action='append', type=str, default=[],
       help='optional, see: source above')
    p.add_argument('--pattern', '-p', type=str,
       help='optional, see: pattern above')
    p.add_argument('--regexp', '-g', action='store_true', default=False,
       help='treat pattern as regular expression (uses Python regexp engine)')
    p.add_argument('--fuzzy', '-f', action='store_true', default=False,
       help='pattern defines only set and order of characters used in filename')
    p.add_argument('--depth', '-D', type=int, default=-1,
        help='how deep we should search (default: -1, means infinite)')
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
    p.add_argument('--mode', '-m', default='all',
        help='allow to choose to search for "files" only, "dirs", or "all"')
    p.add_argument('--exec', '-x', metavar='COMMAND', dest='execute', type=str,
       help='execute some command on every found item. In command, placeholders: {path}, '
           '{dirname}, {basename} are replaced with correct value')
    p.add_argument('--prefix', action='store_true', default=False,
       help='add prefix "d: " (directory) or "f: " (file) to every found item')
    p.add_argument('--no-display', dest='display', action='store_false', default=True,
       help='don\'t display element (useful with --exec argument)')
    p.add_argument('--no-colorize', action="store_false", dest='colorize',
        help='Colorize output')
    p.add_argument('--verbose-exec', action='store_true', default=False,
       help='show command before execute it')
    p.add_argument('--interactive-exec', action='store_true', default=False,
       help='ask before execute command on every item')
    p.add_argument('--shell-exec', action='store_true', default=False,
       help='execute command from --exec argument in shell (with shell expansion etc)')
    p.add_argument('--vcs', dest='include_vcs', action='store_true', default=False,
        help='do not skip VCS directories (.git, .svn etc)')
    p.add_argument('--exclude-path', '-c', metavar='EXCLUDED_PATH', dest='excluded_paths', action='append', type=str, default=[],
       help='skip given paths from scanning')
    p.add_argument('--test', '-t', dest='tests', action='append', default=[],
       help='additional tests, available by plugins (see annotations below or --help-test-plugins)')
    p.add_argument('--plugins-path', type=str, action='append',
       help='additional path where to search plugins (see annotations below)')
    p.add_argument('--version', action='version', version="%s %s\n%s" % (os.path.basename(sys.argv[0]), ff.__version__, args_description))
    p.add_argument('--help-test-plugins', metavar='TEST_NAME[,TEST2_NAME]', nargs=argparse.OPTIONAL, action='append', default=[],
       help='display help for installed test plugins')
    p.add_argument('anon_pattern', metavar='pattern', type=str, nargs=argparse.OPTIONAL,
       help='pattern to search')
    p.add_argument('anon_sources', metavar='source', type=str, nargs=argparse.ZERO_OR_MORE,
       help='optional source (if missing, use current directory)')

    args = p.parse_args(args)
    del args_description, args_epilog

    # for displaying help we don't need to parse or validate nothing more
    if args.help_test_plugins:
        return args

    # mode
    modes = {
        'files': scanner.MODE_FILES, 'file': scanner.MODE_FILES, 'f': scanner.MODE_FILES,
        'dirs': scanner.MODE_DIRS, 'dir': scanner.MODE_DIRS, 'd': scanner.MODE_DIRS,
        'all': scanner.MODE_ALL, 'a': scanner.MODE_ALL
    }
    try:
        args.mode = modes[args.mode.lower()]
    except KeyError:
        p.error("argument -m/--mode: invalid choice: '%s' (choose from 'files', 'dirs', 'all')" % args.mode)

    # prepare pattern
    # TODO: should be converted to UTF8 in this place?
    if args.pattern is not None:
        if args.anon_pattern:
            args.anon_sources.insert(0, args.anon_pattern)
        args.magic_pattern = False
    else:
        args.pattern = args.anon_pattern
        args.magic_pattern = True

    if not args.pattern:
        p.error('argument -p/--pattern is required')

    try:
        pat = pattern.Pattern()

        opts_list = ('fnmatch_begin', 'fnmatch_end', 'ignorecase', 'regex_dotall', 'regex_multiline',
        'invert_match', 'regexp', 'fuzzy', 'magic_pattern', 'pattern')

        for opt in opts_list:
            # TODO: should be converted to UTF8 in this place?
            setattr(pat, opt, getattr(args, opt))

        pat.compile()
        args.pattern = pat

        del pat, opts_list
    except pattern.PatternError as ex:
        raise p.error(str(ex))

    # prepare sources
    args.sources += args.anon_sources
    if not args.sources:
        args.sources.append('.')

    for i, src in enumerate(args.sources):
        try:
            src = u(src)
        except UnicodeDecodeError as ex:
            err('%s: %s' % (src, ex), sep='', exit_code=1)

        if not os.path.isdir(src):
            p.error('Source %s doesn\'t exists or is not a directory' % src)

        src = os.path.abspath(src)
        args.sources[i] = normalize(src)

    # prepare exec
    args.execute = u(args.execute)

    # prepare excluded paths
    for i, ex_path in enumerate(args.excluded_paths):
        ex_path = u(ex_path)
        ex_path = normalize(ex_path)
        args.excluded_paths[i] = os.path.abspath(ex_path).rstrip(os.sep)

    if args.print0:
        args.delim = chr(0)
    else:
        args.delim = os.linesep

    return args


def detect_plugins_paths(args):
    """
    Detect and collect plugins paths
    :param args:
    :return:
    """
    plugins_path = os.path.dirname(os.path.abspath(__file__))
    plugins_path = os.path.join(plugins_path, '..', 'ff_plugins')
    FFPlugins.path_add(os.path.abspath(plugins_path))
    FFPlugins.path_add(os.path.expanduser('~/.ff/plugins'))

    if args.plugins_path:
        for plugins_path in args.plugins_path:
            try:
                plugins_path = u(plugins_path)
            except UnicodeDecodeError as ex:
                raise InvalidPluginsPath(str(ex), plugins_path)
            else:
                plugins_path = os.path.expanduser(plugins_path)
                FFPlugins.path_add(plugins_path)


def initialize_plugins(args):
    """
    Find and prepare plugins for use
    :param args:
    :return:
    """
    plugins = FFPlugins()
    for plugin in args.tests:
        if ':' in plugin:
            plugin_name, plugin_argument = plugin.split(':', 1)
        else:
            plugin_name, plugin_argument = plugin, None

        try:
            plugin = FFPlugin(plugin_name, 'test', argument=plugin_argument)
            plugins.append(plugin)
        except ImportError:
            raise FFPluginError('unknown plugin: %s' % plugin_name)
        except AttributeError:
            raise FFPluginError('broken plugin: %s' % plugin_name)

    return plugins


def prepare_execute(exe, path, dirname, basename):
    """ Replace keywords and env variables in 'exe' with values.
        Recognized keywords:
        {path} - full file path
        {dirname} - parent directory for file
        {basename} - filename without path
        :param exe:list|tuple
        :param path:str
        :param dirname:str
        :param basename:str
        :return:list
    """

    exe = copy.copy(exe)
    for i, elem in enumerate(exe):
        elem = elem.replace('{path}', path)
        elem = elem.replace('{dirname}', dirname)
        elem = elem.replace('{basename}', basename)
        exe[i] = elem

    return exe


def colorize(cfg, path):
    """
    Colorize matched part of path
    :param cfg:argparse.Namespace
    :param path:str
    :return:str
    """
    if not sys.stdout.isatty():
        return path

    repl = tmcolors.colorize(r'\1', fg='green')
    if cfg.path_search:
        path = cfg.pattern.pattern.sub(repl, path)
    else:
        dirname, basename = os.path.split(path)
        basename = cfg.pattern.pattern.sub(repl, basename)
        path = os.path.join(dirname, basename)

    return path


def process_item(cfg, path):
    """
    Print item and/or execute command if given.
    :param cfg:argparse.Namespace
    :param path:str
    """

    if cfg.colorize:
        path = colorize(cfg, path)

    if cfg.display:
        if not cfg.prefix:
            prefix = ''
        elif os.path.isdir(path):
            prefix = 'd: '
        else:
            prefix = 'f: '

        disp(prefix, path, sep='', end=cfg.delim)

    if cfg.execute:
        if cfg.shell_exec:
            execute = [cfg.execute]
        else:
            execute = shlex.split(cfg.execute)

        execute = prepare_execute(execute, path, os.path.dirname(path), os.path.basename(path))
        if cfg.verbose_exec:
            disp(*execute)
        if not cfg.interactive_exec or ask('Execute command on %s?' % path, 'yn', 'n') == 'y':
            subprocess.call(execute, shell=cfg.shell_exec)


def main():
    """ Run program
    """
    try:
        args = parse_input_args(sys.argv[1:])
    except argparse.ArgumentError as ex:
        err(str(ex), exit_code=1)

    # where to search for plugins
    try:
        detect_plugins_paths(args)
    except InvalidPluginsPath as ex:
        err('%s: %s' % (ex.path, str(ex)), sep='', exit_code=1)

    try:
        # None means: show me the list of plugins
        if None in args.help_test_plugins:
            plugins = FFPlugins.find_all('test')
            plugins.print_list()

            sys.exit()
        # show info about testing plugins
        elif args.help_test_plugins:
            # plugins names can be separated with comma
            plugins = [plugin.split(',') for plugin in args.help_test_plugins]
            plugins = itertools.chain(*plugins)

            plugins = FFPlugins.find(plugins, 'test')
            plugins.print_help()

            sys.exit()
    except ImportError as ex:
        err('Unknown plugin: %s' % ex, exit_code=1)

    # find all requested test plugins
    try:
        args.tests = initialize_plugins(args)
    except FFPluginError as ex:
        err(str(ex), exit_code=1)

    try:
        for item in scanner.Scanner(args):
            process_item(args, item)
    except FFPluginError as ex:
        # TODO: failed plugin name
        err('Plugin error: %s' % ex, exit_code=1)
    except KeyboardInterrupt:
        disp('Interrupted by CTRL-C, aborting', file=sys.stderr)
