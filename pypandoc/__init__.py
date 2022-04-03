# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import logging
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import warnings

from .handler import _check_log_handler
from .pandoc_download import DEFAULT_TARGET_FOLDER, download_pandoc
from .py3compat import cast_bytes, cast_unicode, string_types, url2path, urlparse

__author__ = u'Juho Vepsäläinen'
__version__ = '1.7.5'
__license__ = 'MIT'
__all__ = ['convert', 'convert_file', 'convert_text',
           'get_pandoc_formats', 'get_pandoc_version', 'get_pandoc_path',
           'download_pandoc']

# Set up the module level logger
logger = logging.getLogger(__name__)


def convert(source, to, format=None, extra_args=(), encoding='utf-8',
            outputfile=None, filters=None, cworkdir=None):
    """Converts given `source` from `format` to `to` (deprecated).

    :param str source: Unicode string or bytes or a file path (see encoding)

    :param str to: format into which the input should be converted; can be one of
            `pypandoc.get_pandoc_formats()[1]`

    :param str format: the format of the inputs; will be inferred if input is a file with an
            known filename extension; can be one of `pypandoc.get_pandoc_formats()[1]`
            (Default value = None)

    :param list extra_args: extra arguments (list of strings) to be passed to pandoc
            (Default value = ())

    :param str encoding: the encoding of the file or the input bytes (Default value = 'utf-8')

    :param str outputfile: output will be written to outfilename or the converted content
            returned if None (Default value = None)

    :param list filters: pandoc filters e.g. filters=['pandoc-citeproc']

    :returns: converted string (unicode) or an empty string if an outputfile was given
    :rtype: unicode

    :raises RuntimeError: if any of the inputs are not valid of if pandoc fails with an error
    :raises OSError: if pandoc is not found; make sure it has been installed and is available at
            path.
    """
    msg = ("Due to possible ambiguity, 'convert()' is deprecated and will be removed in pypandoc 1.8. "
           "Use 'convert_file()'  or 'convert_text()'.")
    warnings.warn(msg, DeprecationWarning, stacklevel=2)

    path = _identify_path(source)
    if path:
        format = _identify_format_from_path(source, format)
        input_type = 'path'
    else:
        source = _as_unicode(source, encoding)
        input_type = 'string'
        if not format:
            raise RuntimeError("Format missing, but need one (identified source as text as no "
                               "file with that name was found).")
    return _convert_input(source, format, input_type, to, extra_args=extra_args,
                          outputfile=outputfile, filters=filters,
                          cworkdir=cworkdir)


def convert_text(source, to, format, extra_args=(), encoding='utf-8',
                 outputfile=None, filters=None, verify_format=True,
                 sandbox=True, cworkdir=None):
    """Converts given `source` from `format` to `to`.

    :param str source: Unicode string or bytes (see encoding)

    :param str to: format into which the input should be converted; can be one of
            `pypandoc.get_pandoc_formats()[1]`

    :param str format: the format of the inputs; can be one of `pypandoc.get_pandoc_formats()[1]`

    :param list extra_args: extra arguments (list of strings) to be passed to pandoc
            (Default value = ())

    :param str encoding: the encoding of the input bytes (Default value = 'utf-8')

    :param str outputfile: output will be written to outfilename or the converted content
            returned if None (Default value = None)

    :param list filters: pandoc filters e.g. filters=['pandoc-citeproc']

    :param bool verify_format: Verify from and to format before converting. Should only be set False when confident of the formats and performance is an issue.
            (Default value = True)

    :param bool sandbox: Run pandoc in pandocs own sandbox mode, limiting IO operations in readers and writers to reading the files specified on the command line. Anyone using pandoc on untrusted user input should use this option. Note: This only does something, on pandoc >= 2.15
            (Default value = True)

    :returns: converted string (unicode) or an empty string if an outputfile was given
    :rtype: unicode

    :raises RuntimeError: if any of the inputs are not valid of if pandoc fails with an error
    :raises OSError: if pandoc is not found; make sure it has been installed and is available at
            path.
    """
    source = _as_unicode(source, encoding)
    return _convert_input(source, format, 'string', to, extra_args=extra_args,
                          outputfile=outputfile, filters=filters,
                          verify_format=verify_format, sandbox=sandbox,
                          cworkdir=cworkdir)


