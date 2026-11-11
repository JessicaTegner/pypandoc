#!/usr/bin/env python

import unittest

import pypandoc


class TestIdentifyFormatFromPath(unittest.TestCase):
    def test_uppercase_extension_is_lowercased(self):
        # "README.MD" must resolve to "markdown" via normalize_format;
        # before the fix the detected "MD" was rejected as an invalid format.
        detected = pypandoc._identify_format_from_path("README.MD", None)
        self.assertEqual(detected, "md")
        self.assertEqual(pypandoc.normalize_format(detected), "markdown")

    def test_lowercase_extension_unchanged(self):
        self.assertEqual(
            pypandoc._identify_format_from_path("doc.md", None), "md"
        )

    def test_explicit_format_takes_precedence(self):
        self.assertEqual(
            pypandoc._identify_format_from_path("README.MD", "html"), "html"
        )


if __name__ == "__main__":
    unittest.main()
