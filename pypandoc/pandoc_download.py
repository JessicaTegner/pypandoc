# -*- coding: utf-8 -*-

import os
import os.path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

DEFAULT_TARGET_FOLDER = {
    "win32": "~\\AppData\\Local\\Pandoc",
    "linux": "~/bin",
    "darwin": "~/Applications/pandoc"
}


def _get_pandoc_urls(version="latest"):
    """Get the urls of pandoc's binaries
    Uses sys.platform keys, but removes the 2 from linux2
    Adding a new platform means implementing unpacking in "DownloadPandocCommand"
    and adding the URL here

    :param str version: pandoc version.
        Valid values are either a valid pandoc version e.g. "1.19.1", or "latest"
        Default: "latest".

    :return: str pandoc_urls: a dictionary with keys as system platform
        and values as the url pointing to respective binaries

    :return: str version: actual pandoc version. (e.g. "lastest" will be resolved to the actual one)
    """
    # url to pandoc download page
    url = "https://github.com/jgm/pandoc/releases/" + \
          ("tag/" if version != "latest" else "") + version
    # read the HTML content
    response = urlopen(url)
    content = response.read()
    # regex for the binaries
    regex = re.compile(r"/jgm/pandoc/releases/download/.*\.(?:msi|deb|pkg)")
    # a list of urls to the bainaries
    pandoc_urls_list = regex.findall(content.decode("utf-8"))
    # actual pandoc version
    version = pandoc_urls_list[0].split('/')[5]
    # dict that lookup the platform from binary extension
    ext2platform = {
        'msi': 'win32',
        'deb': 'linux',
        'pkg': 'darwin'
    }
    # parse pandoc_urls from list to dict
    # py26 don't like dict comprehension. Use this one instead when py26 support is dropped
    # pandoc_urls = {ext2platform[url_frag[-3:]]: ("https://github.com" + url_frag) for url_frag in pandoc_urls_list}
    pandoc_urls = dict((ext2platform[
                            url_frag[-3:]], ("https://github.com" + url_frag)) for url_frag in pandoc_urls_list)
    return pandoc_urls, version


def _make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    print("* Making %s executeable..." % (path))
    os.chmod(path, mode)


def _handle_linux(filename, targetfolder):
    print("* Unpacking %s to tempfolder..." % (filename))

    tempfolder = tempfile.mkdtemp()
    cur_wd = os.getcwd()
    filename = os.path.abspath(filename)
    try:
        os.chdir(tempfolder)
        cmd = ["ar", "x", filename]
        # if only 3.5 is supported, should be `run(..., check=True)`
        subprocess.check_call(cmd)
        files = os.listdir(".")
        archive_name = next(x for x in files if x.startswith('data.tar'))
        cmd = ["tar", "xf", archive_name]
        subprocess.check_call(cmd)
        # pandoc and pandoc-citeproc are in ./usr/bin subfolder
        for exe in ["pandoc", "pandoc-citeproc"]:
            src = os.path.join(tempfolder, "usr", "bin", exe)
            dst = os.path.join(targetfolder, exe)
            print("* Copying %s to %s ..." % (exe, targetfolder))
            shutil.copyfile(src, dst)
            _make_executable(dst)
        src = os.path.join(tempfolder, "usr", "share", "doc", "pandoc", "copyright")
        dst = os.path.join(targetfolder, "copyright.pandoc")
        print("* Copying copyright to %s ..." % (targetfolder))
        shutil.copyfile(src, dst)
    finally:
        os.chdir(cur_wd)
        shutil.rmtree(tempfolder)


def _handle_darwin(filename, targetfolder):
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
        _make_executable(dst)

    # remove temporary dir
    shutil.rmtree(tempfolder)
    print("* Done.")


def _handle_win32(filename, targetfolder):
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


def download_pandoc(url=None, targetfolder=None, version="latest", quiet=False, delete_installer=False, download_folder=None):
    """Download and unpack pandoc

    Downloads prebuild binaries for pandoc from `url` and unpacks it into
    `targetfolder`.

    :param str url: URL for the to be downloaded pandoc binary distribution for
        the platform under which this python runs. If no `url` is give, uses
        the latest available release at the time pypandoc was released.

    :param str targetfolder: directory, where the binaries should be installed
        to. If no `targetfolder` is given, uses a platform specific user
        location: `~/bin` on Linux, `~/Applications/pandoc` on Mac OS X, and
        `~\\AppData\\Local\\Pandoc` on Windows.

    :param str download_folder: Directory, where the installer should download files before unpacking
        to the target folder. If no `download_folder` is given, uses the current directory. example: `/tmp/`, `/tmp`
    """
    if quiet:
        sys.stdout = open(os.devnull, 'w')

    pf = sys.platform

    if url is None:
        # compatibility with py3
        if pf.startswith("linux"):
            pf = "linux"
            if platform.architecture()[0] != "64bit":
                raise RuntimeError("Linux pandoc is only compiled for 64bit.")

        # get pandoc_urls
        pandoc_urls, _ = _get_pandoc_urls(version)
        if pf not in pandoc_urls:
            raise RuntimeError("Can't handle your platform (only Linux, Mac OS X, Windows).")

        url = pandoc_urls[pf]

    filename = url.split("/")[-1]

    if download_folder is not None:
        if download_folder.endswith('/'):
            download_folder = download_folder[:-1]

        filename = os.path.expanduser(download_folder) + '/' + filename

    if os.path.isfile(filename):
        print("* Using already downloaded file %s" % (filename))
    else:
        print("* Downloading pandoc from %s ..." % url)
        # https://stackoverflow.com/questions/30627937/tracebaclk-attributeerroraddinfourl-instance-has-no-attribute-exit
        response = urlopen(url)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    if targetfolder is None:
        targetfolder = DEFAULT_TARGET_FOLDER[pf]
    targetfolder = os.path.expanduser(targetfolder)

    # Make sure target folder exists...
    try:
        os.makedirs(targetfolder)
    except OSError:
        pass  # dir already exists...

    unpack = globals().get("_handle_" + pf)
    assert unpack is not None, "Can't handle download, only Linux, Windows and OS X are supported."

    unpack(filename, targetfolder)
    if delete_installer:
        os.remove(filename)
    if quiet:
        sys.stdout = sys.__stdout__
