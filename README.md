# pypandoc

pypandoc provides a thin wrapper for [pandoc](http://johnmacfarlane.net/pandoc/), a universal document converter.

## Usage

The basic invocation looks like this: `pypandoc.convert('input', 'output format')`. `pypandoc` tries to infer the type of the input automatically. If it's a file, it will load it. In case you pass a string, you can define the `format` using the parameter. The example below should clarify the usage:

```python
import pypandoc

output = pypandoc.convert('somefile.md', 'rst')

# alternatively you could just pass some string to it and define its format
output = pypandoc.convert('#some title', 'rst', format='md')
```

In addition to `format`, it is possible to pass `extra_args`. That makes it possible to access various pandoc options easily. Please refer to `pandoc -h` and the [official documentation](http://johnmacfarlane.net/pandoc/README.html) for further details.

See also [pyandoc](http://pypi.python.org/pypi/pyandoc/) for an alternative implementation.

## Django Service Example

See `services.py` at the project root for implementation. Use it like this:

```python
from .services import PandocDocxService

service = PandocDocxService()
doc_file = service.generate(html='<html><body><h1>Heading 1</h1><p>testing testing 123</p></body></html>')
```

## Contributors

* [Valentin Haenel](https://github.com/esc) - String conversion fix
* [Daniel Sanchez](https://github.com/ErunamoJAZZ) - Automatic parsing of input/output formats
* [Thomas G.](https://github.com/coldfix) - Python 3 support
* [Ben Jao Ming](https://github.com/benjaoming) - Fail gracefully if `pandoc` is missing
* [Ross Crawford-d'Heureuse](http://github.com/rosscdh) - Encode input in UTF-8 and add Django example
* [Michael Chow](https://github.com/machow) - Decode output in UTF-8
* [Janusz Skonieczny](https://github.com/wooyek) - Support Windows newlines and allow encoding to be specified.

## License

`pypandoc` is available under MIT license. See LICENSE for more details.

