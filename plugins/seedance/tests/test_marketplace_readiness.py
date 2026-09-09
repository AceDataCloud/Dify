from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import yaml


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from tools.acedata_client import AceDataSeedanceClient, AceDataSeedanceError  # noqa: E402


class SeedanceClientSecurityTest(unittest.TestCase):
    @patch("tools.acedata_client.requests.post")
    def test_uses_fixed_public_endpoint_and_authorization_header(
        self, post: Mock
    ) -> None:
        response = Mock(status_code=200)
        response.json.return_value = {"success": True, "trace_id": "trace", "data": []}
        post.return_value = response

        AceDataSeedanceClient(" Bearer secret-token ").generate_video(prompt="test")

        self.assertEqual(
            post.call_args.args[0], "https://api.acedata.cloud/seedance/videos"
        )
        self.assertEqual(
            post.call_args.kwargs["headers"]["authorization"], "Bearer secret-token"
        )
        self.assertEqual(
            post.call_args.kwargs["json"]["content"], [{"type": "text", "text": "test"}]
        )

    @patch("tools.acedata_client.requests.post")
    def test_api_error_redacts_configured_token(self, post: Mock) -> None:
        response = Mock(status_code=401)
        response.json.return_value = {
            "error": {"code": "invalid_token", "message": "Rejected secret-token"},
            "trace_id": "trace-401",
        }
        post.return_value = response

        with self.assertRaises(AceDataSeedanceError) as raised:
            AceDataSeedanceClient("secret-token").generate_video(prompt="test")

        self.assertEqual(raised.exception.trace_id, "trace-401")
        self.assertNotIn("secret-token", str(raised.exception))
        self.assertIn("[redacted]", str(raised.exception))

    def test_empty_token_fails_closed(self) -> None:
        with self.assertRaises(AceDataSeedanceError) as raised:
            AceDataSeedanceClient("Bearer  ")
        self.assertEqual(raised.exception.code, "token_empty")


class SeedanceMarketplaceContractTest(unittest.TestCase):
    def test_manifest_does_not_claim_external_verification(self) -> None:
        manifest = yaml.safe_load((PLUGIN_ROOT / "manifest.yaml").read_text())
        self.assertIs(manifest["verified"], False)
        self.assertEqual(manifest["privacy"], "PRIVACY.md")

    def test_package_excludes_development_and_environment_files(self) -> None:
        ignore = (PLUGIN_ROOT / ".difyignore").read_text().splitlines()
        self.assertIn("tests/", ignore)
        self.assertIn(".env.*", ignore)
        self.assertIn("*.difypkg", ignore)

    def test_readme_has_sync_review_path_cost_support_and_external_gate(self) -> None:
        readme = (PLUGIN_ROOT / "README.md").read_text()
        for text in (
            "https://github.com/AceDataCloud/Dify/tree/main/plugins/seedance",
            "utm_campaign=dify-seedance",
            "can consume credits",
            "current Seedance pricing",
            "leave `async` disabled",
            "does not expose task retrieval",
            "does not represent Dify Marketplace approval or publication",
            "Last contract review: **2026-09-10**",
        ):
            self.assertIn(text, readme)

    def test_privacy_matches_fixed_endpoint_and_no_local_storage(self) -> None:
        privacy = (PLUGIN_ROOT / "PRIVACY.md").read_text()
        self.assertIn("https://api.acedata.cloud/seedance/videos", privacy)
        self.assertIn("contains no telemetry code", privacy)
        self.assertIn(
            "does not write prompts, referenced media, responses, or credentials",
            privacy,
        )
        self.assertIn("redacts the configured token", privacy)


if __name__ == "__main__":
    unittest.main()
