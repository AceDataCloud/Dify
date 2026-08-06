from unittest.mock import Mock, patch

import pytest

from tools.acedata_client import AceDataMinimaxClient, parse_urls


def test_parse_urls_accepts_array_and_enforces_limits():
    assert parse_urls([" https://a.test/1.png ", "https://a.test/2.png"], field_name="image_urls", limit=9) == [
        "https://a.test/1.png",
        "https://a.test/2.png",
    ]
    with pytest.raises(ValueError, match="at most 3"):
        parse_urls(["a", "b", "c", "d"], field_name="audio_urls", limit=3)


@patch("tools.acedata_client.requests.post")
def test_generate_async_multimodal_payload(post: Mock):
    response = Mock(status_code=200)
    response.json.return_value = {"task_id": "task-1"}
    post.return_value = response
    client = AceDataMinimaxClient("token", base_url="https://api.test")

    result = client.generate_video(
        prompt="dance",
        image_urls=["https://a.test/image.png"],
        audio_urls=["https://a.test/audio.mp3"],
        ratio="9:16",
        duration=8,
        async_mode=True,
    )

    assert result.task_id == "task-1"
    assert post.call_args.kwargs["json"] == {
        "model": "minimax-h3",
        "prompt": "dance",
        "image_urls": ["https://a.test/image.png"],
        "audio_urls": ["https://a.test/audio.mp3"],
        "ratio": "9:16",
        "duration": 8,
        "async": True,
    }


@patch("tools.acedata_client.requests.post")
def test_retrieve_task_payload(post: Mock):
    response = Mock(status_code=200)
    response.json.return_value = {"id": "task-1", "response": {"success": True}}
    post.return_value = response
    client = AceDataMinimaxClient("token", base_url="https://api.test")

    result = client.retrieve_task(task_id="task-1")

    assert result["id"] == "task-1"
    assert post.call_args.kwargs["json"] == {"action": "retrieve", "id": "task-1"}
