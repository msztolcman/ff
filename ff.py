#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ff - Easily search and process files.
    http://mysz.github.io/ff
    Author: Marcin Sztolcman (marcin@urzenia.net)

    Get help with: ff --help
    Information about version: ff --version
"""

from __future__ import print_function, unicode_literals

import argparse
import copy
import collections
import glob
import itertools
import os, os.path
import re
import shlex
import subprocess
import sys
import textwrap
import unicodedata

from pprint import pprint, pformat # pylint: disable-msg=unused-import

__version__ = '0.5'

class FFPluginError(Exception):
    """ Exception class for plugins.
    """
    pass


class FFPlugin(dict):
    """ Wrapper for custoom plugin.

        Loads module, read data, bind custom argument and allow to easy run plugin.
    """
    def __init__(self, name, type_, **kw):
        """ Initializer.

            Allow to set values of instance:
                * name (required)
                * type_ (required)
                * action (optional) (will be overwrited by `FFPlugin`.`load`)
                * descr (optional) (will be overwrited by `FFPlugin`.`load`)
                * help (optional) (will be overwrited by `FFPlugin`.`load`)
                * argument (optional)
        """
        super(FFPlugin, self).__init__()

        self.name = self['name'] = name
        self.type = self['type'] = type_
        self.action = self['action'] = kw.get('action', None)
        self.descr = self['descr'] = kw.get('descr', '')
        self.help = self['help'] = kw.get('help', '')
        self.argument = self['argument'] = kw.get('argument', None)

        self.load()

    @staticmethod
    def _import(type_, name):
        """ Imports plugins module.

            Plugin's name is created from three parts:
            fixed prefix: 'ffplugin'
            plugin type (just 'test' right now)
            plugin name

            joined with underscore.

            Returns imported module.
        """
        _mod = __import__('_'.join(['ffplugin', type_, name]), {}, {}, [], 0)
        ## monkey patch - plugin doesn't need to import FFPluginError
        _mod.FFPluginError = FFPluginError

        return _mod

    def load(self):
        """ Load and initialize plugin with data from module.

            Set `descr`, `help` and `action`.
        """
        _module = self._import(self.type, self.name)
        self.descr = getattr(_module, 'PLUGIN_DESCR', '')
        if isinstance(self.descr, collections.Callable):
            self.descr = self.descr(self.name)
        self.help = getattr(_module, 'PLUGIN_HELP', '')
        if isinstance(self.help, collections.Callable):
            self.help = self.help(self.name)
        self.action = _module.plugin_action

        self['descr'] = self.descr
        self['help'] = self.help
        self['action'] = self.action

    def run(self, path):
        """ Run plugins callable.

            Pass self.name, self.argument and path.
        """
        return self.action(self.name, self.argument, path)


class FFPlugins(list):
    """ List of plugins available for `ff`.

        Static fields:
            * list of paths where to search for plugins.
    """

    _paths = set()

    @staticmethod
    def _print_descr(item):
        """ Helper for FFPlugins.print_help/FFPlugins.print_list.
            Prints single plugin description
        """
        text = 'ff plugin: ' + item.name + (' - ' + textwrap.fill(item.descr) if item.descr else '')
        print(text)

    def print_help(self):
        """ Print list of plugins with their help to STDOUT
        """
        for item in self:
            self._print_descr(item)
            if item.help:
                print(item.help.rstrip() + "\n")

    def print_list(self):
        """ Print list of plugins with their short descriptions to STDOUT
        """
        for item in self:
            self._print_descr(item)

    @classmethod
    def path_add(cls, path):
        """ Append path to known plugins paths.
        """
        if path not in cls._paths:
            cls._paths.add(path)
            sys.path.append(path)

    @classmethod
    def find_all(cls, type_):
        """ Find all plugins available for `ff` and return FFPlugins
            initialized with it.

            Every item is instance of FFPlugin.

            Uses `FFPlugins.find` to load plugins.
        """
        result = {}
        prefix_len = len('ffplugin_') + len(type_) + 1
        for path in cls._paths:
            if not os.path.isdir(path):
                continue

            for file_ in glob.glob(os.path.join(path, '_'.join(['ffplugin', type_, '*.py']))):
                plugin_name = os.path.basename(file_)[prefix_len:-3]
                ## paths order describe priority of plugins too (first found are most important)
                if plugin_name in result:
                    continue
                result[plugin_name] = True

        order = list(result.keys())
        order.sort()

        return cls.find(order, type_=type_)

    @classmethod
    def find(cls, names, type_):
        """ Load given plugins list and initialize `FFPlugins` with them.

            Returns `FFPlugins` instance.
        """
        plugins = cls()
        for plugin_name in names:
            plugins.append(FFPlugin(plugin_name, type_))

        return plugins


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
        try:
            raw_input
        except NameError:
            reply = input(question).lower() # pylint: disable-msg=bad-builtin
        else:
            reply = raw_input(question).lower()

        if reply == '':
            if default:
                return default
        elif reply in replies:
            return reply

def _prepare_pattern__magic(args): # pylint: disable-msg=too-many-branches
    """ Parse pattern and try to recognize it is magic pattern.
        If so, parse magic pattern and set options for argparse
        result as in magic pattern is set.
    """

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
    if not match:
        return

    pattern_parts = match.groupdict()

    delim_closed = {
        ## match same
        '/': '/', '!': '!', '@': '@', '#': '#', '%': '%', '|': '|',
        ## match pair
        '}': '{', ']': '[', ')': '(', '>': '<'
    }
    if pattern_parts['delim_close'] not in delim_closed or \
            delim_closed[pattern_parts['delim_close']] != pattern_parts['delim_open']:
        return 'Invalid pattern'

    args.pattern = pattern_parts['pattern']

    for item in (pattern_parts['modifier'] or ''):
        # pylint: disable-msg=multiple-statements
        if item == 'i': args.ignorecase = True
        elif item == 'm': args.regex_multiline = True
        elif item == 's': args.regex_dotall = True
        elif item == 'v': pass
        elif item == 'r': args.invert_match = True
        elif item == 'q': args.path_search = True
        else:
            return 'Unknown modifier in pattern: %s. Allowed modifiers: i, m, s, v, r,' % item

    for item in (pattern_parts['mode'] or ''):
        # pylint: disable-msg=multiple-statements
        if item == 'g': args.regexp = True
        elif item == 'p': pass
        elif item == 'f': args.fuzzy = True
        else:
            return 'Unknown mode in pattern: %s. Allowed modes: p, g, f.' % item

def _prepare_pattern__compile_fuzzy(cfg):
    """ Compile pattern to compiled regular expression using fuzzy syntax.

        fuzzy syntax mean that we search for name where are all given characters
        in given order, but there can be anything between them.
    """

    pattern = ''
    if cfg.fnmatch_begin:
        pattern += '^'
    for char in cfg.pattern:
        pattern += '.*' + re.escape(char)
    if cfg.fnmatch_end:
        pattern += '$'

    flags = 0 | re.DOTALL | re.MULTILINE
    if cfg.ignorecase:
        flags = flags | re.IGNORECASE

    return re.compile(pattern, flags)

def _prepare_pattern__compile_regexp(cfg): # pylint: disable-msg=invalid-name
    """ Compile pattern to compiled regular expression using regexp syntax.

        We found that pattern is regular expression, and just pass there
        flags from arguments.
    """

    flags = 0
    if cfg.ignorecase:
        flags = flags | re.IGNORECASE
    if cfg.regex_dotall:
        flags = flags | re.DOTALL
    if cfg.regex_multiline:
        flags = flags | re.MULTILINE

    return re.compile(cfg.pattern, flags)

def _prepare_pattern__compile_fnmatch(cfg): # pylint: disable-msg=invalid-name
    """ Compile pattern to compiled regular expression using fnmatch syntax.

        See: http://docs.python.org/library/fnmatch.html
    """
    import fnmatch

    flags = 0
    if cfg.ignorecase:
        flags = flags | re.IGNORECASE

    pattern = fnmatch.translate(cfg.pattern)
    if cfg.fnmatch_begin:
        pattern = r'\A' + pattern

    ## our behaviour is in the opposite to fnmatch: by default *do not* match end of string
    if not cfg.fnmatch_end:
        pattern = re.sub(r'\\Z (?: \( [^)]+ \) )? $', '', pattern, flags=re.VERBOSE)

    return re.compile(pattern, flags)

def prepare_pattern(cfg):
    """ Prepare pattern from input args to use.

        If work in regex mode, there pattern is only compiled with flags. In normal mode,
        pattern is converted to regex, and then compiled. Recognize also fuzzy mode.

        Returns always compiled regexp, ready to use.
    """

    parse_magic_pattern = False
    if cfg.pattern is not None:
        cfg.anon_sources.insert(0, cfg.anon_pattern)
    else:
        parse_magic_pattern = True
        cfg.pattern = cfg.anon_pattern

    if cfg.pattern is None:
        return 'argument -p/--pattern is required'

    cfg.pattern = cfg.pattern.decode('utf-8')
    cfg.pattern = unicodedata.normalize('NFKC', cfg.pattern)

    if parse_magic_pattern:
        err_msg = _prepare_pattern__magic(cfg)
        if err_msg:
            return err_msg

    if cfg.fuzzy:
        cfg.pattern = _prepare_pattern__compile_fuzzy(cfg)
    elif cfg.regexp:
        cfg.pattern = _prepare_pattern__compile_regexp(cfg)
    else:
        cfg.pattern = _prepare_pattern__compile_fnmatch(cfg)

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
            https://github.com/mysz/ff/
    ''').strip()

    p = argparse.ArgumentParser(description=args_description, epilog=args_epilog,       # pylint: disable-msg=invalid-name
                                formatter_class=argparse.RawDescriptionHelpFormatter)

    p.add_argument('-0', '--print0', action='store_true', default=False,
                   help='split results by binary zero instead of new line (useful to work with xargs)')
    p.add_argument('-i', '--ignorecase', '--ignore-case', action='store_true', default=False,
                   help='')
    p.add_argument('-s', '--source', action='append', type=str, default=[],
                   help='optional, see: source above')
    p.add_argument('-p', '--pattern', type=str,
                   help='optional, see: pattern above')
    p.add_argument('-g', '--regexp', action='store_true', default=False,
                   help='treat pattern as regular expression (uses Python regexp engine)')
    p.add_argument('-f', '--fuzzy', action='store_true', default=False,
                   help='pattern defines only set and order of characters used in filename')
    p.add_argument('-q', '--path-search', action='store_true', default=False,
                   help='search in full path, instead of bare name of item')
    p.add_argument('-l', '--regex-multiline', action='store_true', default=False,
                   help='')
    p.add_argument('-d', '--regex-dotall', action='store_true', default=False,
                   help='')
    p.add_argument('-B', '--begin', dest='fnmatch_begin', action='store_true', default=False,
                   help='match pattern to begin of item name (ignored in regexp mode)')
    p.add_argument('-E', '--end', dest='fnmatch_end', action='store_true', default=False,
                   help='match pattern to end of item name (ignored in regexp mode)')
    p.add_argument('-v', '-r', '--invert-match', action='store_true', default=False,
                   help='')
    p.add_argument('-m', '--mode', choices=('all', 'files', 'dirs'), default='all',
                   help='')
    p.add_argument('-x', '--exec', metavar='COMMAND', dest='execute', type=str,
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
    p.add_argument('-c', '--exclude-path', metavar='EXCLUDED_PATH', dest='excluded_paths', action='append', type=str, default=[],
                   help='skip given paths from scanning')
    p.add_argument('-t', '--test', dest='tests', action='append', default=[],
                   help='additional tests, available by plugins (see annotations below or --help-test-plugins)')
    p.add_argument('--plugins-path', type=str,
                   help='additional path where to search plugins (see annotations below)')
    p.add_argument('--version', action='version', version="%s %s\n%s" % (os.path.basename(sys.argv[0]), __version__, args_description))
    p.add_argument('--help-test-plugins', metavar='TEST_NAME', nargs='?', action='append', default=[],
                   help='display help for installed test plugins')
    p.add_argument('anon_pattern', metavar='pattern', type=str, nargs='?',
                   help='pattern to search')
    p.add_argument('anon_sources', metavar='sources', type=str, nargs='*',
                   help='optional source (if missing, use current directory)')

    args = p.parse_args()
    del args_description, args_epilog

    ## where to search for plugins
    if args.plugins_path:
        try:
            plugins_path = args.plugins_path.decode('utf-8')
        except UnicodeDecodeError as ex:
            print('ERROR: ', plugins_path, ': ', ex, sep='', file=sys.stderr)
            sys.exit(1)
        else:
            plugins_path = os.path.expanduser(plugins_path)
            FFPlugins.path_add(plugins_path)

    FFPlugins.path_add(os.path.expanduser('~/.ff/plugins'))
    FFPlugins.path_add(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ff_plugins'))

    ## show info about test plugins
    if args.help_test_plugins:
        ## None means: show me list of plugins
        if None in args.help_test_plugins:
            help_data = FFPlugins.find_all('test')
            help_data.print_list()

        else:
            ## plugins names can be separated with comma
            args.help_test_plugins = itertools.chain(*[ data.split(',') for data in args.help_test_plugins])

            try:
                help_data = FFPlugins.find(args.help_test_plugins, 'test')
            except ImportError as ex:
                print('ERROR: Unknown plugin: %s' % ex.message, file=sys.stderr)
                sys.exit(1)
            help_data.print_help()

        sys.exit()

    ## find all requested test plugins
    plugins = FFPlugins()
    for plugin in args.tests:
        if ':' in plugin:
            plugin_name, plugin_argument = plugin.split(':', 1)
        else:
            plugin_name, plugin_argument = plugin, None

        try:
            plugins.append(FFPlugin(plugin_name, 'test', argument=plugin_argument))
        except ImportError:
            print('ERROR: unknown plugin: %s' % plugin_name, file=sys.stderr)
            sys.exit(1)
        except AttributeError:
            print('ERROR: broken plugin: %s' % plugin_name, file=sys.stderr)
            sys.exit(1)
    args.tests = plugins

    ## prepare pattern
    err_msg = prepare_pattern(args)
    if err_msg:
        raise p.error(err_msg)

    ## prepare sources
    args.source += args.anon_sources
    if not args.source:
        args.source.append('.')

    for i, src in enumerate(args.source):
        try:
            src = src.decode('utf-8')
        except UnicodeDecodeError as ex:
            print('ERROR: ', src, ': ', ex, sep='', file=sys.stderr)
            sys.exit()

        if not os.path.isdir(src):
            p.error('Source %s doesn\'t exists or is not a directory' % src)
        args.source[i] = os.path.abspath(src)

    ## prepare exec
    if args.shell_exec:
        args.execute = [args.execute.decode('utf-8')]
    elif args.execute:
        args.execute = [ part.decode('utf-8') for part in shlex.split(args.execute) ]

    ## prepare excluded paths
    for i, ex_path in enumerate(args.excluded_paths):
        ex_path = ex_path.decode('utf-8')
        ex_path = unicodedata.normalize('NFKC', ex_path)
        args.excluded_paths[i] = os.path.abspath(ex_path).rstrip('/')

    if args.print0:
        args.delim = chr(0)
    else:
        args.delim = "\n"

    return args

def _prepare_execute__vars(match):
    """ Helper method for prepare_execute, used in replacement of regular expression.
        Returns environment variable if found and quantity of escape characters ('\')
        is even.
    """
    if len(match.group(1)) % 2 == 0:
        return os.environ.get(match.group(2), '')
    else:
        return match.group(0)

_RXP_VARIABLE = re.compile(r' (\\*)\$ ([_a-zA-Z0-9]+) ', re.VERBOSE)
def prepare_execute(exe, path, dirname, basename, expand_vars=True):
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
        if expand_vars:
            elem = _RXP_VARIABLE.sub(_prepare_execute__vars, elem)

        exe[i] = elem

    return exe

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
                print('Plugin "%s" error: %s' % (test.name, ex), file=sys.stderr)
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
        print(prefix, path.encode(sys.stdout.encoding or 'utf-8'), sep='', end=cfg.delim)

    if cfg.execute:
        exe = prepare_execute(cfg.execute, path, os.path.dirname(path), os.path.basename(path), not cfg.shell_exec)
        if cfg.verbose_exec:
            print(' '.join(exe))
        if not cfg.interactive_exec or ask('Execute command on %s?' % path, 'yn', 'n') == 'y':
            subprocess.call(exe, shell=cfg.shell_exec)

def is_path_excluded(excluded_paths, path):
    """ Check that path is excluded from processing
    """
    path = path.rstrip('/')
    path = unicodedata.normalize('NFKC', path)
    for exc in excluded_paths:
        if path == exc or exc + '/' in path:
            return True
    return False

_RXP_VCS = re.compile(r'(?:^|/)(?:\.git|\.svn|\.CVS|\.hg|_MTN|CVS|RCS|SCCS|_darcs|_sgbak)(?:$|/)')

def process_source(src, cfg):
    """ Process single source: search for items and call process_item on them.
    """
    for root, __, files in os.walk(src):
        root = unicodedata.normalize('NFKC', root)
        if is_path_excluded(cfg.excluded_paths, root):
            continue

        if cfg.mode in ('dirs', 'all'):
            if cfg.vcs or not _RXP_VCS.search(root):
                process_item(cfg, root)

        if cfg.mode in ('files', 'all'):
            for file_ in files:
                file_ = unicodedata.normalize('NFKC', file_)
                path = os.path.join(root, file_)
                if is_path_excluded(cfg.excluded_paths, path):
                    continue
                if cfg.vcs or not _RXP_VCS.search(path):
                    process_item(cfg, path)

def main():
    """ Run program
    """
    try:
        config = parse_input_args(sys.argv[1:])
    except argparse.ArgumentError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    try:
        for source in config.source:
            process_source(source, config)
    except KeyboardInterrupt:
        print('Interrupted by CTRL-C, aborting', file=sys.stderr)

if __name__ == '__main__':
    main()
