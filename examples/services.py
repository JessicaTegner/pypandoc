# -*- coding: utf-8 -*-
"""
Example Services for using pypandoc
"""
from tempfile import NamedTemporaryFile

import pypandoc


class BasePandocService(object):
    """
    Base class for converting provided HTML to a doc or docx
    """
    file_object = None

    def __init__(self):
        self.service = self.get_service()

    def get_service(self):
        return pypandoc

    def generate(self, **kwargs):
        raise NotImplementedError


class PandocPDFService(BasePandocService):
    """
    Generate html to pdf format
    """
    def generate(self, html, **kwargs):
        """
        generate the pdf but needs to be set as tex so pandoc handles it
        correctly see docs: http://johnmacfarlane.net/pandoc/ #search pdf
        """
        from_format = kwargs.get('from_format', 'html')
        to_format = kwargs.get('to_format', 'tex')
        # create temp file
        self.file_object = NamedTemporaryFile(suffix='.pdf')

        extra_args = (
            '--smart',
            '--standalone',
            '-o', self.file_object.name
        )
        # generate it using pandoc
        self.service.convert(html, to_format, format=from_format, extra_args=extra_args)
        # return the file which is now populated with the docx forms
        return self.file_object


class PandocDocxService(BasePandocService):
    """
    Generate html to docx format
    """
    def generate(self, html, **kwargs):
        from_format = kwargs.get('from_format', 'html')
        to_format = kwargs.get('to_format', 'docx')
        # create temp file
        self.file_object = NamedTemporaryFile(suffix='.docx')

        extra_args = (
            '--smart',
            '--standalone',
            '-o', self.file_object.name
        )
        # generate it using pandoc
        self.service.convert(html, to_format, format=from_format, extra_args=extra_args)
        # return the file which is now populated with the docx forms
        return self.file_object
