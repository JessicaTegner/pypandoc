# pypandoc

pypandoc provides a thin wrapper for [pandoc](http://johnmacfarlane.net/pandoc/), a universal document converter. Use it as follows:

```python
import pypandoc

output = pypandoc.convert('somefile.md', 'rst')

# alternatively you could just pass some string to it and define its format
output = pypandoc.convert('#some title', 'rst', format='md')
```

The code infers pandoc `--from` format automatically based on given file extension unless one is provided explicitly. `extra_args` parameter makes it possible to access various pandoc options. Please refer to `pandoc -h` and the [official documentation](http://johnmacfarlane.net/pandoc/README.html) for further details.

See also [pyandoc](http://pypi.python.org/pypi/pyandoc/).

## Contributors

* [Valentin Haenel](https://github.com/esc) - String conversion fix
* [Daniel Sanchez](https://github.com/ErunamoJAZZ) - Automatic parsing of input/output formats
* [Thomas G.](https://github.com/coldfix) - Python 3 support
* [Ben Jao Ming](https://github.com/benjaoming) - Fail gracefully if `pandoc` is missing

## License

pypandoc is available under MIT license. See LICENSE for more details.


# Service Examples Useage

**Assuming you are using django**

As within the service we make use of: django.core.files.File

```
from .services import PandocDocxService
service = PandocDocxService()
doc_file = service.generate(html='<html><body><h1>Heading 1</h1><p>testing testing 123</p></body></html>')
```