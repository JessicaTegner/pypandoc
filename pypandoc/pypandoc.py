from __future__ import with_statement
import subprocess
import os

def convert(source, to, format=None, extra_args=()):
    '''Converts given `source` from `format` `to` another. `source` may be either a file path or a string to be converted. It's possible to pass `extra_args` if needed. In case `format` is not provided, it will try to invert the format based on given `source`.

    Raises OSError if pandoc is not found! Make sure it has been installed and is available at path.
    '''
    with open(source) as f:
        source = f.read()
        format = format or os.path.splitext(source)[1]

    format = {
        'dbk': 'docbook',
        'md': 'markdown',
        'rest': 'rst',
        'tex': 'latex',
    }.get(format, format)

    if not format:
        raise RunTimeError('Missing format!')

    p = subprocess.Popen(['pandoc', '--from=' + format, '--to=' + to].extend(extra_args),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
    return p.communicate(source)[0]

