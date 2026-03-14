import unittest
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch


class TestUrlopenWithRetry(unittest.TestCase):
    """Tests for _urlopen_with_retry retry and auth behavior."""

    def _get_func(self):
        from pypandoc.pandoc_download import _urlopen_with_retry

        return _urlopen_with_retry

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_succeeds_on_first_try(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        result = self._get_func()("https://example.com/file")

        self.assertEqual(result, mock_response)
        mock_sleep.assert_not_called()

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_retries_on_429(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        error_429 = urllib.error.HTTPError(
            "https://example.com", 429, "Too Many Requests", {}, None
        )
        mock_opener = MagicMock()
        mock_opener.open.side_effect = [error_429, mock_response]
        mock_build_opener.return_value = mock_opener

        result = self._get_func()("https://example.com/file")

        self.assertEqual(result, mock_response)
        self.assertEqual(mock_opener.open.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_retries_on_5xx(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        error_503 = urllib.error.HTTPError(
            "https://example.com", 503, "Service Unavailable", {}, None
        )
        mock_opener = MagicMock()
        mock_opener.open.side_effect = [error_503, mock_response]
        mock_build_opener.return_value = mock_opener

        result = self._get_func()("https://example.com/file")

        self.assertEqual(result, mock_response)
        self.assertEqual(mock_opener.open.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_raises_after_max_retries(self, mock_build_opener, mock_sleep):
        error_429 = urllib.error.HTTPError(
            "https://example.com", 429, "Too Many Requests", {}, None
        )
        mock_opener = MagicMock()
        mock_opener.open.side_effect = error_429
        mock_build_opener.return_value = mock_opener

        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get_func()("https://example.com/file", max_retries=3)

        self.assertEqual(ctx.exception.code, 429)
        # 1 initial + 3 retries = 4 calls
        self.assertEqual(mock_opener.open.call_count, 4)
        self.assertEqual(mock_sleep.call_count, 3)

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_does_not_retry_on_404(self, mock_build_opener, mock_sleep):
        error_404 = urllib.error.HTTPError(
            "https://example.com", 404, "Not Found", {}, None
        )
        mock_opener = MagicMock()
        mock_opener.open.side_effect = error_404
        mock_build_opener.return_value = mock_opener

        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get_func()("https://example.com/file")

        self.assertEqual(ctx.exception.code, 404)
        self.assertEqual(mock_opener.open.call_count, 1)
        mock_sleep.assert_not_called()

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_respects_retry_after_header(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        headers = MagicMock()
        headers.get.return_value = "30"
        error_429 = urllib.error.HTTPError(
            "https://example.com", 429, "Too Many Requests", headers, None
        )
        mock_opener = MagicMock()
        mock_opener.open.side_effect = [error_429, mock_response]
        mock_build_opener.return_value = mock_opener

        self._get_func()("https://example.com/file")

        # sleep should be called with ~30 + jitter (0-1)
        sleep_val = mock_sleep.call_args[0][0]
        self.assertGreaterEqual(sleep_val, 30.0)
        self.assertLess(sleep_val, 31.0)

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_exponential_backoff_timing(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        error_429 = urllib.error.HTTPError(
            "https://example.com", 429, "Too Many Requests", {}, None
        )
        mock_opener = MagicMock()
        mock_opener.open.side_effect = [error_429, error_429, error_429, mock_response]
        mock_build_opener.return_value = mock_opener

        self._get_func()("https://example.com/file", backoff_factor=1.0)

        self.assertEqual(mock_sleep.call_count, 3)
        # Check backoff values: 2^0+jitter, 2^1+jitter, 2^2+jitter
        for i, call in enumerate(mock_sleep.call_args_list):
            sleep_val = call[0][0]
            expected_base = 1.0 * (2**i)
            self.assertGreaterEqual(sleep_val, expected_base)
            self.assertLess(sleep_val, expected_base + 1.0)

    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_max_backoff_cap(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        error_429 = urllib.error.HTTPError(
            "https://example.com", 429, "Too Many Requests", {}, None
        )
        mock_opener = MagicMock()
        # Force enough retries to exceed max_backoff
        mock_opener.open.side_effect = [
            error_429,
            error_429,
            error_429,
            error_429,
            mock_response,
        ]
        mock_build_opener.return_value = mock_opener

        self._get_func()(
            "https://example.com/file", backoff_factor=10.0, max_backoff=15.0
        )

        for call in mock_sleep.call_args_list:
            sleep_val = call[0][0]
            # max_backoff(15) + max_jitter(1) = 16
            self.assertLess(sleep_val, 16.0)

    @patch.dict("os.environ", {"GITHUB_TOKEN": "ghp_test123"})
    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_adds_auth_header_for_github(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        self._get_func()("https://api.github.com/repos/jgm/pandoc/releases/latest")

        req = mock_opener.open.call_args[0][0]
        self.assertEqual(req.get_header("Authorization"), "token ghp_test123")

    @patch.dict("os.environ", {"GITHUB_TOKEN": "ghp_test123"})
    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_no_auth_header_for_non_github(self, mock_build_opener, mock_sleep):
        mock_response = MagicMock()
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        self._get_func()("https://example.com/file")

        req = mock_opener.open.call_args[0][0]
        self.assertIsNone(req.get_header("Authorization"))

    @patch.dict("os.environ", {}, clear=False)
    @patch("pypandoc.pandoc_download.time.sleep")
    @patch("pypandoc.pandoc_download.urllib.request.build_opener")
    def test_no_auth_header_without_token(self, mock_build_opener, mock_sleep):
        # Remove GITHUB_TOKEN if present
        import os

        os.environ.pop("GITHUB_TOKEN", None)

        mock_response = MagicMock()
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        self._get_func()("https://api.github.com/repos/jgm/pandoc/releases/latest")

        req = mock_opener.open.call_args[0][0]
        self.assertIsNone(req.get_header("Authorization"))


class TestNoAuthRedirectHandler(unittest.TestCase):
    """Tests for _NoAuthRedirectHandler stripping auth on cross-domain redirects."""

    def _get_handler_class(self):
        from pypandoc.pandoc_download import _NoAuthRedirectHandler

        return _NoAuthRedirectHandler

    def test_strips_auth_on_cross_domain_redirect(self):
        handler = self._get_handler_class()()
        req = urllib.request.Request(
            "https://github.com/jgm/pandoc/releases/download/3.1/pandoc.deb",
            headers={"Authorization": "token ghp_test123"},
        )
        # Simulate a 302 redirect to S3
        new_req = handler.redirect_request(
            req,
            None,
            302,
            "Found",
            {},
            "https://objects.githubusercontent.com/some-presigned-url",
        )
        self.assertIsNotNone(new_req)
        self.assertIsNone(new_req.get_header("Authorization"))

    def test_keeps_auth_on_same_domain_redirect(self):
        handler = self._get_handler_class()()
        req = urllib.request.Request(
            "https://github.com/jgm/pandoc/releases/latest",
            headers={"Authorization": "token ghp_test123"},
        )
        new_req = handler.redirect_request(
            req,
            None,
            302,
            "Found",
            {},
            "https://github.com/jgm/pandoc/releases/tag/3.1",
        )
        self.assertIsNotNone(new_req)
        self.assertEqual(new_req.get_header("Authorization"), "token ghp_test123")


if __name__ == "__main__":
    unittest.main()
