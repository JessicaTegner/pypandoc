# -*- coding: utf-8 -*-
from __future__ import with_statement

import subprocess
import sys
import textwrap
import os
import re
import locale

__author__ = 'Juho Vepsäläinen'
__version__ = '1.0.3'
__license__ = 'MIT'
__all__ = ['convert', 'get_pandoc_formats']

# compat code from IPython py3compat.py and encoding.py, which is licensed under the terms of the
# Modified BSD License (also known as New or Revised or 3-Clause BSD)
try:
    # There are reports of getpreferredencoding raising errors
    # in some cases, which may well be fixed, but let's be conservative here.
    _DEFAULT_ENCODING = locale.getpreferredencoding()
except Exception:
    pass
_DEFAULT_ENCODING = _DEFAULT_ENCODING or sys.getdefaultencoding()


def _decode(s, encoding=None):
    encoding = encoding or _DEFAULT_ENCODING
    return s.decode(encoding)


def _encode(u, encoding=None):
    encoding = encoding or _DEFAULT_ENCODING
    return u.encode(encoding)


def _cast_unicode(s, encoding=None):
    if isinstance(s, bytes):
        return _decode(s, encoding)
    return s


def _cast_bytes(s, encoding=None):
    # bytes == str on py2.7 -> always encode on py2
    if not isinstance(s, bytes):
        return _encode(s, encoding)
    return s


if sys.version_info[0] >= 3:
    PY3 = True

    string_types = (str,)
    unicode_type = str
else:
    PY3 = False

    string_types = (str, unicode)
    unicode_type = unicode


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
            'Invalid input format! Expected one of these: ' +
            ', '.join(from_formats))

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
                source = _cast_unicode(source, encoding=encoding)
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
        input_type = 'string'
    return source, format, input_type


def _process_file(source, input_type, to, format, extra_args, outputfile=None,
                  filters=None):
    string_input = input_type == 'string'
    input_file = [source] if not string_input else []
    args = ['pandoc', '--from=' + format]

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
        source = _cast_bytes(source, encoding='utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        # assume that it is already a utf-8 encoded string
        pass

    stdout, stderr = p.communicate(source if string_input else None)

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
    try:
        p = subprocess.Popen(
            ['pandoc', '-h'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
    except OSError:
        sys.stderr.write(textwrap.dedent("""\
            ---------------------------------------------------------------
            An error occurred while trying to run `pandoc`
        """))
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
        raise OSError("You probably do not have pandoc installed.")

    help_text = p.communicate()[0].decode().splitlines(False)
    txt = ' '.join(help_text[1:help_text.index('Options:')])

    aux = txt.split('Output formats: ')
    in_ = re.sub('Input\sformats:\s|\*', '', aux[0]).split(',')
    out = re.sub('\*|\[.*?\]', '', aux[1]).split(',')

    return [f.strip() for f in in_], [f.strip() for f in out]


# copied and adapted from jupyter_nbconvert/utils/pandoc.py, Modified BSD License
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
        p = subprocess.Popen(
            ['pandoc', '-v'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

        out_lines = p.communicate()[0].decode().splitlines(False)
        version_pattern = re.compile(r"^\d+(\.\d+){1,}$")
        for tok in out_lines[0].split():
            if version_pattern.match(tok):
                __version = tok
                break
    return __version


# -----------------------------------------------------------------------------
# Internal state management
# -----------------------------------------------------------------------------
def clean_version_cache():
    global __version
    __version = None

__version = None
