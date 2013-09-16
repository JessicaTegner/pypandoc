# -*- coding: utf-8 -*-

try:
    from .pypandoc import convert
except SyntaxError:
    from pypandoc import convert

__author__ = 'Juho Vepsäläinen'
__version__ = '0.6.0'
__license__ = 'MIT'