def convert_file(source_file, to, format=None, extra_args=(), encoding='utf-8',
                 outputfile=None, filters=None, verify_format=True,
                 sandbox=True, cworkdir=None):
    """Converts given `source` from `format` to `to`.

    :param str source_file: file path (see encoding)

    :param str to: format into which the input should be converted; can be one of
            `pypandoc.get_pandoc_formats()[1]`

    :param str format: the format of the inputs; will be inferred from the source_file with an
            known filename extension; can be one of `pypandoc.get_pandoc_formats()[1]`
            (Default value = None)

    :param list extra_args: extra arguments (list of strings) to be passed to pandoc
            (Default value = ())

    :param str encoding: the encoding of the file or the input bytes (Default value = 'utf-8')

    :param str outputfile: output will be written to outfilename or the converted content
            returned if None (Default value = None)

    :param list filters: pandoc filters e.g. filters=['pandoc-citeproc']

    :param bool verify_format: Verify from and to format before converting. Should only be set False when confident of the formats and performance is an issue.
            (Default value = True)

    :param bool sandbox: Run pandoc in pandocs own sandbox mode, limiting IO operations in readers and writers to reading the files specified on the command line. Anyone using pandoc on untrusted user input should use this option. Note: This only does something, on pandoc >= 2.15
            (Default value = True)

    :returns: converted string (unicode) or an empty string if an outputfile was given
    :rtype: unicode

    :raises RuntimeError: if any of the inputs are not valid of if pandoc fails with an error
    :raises OSError: if pandoc is not found; make sure it has been installed and is available at
            path.
    """
    if not _identify_path(source_file):
        raise RuntimeError("source_file is not a valid path")
    format = _identify_format_from_path(source_file, format)
    return _convert_input(source_file, format, 'path', to, extra_args=extra_args,
                          outputfile=outputfile, filters=filters,
                          verify_format=verify_format, sandbox=sandbox,
                          cworkdir=cworkdir)


def _identify_path(source):
    # guard against problems
    if source is None or not isinstance(source, string_types):
        return False

    is_path = False
    try:
        is_path = os.path.exists(source)
    except UnicodeEncodeError:
        is_path = os.path.exists(source.encode('utf-8'))
    except:  # noqa
        # still false
        pass

    if not is_path:
        # check if it's an URL
        result = urlparse(source)
        if result.scheme in ["http", "https"]:
            is_path = True
        elif result.scheme and result.netloc and result.path:
            # complete uri including one with a network path
            is_path = True
        elif result.scheme == "file" and result.path:
            is_path = os.path.exists(url2path(source))

    return is_path


def _identify_format_from_path(sourcefile, format):
    return format or os.path.splitext(sourcefile)[1].strip('.')


def _as_unicode(source, encoding):
    if encoding != 'utf-8':
        # if a source and a different encoding is given, try to decode the the source into a
        # unicode string
        try:
            source = cast_unicode(source, encoding=encoding)
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    return source


def _identify_input_type(source, format, encoding='utf-8'):
    path = _identify_path(source)
    if path:
        format = _identify_format_from_path(source, format)
        input_type = 'path'
    else:
        source = _as_unicode(source, encoding)
        input_type = 'string'
    return source, format, input_type


def normalize_format(fmt):
    formats = {
        'dbk': 'docbook',
        'md': 'markdown',
        'tex': 'latex',
    }
    fmt = formats.get(fmt, fmt)
    # rst format can have extensions
    if fmt[:4] == "rest":
        fmt = "rst" + fmt[4:]
    return fmt


