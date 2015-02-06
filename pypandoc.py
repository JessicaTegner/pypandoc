# -*- coding: utf-8 -*-
from __future__ import with_statement

__author__ = 'Juho Vepsäläinen'
__version__ = '0.9.1'
__license__ = 'MIT'
__all__ = ['convert', 'get_pandoc_formats']

import subprocess
import sys
import textwrap
import os
import re


def convert(source, to, format=None, extra_args=(), encoding='utf-8'):
    '''Converts given `source` from `format` `to` another. `source` may be
    either a file path or a string to be converted. It's possible to pass
    `extra_args` if needed. In case `format` is not provided, it will try to
    invert the format based on given `source`.

    Raises OSError if pandoc is not found! Make sure it has been installed and
    is available at path.

    '''
    return _convert(_read_file, _process_file, source, to,
                    format, extra_args, encoding=encoding)


def _convert(reader, processor, source, to,
             format=None, extra_args=(), encoding=None):
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

    if format not in from_formats:
        raise RuntimeError(
            'Invalid input format! Expected one of these: ' +
            ', '.join(from_formats))

    # Markdown syntax extensions can be individually enabled or disabled by
    # appending +EXTENSION or -EXTENSION to the format name.
    to_base = re.split('\+|-', to)[0]
    if to_base not in to_formats:
        raise RuntimeError(
            'Invalid output format! Expected one of these: ' +
            ', '.join(to_formats))

    return processor(source, to, format, extra_args)


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


def _process_file(source, to, format, extra_args):
    args = ['pandoc', '--from=' + format, '--to=' + to]
    args.extend(extra_args)

    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

    try:
        c = p.communicate(source.encode('utf-8'))[0].decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        c = p.communicate(source)[0]

    return c


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
