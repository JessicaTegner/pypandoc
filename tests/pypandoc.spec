from pypandoc import pypandoc

def test_converter(to, format=None, extra_args=()):
    def reader(*args):
        return source, format

    def processor(*args):
        return 'ok'

    source = 'foo'

    return pypandoc._convert(reader, processor, source, to, format, extra_args)

converts valid format
    test_converter(format='md', to='rest') == 'ok'

does not convert to invalid format
    test_converter(format='md', to='invalid') raises RuntimeError

does not convert from invalid format
    test_converter(format='invalid', to='rest') raises RuntimeError

