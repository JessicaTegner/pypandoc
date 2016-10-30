#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import tempfile
import pypandoc
from pypandoc.py3compat import unicode_type, string_types
import os
import io
import sys
import warnings

import contextlib
import shutil
import subprocess


@contextlib.contextmanager
def closed_tempfile(suffix, text=None):
    with tempfile.NamedTemporaryFile('w+t', suffix=suffix, delete=False) as test_file:
        file_name = test_file.name
        if text:
            test_file.write(text)
            test_file.flush()
    yield file_name
    shutil.rmtree(file_name, ignore_errors=True)


# Stolen from pandas
def is_list_like(arg):
    return (hasattr(arg, '__iter__') and
            not isinstance(arg, string_types))


@contextlib.contextmanager
def assert_produces_warning(expected_warning=Warning, filter_level="always",
                            clear=None, check_stacklevel=True):
    """
    Context manager for running code that expects to raise (or not raise)
    warnings.  Checks that code raises the expected warning and only the
    expected warning. Pass ``False`` or ``None`` to check that it does *not*
    raise a warning. Defaults to ``exception.Warning``, baseclass of all
    Warnings. (basically a wrapper around ``warnings.catch_warnings``).
    >>> import warnings
    >>> with assert_produces_warning():
    ...     warnings.warn(UserWarning())
    ...
    >>> with assert_produces_warning(False):
    ...     warnings.warn(RuntimeWarning())
    ...
    Traceback (most recent call last):
        ...
    AssertionError: Caused unexpected warning(s): ['RuntimeWarning'].
    >>> with assert_produces_warning(UserWarning):
    ...     warnings.warn(RuntimeWarning())
    Traceback (most recent call last):
        ...
    AssertionError: Did not see expected warning of class 'UserWarning'.
    ..warn:: This is *not* thread-safe.
    """
    with warnings.catch_warnings(record=True) as w:

        if clear is not None:
            # make sure that we are clearning these warnings
            # if they have happened before
            # to guarantee that we will catch them
            if not is_list_like(clear):
                clear = [clear]
            for m in clear:
                try:
                    m.__warningregistry__.clear()
                except:
                    pass

        saw_warning = False
        warnings.simplefilter(filter_level)
        yield w
        extra_warnings = []

        for actual_warning in w:
            if (expected_warning and issubclass(actual_warning.category,
                                                expected_warning)):
                saw_warning = True

                if check_stacklevel and issubclass(actual_warning.category,
                                                   (FutureWarning,
                                                    DeprecationWarning)):
                    from inspect import getframeinfo, stack
                    caller = getframeinfo(stack()[2][0])
                    msg = ("Warning not set with correct stacklevel. "
                           "File where warning is raised: {0} != {1}. "
                           "Warning message: {2}".format(
                               actual_warning.filename, caller.filename,
                               actual_warning.message))
                    assert actual_warning.filename == caller.filename, msg
            else:
                extra_warnings.append(actual_warning.category.__name__)
        if expected_warning:
            assert saw_warning, ("Did not see expected warning of class %r."
                                 % expected_warning.__name__)
        assert not extra_warnings, ("Caused unexpected warning(s): %r."
                                    % extra_warnings)


