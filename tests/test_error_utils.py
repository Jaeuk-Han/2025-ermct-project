from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

from app.error_utils import sanitize_error_text
from app.services.ermct_client import ErmctClient


class ErrorUtilsTests(unittest.TestCase):
    def test_sanitize_error_text_redacts_service_key_case_insensitively(self) -> None:
        raw = "request failed: ?serviceKey=secret-value&STAGE1=x"

        self.assertEqual(
            sanitize_error_text(raw),
            "request failed: ?serviceKey=<redacted>&STAGE1=x",
        )

    def test_sanitize_error_text_redacts_encoded_service_key(self) -> None:
        raw = "request failed: ?serviceKey=abc%2Fdef%3D&x=1"

        self.assertNotIn("abc%2Fdef%3D", sanitize_error_text(raw))

    def test_ermct_client_redacts_service_key_before_http_error_escapes(self) -> None:
        response = Mock(status_code=429)
        response.raise_for_status.side_effect = requests.HTTPError(
            "429 for url?serviceKey=raw-secret&x=1",
            response=response,
        )
        with patch("app.services.ermct_client.requests.get", return_value=response):
            with self.assertRaises(requests.HTTPError) as raised:
                ErmctClient(service_key="raw-secret")._get("endpoint", {})

        self.assertNotIn("raw-secret", str(raised.exception))
        self.assertEqual(raised.exception.response.status_code, 429)


if __name__ == "__main__":
    unittest.main()
