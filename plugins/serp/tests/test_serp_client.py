from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from tools.acedata_client import AceDataSerpClient, AceDataSerpError  # noqa: E402


class SerpClientTest(unittest.TestCase):
    @patch("tools.acedata_client.requests.post")
    def test_sends_only_requested_search_fields_to_fixed_api(self, post: Mock) -> None:
        response = Mock(status_code=200)
        response.json.return_value = {"success": True, "trace_id": "trace", "data": {"items": []}}
        post.return_value = response

        result = AceDataSerpClient(" Bearer secret-token ").google(
            query="dify plugin",
            type="news",
            country="US",
            number=5,
        )

        self.assertEqual(result.trace_id, "trace")
        post.assert_called_once_with(
            "https://api.acedata.cloud/serp/google",
            json={"query": "dify plugin", "type": "news", "country": "US", "number": 5},
            headers={
                "authorization": "Bearer secret-token",
                "accept": "application/json",
                "content-type": "application/json",
            },
            timeout=60,
        )

    @patch("tools.acedata_client.requests.post")
    def test_preserves_structured_api_error_and_trace(self, post: Mock) -> None:
        response = Mock(status_code=401)
        response.json.return_value = {
            "error": {"code": "invalid_token", "message": "Token is invalid."},
            "trace_id": "trace-401",
        }
        post.return_value = response

        with self.assertRaises(AceDataSerpError) as raised:
            AceDataSerpClient("secret-token").google(query="test")

        self.assertEqual(raised.exception.code, "invalid_token")
        self.assertEqual(raised.exception.trace_id, "trace-401")
        self.assertEqual(raised.exception.status_code, 401)

    @patch("tools.acedata_client.requests.post")
    def test_network_error_does_not_include_token(self, post: Mock) -> None:
        import requests

        post.side_effect = requests.Timeout("request timed out")
        with self.assertRaises(AceDataSerpError) as raised:
            AceDataSerpClient("secret-token").google(query="test")

        self.assertEqual(raised.exception.code, "request_failed")
        self.assertNotIn("secret-token", str(raised.exception))

    def test_empty_token_fails_closed(self) -> None:
        with self.assertRaises(AceDataSerpError) as raised:
            AceDataSerpClient("Bearer  ")
        self.assertEqual(raised.exception.code, "token_empty")


class MarketplaceDocumentationTest(unittest.TestCase):
    def test_package_excludes_development_and_environment_files(self) -> None:
        ignore = (PLUGIN_ROOT / ".difyignore").read_text().splitlines()
        self.assertIn("tests/", ignore)
        self.assertIn(".env.*", ignore)

    def test_readme_links_source_and_token_setup(self) -> None:
        readme = (PLUGIN_ROOT / "README.md").read_text()
        self.assertIn("https://github.com/AceDataCloud/Dify/tree/main/plugins/serp", readme)
        self.assertIn("https://platform.acedata.cloud", readme)

    def test_privacy_discloses_actual_query_flow_without_telemetry_claim(self) -> None:
        privacy = (PLUGIN_ROOT / "PRIVACY.md").read_text()
        self.assertIn("search query", privacy.lower())
        self.assertIn("https://api.acedata.cloud/serp/google", privacy)
        self.assertIn("does not write queries, responses, or credentials", privacy.lower())
        self.assertIn("contains no telemetry code", privacy.lower())
        self.assertNotIn("usage data (telemetry)", privacy.lower())
        self.assertNotIn("if telemetry is enabled", privacy.lower())


if __name__ == "__main__":
    unittest.main()
