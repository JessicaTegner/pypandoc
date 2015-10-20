#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pypandoc
from setuptools import setup, Command

import sys
import os
import shutil
import tempfile
import os.path
import subprocess
import urllib.request

try:
    long_description = pypandoc.convert('README.md', 'rst')
except OSError:
    # pandoc is not installed, fallback to using raw contents
    long_description = open('README.md').read()

# Uses sys.platform keys, but removes the 2 from linux2
# Adding a new plattform means implemnting unpacking in "DownloadPandocCommand" and adding the URL here
# For macosx: http://stackoverflow.com/questions/11298855/how-to-unpack-and-pack-pkg-file
# for deb: https://www.tablix.org/~avian/blog/archives/2005/09/unpacking_a_deb_without_dpkg/
PANDOC_URLS = {
    "win32": "https://github.com/jgm/pandoc/releases/download/1.15.1.1/pandoc-1.15.1.1-windows.msi", 
    #"linux": "https://github.com/jgm/pandoc/releases/download/1.15.1/pandoc-1.15.1-1-amd64.deb",
    #"darwin": "https://github.com/jgm/pandoc/releases/download/1.15.1/pandoc-1.15.1-osx.pkg"
}

class DownloadPandocCommand(Command):

    """Download pandoc"""

    description = "downloads a pandc release and adds it to the package"

    user_options = []

    def initialize_options(self):
         pass

    def finalize_options(self):
         pass
         
    def _unpack_win32(self, filename):
        targetfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pypandoc", "files")
        print("* Unpacking %s to tempfolder..." % (filename))
        
        tempfolder = tempfile.mkdtemp()
        
        # Make sure the targetfolder exists...
        try:
            os.makedirs(targetfolder)
        except OSError:
            pass # dir already exists...
              
        cmd = ["msiexec", "/a", filename, "/qb", "TARGETDIR=%s" % (tempfolder)]
        # if only 3.5 is supported, should be `run(..., check=True)`
        subprocess.check_call(cmd)
        
        # pandoc.exe and citeproc.exe and pandoc-citeproc.exe are in the Pandoc subfolder
        for exe in ["pandoc.exe", "pandoc-citeproc.exe"]:
            src = os.path.join(tempfolder, "Pandoc", exe)
            dst = os.path.join(targetfolder, exe)
            print("* Copying %s to %s ..." % (exe, targetfolder))
            print("%s, %s" % (src, dst))
            shutil.copyfile(src, dst)
        
        # remove temporary dir
        #shutil.rmtree(tempfolder)
        print("* Done.")
        
    def run(self):      
        platform = sys.platform
        # compatibility with py3
        if platform.startswith("linux"):
            platform = "linux"
            
        try:
            url = PANDOC_URLS[platform]
        except:
            raise Exception("No prebuilt pandoc available or not yet implmented for your platform")
        
        filename = url.split("/")[-1]
        if os.path.isfile(filename):
            print("* Using alread downloaded file %s" % (filename))
        else:

            print("* Downloading pandoc from %s ..." % url)
            with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        
        unpack = getattr(self, "_unpack_"+platform)
        unpack(filename)

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
    test_suite = 'tests',
    cmdclass={'download_pandoc': DownloadPandocCommand}
)
