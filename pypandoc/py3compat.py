# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys
import locale

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


def _encode(u, encoding=None):
    encoding = encoding or _DEFAULT_ENCODING
    return u.encode(encoding)


def cast_unicode(s, encoding=None):
    if isinstance(s, bytes):
        return _decode(s, encoding)
    return s


def cast_bytes(s, encoding=None):
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
