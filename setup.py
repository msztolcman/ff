#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from setuptools import setup, find_packages
from codecs import open
import os.path

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ff',
    version='0.5.1',
    description='Easily search and process files by names.',
    long_description=long_description,
    url='http://mysz.github.io/ff/',
    author='Marcin Sztolcman',
    author_email='marcin@urzenia.net',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities'
    ],
    keywords='search find filesystem files directories',
    install_requires=['argparse'],
    py_modules=['ff'],
    entry_points={
        'console_scripts': [
            'ff=ff:main',
        ],
    },
)
