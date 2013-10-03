ff
==

Easily search and process files.

If you need to search files by their contents, *or* search for their contents, please look at [ack](https://github.com/petdance/ack2) or [pss](https://github.com/eliben/pss). These are better suited for this kind of task.

Current stable version
----------------------

0.5

Why `ff` and not `find`?
------------------------

Just because I find that most of my searches was:

    find . -iname '*name*'

And it's easier to me to enter:

    ff name

Also, my `find` have sometimes problems with non ascii files:

    % find /etc -name '*GÖS*'
    % 

And with `ff`:

    % ./ff.py '*GÖS*' /etc
    /etc/eee_GÖS_från_förstår_pas
    /etc/eee_GÖS_från_pas_förstår_qq
    /etc/pas_GÖS_från_förstår
    %

:)

Basic usage
-----------

    ff passwd

Search for all files and directories in current directory and below, which is match to pattern: `*passwd*`.

    ff -B passwd

Search for all files and directories in current directory and below, which is match to pattern: `*passwd`.

    ff -E passwd

Search for all files and directories in current directory and below, which is match to pattern: `passwd*`.

    ff -EB passwd

Advanced usage
--------------

    ./ff.py -p pa -s /etc --shell-exec -x '[ -f "{path}" ] && mkdir -p /tmp{dirname}; cp -r "{path}" "/tmp{path}"'

Find all files and directories in /etc that match expression: `*pa*`, and copy them (with original directories hierarchy!) to /tmp.

So powerful!

Magic pattern
-------------

It's form of pattern known good for Perl or AWK lovers :)

If patterns is in general form:

    mode/pattern/modifier

(decribed more in full usage below), then it is parsed and used in a little other manner.

Instead of arguments `--regexp` or `--fuzzy`, you can pass it in `mode` part of pattern.
Next there is delimiter, which usually is `/` (backslash), but there can be more characters,
described in Usage section.

After that is a pattern, next delimiter again, and then modifiers (again, modifiers are described in Usage section).

Some examples:

Search for all files and directories in current directory and below, which is match to pattern: `passwd`.

    ff f/pwd/

Search for all files and directories in current directory and below, which name contains letters 'p', 'w', 'd', with any other characters between them.

    ff g/^(chk)?passwd/

Search for all files and directories in current directory and below, which name starts from 'chkpasswd' or 'passwd'.

Plugins
-------

Plugins are the way to easily extend capabilities of `ff`. Currently there is only support for plugins allowing to extend tests made on files list. In future, there is plan to add support for plugins allowing to make some actions on found files (currently is _built-in plugin_: `--shell`), for example modifying, copying or anything else).

`ff` search for plugins in two places (by default), but there is posibility to tell him about third one.
Automaticaly recognized paths are:

* `~/.ff/plugins`
* directory `ff_plugins` in programs root (if You have `ff` placed in `~/bin`, it will search for plugins in `~/bin/ff_plugins`)

And using switch `--plugins-path` You can tell `ff` where the plugins must be searched.

