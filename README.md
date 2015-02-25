# pypandoc

[![Latest Version](https://pypip.in/version/pypandoc/badge.svg)](https://pypi.python.org/pypi/pypandoc/)
[![Build Status](https://travis-ci.org/bebraw/pypandoc.svg?branch=master)](https://travis-ci.org/bebraw/pypandoc)

pypandoc provides a thin wrapper for [pandoc](http://johnmacfarlane.net/pandoc/), a universal document converter.

## Installation

- Install pandoc
  - Ubuntu/Debian: `sudo apt-get install pandoc`
  - Fedora/Red Hat: `sudo yum install pandoc`
  - Mac OS X with Homebrew: `brew install pandoc`
  - Machine with Haskell: `cabal-install pandoc`
  - Windows: There is an installer available [here](http://johnmacfarlane.net/pandoc/installing.html)
  - [FreeBSD port](http://www.freshports.org/textproc/pandoc/)
  - Or see http://johnmacfarlane.net/pandoc/installing.html
- `pip install pypandoc`

## Usage

The basic invocation looks like this: `pypandoc.convert('input', 'output format')`. `pypandoc` tries to infer the type of the input automatically. If it's a file, it will load it. In case you pass a string, you can define the `format` using the parameter. The example below should clarify the usage:

```python
import pypandoc

output = pypandoc.convert('somefile.md', 'rst')

# alternatively you could just pass some string to it and define its format
output = pypandoc.convert('#some title', 'rst', format='md')
# output == 'some title\r\n==========\r\n\r\n'
```

In addition to `format`, it is possible to pass `extra_args`.
That makes it possible to access various pandoc options easily.

```python
output = pypandoc.convert(
    '<h1>Primary Heading</h1>',
    'md', format='html',
    extra_args=['--atx-headers'])
# output == '# Primary Heading\r\n'
output = pypandoc.convert(
    '# Primary Heading',
    'html', format='md',
    extra_args=['--base-header-level=2'])
# output == '<h2 id="primary-heading">Primary Heading</h2>\r\n'
```

Please refer to `pandoc -h` and the [official documentation](http://johnmacfarlane.net/pandoc/README.html) for further details.

## Related

[pydocverter](https://github.com/msabramo/pydocverter) is a client for a service called [Docverter](http://www.docverter.com/), 
which offers pandoc as a service (plus some extra goodies).
It has the same API as pypandoc,
so you can easily write code that uses one and falls back to the other. 
E.g.:

```python
try:
    import pypandoc as converter
except ImportError:
    import pydocverter as converter

converter.convert('somefile.md', 'rst')
```

See [pyandoc](http://pypi.python.org/pypi/pyandoc/) for an alternative implementation of a pandoc wrapper from Kenneth Reitz.
This one hasn't been active in a while though.

## Contributors

* [Valentin Haenel](https://github.com/esc) - String conversion fix
* [Daniel Sanchez](https://github.com/ErunamoJAZZ) - Automatic parsing of input/output formats
* [Thomas G.](https://github.com/coldfix) - Python 3 support
* [Ben Jao Ming](https://github.com/benjaoming) - Fail gracefully if `pandoc` is missing
* [Ross Crawford-d'Heureuse](http://github.com/rosscdh) - Encode input in UTF-8 and add Django example
* [Michael Chow](https://github.com/machow) - Decode output in UTF-8
* [Janusz Skonieczny](https://github.com/wooyek) - Support Windows newlines and allow encoding to be specified.
* [gabeos](https://github.com/gabeos) - Fix help parsing
* [Marc Abramowitz](https://github.com/msabramo) - Make `setup.py` fail hard if `pandoc` is missing, Travis, Dockerfile, PyPI badge, Tox, PEP-8, improved documentation
* [Daniel L.](https://github.com/mcktrtl) - Add `extra_args` example to README
* [Amy Guy](https://github.com/rhiaro) - Exception handling for unicode errors
* [Florian Eßer](https://github.com/flesser) - Allow Markdown extensions in output format

## License

`pypandoc` is available under MIT license. See LICENSE for more details.
