#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os, os.path
import sys
import re
from pprint import pprint, pformat

__all__ = ['PLAYGROUND_PATH']

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PLAYGROUND_PATH = os.path.join(os.path.dirname(__file__), 'playground')