You can also pass argument to plugins. For example, in `size` plugin (You can download it from [GitHub](https://github.com/mysz/ff/tree/master/ff_plugins)), You must to tell the plugin what size of file You expect:

    `ff pas --test size:=5k`

Above example will find every file with _pas_ part in its name, and its size is *exactly* 5 [kibibytes](http://en.wikipedia.org/wiki/Binary_prefix#IEC_standard_prefixes). More about `size` plugin in [projects wiki](https://github.com/mysz/ff/wiki/).

Writing plugins
---------------

Plugins are written in [Python](http://python.org), and are simple Python modules with at least `plugin_action` callable specified. Plugins are imported, and `plugin_action` must return `True` or `False` to tell `ff` that given found object meets expectations, and should be returned.

`ff` recognize and use only 3 objects in plugin:

* `plugin_action` - (REQUIRED) [callable] must return `True` od `False`. Must recognize 3 arguments:
    * `name` - name of plugin
    * `argument` - argument passed by user
    * `path` - absolute path to tested object
* `PLUGIN_DESCR` - (OPTIONAL) [string or callable] short descr of plugin, printed when `ff` is called with switch `--help-test-plugins`
* `PLUGIN_HELP` - (OPTIONAL) [string or callable] full help for plugin, printed when `ff` is called with switch `--help-test-plugins TEST_NAME`

Plugin file also must have special name, and be placed in directory recognized by `ff` (see: [plugins][plugins]).
Name of file is built with three parts, connected with underscore:
* `ffplugin` - fixed prefix
* `test` - type of plugin (currently only `test` plugins are recignized)
* `NAME` - name of plugin

And as Python module, must and with `.py` extension :)

Plugin must validate input data (`argument`), and raise `PluginError` exception with approbiate message on any error. Plugin shouldn't raise any other exceptions.
There is one caveat with this: `PluginError` exception is declared *inside* `ff`! When given plugin is imported, it is _monkeypatched_ and `PluginError` exception is injected into.

This is made by one of goals I have: try to have whole `ff` program in single file. It's important to me that I can move it easy between servers.

There is an example plugin, which allow us to search for files in specified size. Is in [project repository](https://github.com/mysz/ff/tree/master/ff_plugins) in directory plugins. You can use it as a base for your own plugins :)

Installation
------------

`ff` should work on any platform where [Python](http://python.org) is available, it means Linux, Windows, MacOS X etc. There is no dependencies, plain Python power :) 

To install, go to [GitHub releases](https://github.com/mysz/ff/releases), download newest release, unpack and put somewhere in `PATH` (ie. `~/bin` or `/usr/local/bin`).

If You want to install newest unstable version, then just copy file to your PATH, for example:

    curl https://raw.github.com/mysz/ff/master/ff.py > /usr/local/bin/ff

or:

    wget https://raw.github.com/mysz/ff/master/ff.py -O /usr/local/bin/ff

Voila!

Usage
-----

    usage: ff.py [-h] [-0] [-i] [-s SOURCE] [-p PATTERN] [-g] [-f] [-q] [-l] [-d]
                [-B] [-E] [-v] [-m MODE] [-x COMMAND] [--prefix] [--no-display]
                [--verbose-exec] [--interactive-exec] [--shell-exec] [--vcs]
                [-c EXCLUDED_PATH] [-t TESTS] [--plugins-path PLUGINS_PATH]
                [--version] [--help-test-plugins [TEST_NAME[,TEST2_NAME]]]
                [pattern] [sources [sources ...]]

    Easily search and process files.

    positional arguments:
    pattern               pattern to search
    sources               optional source (if missing, use current directory)

    optional arguments:
    -h, --help            show this help message and exit
    -0, --print0          split results by binary zero instead of new line
                          (useful to work with xargs)
    -i, --ignorecase, --ignore-case
                          ignore case when match pattern to paths
    -s SOURCE, --source SOURCE
                          optional, see: source above
    -p PATTERN, --pattern PATTERN
                          optional, see: pattern above
    -g, --regexp          treat pattern as regular expression (uses Python
                          regexp engine)
    -f, --fuzzy           pattern defines only set and order of characters used
                          in filename
    -q, --path-search     search in full path, instead of bare name of item
    -l, --regex-multiline
                          modify meta characters: "^" and "$" behaviour when
                          pattern is regular expression. See:
                          http://docs.python.org/2/library/re.html#re.MULTILINE
    -d, --regex-dotall    modify meta character: "." behaviour when pattern is
                          regular expression. See:
                          http://docs.python.org/2/library/re.html#re.DOTALL
    -B, --begin           match pattern to begin of item name (ignored in regexp
                          mode)
    -E, --end             match pattern to end of item name (ignored in regexp
                          mode)
    -v, -r, --invert-match
                          find objects that do *not* match pattern
    -m MODE, --mode MODE  allow to choose to search for "files" only, "dirs", or
                          "all"
    -x COMMAND, --exec COMMAND
                          execute some command on every found item. In command,
                          placeholders: {path}, {dirname}, {basename} are
                          replaced with correct value
    --prefix              add prefix "d: " (directory) or "f: " (file) to every
                          found item
    --no-display          don't display element (useful with --exec argument)
    --verbose-exec        show command before execute it
    --interactive-exec    ask before execute command on every item
    --shell-exec          execute command from --exec argument in shell (with
                          shell expansion etc)
    --vcs                 do not skip VCS directories (.git, .svn etc)
    -c EXCLUDED_PATH, --exclude-path EXCLUDED_PATH
                          skip given paths from scanning
    -t TESTS, --test TESTS
                          additional tests, available by plugins (see
                          annotations below or --help-test-plugins)
    --plugins-path PLUGINS_PATH
                          additional path where to search plugins (see
                          annotations below)
    --version             show program's version number and exit
    --help-test-plugins [TEST_NAME[,TEST2_NAME]]
                          display help for installed test plugins

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

Contact
-------

If you like or dislike this software, please do not hesitate to tell me about this me via email (marcin@urzenia.net).

If you find bug or have an idea to enhance this tool, please use GitHub's [issues](https://github.com/mysz/ff/issues).

License
-------

The MIT License (MIT)

Copyright (c) 2013 Marcin Sztolcman

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ChangeLog
---------
### v0.5
* ability to run plugins for tests (with first plugin: size)
* many improvements to proper handling UTF-8
* many improvements for work in Python3
* improved PEP8 compatibility
* refactored code
* added --version switch
* removed expanding shell variables when execute external command if no --shell-exec is given

### v.04
* added changelog
* added fuzzy-search mode
* added 'magic pattern' mode
* -r argument is now an alias to -v
* better handling unicode characters in paths
* handling CTRL-C
* added modifier: --path-search

### v0.3
* use argparse instead of getopt to parse options
* allow to exclude path from search
* improved help and documentation

### v0.2
* added option 'shell-exec' - allow to exec programs with shell expansion
* exec: add shell variables expansion
* by default, skip VCS directories
* added option 'print0' - delimit entries with binary 0, as for xargs
* added options 'interactive-exec' - ask before every exec
* much more powerfull exec engine
* added option 'no-display' - do not display results (useful with --exec)
* added option 'verbose-exec' - show executed command
* added option 'invert-match' - like in grep
* improved help and documentation
* cleanups in code

### v0.1
* initial version
