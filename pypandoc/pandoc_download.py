import json
import os
import os.path
import platform
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Union

from .handler import _check_log_handler, logger

DEFAULT_TARGET_FOLDER = {
    "win32": "~\\AppData\\Local\\Pandoc",
    "linux": "~/bin",
    "darwin": "~/Applications/pandoc",
}


class _NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Strips Authorization header on cross-domain redirects.

    GitHub redirects release asset downloads to S3/Azure presigned URLs.
    If the Authorization header is forwarded, the storage backend rejects
    the request (403) due to conflicting auth mechanisms.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req is not None:
            original_host = urllib.parse.urlparse(req.full_url).hostname
            redirect_host = urllib.parse.urlparse(newurl).hostname
            if original_host != redirect_host:
                new_req.remove_header("Authorization")
        return new_req


def _urlopen_with_retry(url, max_retries=5, backoff_factor=1.0, max_backoff=60.0):
    """Open a URL with exponential backoff retry on 429 and 5xx errors.

    If a GITHUB_TOKEN environment variable is set, it will be used to
    authenticate requests to github.com, raising the rate limit from
    60 req/hr (shared by IP) to 1,000 req/hr (per-repo).
    """
    github_token = os.environ.get("GITHUB_TOKEN", "")

    if isinstance(url, str):
        req = urllib.request.Request(url)
    else:
        req = url

    # Add auth header for github.com requests when token is available
    hostname = urllib.parse.urlparse(req.full_url).hostname or ""
    is_github = hostname in {"github.com", "api.github.com"}
    if github_token and is_github:
        req.add_header("Authorization", f"token {github_token}")

    # Use custom opener that strips auth on cross-domain redirects
    opener = urllib.request.build_opener(_NoAuthRedirectHandler)

    for attempt in range(max_retries + 1):
        try:
            return opener.open(req)
        except urllib.error.HTTPError as e:
            if e.code == 429 or (500 <= e.code < 600):
                if attempt == max_retries:
                    raise
                # Respect Retry-After header if present
                retry_after = e.headers.get("Retry-After")
                if retry_after is not None:
                    try:
                        wait = int(retry_after)
                    except ValueError:
                        wait = backoff_factor * (2**attempt)
                else:
                    wait = backoff_factor * (2**attempt)
                wait = min(wait, max_backoff)
                wait += random.uniform(0, 1)  # jitter to avoid thundering herd
                logger.info(
                    f"HTTP {e.code} for {req.full_url}, "
                    f"retrying in {wait:.1f}s (attempt {attempt + 1}/{max_retries})..."
                )
                time.sleep(wait)
            else:
                raise


def _get_pandoc_urls(version="latest"):
    """Get the urls of pandoc's binaries
    Uses the GitHub API to fetch release assets instead of scraping HTML.
    Uses sys.platform keys, but removes the 2 from linux2
    Adding a new platform means implementing unpacking in "DownloadPandocCommand"
    and adding the URL here

    :param str version: pandoc version.
        Valid values are either a valid pandoc version e.g. "1.19.1", or "latest"
        Default: "latest".

    :return: str pandoc_urls: a dictionary with keys as system platform
        and values as the url pointing to respective binaries

    :return: str version: actual pandoc version.
        (e.g. "latest" will be resolved to the actual one)
    """
    # Use GitHub API instead of scraping HTML release pages
    url = (
        "https://api.github.com/repos/jgm/pandoc/releases/"
        + ("tags/" if version != "latest" else "")
        + version
    )
    # try to open the url
    try:
        response = _urlopen_with_retry(url)
    except urllib.error.HTTPError:
        raise RuntimeError(f"Invalid pandoc version {version}.")
    # read json response
    data = json.loads(response.read())
    # regex for the binaries
    uname = platform.uname()[4]
    processor_architecture = (
        "arm" if uname.startswith("arm") or uname.startswith("aarch") else "amd"
    )
    regex = re.compile(
        rf"/jgm/pandoc/releases/download/.*"
        rf"(?:{processor_architecture}|x86|mac).*\.(?:msi|deb|pkg)"
    )
    # actual pandoc version
    version = data["tag_name"]
    # dict that lookup the platform from binary extension
    ext2platform = {"msi": "win32", "deb": "linux", "pkg": "darwin"}
    # collect pandoc urls from json content
    pandoc_urls = {}
    for asset in data["assets"]:
        download_url = asset["browser_download_url"]
        if regex.match(urllib.parse.urlparse(download_url).path):
            ext = asset["name"][-3:]
            if ext in ext2platform:
                pandoc_urls[ext2platform[ext]] = download_url
    return pandoc_urls, version


def _make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    logger.info(f"Making {path} executable...")
    os.chmod(path, mode)


