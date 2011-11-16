from __future__ import with_statement
import subprocess
import os

def convert(source, to, format=None, extra_args=()):
    '''Converts given `source` from `format` `to` another. `source` may be either a file path or a string to be converted. It's possible to pass `extra_args` if needed. In case `format` is not provided, it will try to invert the format based on given `source`.

    Raises OSError if pandoc is not found! Make sure it has been installed and is available at path.
    '''
    return _convert(_read_file, _process_file, source, to, format, extra_args)

def _convert(reader, processor, source, to, format=None, extra_args=()):
    source, format = reader(source, format)

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

    from_formats = ('native', 'json', 'markdown', 'markdown+lhs', 'rst',
        'rst+lhs', 'textile', 'html', 'latex', 'latex+lhs', )
    if format not in from_formats:
        raise RuntimeError('Invalid input format!')

    to_formats = ('native', 'json', 'html', 'html+lhs', 's5', 'slidy',
        'docbook', 'opendocument', 'latex', 'latex+lhs', 'context',
        'texinfo', 'man', 'markdown', 'markdown+lhs', 'plain', 'rst',
        'rst+lhs', 'mediawiki', 'textile', 'rtf', 'org', 'odt', 'epub', )
    if to not in to_formats:
        raise RuntimeError('Invalid to format!')

    return processor(source, to, format, extra_args)

def _read_file(source, format):
    with open(source) as f:
        format = format or os.path.splitext(source)[1].strip('.')
        source = f.read()

    return source, format

def _process_file(source, to, format, extra_args):
    args = ['pandoc', '--from=' + format, '--to=' + to]
    args.extend(extra_args)

    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    return p.communicate(source)[0]

