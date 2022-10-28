# -*- coding: utf-8 -*-

import locale
import sys

# compat code from IPython py3compat.py and encoding.py, which is licensed under the terms of the
# Modified BSD License (also known as New or Revised or 3-Clause BSD)
_DEFAULT_ENCODING = None
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

def cast_unicode(s, encoding=None):
    if isinstance(s, bytes):
        return _decode(s, encoding)
    return s
