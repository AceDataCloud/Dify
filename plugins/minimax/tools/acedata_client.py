from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class AceDataMinimaxError(RuntimeError):
    code: str
    message: str
    trace_id: str | None = None
    status_code: int | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


@dataclass(frozen=True)
class AceDataMinimaxVideosResult:
    task_id: str | None
    trace_id: str | None
    data: list[dict[str, Any]]


def parse_urls(value: Any, *, field_name: str, limit: int) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        values = [part.strip() for part in value.replace(",", "\n").splitlines()]
    elif isinstance(value, list):
        values = [str(part).strip() for part in value]
    else:
        raise TypeError(f"`{field_name}` must be an array of URLs.")
    values = [part for part in values if part]
    if len(values) > limit:
        raise ValueError(f"`{field_name}` accepts at most {limit} URLs.")
    return values


def _normalize_token(raw_token: str) -> str:
    token = raw_token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token


class AceDataMinimaxClient:
    def __init__(self, bearer_token: str, base_url: str = "https://api.acedata.cloud") -> None:
        token = _normalize_token(bearer_token)
        if not token:
            raise AceDataMinimaxError(code="token_empty", message="Empty bearer token.")
        self._token = token
        self._base_url = base_url.rstrip("/")

    def validate_credentials(self, timeout_s: int = 30) -> None:
        try:
            response = requests.post(
                f"{self._base_url}/minimax/videos",
                json={},
                headers={"authorization": f"Bearer {self._token}", "content-type": "application/json"},
                timeout=timeout_s,
            )
        except requests.RequestException as exc:
            raise AceDataMinimaxError(code="request_failed", message=str(exc)) from exc
        if response.status_code == 401:
            raise AceDataMinimaxError(code="invalid_token", message="Invalid AceDataCloud token.", status_code=401)
        if response.status_code >= 500:
            raise AceDataMinimaxError(
                code="validation_unavailable",
                message="MiniMax credential validation is temporarily unavailable.",
                status_code=response.status_code,
            )

    def generate_video(
        self,
        *,
        prompt: str | None = None,
        image_urls: list[str] | None = None,
        audio_urls: list[str] | None = None,
        model: str = "minimax-h3",
        ratio: str = "16:9",
        duration: int = 4,
        callback_url: str | None = None,
        async_mode: bool = False,
        timeout_s: int = 1800,
    ) -> AceDataMinimaxVideosResult:
        payload: dict[str, Any] = {"model": model, "ratio": ratio, "duration": duration}
        if prompt:
            payload["prompt"] = prompt
        if image_urls:
            payload["image_urls"] = image_urls
        if audio_urls:
            payload["audio_urls"] = audio_urls
        if callback_url:
            payload["callback_url"] = callback_url
        if async_mode:
            payload["async"] = True

        body = self._post(path="/minimax/videos", payload=payload, timeout_s=timeout_s)
        task_id = body.get("task_id") if isinstance(body.get("task_id"), str) else None
        trace_id = body.get("trace_id") if isinstance(body.get("trace_id"), str) else None
        if async_mode or callback_url:
            if not task_id:
                raise AceDataMinimaxError(code="api_error", message=str(body), trace_id=trace_id)
        elif body.get("success") is not True:
            raise AceDataMinimaxError(code="api_error", message=str(body), trace_id=trace_id)
        raw_data = body.get("data")
        data = [item for item in raw_data if isinstance(item, dict)] if isinstance(raw_data, list) else []
        return AceDataMinimaxVideosResult(task_id=task_id, trace_id=trace_id, data=data)

    def retrieve_task(self, *, task_id: str, timeout_s: int = 60) -> dict[str, Any]:
        return self._post(
            path="/minimax/tasks",
            payload={"action": "retrieve", "id": task_id},
            timeout_s=timeout_s,
        )

    def _post(self, *, path: str, payload: dict[str, Any], timeout_s: int) -> dict[str, Any]:
        try:
            response = requests.post(
                f"{self._base_url}{path}",
                json=payload,
                headers={
                    "authorization": f"Bearer {self._token}",
                    "accept": "application/json",
                    "content-type": "application/json",
                },
                timeout=timeout_s,
            )
        except requests.RequestException as exc:
            raise AceDataMinimaxError(code="request_failed", message=str(exc)) from exc
        try:
            body = response.json()
        except ValueError as exc:
            raise AceDataMinimaxError(
                code="invalid_json",
                message=f"Invalid JSON response: {(response.text or '')[:500]}",
                status_code=response.status_code,
            ) from exc
        if not isinstance(body, dict):
            raise AceDataMinimaxError(code="invalid_payload", message="Response must be an object.")
        if response.status_code >= 400 or body.get("success") is False:
            error = body.get("error") if isinstance(body.get("error"), dict) else {}
            raise AceDataMinimaxError(
                code=error.get("code") if isinstance(error.get("code"), str) else "api_error",
                message=error.get("message") if isinstance(error.get("message"), str) else str(body),
                trace_id=body.get("trace_id") if isinstance(body.get("trace_id"), str) else None,
                status_code=response.status_code,
            )
        return body
