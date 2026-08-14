from unittest.mock import Mock, patch

from tools.acedata_client import AceDataSeedanceClient


def test_generate_seedance_25_multimodal_payload_and_object_response() -> None:
    response = Mock(status_code=200)
    response.json.return_value = {
        "success": True,
        "task_id": "public-task",
        "trace_id": "trace-id",
        "data": {
            "model": "doubao-seedance-2-5-260628",
            "status": "succeeded",
            "content": {"video_url": "https://cdn.test/video.mov"},
        },
    }
    with patch("tools.acedata_client.requests.post", return_value=response) as post:
        result = AceDataSeedanceClient("token").generate_video(
            model="doubao-seedance-2-5-260628",
            prompt="Extend the shot",
            reference_audio_urls=["https://cdn.test/audio.mp3"],
            reference_video_urls=["https://cdn.test/input.mp4"],
            resolution="720p",
            ratio="adaptive",
            duration=30,
            omni_reference_task_type="extend",
            output_format="mov",
            tools=[{"type": "web_search"}],
            async_mode=True,
        )
    payload = post.call_args.kwargs["json"]
    assert payload["content"][1]["role"] == "reference_audio"
    assert payload["content"][2]["role"] == "reference_video"
    assert payload["omni_reference_task_type"] == "extend"
    assert payload["output_format"] == "mov"
    assert payload["tools"] == [{"type": "web_search"}]
    assert payload["async"] is True
    assert result.video_urls == ["https://cdn.test/video.mov"]


def test_seedance_20_omits_seedance_25_options() -> None:
    response = Mock(status_code=200)
    response.json.return_value = {"success": True, "task_id": "task", "data": {}}
    with patch("tools.acedata_client.requests.post", return_value=response) as post:
        AceDataSeedanceClient("token").generate_video(
            model="doubao-seedance-2-0-260128",
            prompt="A scene",
        )
    payload = post.call_args.kwargs["json"]
    assert "output_format" not in payload
    assert "omni_reference_task_type" not in payload
