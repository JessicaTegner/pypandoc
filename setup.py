#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pypandoc
from setuptools import setup, Command

import os
import os.path

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

try:
    long_description = pypandoc.convert('README.md', 'rst')
    long_description = long_description.replace("\r","")
except OSError:
    print("\n\n!!! pandoc not found, long_description is bad, don't upload this to PyPI !!!\n\n")
    import io
    # pandoc is not installed, fallback to using raw contents
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

# add our own bdist_wheel command, so that it ends up platform specific,
# even if we only compile python code and no platform specific
# binaries.
if (os.path.isfile(os.path.join("pypandoc", "files", "pandoc")) or
    os.path.isfile(os.path.join("pypandoc", "files", "pandoc.exe"))):
    print("Patching wheel building...")
    try:
        from wheel.bdist_wheel import bdist_wheel
    except ImportError:
        # No wheel installed, so we also can't run that command...
        pass
    else:
        # these imports should fail as our our later functions relies on it...
        from wheel.bdist_wheel import (get_platform, get_abbr_impl,
                                       get_impl_ver, pep425tags, sysconfig)
        print("Making sure that wheel is platform specific...")
        class new_bdist_wheel(bdist_wheel):
            def get_tag(self):
                # originally get_tag would branch for 'root_is_pure" and return
                # tags suitable for wheels running on any py3/py2 system. So
                # setting the attribute in finalize_options was enough. But
                # In the 3.5 instead of the attribute,
                # self.distribution.is_pure() is called, so we have to overwrite
                # the complete functions...

                supported_tags = pep425tags.get_supported()
                plat_name = self.plat_name
                if plat_name is None:
                    plat_name = get_platform()
                plat_name = plat_name.replace('-', '_').replace('.', '_')
                impl_name = get_abbr_impl()
                impl_ver = get_impl_ver()
                # PEP 3149 -- no SOABI in Py 2
                # For PyPy?
                # "pp%s%s" % (sys.pypy_version_info.major,
                # sys.pypy_version_info.minor)
                abi_tag = sysconfig.get_config_vars().get('SOABI', 'none')
                if abi_tag.startswith('cpython-'):
                    abi_tag = 'cp' + abi_tag.rsplit('-', 1)[-1]

                tag = (impl_name + impl_ver, abi_tag, plat_name)
                # XXX switch to this alternate implementation for non-pure:
                assert tag == supported_tags[0]
                return tag
            def finalize_options(self):
                bdist_wheel.finalize_options(self)
                assert "any" not in self.get_archive_basename(), "bdist_wheel will not generate platform specific names, aborting!"
        cmd_classes["bdist_wheel"] = new_bdist_wheel

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
    packages = ['pypandoc'],
    package_data={'pypandoc': ['files/*']},
    install_requires = ['setuptools', 'pip>=8.1.0', 'wheel>=0.25.0'],
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
    test_suite = 'tests',
    cmdclass=cmd_classes
)
