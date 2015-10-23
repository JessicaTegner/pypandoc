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
import platform

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

try:
    long_description = pypandoc.convert('README.md', 'rst')
except OSError:
    print("\n\n!!! pandoc not found, long_description is bad, don't upload this to PyPI !!!\n\n")
    import io
    # pandoc is not installed, fallback to using raw contents
    with io.open('README.md', encoding="utf-8") as f:
        long_description = f.read()

# Uses sys.platform keys, but removes the 2 from linux2
# Adding a new platform means implementing unpacking in "DownloadPandocCommand" and adding the URL here
PANDOC_URLS = {
    "win32": "https://github.com/jgm/pandoc/releases/download/1.15.1.1/pandoc-1.15.1.1-windows.msi",
    "linux": "https://github.com/jgm/pandoc/releases/download/1.15.1/pandoc-1.15.1-1-amd64.deb",
    "darwin": "https://github.com/jgm/pandoc/releases/download/1.15.1/pandoc-1.15.1-osx.pkg"
}

class DownloadPandocCommand(Command):

    """Download pandoc"""

    description = "downloads a pandoc release and adds it to the package"

    user_options = []

    def initialize_options(self):
         pass

    def finalize_options(self):
         pass
    
    def _unpack_linux(self, filename, targetfolder):
        
        assert platform.architecture()[0] == "64bit", "Downloaded linux pandoc is only compiled for 64bit."
        
        print("* Unpacking %s to tempfolder..." % (filename))

        tempfolder = tempfile.mkdtemp()
        cur_wd = os.getcwd()
        filename = os.path.abspath(filename)
        try:
            os.chdir(tempfolder)
            cmd = ["ar", "x", filename]
            # if only 3.5 is supported, should be `run(..., check=True)`
            subprocess.check_call(cmd)
            cmd = ["tar", "xzf", "data.tar.gz"]
            subprocess.check_call(cmd)
            # pandoc and pandoc-citeproc are in ./usr/bin subfolder
            for exe in ["pandoc", "pandoc-citeproc"]:
                src = os.path.join(tempfolder, "usr", "local", "bin", exe)
                dst = os.path.join(targetfolder, exe)
                print("* Copying %s to %s ..." % (exe, targetfolder))
                shutil.copyfile(src, dst)
            src = os.path.join(tempfolder, "usr", "share", "doc", "pandoc", "copyright")
            dst = os.path.join(targetfolder, "copyright")
            print("* Copying %s to %s ..." % (exe, targetfolder))
            shutil.copyfile(src, dst)
        finally:
            os.chdir(cur_wd)
            shutil.rmtree(tempfolder)
            
    def _unpack_darwin(self, filename, targetfolder):
        print("* Unpacking %s to tempfolder..." % (filename))

        tempfolder = tempfile.mkdtemp()

        pkgutilfolder = os.path.join(tempfolder, 'tmp')
        cmd = ["pkgutil", "--expand", filename, pkgutilfolder]
        # if only 3.5 is supported, should be `run(..., check=True)`
        subprocess.check_call(cmd)

        # this will generate usr/local/bin below the dir
        cmd = ["tar", "xvf", os.path.join(pkgutilfolder, "pandoc.pkg", "Payload"),
            "-C", pkgutilfolder]
        subprocess.check_call(cmd)

        # pandoc and pandoc-citeproc are in the ./usr/local/bin subfolder
        for exe in ["pandoc", "pandoc-citeproc"]:
            src = os.path.join(pkgutilfolder, "usr", "local", "bin", exe)
            dst = os.path.join(targetfolder, exe)
            print("* Copying %s to %s ..." % (exe, targetfolder))
            shutil.copyfile(src, dst)

        # remove temporary dir
        shutil.rmtree(tempfolder)
        print("* Done.")

    def _unpack_win32(self, filename, targetfolder):
        print("* Unpacking %s to tempfolder..." % (filename))

        tempfolder = tempfile.mkdtemp()

        cmd = ["msiexec", "/a", filename, "/qb", "TARGETDIR=%s" % (tempfolder)]
        # if only 3.5 is supported, should be `run(..., check=True)`
        subprocess.check_call(cmd)

        # pandoc.exe, pandoc-citeproc.exe, and the COPYRIGHT are in the Pandoc subfolder
        for exe in ["pandoc.exe", "pandoc-citeproc.exe", "COPYRIGHT.txt"]:
            src = os.path.join(tempfolder, "Pandoc", exe)
            dst = os.path.join(targetfolder, exe)
            print("* Copying %s to %s ..." % (exe, targetfolder))
            shutil.copyfile(src, dst)

        # remove temporary dir
        shutil.rmtree(tempfolder)
        print("* Done.")

    def run(self):
        pf = sys.platform
        # compatibility with py3
        if pf.startswith("linux"):
            pf = "linux"

        try:
            url = PANDOC_URLS[pf]
        except:
            raise Exception("No prebuilt pandoc available or not yet implemented for your platform")

        filename = url.split("/")[-1]
        if os.path.isfile(filename):
            print("* Using already downloaded file %s" % (filename))
        else:
            print("* Downloading pandoc from %s ..." % url)
            # https://stackoverflow.com/questions/30627937/tracebaclk-attributeerroraddinfourl-instance-has-no-attribute-exit
            response = urlopen(url)
            with open(filename, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        
        targetfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pypandoc", "files")

        # Make sure target folder exists...
        try:
            os.makedirs(targetfolder)
        except OSError:
            pass # dir already exists...

        unpack = getattr(self, "_unpack_"+pf)
        
        unpack(filename, targetfolder)


cmd_classes = {'download_pandoc': DownloadPandocCommand}

# add our own bdist_wheel command, so that it ends up platform specific,
# even if we only compile python code and no platform specific
# binaries.
if (os.path.isfile(os.path.join("pypandoc", "files", "pandoc")) or
    os.path.isfile(os.path.join("pypandoc", "files", "pandoc.exe"))):

    try:
        from wheel.bdist_wheel import bdist_wheel
    except ImportError:
        # No wheel installed, so we also can't run that command...
        pass
    else:
        class new_bdist_wheel(bdist_wheel):
            def finalize_options(self):
                bdist_wheel.finalize_options(self)
                # this turns on the proper filenames
                self.root_is_pure = False
                # in the orig finalize_options this is set to:
                # self.root_is_pure = not (self.distribution.has_ext_modules()
                #                  or self.distribution.has_c_libraries())

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
    cmdclass=cmd_classes
)
