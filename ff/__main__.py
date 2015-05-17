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
import sys

from ff.cli import parse_input_args
from ff.processing import process_source
from ff.utils import disp

def main():
    """ Run program
    """
    try:
        config = parse_input_args(sys.argv[1:])
    except argparse.ArgumentError as ex:
        disp(ex, file=sys.stderr)
        sys.exit(1)

    try:
        for source in config.source:
            process_source(source, config)
    except KeyboardInterrupt:
        disp('Interrupted by CTRL-C, aborting', file=sys.stderr)


if __name__ == '__main__':
    main()
