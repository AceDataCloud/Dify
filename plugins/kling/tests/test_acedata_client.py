from unittest.mock import Mock, patch

import pytest

from tools.acedata_client import (
    AceDataKlingClient,
    parse_camera_control,
    parse_reference_list,
    validate_video_request,
)


def test_generate_video_forwards_sanitized_omni_references() -> None:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True, "task_id": "task-1"}

    with patch("tools.acedata_client.requests.post", return_value=response) as post:
        result = AceDataKlingClient("token", "https://example.com").generate_video(
            action="text2video",
            model="kling-o1",
            prompt="Use <<<image_1>>>",
            duration=5,
            image_list=[{"image_url": "https://example.com/ref.jpg"}],
            video_list=[
                {
                    "video_url": "https://example.com/ref.mp4",
                    "refer_type": "feature",
                    "keep_original_sound": "yes",
                }
            ],
        )

    assert result.task_id == "task-1"
    assert post.call_args.kwargs["json"]["model"] == "kling-o1"
    assert post.call_args.kwargs["json"]["image_list"] == [
        {"image_url": "https://example.com/ref.jpg"}
    ]
    assert post.call_args.kwargs["json"]["video_list"][0]["refer_type"] == "feature"


def test_generate_video_forwards_async_without_callback() -> None:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"success": True, "task_id": "task-async"}

    with patch("tools.acedata_client.requests.post", return_value=response) as post:
        AceDataKlingClient("token", "https://example.com").generate_video(
            action="text2video",
            model="kling-v3",
            prompt="test",
            async_mode=True,
        )

    assert post.call_args.kwargs["json"]["async"] is True
    assert "callback_url" not in post.call_args.kwargs["json"]


def test_reference_parser_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError, match="Unsupported `image_list` fields"):
        parse_reference_list(
            '[{"image_url":"https://example.com/ref.jpg","element_id":"unsafe"}]',
            field_name="image_list",
            allowed_keys={"image_url", "type"},
        )
    with pytest.raises(ValueError, match="must contain valid JSON"):
        parse_reference_list(
            '[{"image_url": invalid}]',
            field_name="image_list",
            allowed_keys={"image_url", "type"},
        )
    with pytest.raises(ValueError, match="must contain valid JSON"):
        parse_camera_control('{"type": invalid}')


def test_contract_rejects_legacy_model_and_invalid_combinations() -> None:
    with pytest.raises(ValueError, match="Unsupported Kling model"):
        validate_video_request(
            action="text2video",
            model="unknown-kling-model",
            mode="std",
            duration=5,
            start_image_url=None,
            end_image_url=None,
            negative_prompt=None,
            camera_control=None,
            cfg_scale=None,
            image_list=[],
            video_list=[],
            generate_audio=None,
        )

    with pytest.raises(ValueError, match="does not support generate_audio"):
        validate_video_request(
            action="text2video",
            model="kling-o1",
            mode="std",
            duration=5,
            start_image_url=None,
            end_image_url=None,
            negative_prompt=None,
            camera_control=None,
            cfg_scale=None,
            image_list=[],
            video_list=[{"video_url": "https://example.com/ref.mp4"}],
            generate_audio=True,
        )


def test_contract_rejects_invalid_reference_items_and_o1_controls() -> None:
    common = {
        "action": "text2video",
        "model": "kling-o1",
        "mode": "std",
        "duration": 5,
        "start_image_url": None,
        "end_image_url": None,
        "negative_prompt": None,
        "camera_control": None,
        "cfg_scale": None,
        "image_list": [],
        "video_list": [],
        "generate_audio": None,
    }

    with pytest.raises(ValueError, match="does not support generate_audio"):
        validate_video_request(**{**common, "generate_audio": True})
    with pytest.raises(ValueError, match="kling-o1.*does not support"):
        validate_video_request(**{**common, "cfg_scale": 0.5})
    with pytest.raises(ValueError, match="requires an HTTP image_url"):
        validate_video_request(
            **{
                **common,
                "image_list": [{"image_url": "file:///tmp/ref.jpg"}],
            }
        )
    with pytest.raises(ValueError, match="start_image_url.*HTTP URL"):
        validate_video_request(
            **{
                **common,
                "start_image_url": "file:///tmp/start.jpg",
            }
        )


def test_contract_rejects_legacy_model_limits_and_extend_references() -> None:
    common = {
        "action": "text2video",
        "model": "kling-v1",
        "mode": "std",
        "duration": 5,
        "start_image_url": None,
        "end_image_url": None,
        "negative_prompt": None,
        "camera_control": None,
        "cfg_scale": None,
        "image_list": [],
        "video_list": [],
        "generate_audio": None,
    }

    with pytest.raises(ValueError, match="only 5- or 10-second"):
        validate_video_request(**{**common, "duration": 6})
    with pytest.raises(ValueError, match="4k mode requires"):
        validate_video_request(**{**common, "mode": "4k"})
    with pytest.raises(ValueError, match="generate_audio.*requires"):
        validate_video_request(**{**common, "generate_audio": True})
    with pytest.raises(ValueError, match="only in pro mode"):
        validate_video_request(
            **{
                **common,
                "model": "kling-v2-6",
                "generate_audio": True,
            }
        )
    with pytest.raises(ValueError, match="not supported with extend"):
        validate_video_request(
            **{
                **common,
                "action": "extend",
                "image_list": [{"image_url": "https://example.com/ref.jpg"}],
            }
        )
    with pytest.raises(ValueError, match="extend requires"):
        validate_video_request(
            **{
                **common,
                "action": "extend",
                "model": "kling-o1",
            }
        )
    with pytest.raises(ValueError, match="at most one first_frame"):
        validate_video_request(
            **{
                **common,
                "model": "kling-v3-omni",
                "start_image_url": "https://example.com/start.jpg",
                "image_list": [
                    {
                        "image_url": "https://example.com/other-start.jpg",
                        "type": "first_frame",
                    }
                ],
            }
        )
