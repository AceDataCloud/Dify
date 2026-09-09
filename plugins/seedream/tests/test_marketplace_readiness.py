from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import yaml


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from tools.acedata_client import AceDataSeedreamClient, AceDataSeedreamError  # noqa: E402


class SeedreamClientSecurityTest(unittest.TestCase):
    @patch("tools.acedata_client.requests.post")
    def test_uses_fixed_public_endpoint_and_authorization_header(
        self, post: Mock
    ) -> None:
        response = Mock(status_code=200)
        response.json.return_value = {"success": True, "trace_id": "trace", "data": []}
        post.return_value = response

        AceDataSeedreamClient(" Bearer secret-token ").generate_images(
            payload={"action": "generate", "prompt": "test"}
        )

        post.assert_called_once_with(
            "https://api.acedata.cloud/seedream/images",
            json={"action": "generate", "prompt": "test"},
            headers={
                "authorization": "Bearer secret-token",
                "accept": "application/json",
                "content-type": "application/json",
            },
            timeout=150,
        )

    @patch("tools.acedata_client.requests.post")
    def test_api_error_redacts_configured_token(self, post: Mock) -> None:
        response = Mock(status_code=401)
        response.json.return_value = {
            "error": {"code": "invalid_token", "message": "Rejected secret-token"},
            "trace_id": "trace-401",
        }
        post.return_value = response

        with self.assertRaises(AceDataSeedreamError) as raised:
            AceDataSeedreamClient("secret-token").generate_images(
                payload={"prompt": "test"}
            )

        self.assertEqual(raised.exception.trace_id, "trace-401")
        self.assertNotIn("secret-token", str(raised.exception))
        self.assertIn("[redacted]", str(raised.exception))

    def test_empty_token_fails_closed(self) -> None:
        with self.assertRaises(AceDataSeedreamError) as raised:
            AceDataSeedreamClient("Bearer  ")
        self.assertEqual(raised.exception.code, "token_empty")


class SeedreamMarketplaceContractTest(unittest.TestCase):
    def test_manifest_does_not_claim_external_verification(self) -> None:
        manifest = yaml.safe_load((PLUGIN_ROOT / "manifest.yaml").read_text())
        self.assertIs(manifest["verified"], False)
        self.assertEqual(manifest["privacy"], "PRIVACY.md")

    def test_package_excludes_development_and_environment_files(self) -> None:
        ignore = (PLUGIN_ROOT / ".difyignore").read_text().splitlines()
        self.assertIn("tests/", ignore)
        self.assertIn(".env.*", ignore)
        self.assertIn("*.difypkg", ignore)

    def test_readme_has_review_setup_cost_support_and_external_gate(self) -> None:
        readme = (PLUGIN_ROOT / "README.md").read_text()
        for text in (
            "https://github.com/AceDataCloud/Dify/tree/main/plugins/seedream",
            "utm_campaign=dify-seedream",
            "can consume credits",
            "current Seedream pricing",
            "success=true",
            "does not represent Dify Marketplace approval or publication",
            "Last contract review: **2026-09-10**",
        ):
            self.assertIn(text, readme)

    def test_privacy_matches_fixed_endpoint_and_no_local_storage(self) -> None:
        privacy = (PLUGIN_ROOT / "PRIVACY.md").read_text()
        self.assertIn("https://api.acedata.cloud/seedream/images", privacy)
        self.assertIn("contains no telemetry code", privacy)
        self.assertIn(
            "does not write prompts, images, responses, or credentials", privacy
        )
        self.assertIn("redacts the configured token", privacy)
        self.assertNotIn("usage data (telemetry)", privacy.lower())


if __name__ == "__main__":
    unittest.main()
