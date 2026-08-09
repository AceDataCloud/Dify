from unittest.mock import Mock, patch

from tools.acedata_client import AceDataMinimaxClient


@patch("tools.acedata_client.requests.post")
def test_generate_async_multimodal_payload(post: Mock):
    response = Mock(status_code=200)
    response.json.return_value = {"task_id": "task-1"}
    post.return_value = response
    client = AceDataMinimaxClient("token", base_url="https://api.test")

    content = [
        {"type": "text", "text": "dance"},
        {
            "type": "image_url",
            "image_url": {"url": "https://a.test/image.png"},
            "role": "reference_image",
        },
        {
            "type": "audio_url",
            "audio_url": {"url": "https://a.test/audio.mp3"},
            "role": "reference_audio",
        },
    ]
    result = client.generate_video(
        content=content,
        resolution="768P",
        ratio="9:16",
        duration=8,
    )

    assert result.task_id == "task-1"
    assert post.call_args.kwargs["json"] == {
        "model": "MiniMax-H3",
        "content": content,
        "resolution": "768P",
        "ratio": "9:16",
        "duration": 8,
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