class TestPypandoc(unittest.TestCase):

    def setUp(self):
        if 'HOME' not in os.environ:
            # if this is used with older versions of pandoc-citeproc
            # https://github.com/jgm/pandoc-citeproc/issues/35
            if 'TRAVIS_BUILD_DIR' in os.environ:
                os.environ["HOME"] = os.environ["TRAVIS_BUILD_DIR"]
                print("Using TRAVIS_BUILD_DIR as HOME")
            else:
                os.environ["HOME"] = str(os.getcwd())
                print("Using current dir as HOME")
        print(os.environ["HOME"])

    def test_get_pandoc_formats(self):
        inputs, outputs = pypandoc.get_pandoc_formats()
        self.assertTrue("markdown" in inputs)
        self.assertTrue("json" in inputs)
        self.assertTrue("twiki" in inputs)
        self.assertTrue("markdown" in outputs)

    def test_get_pandoc_version(self):
        assert "HOME" in os.environ, "No HOME set, this will error..."
        version = pypandoc.get_pandoc_version()
        self.assertTrue(isinstance(version, pypandoc.string_types))
        major = int(version.split(".")[0])
        # according to http://pandoc.org/releases.html there were only two versions 0.x ...
        self.assertTrue(major in [0, 1])

    def test_converts_valid_format(self):
        self.assertEqualExceptForNewlineEnd(pypandoc.convert("ok", format='md', to='rest'), 'ok')

    def test_does_not_convert_to_invalid_format(self):
        def f():
            pypandoc.convert("ok", format='md', to='invalid')
        self.assertRaises(RuntimeError, f)

    def test_does_not_convert_from_invalid_format(self):
        def f():
            pypandoc.convert("ok", format='invalid', to='rest')
        self.assertRaises(RuntimeError, f)

    def test_basic_conversion_from_file(self):
        with closed_tempfile('.md', text='#some title\n') as file_name:
            expected = u'some title{0}=========={0}{0}'.format(os.linesep)
            received = pypandoc.convert(file_name, 'rst')
            self.assertEqualExceptForNewlineEnd(expected, received)

    def test_convert_with_custom_writer(self):
        lua_file_content = self.create_sample_lua()
        with closed_tempfile('.md', text='#title\n') as file_name:
            with closed_tempfile('.lua', text=lua_file_content) as lua_file_name:
                expected = u'<h1 id="title">title</h1>{0}'.format(os.linesep)
                received = pypandoc.convert_file(file_name, lua_file_name)
                self.assertEqualExceptForNewlineEnd(expected, received)

    def test_basic_conversion_from_file_with_format(self):
        with closed_tempfile('.md', text='#some title\n') as file_name:
            expected = u'some title{0}=========={0}{0}'.format(os.linesep)
            received = pypandoc.convert(file_name, 'rst', format='md')
            self.assertEqualExceptForNewlineEnd(expected, received)

            received = pypandoc.convert_file(file_name, 'rst', format='md')
            self.assertEqualExceptForNewlineEnd(expected, received)

    def test_basic_conversion_from_string(self):
        expected = u'some title{0}=========={0}{0}'.format(os.linesep)
        received = pypandoc.convert('#some title', 'rst', format='md')
        self.assertEqualExceptForNewlineEnd(expected, received)

        expected = u'some title{0}=========={0}{0}'.format(os.linesep)
        received = pypandoc.convert_text('#some title', 'rst', format='md')
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
        with closed_tempfile('.rst',) as file_name:
            expected = u'some title{0}=========={0}{0}'.format(os.linesep)
            received = pypandoc.convert('#some title\n', to='rst', format='md', outputfile=file_name)
            self.assertEqualExceptForNewlineEnd("", received)
            with io.open(file_name) as f:
                written = f.read()
            self.assertEqualExceptForNewlineEnd(expected, written)

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
        self.assertTrue(isinstance(written, unicode_type))
        self.assertEqualExceptForNewlineEnd(expected, written)
        bytes = u'<h1>üäöîôû</h1>'.encode("utf-8")
        written = pypandoc.convert(bytes, 'md', format='html')
        self.assertEqualExceptForNewlineEnd(expected, written)
        self.assertTrue(isinstance(written, unicode_type))

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
        self.assertTrue(isinstance(written, unicode_type))

    def test_conversion_from_non_plain_text_file(self):
        with closed_tempfile('.docx') as file_name:
            expected = u'some title{0}=========={0}{0}'.format(os.linesep)
            # let's just test conversion (to and) from docx, testing e.g. odt
            # as well would really be testing pandoc rather than pypandoc
            received = pypandoc.convert('#some title\n', to='docx', format='md', outputfile=file_name)
            self.assertEqualExceptForNewlineEnd("", received)
            received = pypandoc.convert(file_name, to='rst')
            self.assertEqualExceptForNewlineEnd(expected, received)

    def test_pdf_conversion(self):
        with closed_tempfile('.pdf') as file_name:
            ret = pypandoc.convert_text('#some title\n', to='pdf', format='md', outputfile=file_name)
            assert ret == ""
            with io.open(file_name, mode='rb') as f:
                written = f.read()
            assert written[:4] == b"%PDF"
            # TODO: find a test for the content?

        def f():
            # needs an outputfile
            pypandoc.convert_text('#some title\n', to='pdf', format='md')

        self.assertRaises(RuntimeError, f)

        def f():
            # outputfile needs to end in pdf
            with closed_tempfile('.WRONG') as file_name:
                pypandoc.convert_text('#some title\n', to='pdf', format='md', outputfile=file_name)

        self.assertRaises(RuntimeError, f)

        def f():
            # no extensions allowed
            with closed_tempfile('.pdf') as file_name:
                pypandoc.convert_text('#some title\n', to='pdf+somethign', format='md', outputfile=file_name)

        self.assertRaises(RuntimeError, f)

    def test_get_pandoc_path(self):
        result = pypandoc.get_pandoc_path()
        assert "pandoc" in result

    def test_call_with_nonexisting_file(self):
        files = ['/file/does/not/exists.md',
                 '',
                 42,
                 None
                 ]

        def f(filepath):
            pypandoc.convert(filepath, 'rst')

        for filepath in files:
            self.assertRaises(RuntimeError, f, filepath)

        def f(filepath):
            pypandoc.convert_file(filepath, 'rst')

        for filepath in files:
            self.assertRaises(RuntimeError, f, filepath)

    def test_convert_text_with_existing_file(self):
        with closed_tempfile('.md', text='#some title\n') as file_name:
            received = pypandoc.convert_text(file_name, 'rst', format='md')
            self.assertTrue("title" not in received)

            # The following is a problematic case
            received = pypandoc.convert(file_name, 'rst', format='md')
            self.assertTrue("title" in received)

    def test_depreaction_warnings(self):
        # convert itself is deprecated...
        with assert_produces_warning(DeprecationWarning):
            pypandoc.convert('#some title\n', to='rst', format='md')

    def create_sample_lua(self):
        args = [pypandoc.get_pandoc_path(), '--print-default-data-file', 'sample.lua']
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = p.communicate()
        return out.decode('utf-8')

    def assertEqualExceptForNewlineEnd(self, expected, received):
        # output written to a file does not seem to have os.linesep
        # handle everything here by replacing the os linesep by a simple \n
        expected = expected.replace(os.linesep, "\n")
        received = received.replace(os.linesep, "\n")
        self.assertEqual(expected.rstrip('\n'), received.rstrip('\n'))


suite = unittest.TestLoader().loadTestsFromTestCase(TestPypandoc)
ret = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if ret.wasSuccessful() else 1)
