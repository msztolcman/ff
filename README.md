ff
==

Easy find files and directories by their names.

If you need to search by file content, use [ack](https://github.com/petdance/ack) or [pss](https://github.com/eliben/pss).

Usage
-----

    ff 
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
        [--vcs] - do not skip VCS directories (.git, .svn etc)
        [-h|--help]
        pattern - pattern to search
        [source1 .. sourceN] - optional source (if missing, use current directory)

