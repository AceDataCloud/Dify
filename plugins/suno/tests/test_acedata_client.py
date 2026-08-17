from unittest.mock import Mock, patch

import pytest

from tools.acedata_client import AceDataSunoClient


@pytest.mark.parametrize("model", ["default", "remi-v1"])
def test_generate_lyrics_forwards_model(model: str) -> None:
    response = Mock(status_code=200)
    response.json.return_value = {"success": True, "task_id": "task-1", "data": {}}

    with patch("tools.acedata_client.requests.post", return_value=response) as post:
        result = AceDataSunoClient("token", "https://example.com").generate_lyrics(
            prompt="A hopeful summer song",
            model=model,
            timeout_s=120,
        )

    assert result.task_id == "task-1"
    assert post.call_args.args[0] == "https://example.com/suno/lyrics"
    assert post.call_args.kwargs["json"] == {
        "prompt": "A hopeful summer song",
        "model": model,
    }
    assert post.call_args.kwargs["timeout"] == 120


def test_wav_forwards_callback_free_async() -> None:
    response = Mock(status_code=200)
    response.json.return_value = {"success": True, "task_id": "task-1", "data": []}

    with patch("tools.acedata_client.requests.post", return_value=response) as post:
        result = AceDataSunoClient("token", "https://example.com").wav(
            audio_id="audio-1",
            async_mode=True,
        )

    assert result.task_id == "task-1"
    assert post.call_args.kwargs["json"] == {"audio_id": "audio-1", "async": True}
