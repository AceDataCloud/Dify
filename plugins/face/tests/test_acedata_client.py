from unittest.mock import Mock, patch

import pytest

from tools.acedata_client import ACTION_PATHS, AceDataFaceClient


@pytest.mark.parametrize(
    ("action", "path"),
    [
        ("keypoints", "/face/analyze"),
        ("beautify", "/face/beautify"),
        ("age", "/face/change-age"),
        ("gender", "/face/change-gender"),
        ("swap", "/face/swap"),
        ("cartoon", "/face/cartoon"),
        ("liveness", "/face/detect-live"),
    ],
)
def test_action_uses_canonical_path(action: str, path: str) -> None:
    response = Mock(status_code=200)
    response.json.return_value = {"success": True, "data": {}}

    with patch("tools.acedata_client.requests.post", return_value=response) as post:
        AceDataFaceClient("token", "https://example.com").invoke(action=action, payload={})

    assert ACTION_PATHS[action] == path
    assert post.call_args.args[0] == f"https://example.com{path}"
