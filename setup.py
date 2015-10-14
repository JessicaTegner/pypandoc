#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pypandoc
from setuptools import setup

try:
    long_description = pypandoc.convert('README.md', 'rst')
except OSError:
    # pandoc is not installed, fallback to using raw contents
    long_description = open('README.md').read()

module = pypandoc
setup(
    name = 'pypandoc',
    version = module.__version__,
    url = 'https://github.com/bebraw/pypandoc',
    license = 'MIT',
    description = 'Thin wrapper for pandoc.',
    long_description = long_description,
    author = module.__author__,
    author_email = 'bebraw@gmail.com',
    py_modules = ['pypandoc', ],
    install_requires = ['setuptools', ],
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
    ],
    test_suite = 'tests'
)
