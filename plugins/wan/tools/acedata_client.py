from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class AceDataWanError(RuntimeError):
    code: str
    message: str
    trace_id: str | None = None
    status_code: int | None = None

    def __str__(self) -> str:
        trace_suffix = f" (trace_id={self.trace_id})" if self.trace_id else ""
        status_suffix = f" (status={self.status_code})" if self.status_code else ""
        return f"{self.code}: {self.message}{trace_suffix}{status_suffix}"


@dataclass(frozen=True)
class AceDataWanVideosResult:
    task_id: str | None
    trace_id: str | None
    data: dict[str, Any]


def _normalize_token(raw_token: str) -> str:
    token = raw_token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token


class AceDataWanClient:
    def __init__(self, bearer_token: str, base_url: str = "https://api.acedata.cloud") -> None:
        token = _normalize_token(bearer_token)
        if not token:
            raise AceDataWanError(code="token_empty", message="Empty bearer token.")
        self._token = token
        self._base_url = base_url.rstrip("/")

    def generate_video(
        self,
        *,
        action: str,
        model: str | None = None,
        prompt: str | None = None,
        image_url: str | None = None,
        negative_prompt: str | None = None,
        resolution: str | None = None,
        duration: int | None = None,
        size: str | None = None,
        audio: bool | None = None,
        audio_url: str | None = None,
        prompt_extend: bool | None = None,
        shot_type: str | None = None,
        reference_video_urls: str | None = None,
        callback_url: str | None = None,
        async_mode: bool | None = None,
        timeout_s: int = 1800,
    ) -> AceDataWanVideosResult:
        payload: dict[str, Any] = {"action": action}
        if model:
            payload["model"] = model
        if prompt:
            payload["prompt"] = prompt
        if image_url:
            payload["image_url"] = image_url
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if resolution:
            payload["resolution"] = resolution
        if duration is not None:
            payload["duration"] = duration
        if size:
            payload["size"] = size
        if audio is not None:
            payload["audio"] = audio
        if audio_url:
            payload["audio_url"] = audio_url
        if prompt_extend is not None:
            payload["prompt_extend"] = prompt_extend
        if shot_type:
            payload["shot_type"] = shot_type
        if reference_video_urls:
            payload["reference_video_urls"] = reference_video_urls
        if callback_url:
            payload["callback_url"] = callback_url
            if async_mode:
                payload["async"] = True

        body = self._post_json(path="/wan/videos", payload=payload, timeout_s=timeout_s)
        return AceDataWanVideosResult(
            task_id=body.get("task_id") if isinstance(body.get("task_id"), str) else None,
            trace_id=body.get("trace_id") if isinstance(body.get("trace_id"), str) else None,
            data=body,
        )

    def _post_json(self, *, path: str, payload: dict[str, Any], timeout_s: int) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = {
            "authorization": f"Bearer {self._token}",
            "accept": "application/json",
            "content-type": "application/json",
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
        except requests.RequestException as e:
            raise AceDataWanError(code="request_failed", message=str(e)) from e

        try:
            body = resp.json()
        except ValueError as e:
            snippet = (resp.text or "")[:500]
            raise AceDataWanError(
                code="invalid_json",
                message=f"Invalid JSON response: {snippet}",
                status_code=resp.status_code,
            ) from e

        if not isinstance(body, dict):
            raise AceDataWanError(
                code="invalid_payload",
                message=f"Invalid response payload: {type(body).__name__}",
                status_code=resp.status_code,
            )

        if resp.status_code >= 400:
            trace_id = body.get("trace_id") if isinstance(body.get("trace_id"), str) else None
            error = body.get("error") if isinstance(body.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), str) else None
            message = error.get("message") if isinstance(error.get("message"), str) else None
            raise AceDataWanError(
                code=code or "error",
                message=message or str(body),
                trace_id=trace_id,
                status_code=resp.status_code,
            )

        if "success" in body and body.get("success") is not True:
            trace_id = body.get("trace_id") if isinstance(body.get("trace_id"), str) else None
            error = body.get("error") if isinstance(body.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), str) else None
            message = error.get("message") if isinstance(error.get("message"), str) else None
            raise AceDataWanError(
                code=code or "api_error",
                message=message or str(body),
                trace_id=trace_id,
                status_code=resp.status_code,
            )

        return body
