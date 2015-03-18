# -*- coding: utf-8 -*-
from __future__ import with_statement

import subprocess
import sys
import textwrap
import os
import re

__author__ = 'Juho Vepsäläinen'
__version__ = '0.9.5'
__license__ = 'MIT'
__all__ = ['convert', 'get_pandoc_formats']


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
    '''Converts given `source` from `format` `to` another. `source` may be
    either a file path or a string to be converted. It's possible to pass
    `extra_args` if needed. In case `format` is not provided, it will try to
    invert the format based on given `source`. Pandoc filters can be passed as
    a list, e.g. filters=['pandoc-citeproc']

    Raises OSError if pandoc is not found! Make sure it has been installed
    and is available at path.

    '''
    return _convert(_read_file, _process_file, source, to,
                    format, extra_args, encoding=encoding,
                    outputfile=outputfile, filters=filters)


def _convert(reader, processor, source, to, format=None, extra_args=(), encoding=None,
             outputfile=None, filters=None):
    source, format = reader(source, format, encoding=encoding)

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

    return processor(source, to, format, extra_args, outputfile=outputfile,
                     filters=filters)


def _read_file(source, format, encoding='utf-8'):
    try:
        path = os.path.exists(source)
    except UnicodeEncodeError:
        path = os.path.exists(source.encode('utf-8'))
    if path:
        import codecs
        with codecs.open(source, encoding=encoding) as f:
            format = format or os.path.splitext(source)[1].strip('.')
            source = f.read()

    return source, format


def _process_file(source, to, format, extra_args, outputfile=None, filters=None):
    args = ['pandoc', '--from=' + format, '--to=' + to]

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
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    # something else than 'None' indicates that the process already terminated
    if not p.returncode is None:
        raise RuntimeError(
            'Pandoc died with exitcode "%s" before receiving input: %s' % (p.returncode,
                                                                           p.stderr.read())
        )

    try:
        source = source.encode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        # assume that it is already a utf-8 encoded string
        pass

    stdout, stderr = p.communicate(source)

    try:
        stdout = stdout.decode('utf-8')
    except UnicodeDecodeError:
        # this shouldn't happen: pandoc more or less garantees that the output is utf-8!
        raise RuntimeError('Pandoc output was not utf-8.')

    # check that pandoc returned successfully
    if p.returncode != 0:
        raise RuntimeError(
            'Pandoc died with exitcode "%s" during conversation: %s' % (p.returncode, stderr)
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
    in_ = re.sub('Input\sformats:\s', '', aux[0]).split(',')
    out = re.sub('\*|\[.*?\]', '', aux[1]).split(',')

    return [f.strip() for f in in_], [f.strip() for f in out]
