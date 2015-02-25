#!/usr/bin/env python

import unittest
import tempfile
import pypandoc
import os
import sys


def test_converter(to, format=None, extra_args=()):

    def reader(*args, **kwargs):
        return source, format

    def processor(*args):
        return 'ok'

    source = 'foo'

    return pypandoc._convert(reader, processor, source, to, format, extra_args)


class TestPypandoc(unittest.TestCase):
    def test_converts_valid_format(self):
        self.assertEqual(test_converter(format='md', to='rest'), 'ok')

    def test_does_not_convert_to_invalid_format(self):
        try:
            test_converter(format='md', to='invalid')
        except RuntimeError:
            pass

    def test_does_not_convert_from_invalid_format(self):
        try:
            test_converter(format='invalid', to='rest')
        except RuntimeError:
            pass

    def test_basic_conversion_from_file(self):
        # This will not work on windows:
        # http://docs.python.org/2/library/tempfile.html
        with tempfile.NamedTemporaryFile('w+t', suffix='.md',
                                         delete=False) as test_file:
            file_name = test_file.name
            test_file.write('#some title\n')
            test_file.flush()
        expected = u'some title{0}=========={0}{0}'.format(os.linesep)
        received = pypandoc.convert(file_name, 'rst')
        self.assertEqualExceptForNewlineEnd(expected, received)

    def test_basic_conversion_from_file_with_format(self):
        # This will not work on windows:
        # http://docs.python.org/2/library/tempfile.html
        with tempfile.NamedTemporaryFile('w+t', suffix='.rst',
                                         delete=False) as test_file:
            file_name = test_file.name
            test_file.write('#some title\n')
            test_file.flush()
        expected = u'some title{0}=========={0}{0}'.format(os.linesep)
        received = pypandoc.convert(file_name, 'rst', format='md')
        self.assertEqualExceptForNewlineEnd(expected, received)

    def test_basic_conversion_from_string(self):
        expected = u'some title{0}=========={0}{0}'.format(os.linesep)
        received = pypandoc.convert('#some title', 'rst', format='md')
        self.assertEqualExceptForNewlineEnd(expected, received)

    def test_conversion_with_markdown_extensions(self):
        input = '<s>strike</s>'
        expected_with_extension = u'~~strike~~'
        expected_without_extension = u'<s>strike</s>'
        received_with_extension = pypandoc.convert(input, 'markdown+strikeout', format='html')
        received_without_extension = pypandoc.convert(input, 'markdown-strikeout', format='html')
        self.assertEqualExceptForNewlineEnd(expected_with_extension, received_with_extension)
        self.assertEqualExceptForNewlineEnd(expected_without_extension, received_without_extension)

    def assertEqualExceptForNewlineEnd(self, expected, received):
        self.assertEqual(expected.rstrip('\n'), received.rstrip('\n'))


suite = unittest.TestLoader().loadTestsFromTestCase(TestPypandoc)
ret = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if ret.wasSuccessful() else 1)
