#!/usr/bin/env python
#  -*- coding: utf-8 -*-

""" ff - Easily search and process files.
    http://mysz.github.io/ff
    Author: Marcin Sztolcman (marcin@urzenia.net)

    Get help with: ff --help
    Information about version: ff --version
"""

from __future__ import print_function, unicode_literals, division

import argparse
import itertools
import os, os.path
import sys

from ff.cli import parse_input_args
from ff.plugin import FFPlugins, FFPlugin, InvalidPluginsPath, FFPluginError
from ff.processing import process_source
from ff.utils import disp, err, u


def _detect_plugins_paths(args):
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


def _initialize_plugins(args):
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


def main():
    """ Run program
    """
    try:
        config = parse_input_args(sys.argv[1:])
    except argparse.ArgumentError as ex:
        err(str(ex), exit_code=1)

    # where to search for plugins
    try:
        _detect_plugins_paths(config)
    except InvalidPluginsPath as ex:
        err('%s: %s' % (ex.path, str(ex)), sep='', exit_code=1)

    try:
        # None means: show me the list of plugins
        if None in config.help_test_plugins:
            plugins = FFPlugins.find_all('test')
            plugins.print_list()

            sys.exit()
        # show info about testing plugins
        elif config.help_test_plugins:
            # plugins names can be separated with comma
            plugins = [plugin.split(',') for plugin in config.help_test_plugins]
            plugins = itertools.chain(*plugins)

            plugins = FFPlugins.find(plugins, 'test')
            plugins.print_help()

            sys.exit()
    except ImportError as ex:
        err('Unknown plugin: %s' % ex, exit_code=1)

    # find all requested test plugins
    try:
        config.tests = _initialize_plugins(config)
    except FFPluginError as ex:
        err(str(ex), exit_code=1)

    try:
        for source in config.source:
            process_source(source, config)
    except KeyboardInterrupt:
        disp('Interrupted by CTRL-C, aborting', file=sys.stderr)


if __name__ == '__main__':
    main()
