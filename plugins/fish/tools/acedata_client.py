from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class AceDataFishError(RuntimeError):
    code: str
    message: str
    trace_id: str | None = None
    status_code: int | None = None

    def __str__(self) -> str:
        trace_suffix = f" (trace_id={self.trace_id})" if self.trace_id else ""
        status_suffix = f" (status={self.status_code})" if self.status_code else ""
        return f"{self.code}: {self.message}{trace_suffix}{status_suffix}"


@dataclass(frozen=True)
class AceDataFishAudioResult:
    task_id: str | None
    trace_id: str | None
    data: dict[str, Any]


def _normalize_token(raw_token: str) -> str:
    token = raw_token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token


class AceDataFishClient:
    def __init__(self, bearer_token: str, base_url: str = "https://api.acedata.cloud") -> None:
        token = _normalize_token(bearer_token)
        if not token:
            raise AceDataFishError(code="token_empty", message="Empty bearer token.")
        self._token = token
        self._base_url = base_url.rstrip("/")

    def generate_audio(
        self,
        *,
        text: str,
        reference_id: str | None = None,
        model: str | None = None,
        format: str | None = None,
        sample_rate: int | None = None,
        mp3_bitrate: int | None = None,
        latency: str | None = None,
        callback_url: str | None = None,
        async_mode: bool | None = None,
        timeout_s: int = 300,
    ) -> AceDataFishAudioResult:
        payload: dict[str, Any] = {"text": text}
        if reference_id:
            payload["reference_id"] = reference_id
        if model:
            payload["model"] = model
        if format:
            payload["format"] = format
        if sample_rate is not None:
            payload["sample_rate"] = sample_rate
        if mp3_bitrate is not None:
            payload["mp3_bitrate"] = mp3_bitrate
        if latency:
            payload["latency"] = latency
        if callback_url:
            payload["callback_url"] = callback_url
        if async_mode:
            payload["async"] = True

        body = self._post_json(path="/fish/audios", payload=payload, timeout_s=timeout_s)
        return AceDataFishAudioResult(
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
            raise AceDataFishError(code="request_failed", message=str(e)) from e

        try:
            body = resp.json()
        except ValueError as e:
            snippet = (resp.text or "")[:500]
            raise AceDataFishError(
                code="invalid_json",
                message=f"Invalid JSON response: {snippet}",
                status_code=resp.status_code,
            ) from e

        if not isinstance(body, dict):
            raise AceDataFishError(
                code="invalid_payload",
                message=f"Invalid response payload: {type(body).__name__}",
                status_code=resp.status_code,
            )

        if resp.status_code >= 400:
            trace_id = body.get("trace_id") if isinstance(body.get("trace_id"), str) else None
            error = body.get("error") if isinstance(body.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), str) else None
            message = error.get("message") if isinstance(error.get("message"), str) else None
            raise AceDataFishError(
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
            raise AceDataFishError(
                code=code or "api_error",
                message=message or str(body),
                trace_id=trace_id,
                status_code=resp.status_code,
            )

        return body
