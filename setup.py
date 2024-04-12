#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pypandoc
import io
from setuptools import setup

with io.open('README.md', encoding="utf-8") as f:
    long_description = f.read()

module = pypandoc
setup(
    name = 'pypandoc',
    version = module.__version__,
    url = pypandoc.__url__,
    license = pypandoc.__license__,
    description = pypandoc.__description__,
    long_description = long_description,
    long_description_content_type='text/markdown',
    author = module.__author__.encode('utf8'),
    author_email = pypandoc.__author_email__,
    packages = ['pypandoc'],
    python_requires=pypandoc.__python_requires__,
    setup_requires = pypandoc.__setup_requires__,
    classifiers=pypandoc.__classifiers__,
    test_suite = 'tests',
    project_urls={
        'Source': pypandoc.__url__,
        'Tracker': pypandoc.__url__ + '/issues',
    }
)