def _validate_formats(format, to, outputfile):

    format = normalize_format(format)
    to = normalize_format(to)

    if not format:
        raise RuntimeError('Missing format!')

    from_formats, to_formats = get_pandoc_formats()

    if _get_base_format(format) not in from_formats:
        raise RuntimeError(
            'Invalid input format! Got "%s" but expected one of these: %s' % (
                _get_base_format(format), ', '.join(from_formats)))

    base_to_format = _get_base_format(to)

    file_extension = os.path.splitext(to)[1]

    if (base_to_format not in to_formats and
            base_to_format != "pdf" and  # pdf is handled later # noqa: E127
            file_extension != '.lua'):
        raise RuntimeError(
            'Invalid output format! Got %s but expected one of these: %s' % (
                base_to_format, ', '.join(to_formats)))

    # list from https://github.com/jgm/pandoc/blob/master/pandoc.hs
    # `[...] where binaries = ["odt","docx","epub","epub3"] [...]`
    # pdf has the same restriction
    if base_to_format in ["odt", "docx", "epub", "epub3", "pdf"] and not outputfile:
        raise RuntimeError(
            'Output to %s only works by using a outputfile.' % base_to_format
        )

    if base_to_format == "pdf":
        # pdf formats needs to actually have a to format of latex and a
        # filename with an ending pf .pdf
        if outputfile[-4:] != ".pdf":
            raise RuntimeError('PDF output needs an outputfile with ".pdf" as a fileending.')
        # to is not allowed to contain pdf, but must point to latex
        # it's also not allowed to contain extensions according to the docs
        if to != base_to_format:
            raise RuntimeError("PDF output can't contain any extensions: %s" % to)
        to = "latex"

    return format, to


