# -*- coding: utf-8 -*-

"""
    Plugins engine
"""

from __future__ import print_function, unicode_literals, division

import collections
import glob
import os
import sys
import textwrap

from ff.utils import disp


class FFPluginError(Exception):
    """ Exception class for plugins.
    """
    # TODO: do not hardocde 'test'
    PREFIX = 'ffplugin_test_'

    def __init__(self, msg, name=None):
        super(FFPluginError, self).__init__(msg)
        self.plugin_name = name

    @staticmethod
    def _get_tb_filename(tb):
        return os.path.splitext(os.path.basename(tb.tb_frame.f_code.co_filename))[0]

    def get_plugin_name(self):
        if not self.plugin_name:
            tb = sys.exc_info()[2]
            i = 7
            while i > 0 and not self._get_tb_filename(tb).startswith(self.PREFIX):
                i -= 1
                tb = tb.tb_next

            self.plugin_name = self._get_tb_filename(tb)[len(self.PREFIX):]

        return self.plugin_name


class InvalidPluginsPath(FFPluginError):
    """ Exception for invalid plugins paths
    """
    def __init__(self, msg, path):
        super(InvalidPluginsPath, self).__init__(msg)
        self.path = path


class FFPlugin(object):
    """ Wrapper for custom plugin.

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

        self.name = name
        self.type = type_
        self.action = kw.get('action')
        self.descr = kw.get('descr', '')
        self.help = kw.get('help', '')
        self.argument = kw.get('argument')

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
        disp(text)

    def print_help(self):
        """ Print list of plugins with their help to STDOUT
        """
        for item in self:
            self._print_descr(item)
            if item.help:
                disp(item.help.rstrip() + os.linesep)

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
    def _find_all_plugins(cls, type_):
        """ Helper for FFPlugins.find_all

            Search for every plugin in specified paths and returns it's names.
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

        return order

    @classmethod
    def find_all(cls, type_):
        """ Find all plugins available for `ff` and return FFPlugins
            initialized with it.

            Every item is instance of FFPlugin.

            Uses `FFPlugins.find` to load plugins.
        """

        plugins_names = cls._find_all_plugins(type_)
        return cls.find(plugins_names, type_=type_)

    @classmethod
    def find(cls, names, type_):
        """ Load given plugins list and initialize `FFPlugins` with them.

            Returns `FFPlugins` instance.
        """
        plugins = cls()
        for plugin_name in names:
            plugins.append(FFPlugin(plugin_name, type_))

        return plugins
