#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pypandoc
from setuptools import setup, Command

import sys
import os
import os.path
import io

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


with io.open('README.md', encoding="utf-8") as f:
    long_description = f.read()

module = pypandoc
setup(
    name = 'pypandoc',
    version = module.__version__,
    url = 'https://github.com/bebraw/pypandoc',
    license = 'MIT',
    description = 'Thin wrapper for pandoc.',
    long_description = long_description,
    long_description_content_type='text/markdown',
    author = module.__author__.encode('utf8'),
    author_email = 'bebraw@gmail.com',
    packages = ['pypandoc'],
    install_requires = ['setuptools'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    test_suite = 'tests',
)