def _convert_input(source, format, input_type, to, extra_args=(),
                   outputfile=None, filters=None, verify_format=True,
                   sandbox=True, cworkdir=None):
    
    _check_log_handler()
    _ensure_pandoc_path()

    if verify_format:
        format, to = _validate_formats(format, to, outputfile)
    else:
        format = normalize_format(format)
        to = normalize_format(to)

    string_input = input_type == 'string'
    input_file = [source] if not string_input else []
    args = [__pandoc_path, '--from=' + format]

    args.append('--to=' + to)

    args += input_file

    if outputfile:
        args.append("--output=" + outputfile)

    if sandbox:
        if ensure_pandoc_minimal_version(2,15): # sandbox was introduced in pandoc 2.15, so only add if we are using 2.15 or above.
            args.append("--sandbox")

    args.extend(extra_args)

    # adds the proper filter syntax for each item in the filters list
    if filters is not None:
        if isinstance(filters, string_types):
            filters = filters.split()
        f = ['--filter=' + x for x in filters]
        args.extend(f)

    # To get access to pandoc-citeproc when we use a included copy of pandoc,
    # we need to add the pypandoc/files dir to the PATH
    new_env = os.environ.copy()
    files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")
    new_env["PATH"] = new_env.get("PATH", "") + os.pathsep + files_path
    creation_flag = 0x08000000 if sys.platform == "win32" else 0 # set creation flag to not open pandoc in new console on windows

    old_wd = os.getcwd()
    if cworkdir and old_wd != cworkdir:
        os.chdir(cworkdir)

    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE if string_input else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=new_env,
        creationflags=creation_flag)

    if cworkdir is not None:
        os.chdir(old_wd)

    # something else than 'None' indicates that the process already terminated
    if not (p.returncode is None):
        raise RuntimeError(
            'Pandoc died with exitcode "%s" before receiving input: %s' % (p.returncode,
                                                                           p.stderr.read())
        )

    try:
        source = cast_bytes(source, encoding='utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        # assume that it is already a utf-8 encoded string
        pass
    try:
        stdout, stderr = p.communicate(source if string_input else None)
    except OSError:
        # this is happening only on Py2.6 when pandoc dies before reading all
        # the input. We treat that the same as when we exit with an error...
        raise RuntimeError('Pandoc died with exitcode "%s" during conversion.' % (p.returncode))

    try:
        stdout = stdout.decode('utf-8')
    except UnicodeDecodeError:
        # this shouldn't happen: pandoc more or less guarantees that the output is utf-8!
        raise RuntimeError('Pandoc output was not utf-8.')
           
    try:
        stderr = stderr.decode('utf-8')
    except UnicodeDecodeError:
        # this shouldn't happen: pandoc more or less guarantees that the output is utf-8!
        raise RuntimeError('Pandoc output was not utf-8.')

    # check that pandoc returned successfully
    if p.returncode != 0:
        raise RuntimeError(
            'Pandoc died with exitcode "%s" during conversion: %s' % (p.returncode, stderr)
        )
    
    # if there is output on stderr, process it and send to logger
    if stderr:
        for level, msg in _classify_pandoc_logging(stderr):
            logger.log(level, msg)

    # if there is an outputfile, then stdout is likely empty!
    return stdout


def _classify_pandoc_logging(raw, default_level="WARNING"):
    # Process raw and yeild the contained logging levels and messages.
    # Assumes that the messages are formatted like "[LEVEL] message". If the 
    # first message does not have a level, use the default_level value instead.
    
    level_map = {"CRITICAL": 50,
                 "ERROR": 40,
                 "WARNING": 30,
                 "INFO": 20,
                 "DEBUG": 10,
                 "NOTSET": 0}
    
    msgs = raw.split("\n")
    first = msgs.pop(0)
    
    search = re.search(r"\[(.*?)\]", first)
    
    # Use the default if the first message doesn't have a level
    if search is None:
        level = default_level
    else:
        level = first[search.start(1):search.end(1)]
    
    log_msgs = [first.replace('[{}] '.format(level), '')]
    
    for msg in msgs:
        
        search = re.search(r"\[(.*?)\]", msg)
        
        if search is not None:
            yield level_map[level], "\n".join(log_msgs)
            level = msg[search.start(1):search.end(1)]
            log_msgs = [msg.replace('[{}] '.format(level), '')]
            continue
        
        log_msgs.append(msg)
    
    yield level_map[level], "\n".join(log_msgs)


def _get_base_format(format):
    '''
    According to http://johnmacfarlane.net/pandoc/README.html#general-options,
    syntax extensions for markdown can be individually enabled or disabled by
    appending +EXTENSION or -EXTENSION to the format name.
    Return the base format without any extensions.
    '''
    return re.split(r'\+|-', format)[0]


def get_pandoc_formats():
    '''
    Dynamic preprocessor for Pandoc formats.
    Return 2 lists. "from_formats" and "to_formats".
    '''
    _ensure_pandoc_path()
    creation_flag = 0x08000000 if sys.platform == "win32" else 0 # set creation flag to not open pandoc in new console on windows
    p = subprocess.Popen(
        [__pandoc_path, '--list-output-formats'],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        creationflags=creation_flag)

    comm = p.communicate()
    out = comm[0].decode().splitlines(False)
    if p.returncode != 0:
        # try the old version and see if that returns something
        return get_pandoc_formats_pre_1_18()

    p = subprocess.Popen(
        [__pandoc_path, '--list-input-formats'],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        creationflags=creation_flag)

    comm = p.communicate()
    in_ = comm[0].decode().splitlines(False)

    return [f.strip() for f in in_], [f.strip() for f in out]


def get_pandoc_formats_pre_1_18():
    '''
    Dynamic preprocessor for Pandoc formats for version < 1.18.
    Return 2 lists. "from_formats" and "to_formats".
    '''
    _ensure_pandoc_path()
    creation_flag = 0x08000000 if sys.platform == "win32" else 0 # set creation flag to not open pandoc in new console on windows
    p = subprocess.Popen(
        [__pandoc_path, '-h'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        creationflags=creation_flag)

    comm = p.communicate()
    help_text = comm[0].decode().splitlines(False)
    if p.returncode != 0 or 'Options:' not in help_text:
        raise RuntimeError("Couldn't call pandoc to get output formats. Output from pandoc:\n%s" %
                           str(comm))
    txt = ' '.join(help_text[1:help_text.index('Options:')])

    aux = txt.split('Output formats: ')
    in_ = re.sub(r'Input\sformats:\s|\*|\[.*?\]', '', aux[0]).split(',')
    out = re.sub(r'\*|\[.*?\]', '', aux[1]).split(',')

    return [f.strip() for f in in_], [f.strip() for f in out]


# copied and adapted from jupyter_nbconvert/utils/pandoc.py, Modified BSD License

def _get_pandoc_version(pandoc_path):
    new_env = os.environ.copy()
    creation_flag = 0x08000000 if sys.platform == "win32" else 0 # set creation flag to not open pandoc in new console on windows
    if 'HOME' not in os.environ:
        new_env['HOME'] = tempfile.gettempdir()
    p = subprocess.Popen(
        [pandoc_path, '--version'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env=new_env,
        creationflags=creation_flag)
    comm = p.communicate()
    out_lines = comm[0].decode().splitlines(False)
    if p.returncode != 0 or len(out_lines) == 0:
        raise RuntimeError("Couldn't call pandoc to get version information. Output from "
                           "pandoc:\n%s" % str(comm))

    version_pattern = re.compile(r"^\d+(\.\d+){1,}$")
    for tok in out_lines[0].split():
        if version_pattern.match(tok):
            version = tok
            break
    return version


def get_pandoc_version():
    """Gets the Pandoc version if Pandoc is installed.

    It will probe Pandoc for its version, cache it and return that value. If a cached version is
    found, it will return the cached version and stop probing Pandoc
    (unless :func:`clean_version_cache()` is called).

    :raises OSError: if pandoc is not found; make sure it has been installed and is available at
            path.
    """
    global __version

    if __version is None:
        _ensure_pandoc_path()
        __version = _get_pandoc_version(__pandoc_path)
    return __version


def get_pandoc_path():
    """Gets the Pandoc path if Pandoc is installed.

    It will return a path to pandoc which is used by pypandoc.

    This might be a full path or, if pandoc is on PATH, simple `pandoc`. It's guaranteed
    to be callable (i.e. we could get version information from `pandoc --version`).
    If `PYPANDOC_PANDOC` is set and valid, it will return that value. If the environment
    variable is not set, either the full path to the included pandoc or the pandoc in
    `PATH` or a pandoc in some of the more usual (platform specific) install locations
    (whatever is the higher version) will be returned.

    If a cached path is found, it will return the cached path and stop probing Pandoc
    (unless :func:`clean_pandocpath_cache()` is called).

    :raises OSError: if pandoc is not found
    """
    _ensure_pandoc_path()
    return __pandoc_path

def ensure_pandoc_minimal_version(major, minor=0):
    """Check if the used pandoc fulfill a minimal version requirement.

    :param bool major: pandoc major version, such as 1 or 2.

    :param bool minor: pandoc minor version, such as 10 or 11.

    :returns: True if the installed pandoc is above the minimal version, False otherwise.
    :rtype: bool
    """
    version = [int(x) for x in get_pandoc_version().split(".")]
    if version[0] > int(major): # if we have pandoc2 but major is request to be 1
        return True
    return version[0] >= int(major) and version[1] >= int(minor)
    


def ensure_pandoc_maximal_version(major, minor=9999):
    """Check if the used pandoc fulfill a maximal version requirement.

    :param bool major: pandoc major version, such as 1 or 2.

    :param bool minor: pandoc minor version, such as 10 or 11.

    :returns: True if the installed pandoc is below the maximal version, False otherwise.
    :rtype: bool
    """
    version = [int(x) for x in get_pandoc_version().split(".")]
    if version[0] < int(major): # if we have pandoc1 but major is request to be 2
        return True
    return version[0] <= int(major) and version[1] <= int(minor)


def _ensure_pandoc_path():
    global __pandoc_path
    
    _check_log_handler()
    
    if __pandoc_path is None:
        included_pandoc = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       "files", "pandoc")
        search_paths = ["pandoc", included_pandoc]
        pf = "linux" if sys.platform.startswith("linux") else sys.platform
        try:
            search_paths.append(os.path.join(DEFAULT_TARGET_FOLDER[pf], "pandoc"))
        except:  # noqa
            # not one of the know platforms...
            pass
        if pf == "linux":
            # Currently we install into ~/bin, but this is equally likely...
            search_paths.append("~/.bin/pandoc")
        # Also add the interpreter script path, as that's where pandoc could be
        # installed if it's an environment and the environment wasn't activated
        if pf == "win32":
            search_paths.append(os.path.join(sys.exec_prefix, "Scripts", "pandoc"))

            # Since this only runs on Windows, use Windows slashes
            if os.getenv('ProgramFiles', None):
                search_paths.append(os.path.expandvars("${ProgramFiles}\\Pandoc\\Pandoc"))
            if os.getenv('ProgramFiles(x86)', None):
                search_paths.append(os.path.expandvars("${ProgramFiles(x86)}\\Pandoc\\Pandoc"))

        # bin can also be used on windows (conda at least has it in path), so
        # include it unconditionally
        search_paths.append(os.path.join(sys.exec_prefix, "bin", "pandoc"))
        # If a user added the complete path to pandoc to an env, use that as the
        # only way to get pandoc so that a user can overwrite even a higher
        # version in some other places.
        if os.getenv('PYPANDOC_PANDOC', None):
            search_paths = [os.getenv('PYPANDOC_PANDOC')]
        curr_version = [0, 0, 0]
        for path in search_paths:
            # Needed for windows and subprocess which can't expand it on it's
            # own...
            path = os.path.expanduser(path)
            version_string = "0.0.0"
            # print("Trying: %s" % path)
            try:
                version_string = _get_pandoc_version(path)
            except Exception:
                # we can't use that path...
                if os.path.exists(path):
                    # path exist but is not useable -> not executable?
                    log_msg = ("Found {}, but not using it because of an "
                               "error:".format(path))
                    logging.exception(log_msg)
                continue
            version = [int(x) for x in version_string.split(".")]
            while len(version) < len(curr_version):
                version.append(0)
            # print("%s, %s" % (path, version))
            # Only use the new version if it is any bigger...
            if version > curr_version:
                # print("Found: %s" % path)
                __pandoc_path = path
                curr_version = version

        if __pandoc_path is None:
            # Only print hints if requested
            if os.path.exists('/usr/local/bin/brew'):
                logger.info(textwrap.dedent("""\
                    Maybe try:

                        brew install pandoc
                """))
            elif os.path.exists('/usr/bin/apt-get'):
                logger.info(textwrap.dedent("""\
                    Maybe try:

                        sudo apt-get install pandoc
                """))
            elif os.path.exists('/usr/bin/yum'):
                logger.info(textwrap.dedent("""\
                    Maybe try:

                    sudo yum install pandoc
                """))
            logger.info(textwrap.dedent("""\
                See http://johnmacfarlane.net/pandoc/installing.html
                for installation options
            """))
            logger.info(textwrap.dedent("""\
                ---------------------------------------------------------------

            """))
            raise OSError("No pandoc was found: either install pandoc and add it\n"
                          "to your PATH or or call pypandoc.download_pandoc(...) or\n"
                          "install pypandoc wheels with included pandoc.")


def ensure_pandoc_installed(url=None, 
                            targetfolder=None,
                            version="latest",
                            quiet=None,
                            delete_installer=False):
    """Try to install pandoc if it isn't installed.

    Parameters are passed to download_pandoc()

    :raises OSError: if pandoc cannot be installed
    """

    if quiet is not None:
        msg = ("The quiet flag in PyPandoc has been deprecated in favour of "
               "logging. See README.md for more information.")
        warnings.warn(msg, DeprecationWarning, stacklevel=2)

    # Append targetfolder to the PATH environment variable so it is found by subprocesses
    if targetfolder is not None:
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + os.path.abspath(os.path.expanduser(targetfolder))

    try:
        _ensure_pandoc_path()

    except OSError:
        download_pandoc(url=url,
                        targetfolder=targetfolder,
                        version=version,
                        delete_installer=delete_installer)

        # Show errors in case of secondary failure
        _ensure_pandoc_path()


# -----------------------------------------------------------------------------
# Internal state management
# -----------------------------------------------------------------------------
def clean_version_cache():
    global __version
    __version = None


def clean_pandocpath_cache():
    global __pandoc_path
    __pandoc_path = None


__version = None
__pandoc_path = None
