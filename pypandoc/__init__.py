# -*- coding: utf-8 -*-
from __future__ import with_statement, absolute_import

import subprocess
import sys
import textwrap
import os
import re

from .py3compat import string_types, cast_bytes, cast_unicode

__author__ = 'Juho Vepsäläinen'
__version__ = '1.0.5'
__license__ = 'MIT'
__all__ = ['convert', 'get_pandoc_formats']


def convert(source, to, format=None, extra_args=(), encoding='utf-8',
            outputfile=None, filters=None):
    """Converts given `source` from `format` `to` another.

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
    return _convert(_read_file, _process_file, source, to,
                    format, extra_args, encoding=encoding,
                    outputfile=outputfile, filters=filters)


def _convert(reader, processor, source, to, format=None, extra_args=(), encoding=None,
             outputfile=None, filters=None):
    source, format, input_type = reader(source, format, encoding=encoding)

    formats = {
        'dbk': 'docbook',
        'md': 'markdown',
        'rest': 'rst',
        'tex': 'latex',
    }

    format = formats.get(format, format)
    to = formats.get(to, to)

    if not format:
        raise RuntimeError('Missing format!')

    from_formats, to_formats = get_pandoc_formats()

    if _get_base_format(format) not in from_formats:
        raise RuntimeError(
            'Invalid input format! Got "%s" but expected one of these: %s' % (
                _get_base_format(format), ', '.join(from_formats)))

    base_to_format = _get_base_format(to)
    if base_to_format not in to_formats:
        raise RuntimeError(
            'Invalid output format! Expected one of these: ' +
            ', '.join(to_formats))

    # list from https://github.com/jgm/pandoc/blob/master/pandoc.hs
    # `[...] where binaries = ["odt","docx","epub","epub3"] [...]`
    if base_to_format in ["odt", "docx", "epub", "epub3"] and not outputfile:
        raise RuntimeError(
            'Output to %s only works by using a outputfile.' % base_to_format
        )

    return processor(source, input_type, to, format, extra_args,
                     outputfile=outputfile, filters=filters)


def _read_file(source, format, encoding='utf-8'):
    try:
        path = os.path.exists(source)
    except UnicodeEncodeError:
        path = os.path.exists(source.encode('utf-8'))
    except ValueError:
        path = ''
    if path:
        format = format or os.path.splitext(source)[1].strip('.')
        input_type = 'path'
    else:
        if encoding != 'utf-8':
            # if a source and a different encoding is given, try to decode the the source into a
            # unicode string
            try:
                source = cast_unicode(source, encoding=encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
        input_type = 'string'
    return source, format, input_type


def _process_file(source, input_type, to, format, extra_args, outputfile=None,
                  filters=None):
    _ensure_pandoc_path()
    string_input = input_type == 'string'
    input_file = [source] if not string_input else []
    args = [__pandoc_path, '--from=' + format]

    # #59 - pdf output won't work with `--to` set!
    if to is not 'pdf':
        args.append('--to=' + to)

    args += input_file

    if outputfile:
        args.append("--output="+outputfile)

    args.extend(extra_args)

    # adds the proper filter syntax for each item in the filters list
    if filters is not None:
        if isinstance(filters, string_types):
            filters = filters.split()
        f = ['--filter=' + x for x in filters]
        args.extend(f)

    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE if string_input else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

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
        # this shouldn't happen: pandoc more or less garantees that the output is utf-8!
        raise RuntimeError('Pandoc output was not utf-8.')

    # check that pandoc returned successfully
    if p.returncode != 0:
        raise RuntimeError(
            'Pandoc died with exitcode "%s" during conversion: %s' % (p.returncode, stderr)
        )

    # if there is an outputfile, then stdout is likely empty!
    return stdout


def _get_base_format(format):
    '''
    According to http://johnmacfarlane.net/pandoc/README.html#general-options,
    syntax extensions for markdown can be individually enabled or disabled by
    appending +EXTENSION or -EXTENSION to the format name.
    Return the base format without any extensions.
    '''
    return re.split('\+|-', format)[0]


def get_pandoc_formats():
    '''
    Dynamic preprocessor for Pandoc formats.
    Return 2 lists. "from_formats" and "to_formats".
    '''
    _ensure_pandoc_path()
    p = subprocess.Popen(
        [__pandoc_path, '-h'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

    comm = p.communicate()
    help_text = comm[0].decode().splitlines(False)
    if p.returncode != 0 or 'Options:' not in help_text:
        raise RuntimeError("Couldn't call pandoc to get output formats. Output from pandoc:\n%s" %
                           str(comm))
    txt = ' '.join(help_text[1:help_text.index('Options:')])

    aux = txt.split('Output formats: ')
    in_ = re.sub('Input\sformats:\s|\*', '', aux[0]).split(',')
    out = re.sub('\*|\[.*?\]', '', aux[1]).split(',')

    return [f.strip() for f in in_], [f.strip() for f in out]


# copied and adapted from jupyter_nbconvert/utils/pandoc.py, Modified BSD License

def _get_pandoc_version(pandoc_path):
    p = subprocess.Popen(
        [pandoc_path, '--version'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
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


def _ensure_pandoc_path():
    global __pandoc_path

    if __pandoc_path is None:
        included_pandoc = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       "files", "pandoc")
        search_paths = ["pandoc",  included_pandoc]
        # If a user added the complete path to pandoc to an env, use that as the
        # only way to get pandoc so that a user can overwrite even a higher
        # version in some other places.
        if os.getenv('PYPANDOC_PANDOC', None):
            search_paths = [os.getenv('PYPANDOC_PANDOC')]
        for path in search_paths:
            curr_version = [0, 0, 0]
            version_string = "0.0.0"
            try:
                version_string = _get_pandoc_version(path)
            except:
                # we can't use that path...
                # print(e)
                continue
            version = [int(x) for x in version_string.split(".")]
            while len(version) < len(curr_version):
                version.append(0)
            # print("%s, %s" % (path, version))
            for pos in range(len(curr_version)):
                # Only use the new version if it is any bigger...
                if version[pos] > curr_version[pos]:
                    # print("Found: %s" % path)
                    __pandoc_path = path
                    curr_version = version
                    break

        if __pandoc_path is None:
            if os.path.exists('/usr/local/bin/brew'):
                sys.stderr.write(textwrap.dedent("""\
                    Maybe try:

                        brew install pandoc
                """))
            elif os.path.exists('/usr/bin/apt-get'):
                sys.stderr.write(textwrap.dedent("""\
                    Maybe try:

                        sudo apt-get install pandoc
                """))
            elif os.path.exists('/usr/bin/yum'):
                sys.stderr.write(textwrap.dedent("""\
                    Maybe try:

                        sudo yum install pandoc
                """))
            sys.stderr.write(textwrap.dedent("""\
                See http://johnmacfarlane.net/pandoc/installing.html
                for installation options
            """))
            sys.stderr.write(textwrap.dedent("""\
                ---------------------------------------------------------------

            """))
            raise RuntimeError("No pandoc was found: either install pandoc and add it\n"
                               "to your PATH or install pypandoc wheels with included pandoc.")


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
