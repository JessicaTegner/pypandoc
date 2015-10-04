#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import tempfile
import pypandoc
import os
import sys


def test_converter(to, format=None, extra_args=()):

    def reader(*args, **kwargs):
        return source, format, input_type

    def processor(*args, **kwargs):
        return 'ok'

    source = 'foo'
    input_type = 'string'

    return pypandoc._convert(reader, processor, source, to, format, extra_args)


class TestPypandoc(unittest.TestCase):

    def test_get_pandoc_formats(self):
        inputs, outputs = pypandoc.get_pandoc_formats()
        self.assertTrue("markdown" in inputs)
        self.assertTrue("json" in inputs)
        self.assertTrue("markdown" in outputs)

    def test_get_pandoc_version(self):
        version = pypandoc.get_pandoc_version()
        self.assertTrue(isinstance(version, pypandoc.string_types))
        major = int(version.split(".")[0])
        # according to http://pandoc.org/releases.html there were only two versions 0.x ...
        self.assertTrue(major in [0, 1])

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
        with tempfile.NamedTemporaryFile('w+t', suffix='.md') as test_file:
            file_name = test_file.name
            test_file.write('#some title\n')
            test_file.flush()

            expected = u'some title{0}=========={0}{0}'.format(os.linesep)
            received = pypandoc.convert(file_name, 'rst')
            self.assertEqualExceptForNewlineEnd(expected, received)

    def test_basic_conversion_from_file_with_format(self):
        # This will not work on windows:
        # http://docs.python.org/2/library/tempfile.html
        with tempfile.NamedTemporaryFile('w+t', suffix='.rst') as test_file:
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
        received_with_extension = pypandoc.convert(input, 'markdown+strikeout',
                                                   format='html')
        received_without_extension = pypandoc.convert(input,
                                                      'markdown-strikeout',
                                                      format='html')
        self.assertEqualExceptForNewlineEnd(expected_with_extension, received_with_extension)
        self.assertEqualExceptForNewlineEnd(expected_without_extension, received_without_extension)

    def test_conversion_from_markdown_with_extensions(self):
        input = u'~~strike~~'
        expected_with_extension = u'<p><del>strike</del></p>'
        expected_without_extension = u'<p><sub><sub>strike</sub></sub></p>'
        received_with_extension = pypandoc.convert(input, 'html', format=u'markdown+strikeout')
        received_without_extension = pypandoc.convert(input, 'html', format=u'markdown-strikeout')
        self.assertEqualExceptForNewlineEnd(expected_with_extension, received_with_extension)
        self.assertEqualExceptForNewlineEnd(expected_without_extension, received_without_extension)

    def test_basic_conversion_to_file(self):
        # we just want to get a temp file name, where we can write to
        tf = tempfile.NamedTemporaryFile(suffix='.rst', delete=False)
        name = tf.name
        tf.close()

        expected = u'some title{0}=========={0}{0}'.format(os.linesep)

        try:
            received = pypandoc.convert('#some title\n', to='rst', format='md', outputfile=name)
            self.assertEqualExceptForNewlineEnd("", received)
            with open(name) as f:
                written = f.read()
            self.assertEqualExceptForNewlineEnd(expected, written)
        except:
            raise
        finally:
            os.remove(name)

        # to odf does not work without a file
        def f():
            pypandoc.convert('#some title\n', to='odf', format='md',
                             outputfile=None)
        self.assertRaises(RuntimeError, f)

    def test_conversion_with_citeproc_filter(self):
        # we just want to get a temp file name, where we can write to
        filters = ['pandoc-citeproc']
        written = pypandoc.convert('./filter_test.md', to='html', format='md',
                                   outputfile=None, filters=filters)
        import re as re
        # only properly converted file will have this in it
        found = re.search(r'Fenner', written)
        self.assertTrue(found.group() == 'Fenner')
        # only properly converted file will have this in it
        found = re.search(r'10.1038', written)
        self.assertTrue(found.group() == '10.1038')

        # make sure that it splits the filter line
        for filters in ['pandoc-citeproc', u'pandoc-citeproc']:
            written = pypandoc.convert('./filter_test.md', to='html', format='md',
                                       outputfile=None, filters=filters)
            # only properly converted file will have this in it
            found = re.search(r'Fenner', written)
            self.assertTrue(found.group() == 'Fenner')
            # only properly converted file will have this in it
            found = re.search(r'10.1038', written)
            self.assertTrue(found.group() == '10.1038')

    def test_conversion_with_empty_filter(self):
        # we just want to get a temp file name, where we can write to
        filters = ''
        written = pypandoc.convert('./filter_test.md', to='html', format='md',
                                   outputfile=None, filters=filters)
        import re as re
        # This should not use the pandoc-citeproc module and will not find the
        # strings
        found = re.search(r'Fenner', written)
        self.assertTrue(found is None)
        found = re.search(r'10.1038', written)
        self.assertTrue(found is None)

    def test_conversion_error(self):
        # pandoc dies on wrong commandline arguments
        def f():
            pypandoc.convert('<h1>Primary Heading</h1>', 'md', format='html', extra_args=["--blah"])
        self.assertRaises(RuntimeError, f)

    def test_unicode_input(self):
        # make sure that pandoc always returns unicode and does not mishandle it
        expected = u'üäöîôû{0}======{0}{0}'.format(os.linesep)
        written = pypandoc.convert(u'<h1>üäöîôû</h1>', 'md', format='html')
        self.assertTrue(isinstance(written, pypandoc.unicode_type))
        self.assertEqualExceptForNewlineEnd(expected, written)
        bytes = u'<h1>üäöîôû</h1>'.encode("utf-8")
        written = pypandoc.convert(bytes, 'md', format='html')
        self.assertEqualExceptForNewlineEnd(expected, written)
        self.assertTrue(isinstance(written, pypandoc.unicode_type))

        # Only use german umlauts in th next test, as iso-8859-15 covers that
        expected = u'üäö€{0}===={0}{0}'.format(os.linesep)
        bytes = u'<h1>üäö€</h1>'.encode("iso-8859-15")
        # Without encoding, this fails as we expect utf-8 per default

        def f():
            pypandoc.convert(bytes, 'md', format='html')
        self.assertRaises(RuntimeError, f)

        def f():
            # we have to use something which interprets '\xa4', so latin and -1 does not work :-/
            pypandoc.convert(bytes, 'md', format='html', encoding="utf-16")
        self.assertRaises(RuntimeError, f)
        # with the right encoding it should work...
        written = pypandoc.convert(bytes, 'md', format='html', encoding="iso-8859-15")
        self.assertEqualExceptForNewlineEnd(expected, written)
        self.assertTrue(isinstance(written, pypandoc.unicode_type))

    def test_conversion_from_non_plain_text_file(self):
        tf = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        name = tf.name
        tf.close()

        expected = u'some title{0}=========={0}{0}'.format(os.linesep)

        try:
            # let's just test conversion (to and) from docx, testing e.g. odt
            # as well would really be testing pandoc rather than pypandoc
            received = pypandoc.convert('#some title\n', to='docx', format='md', outputfile=name)
            self.assertEqualExceptForNewlineEnd("", received)
            received = pypandoc.convert(name, to='rst')
            self.assertEqualExceptForNewlineEnd(expected, received)
        except:
            raise
        finally:
            os.remove(name)

    def test_pdf_conversion(self):
        tf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        name = tf.name
        tf.close()

        try:
            pypandoc.convert('#some title\n', to='pdf', format='md', outputfile=name)
        except:
            raise
        finally:
            os.remove(name)

    def assertEqualExceptForNewlineEnd(self, expected, received):
        # output written to a file does not seem to have os.linesep
        # handle everything here by replacing the os linesep by a simple \n
        expected = expected.replace(os.linesep, "\n")
        received = received.replace(os.linesep, "\n")
        self.assertEqual(expected.rstrip('\n'), received.rstrip('\n'))


suite = unittest.TestLoader().loadTestsFromTestCase(TestPypandoc)
ret = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if ret.wasSuccessful() else 1)