def _handle_linux(filename, targetfolder):
    logger.info(f"Unpacking {filename} to tempfolder...")

    tempfolder = tempfile.mkdtemp()
    cur_wd = os.getcwd()
    filename = os.path.abspath(filename)
    try:
        os.chdir(tempfolder)
        cmd = ["ar", "x", filename]
        # if only 3.5 is supported, should be `run(..., check=True)`
        subprocess.check_call(cmd)
        files = os.listdir(".")
        archive_name = next(x for x in files if x.startswith("data.tar"))
        cmd = ["tar", "xf", archive_name]
        subprocess.check_call(cmd)
        # pandoc and pandoc-citeproc are in ./usr/bin subfolder
        exe = "pandoc"
        src = os.path.join(tempfolder, "usr", "bin", exe)
        dst = os.path.join(targetfolder, exe)
        logger.info(f"Copying {exe} to {targetfolder} ...")
        shutil.copyfile(src, dst)
        _make_executable(dst)
        exe = "pandoc-citeproc"
        src = os.path.join(tempfolder, "usr", "bin", exe)
        dst = os.path.join(targetfolder, exe)
        if os.path.exists(src):
            logger.info(f"Copying {exe} to {targetfolder} ...")
            shutil.copyfile(src, dst)
            _make_executable(dst)
        src = os.path.join(tempfolder, "usr", "share", "doc", "pandoc", "copyright")
        dst = os.path.join(targetfolder, "copyright.pandoc")
        logger.info(f"Copying copyright to {targetfolder} ...")
        shutil.copyfile(src, dst)
    finally:
        os.chdir(cur_wd)
        shutil.rmtree(tempfolder)


def _handle_darwin(filename, targetfolder):
    logger.info(f"Unpacking {filename} to tempfolder...")

    tempfolder = tempfile.mkdtemp()

    pkgutilfolder = os.path.join(tempfolder, "tmp")
    cmd = ["pkgutil", "--expand", filename, pkgutilfolder]
    # if only 3.5 is supported, should be `run(..., check=True)`
    subprocess.check_call(cmd)

    # this will generate usr/local/bin below the dir
    cmd = [
        "tar",
        "xvf",
        os.path.join(pkgutilfolder, "pandoc.pkg", "Payload"),
        "-C",
        pkgutilfolder,
    ]
    subprocess.check_call(cmd)

    # pandoc and pandoc-citeproc are in the ./usr/local/bin subfolder

    exe = "pandoc"
    src = os.path.join(pkgutilfolder, "usr", "local", "bin", exe)
    dst = os.path.join(targetfolder, exe)
    logger.info(f"Copying {exe} to {targetfolder} ...")
    shutil.copyfile(src, dst)
    _make_executable(dst)

    exe = "pandoc-citeproc"
    src = os.path.join(pkgutilfolder, "usr", "local", "bin", exe)
    dst = os.path.join(targetfolder, exe)
    if os.path.exists(src):
        logger.info(f"Copying {exe} to {targetfolder} ...")
        shutil.copyfile(src, dst)
        _make_executable(dst)

    # remove temporary dir
    shutil.rmtree(tempfolder)
    logger.info("Done.")


def _handle_win32(filename, targetfolder):
    logger.info(f"Unpacking {filename} to tempfolder...")

    tempfolder = tempfile.mkdtemp()

    cmd = ["msiexec", "/a", filename, "/qb", "TARGETDIR=%s" % (tempfolder)]
    # if only 3.5 is supported, should be `run(..., check=True)`
    subprocess.check_call(cmd)

    # pandoc.exe, pandoc-citeproc.exe, and the COPYRIGHT are in the Pandoc subfolder

    exe = "pandoc.exe"
    src = os.path.join(tempfolder, "Pandoc", exe)
    dst = os.path.join(targetfolder, exe)
    logger.info(f"Copying {exe} to {targetfolder} ...")
    shutil.copyfile(src, dst)

    exe = "pandoc-citeproc.exe"
    src = os.path.join(tempfolder, "Pandoc", exe)
    dst = os.path.join(targetfolder, exe)
    if os.path.exists(src):
        logger.info(f"Copying {exe} to {targetfolder} ...")
        shutil.copyfile(src, dst)

    exe = "COPYRIGHT.txt"
    src = os.path.join(tempfolder, "Pandoc", exe)
    dst = os.path.join(targetfolder, exe)
    logger.info(f"Copying {exe} to {targetfolder} ...")
    shutil.copyfile(src, dst)

    # remove temporary dir
    shutil.rmtree(tempfolder)
    logger.info("Done.")


def download_pandoc(
    url: Union[str, None] = None,
    targetfolder: Union[str, None] = None,
    version: str = "latest",
    delete_installer: bool = False,
    download_folder: Union[str, None] = None,
) -> None:
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

    :param str download_folder: Directory where the installer should download files
        before unpacking to the target folder. If no `download_folder` is given,
        uses the current directory. example: `/tmp/`, `/tmp`
    """

    _check_log_handler()

    pf = sys.platform

    if url is None:
        # compatibility with py3
        if pf.startswith("linux"):
            pf = "linux"
            arch = platform.architecture()[0]
            if arch != "64bit":
                raise RuntimeError(
                    f"Linux pandoc is only compiled for 64bit. Got arch={arch}."
                )

        # get pandoc_urls
        pandoc_urls, _ = _get_pandoc_urls(version)
        if pf not in pandoc_urls:
            raise RuntimeError(
                "Can't handle your platform (only Linux, Mac OS X, Windows)."
            )

        url = pandoc_urls[pf]

    filename = url.split("/")[-1]

    if download_folder is not None:
        if download_folder.endswith("/"):
            download_folder = download_folder[:-1]

        filename = os.path.join(os.path.expanduser(download_folder), filename)

    if os.path.isfile(filename):
        logger.info(f"Using already downloaded file {filename}")
    else:
        logger.info(f"Downloading pandoc from {url} ...")
        # https://stackoverflow.com/questions/30627937/
        response = _urlopen_with_retry(url)
        with open(filename, "wb") as out_file:
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
    assert (
        unpack is not None
    ), "Can't handle download, only Linux, Windows and OS X are supported."

    unpack(filename, targetfolder)
    if delete_installer:
        os.remove(filename)
