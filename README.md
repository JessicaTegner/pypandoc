# pypandoc

[![Latest Version](https://pypip.in/version/pypandoc/badge.svg)](https://pypi.python.org/pypi/pypandoc/)
[![Build Status](https://travis-ci.org/bebraw/pypandoc.svg?branch=master)](https://travis-ci.org/bebraw/pypandoc)

pypandoc provides a thin wrapper for [pandoc](http://johnmacfarlane.net/pandoc/), a universal
document converter.

## Installation

- Install pandoc
  - Ubuntu/Debian: `sudo apt-get install pandoc`
  - Fedora/Red Hat: `sudo yum install pandoc`
  - Mac OS X with Homebrew: `brew install pandoc`
  - Machine with Haskell: `cabal-install pandoc`
  - Windows: There is an installer available
    [here](http://johnmacfarlane.net/pandoc/installing.html)
  - [FreeBSD port](http://www.freshports.org/textproc/pandoc/)
  - Or see http://johnmacfarlane.net/pandoc/installing.html
- `pip install pypandoc`
- To use pandoc filters, you must have the relevant filter installed on your machine

## Usage

The basic invocation looks like this: `pypandoc.convert('input', 'output format')`. `pypandoc`
tries to infer the type of the input automatically. If it's a file, it will load it. In case you
pass a string, you can define the `format` using the parameter. The example below should clarify
the usage:

```python
import pypandoc

output = pypandoc.convert('somefile.md', 'rst')

# alternatively you could just pass some string to it and define its format
output = pypandoc.convert('#some title', 'rst', format='md')
# output == 'some title\r\n==========\r\n\r\n'
```

If you pass in a string (and not a filename), `convert` expects this string to be unicode or
utf-8 encoded bytes. `convert` will always return a unicode string.

It's also possible to directly let pandoc write the output to a file. This is the only way to
convert to some output formats (e.g. odt, docx, epub, epub3, pdf). In that case `convert()` will
return an empty string.

```python
import pypandoc

output = pypandoc.convert('somefile.md', 'docx', outputfile="somefile.docx")
assert output == ""
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
pypandoc now supports easy addition of
[pandoc filters](http://johnmacfarlane.net/pandoc/scripting.html).

```python
filters = ['pandoc-citeproc']
pdoc_args = ['--mathjax',
             '--smart']
output = pd.convert(source=filename,
                    to='html5',
                    format='md',
                    extra_args=pdoc_args,
                    filters=filters)
```
Please pass any filters in as a list and not a string.

Please refer to `pandoc -h` and the
[official documentation](http://johnmacfarlane.net/pandoc/README.html) for further details.

## Dealing with Formatting Arguments

Pandoc supports custom formatting though `-V` parameter. In order to use it through pypandoc, use code such as this:

```python
output = pypandoc.convert('demo.md', 'pdf', outputfile='demo.pdf',
  extra_args=['-V', 'geometry:margin=1.5cm'])
```

Note that it's important to separate `-V` and its argument within a list like that or else it won't work. This gotcha has to do with the way `subprocess.Popen` works.

## Getting Pandoc Version

As it can be useful sometimes to check what Pandoc version is available at your system, `pypandoc` provides an utility for this. Example:

```
version = pypandoc.get_pandoc_version()
```

## Related

[pydocverter](https://github.com/msabramo/pydocverter) is a client for a service called
[Docverter](http://www.docverter.com/), which offers pandoc as a service (plus some extra goodies).
It has the same API as pypandoc, so you can easily write code that uses one and falls back to the
other. E.g.:

```python
try:
    import pypandoc as converter
except ImportError:
    import pydocverter as converter

converter.convert('somefile.md', 'rst')
```

See [pyandoc](http://pypi.python.org/pypi/pyandoc/) for an alternative implementation of a pandoc
wrapper from Kenneth Reitz. This one hasn't been active in a while though.

## Contributing

Contributions are welcome. When opening a PR, please keep the following guidelines in mind:

1. Before implementing, please open an issue for discussion.
2. Make sure you have tests for the new logic.
3. Make sure your code passes `flake8 pypandoc.py tests.py`
4. Add yourself to contributors at `README.md` unless you are already there. In that case tweak your contributions.

Note that for citeproc tests to pass you'll need to have [pandoc-citeproc](https://github.com/jgm/pandoc-citeproc) installed.

> IMPORTANT! Currently Travis build is a bit broken. If you have any idea on how to debug that, please see [#55](https://github.com/bebraw/pypandoc/issues/55).

## Contributors

* [Valentin Haenel](https://github.com/esc) - String conversion fix
* [Daniel Sanchez](https://github.com/ErunamoJAZZ) - Automatic parsing of input/output formats
* [Thomas G.](https://github.com/coldfix) - Python 3 support
* [Ben Jao Ming](https://github.com/benjaoming) - Fail gracefully if `pandoc` is missing
* [Ross Crawford-d'Heureuse](http://github.com/rosscdh) - Encode input in UTF-8 and add Django
  example
* [Michael Chow](https://github.com/machow) - Decode output in UTF-8
* [Janusz Skonieczny](https://github.com/wooyek) - Support Windows newlines and allow encoding to
  be specified.
* [gabeos](https://github.com/gabeos) - Fix help parsing
* [Marc Abramowitz](https://github.com/msabramo) - Make `setup.py` fail hard if `pandoc` is
  missing, Travis, Dockerfile, PyPI badge, Tox, PEP-8, improved documentation
* [Daniel L.](https://github.com/mcktrtl) - Add `extra_args` example to README
* [Amy Guy](https://github.com/rhiaro) - Exception handling for unicode errors
* [Florian Eßer](https://github.com/flesser) - Allow Markdown extensions in output format
* [Philipp Wendler](https://github.com/PhilippWendler) - Allow Markdown extensions in input format
* [Jan Schulz](https://github.com/JanSchulz) - Handling output to a file, Travis to work on newer version of Pandoc, return code checking, get_pandoc_version. Helped to fix the Travis build.
* [Aaron Gonzales](https://github.com/xysmas) - Added better filter handling
* [David Lukes](https://github.com/dlukes) - Enabled input from non-plain-text files and made sure tests clean up template files correctly if they fail
* [valholl](https://github.com/valholl) - Set up licensing information correctly and include examples to distribution version
* [Cyrille Rossant](https://github.com/rossant) - Fixed bug by trimming out stars in the list of pandoc formats. Helped to fix the Travis build.

## License

`pypandoc` is available under MIT license. See LICENSE for more details.
