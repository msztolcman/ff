ff
==

Easy find files and directories by their names.

If you need to search by file content, use [ack](https://github.com/petdance/ack) or [pss](https://github.com/eliben/pss).

Basic usage
-----------

    ff passwd

Search for all files and folders in current directory and below, which is match to pattern: `*passwd*`.

    ff -B passwd

Search for all files and folders in current directory and below, which is match to pattern: `*passwd`.

    ff -E passwd

Search for all files and folders in current directory and below, which is match to pattern: `passwd*`.

    ff -EB passwd

Search for all files and folders in current directory and below, which is match to pattern: `passwd`.

Advanced usage
--------------

    ./ff.py -p pa -s /etc --shell-exec -x '[ -f "{path}" ] && mkdir -p /tmp{dirname}; cp -r "{path}" "/tmp{path}"'

Find all files and directories in /etc that match expression: `*pa*`, and copy them (with original directories hierarchy!) to /tmp.

So powerful...

Installation
------------

`ff` should work on any platform where [Python](http://python.org) is available, it means Linux, Windows, MacOS X etc. There is no dependencies, plain Python power :) Just copy file to your PATH, for example:

    curl https://raw.github.com/mysz/ff/master/ff.py > /usr/local/bin/ff

or:

    wget https://raw.github.com/mysz/ff/master/ff.py -O /usr/local/bin/ff

Voila!

Usage
-----

    ff
        [-0|--print0] split results by binary zero instead of new line (useful to work with xargs)
        [-i|--ignorecase]
        *[-s|--source source] - optional, see: source below
        *[-p|--pattern] - optional, see: pattern below
        [-g|--regexp] - treat pattern as regular expression (uses Python regexp engine)
        [-l|--regex-multiline]
        [-d|--regex-dotall]
        [-B|--begin] - anchor pattern to begin of item name (ignored in regexp mode)
        [-E|--end] - anchor pattern to end of item name (ignored in regexp mode)
        [-v|--invert-match]
        [-m|--mode] - one of: 'all' (default), 'dirs', 'files'
        [-x|--exec] - execute some command on every found item. In command, placeholders: {path}, {dirname}, {basename} are replaced with correct value
        [--prefix] - add prefix 'd: ' (directory) or 'f: ' (file) to every found item
        [--no-display] - don't display element (useful with --exec argument)
        [--verbose-exec] - show command before execute it
        [--interactive-exec] - ask before execute command on every item
        [--shell-exec] - execute command from --exec argument in shell (with shell expansion etc)
        [--vcs] - do not skip VCS directories (.git, .svn etc)
        [-h|--help]
        pattern - pattern to search
        [source1 .. sourceN] - optional source (if missing, use current directory)

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
