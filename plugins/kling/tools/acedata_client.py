from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests


KLING_MODELS = {
    "kling-v1",
    "kling-v1-6",
    "kling-v2-master",
    "kling-v2-1-master",
    "kling-v2-5-turbo",
    "kling-v2-6",
    "kling-v3",
    "kling-v3-omni",
    "kling-o1",
}
KLING_OMNI_MODELS = {"kling-v3-omni", "kling-o1"}


def _is_http_url(value: Any) -> bool:
    return isinstance(value, str) and urlparse(value).scheme in {"http", "https"}


@dataclass(frozen=True)
class AceDataKlingError(RuntimeError):
    code: str
    message: str
    trace_id: str | None = None
    status_code: int | None = None

    def __str__(self) -> str:
        trace_suffix = f" (trace_id={self.trace_id})" if self.trace_id else ""
        status_suffix = f" (status={self.status_code})" if self.status_code else ""
        return f"{self.code}: {self.message}{trace_suffix}{status_suffix}"


@dataclass(frozen=True)
class AceDataKlingVideosResult:
    task_id: str | None
    trace_id: str | None
    data: dict[str, Any]

    @property
    def video_url(self) -> str | None:
        value = self.data.get("video_url")
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    @property
    def video_id(self) -> str | None:
        value = self.data.get("video_id")
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None


def _normalize_token(raw_token: str) -> str:
    token = raw_token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token


class AceDataKlingClient:
    def __init__(
        self, bearer_token: str, base_url: str = "https://api.acedata.cloud"
    ) -> None:
        token = _normalize_token(bearer_token)
        if not token:
            raise AceDataKlingError(code="token_empty", message="Empty bearer token.")

        self._token = token
        self._base_url = base_url.rstrip("/")

    def generate_video(
        self,
        *,
        action: str,
        model: str | None = None,
        mode: str | None = None,
        prompt: str | None = None,
        start_image_url: str | None = None,
        end_image_url: str | None = None,
        negative_prompt: str | None = None,
        aspect_ratio: str | None = None,
        duration: int | None = None,
        camera_control: dict[str, Any] | None = None,
        cfg_scale: float | None = None,
        image_list: list[dict[str, Any]] | None = None,
        video_list: list[dict[str, Any]] | None = None,
        callback_url: str | None = None,
        async_mode: bool | None = None,
        video_id: str | None = None,
        mirror: bool | None = None,
        generate_audio: bool | None = None,
        timeout_s: int = 1800,
    ) -> AceDataKlingVideosResult:
        payload: dict[str, Any] = {"action": action}
        if model:
            payload["model"] = model
        if mode:
            payload["mode"] = mode
        if prompt:
            payload["prompt"] = prompt
        if start_image_url:
            payload["start_image_url"] = start_image_url
        if end_image_url:
            payload["end_image_url"] = end_image_url
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if aspect_ratio:
            payload["aspect_ratio"] = aspect_ratio
        if duration is not None:
            payload["duration"] = duration
        if camera_control is not None:
            payload["camera_control"] = camera_control
        if cfg_scale is not None:
            payload["cfg_scale"] = cfg_scale
        if image_list:
            payload["image_list"] = image_list
        if video_list:
            payload["video_list"] = video_list
        if callback_url:
            payload["callback_url"] = callback_url
        if async_mode:
            payload["async"] = True
        if video_id:
            payload["video_id"] = video_id
        if mirror is not None:
            payload["mirror"] = mirror
        if generate_audio is not None:
            payload["generate_audio"] = generate_audio

        body = self._post_json(
            path="/kling/videos", payload=payload, timeout_s=timeout_s
        )
        return AceDataKlingVideosResult(
            task_id=body.get("task_id")
            if isinstance(body.get("task_id"), str)
            else None,
            trace_id=body.get("trace_id")
            if isinstance(body.get("trace_id"), str)
            else None,
            data=body,
        )

    def _post_json(
        self, *, path: str, payload: dict[str, Any], timeout_s: int
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = {
            "authorization": f"Bearer {self._token}",
            "accept": "application/json",
            "content-type": "application/json",
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
        except requests.RequestException as e:
            raise AceDataKlingError(code="request_failed", message=str(e)) from e

        try:
            body = resp.json()
        except ValueError as e:
            snippet = (resp.text or "")[:500]
            raise AceDataKlingError(
                code="invalid_json",
                message=f"Invalid JSON response: {snippet}",
                status_code=resp.status_code,
            ) from e

        if not isinstance(body, dict):
            raise AceDataKlingError(
                code="invalid_payload",
                message=f"Invalid response payload: {type(body).__name__}",
                status_code=resp.status_code,
            )

        if resp.status_code >= 400:
            trace_id = (
                body.get("trace_id") if isinstance(body.get("trace_id"), str) else None
            )
            error = body.get("error") if isinstance(body.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), str) else None
            message = (
                error.get("message") if isinstance(error.get("message"), str) else None
            )
            raise AceDataKlingError(
                code=code or "error",
                message=message or str(body),
                trace_id=trace_id,
                status_code=resp.status_code,
            )

        if "success" in body and body.get("success") is not True:
            trace_id = (
                body.get("trace_id") if isinstance(body.get("trace_id"), str) else None
            )
            error = body.get("error") if isinstance(body.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), str) else None
            message = (
                error.get("message") if isinstance(error.get("message"), str) else None
            )
            raise AceDataKlingError(
                code=code or "api_error",
                message=message or str(body),
                trace_id=trace_id,
                status_code=resp.status_code,
            )

        return body


