ff
==

Easy find files and directories by their names.

If you need to search by file content, use [ack](https://github.com/petdance/ack2) or [pss](https://github.com/eliben/pss).

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

So powerful...

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

Installation
------------

`ff` should work on any platform where [Python](http://python.org) is available, it means Linux, Windows, MacOS X etc. There is no dependencies, plain Python power :) Just copy file to your PATH, for example:

    curl https://raw.github.com/mysz/ff/master/ff.py > /usr/local/bin/ff

or:

    wget https://raw.github.com/mysz/ff/master/ff.py -O /usr/local/bin/ff

Voila!

Usage
-----

    usage: ff.py [-h] [-0] [-i] [-s SOURCE] [-p PATTERN] [-g] [-f] [-q] [-l] [-d]
                [-B] [-E] [-v] [-m {all,files,dirs}] [-x COMMAND] [--prefix]
                [--no-display] [--verbose-exec] [--interactive-exec]
                [--shell-exec] [--vcs] [-c EXCLUDED_PATH]
                [pattern] [sources [sources ...]]

    Easily search and process files by names.

    positional arguments:
    pattern               pattern to search
    sources               optional source (if missing, use current directory)

    optional arguments:
    -h, --help            show this help message and exit
    -0, --print0          split results by binary zero instead of new line
                          (useful to work with xargs)
    -i, --ignorecase, --ignore-case
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
    -d, --regex-dotall
    -B, --begin           match pattern to begin of item name (ignored in regexp
                          mode)
    -E, --end             match pattern to end of item name (ignored in regexp
                          mode)
    -v, -r, --invert-match
    -m {all,files,dirs}, --mode {all,files,dirs}
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
            's' (--regex_dotall), 'v' (not used currently), 'r' (--invert-match)
            'q' (--path-search)

    Author:
        Marcin Sztolcman <marcin@urzenia.net> // http://urzenia.net

    HomePage:
        https://github.com/mysz/ff/

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

# v0.3
* use argparse instead of getopt to parse options
* allow to exclude path from search
* improved help and documentation

# v0.2
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

# v0.1
* initial version
