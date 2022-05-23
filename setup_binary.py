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



class DownloadPandocCommand(Command):

    """Download pandoc"""

    description = "downloads a pandoc release and adds it to the package"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pypandoc.pandoc_download import download_pandoc
        targetfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pypandoc", "files")
        download_pandoc(targetfolder=targetfolder)


cmd_classes = {'download_pandoc': DownloadPandocCommand}

# Make sure wheels end up platform specific, if they include a pandoc binary
has_pandoc = (os.path.isfile(os.path.join("pypandoc", "files", "pandoc")) or
              os.path.isfile(os.path.join("pypandoc", "files", "pandoc.exe")))
is_build_wheel = ("bdist_wheel" in sys.argv)
is_download_pandoc = ("download_pandoc" in sys.argv)

if is_build_wheel:
    if has_pandoc or is_download_pandoc:
        # we need to make sure that bdist_wheel is after is_download_pandoc,
        # otherwise we don't include pandoc in the wheel... :-(
        pos_bdist_wheel = sys.argv.index("bdist_wheel")
        if is_download_pandoc:
            pos_download_pandoc = sys.argv.index("download_pandoc")
            if pos_bdist_wheel < pos_download_pandoc:
                raise RuntimeError("'download_pandoc' needs to be before 'bdist_wheel'.")
        # we also need to make sure that this version of bdist_wheel supports
        # the --plat-name argument
        try:
            import wheel
            from distutils.version import StrictVersion
            if not StrictVersion(wheel.__version__) >= StrictVersion("0.27"):
                msg = "Including pandoc in wheel needs wheel >=0.27 but found %s.\nPlease update wheel!"
                raise RuntimeError(msg % wheel.__version__)
        except ImportError:
            # the real error will happen further down...
            print("No wheel installed, please install 'wheel'...")
        print("forcing platform specific wheel name...")
        from distutils.util import get_platform
        sys.argv.insert(pos_bdist_wheel + 1, '--plat-name')
        sys.argv.insert(pos_bdist_wheel + 2, get_platform())
    else:
        print("no pandoc found, building platform unspecific wheel...")
        print("use 'python setup.py download_pandoc' to download pandoc.")

module = pypandoc
setup(
    name = 'pypandoc_binary',
    version = module.__version__,
    url = pypandoc.__url__,
    license = pypandoc.__license__,
    description = pypandoc.__description__,
    long_description = long_description,
    long_description_content_type='text/markdown',
    author = module.__author__.encode('utf8'),
    author_email = pypandoc.__author_email__,
    packages = ['pypandoc'],
    package_data={'pypandoc': ['files/*']},
    python_requires=pypandoc.__python_requires__,
    setup_requires = pypandoc.__setup_requires__,
    classifiers=pypandoc.__classifiers__,
    test_suite = 'tests',
    cmdclass=cmd_classes
)