def parse_camera_control(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.startswith("{"):
            import json

            try:
                loaded = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError("`camera_control` must contain valid JSON.") from exc
            if not isinstance(loaded, dict):
                raise ValueError("`camera_control` must be a JSON object.")
            return loaded
        raise ValueError("`camera_control` must be a JSON object.")
    raise ValueError("`camera_control` must be an object or a JSON object string.")


def parse_reference_list(
    value: Any,
    *,
    field_name: str,
    allowed_keys: set[str],
) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        import json

        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"`{field_name}` must contain valid JSON.") from exc
    if not isinstance(value, list):
        raise ValueError(f"`{field_name}` must be an array of objects.")

    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"Every `{field_name}` item must be an object.")
        unknown = set(item) - allowed_keys
        if unknown:
            raise ValueError(
                f"Unsupported `{field_name}` fields: {', '.join(sorted(unknown))}."
            )
        result.append(dict(item))
    return result


def validate_video_request(
    *,
    action: str,
    model: str | None,
    mode: str | None,
    duration: int | None,
    start_image_url: str | None,
    end_image_url: str | None,
    negative_prompt: str | None,
    camera_control: dict[str, Any] | None,
    cfg_scale: float | None,
    image_list: list[dict[str, Any]],
    video_list: list[dict[str, Any]],
    generate_audio: bool | None,
) -> None:
    if action not in {"text2video", "image2video", "extend"}:
        raise ValueError("`action` must be text2video, image2video, or extend.")
    if model is None:
        raise ValueError("`model` is required.")
    if model not in KLING_MODELS:
        raise ValueError(f"Unsupported Kling model: {model}.")
    if mode is not None and mode not in {"std", "pro", "4k"}:
        raise ValueError("`mode` must be std, pro, or 4k.")
    if cfg_scale is not None and not 0 <= cfg_scale <= 1:
        raise ValueError("`cfg_scale` must be between 0 and 1.")
    if (
        model in {"kling-v3", "kling-v3-omni"}
        and duration is not None
        and not 3 <= duration <= 15
    ):
        raise ValueError(
            "Kling V3 models support integer durations from 3 to 15 seconds."
        )
    if model == "kling-o1" and duration not in {None, 5}:
        raise ValueError("`kling-o1` supports only 5-second generation.")
    if model == "kling-o1" and mode not in {None, "std", "pro"}:
        raise ValueError("`kling-o1` supports only std and pro modes.")
    if model not in {"kling-v3", "kling-v3-omni", "kling-o1"} and duration not in {
        None,
        5,
        10,
    }:
        raise ValueError("This Kling model supports only 5- or 10-second generation.")
    if mode == "4k" and model not in {"kling-v3", "kling-v3-omni"}:
        raise ValueError("4k mode requires `kling-v3` or `kling-v3-omni`.")
    if action == "extend" and model not in {
        "kling-v1",
        "kling-v1-6",
        "kling-v2-5-turbo",
    }:
        raise ValueError("extend requires kling-v1, kling-v1-6, or kling-v2-5-turbo.")
    if action == "extend" and (image_list or video_list):
        raise ValueError("`image_list` and `video_list` are not supported with extend.")
    if model == "kling-o1" and generate_audio:
        raise ValueError("`kling-o1` does not support generate_audio.")
    if generate_audio and model not in {"kling-v3", "kling-v3-omni", "kling-v2-6"}:
        raise ValueError(
            "`generate_audio` requires a V3 model or `kling-v2-6` pro mode."
        )
    if generate_audio and model == "kling-v2-6" and mode != "pro":
        raise ValueError("`kling-v2-6` supports generate_audio only in pro mode.")
    if end_image_url and not start_image_url:
        raise ValueError("`start_image_url` is required with `end_image_url`.")
    if start_image_url is not None and not _is_http_url(start_image_url):
        raise ValueError("`start_image_url` must be an HTTP URL.")
    if end_image_url is not None and not _is_http_url(end_image_url):
        raise ValueError("`end_image_url` must be an HTTP URL.")

    references = bool(image_list or video_list)
    if references and model not in KLING_OMNI_MODELS:
        raise ValueError(
            "`image_list` and `video_list` require `kling-o1` or `kling-v3-omni`."
        )
    if references and mode == "4k":
        raise ValueError("4k cannot be combined with Omni references.")
    if model == "kling-o1" and (
        negative_prompt is not None
        or camera_control is not None
        or cfg_scale is not None
    ):
        raise ValueError(
            "`kling-o1` does not support negative_prompt, camera_control, or cfg_scale."
        )
    if references and (
        negative_prompt is not None
        or camera_control is not None
        or cfg_scale is not None
    ):
        raise ValueError(
            "Omni references cannot be combined with negative_prompt, camera_control, or cfg_scale."
        )
    if video_list and generate_audio:
        raise ValueError("`generate_audio` cannot be combined with `video_list`.")
    if len(video_list) > 1:
        raise ValueError("`video_list` accepts at most one video.")

    for image in image_list:
        image_url = image.get("image_url")
        if not _is_http_url(image_url):
            raise ValueError("Every image_list item requires an HTTP image_url.")
        if image.get("type") not in {None, "first_frame", "end_frame"}:
            raise ValueError("image_list type must be first_frame or end_frame.")
    for video in video_list:
        video_url = video.get("video_url")
        if not _is_http_url(video_url):
            raise ValueError("Every video_list item requires an HTTP video_url.")
        if video.get("refer_type") not in {None, "base", "feature"}:
            raise ValueError("video_list refer_type must be base or feature.")
        if video.get("keep_original_sound") not in {None, "yes", "no"}:
            raise ValueError("video_list keep_original_sound must be yes or no.")

    first_frames = int(bool(start_image_url)) + sum(
        item.get("type") == "first_frame" for item in image_list
    )
    end_frames = int(bool(end_image_url)) + sum(
        item.get("type") == "end_frame" for item in image_list
    )
    if first_frames > 1 or end_frames > 1:
        raise ValueError(
            "`image_list` accepts at most one first_frame and one end_frame."
        )
    if end_frames and not first_frames:
        raise ValueError("An image_list end_frame requires a first frame.")
    if (
        video_list
        and video_list[0].get("refer_type", "base") == "base"
        and (first_frames or end_frames)
    ):
        raise ValueError(
            "A base reference video cannot be combined with first or end frames."
        )

    image_count = len(image_list) + bool(start_image_url) + bool(end_image_url)
    image_limit = 4 if video_list else 7
    if image_count > image_limit:
        raise ValueError(
            f"Reference images cannot exceed {image_limit} for this request."
        )
