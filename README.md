# pypandoc

pypandoc provides a thin wrapper for [pandoc](http://johnmacfarlane.net/pandoc/), a universal document converter. Use it as follows:

    import pypandoc

    output = pypandoc.convert('somefile.md', 'rst')

    # do something with output now...

In addition to filename it's possible to pass pure string data to the converter. In case that data does not match any existing file, it will be converted to the given format instead.

The code infers pandoc `--from` format automatically based on given file extension. It is possible to override this behavior by passing `--from=myformat` within `extra_args`. This allows other customizations as well. Please refer to `pandoc -h` and the [official documentation](http://johnmacfarlane.net/pandoc/README.html) for exact formats and options supported.

See also [pypandoc](http://pypi.python.org/pypi/pyandoc/).

## License

pypandoc is available under MIT license. See LICENSE for more details.

