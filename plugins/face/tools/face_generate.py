from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataFaceClient, AceDataFaceError


def _str_or_none(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _int_or_none(value: Any, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"`{name}` must be a number.")
    return int(value)


class FaceTransformTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        action = _str_or_none(tool_parameters.get("action"))
        if not action:
            raise ValueError("`action` is required.")

        image_url = _str_or_none(tool_parameters.get("image_url"))
        source_image_url = _str_or_none(tool_parameters.get("source_image_url"))
        target_image_url = _str_or_none(tool_parameters.get("target_image_url"))
        callback_url = _str_or_none(tool_parameters.get("callback_url"))

        smoothing = _int_or_none(tool_parameters.get("smoothing"), "smoothing")
        whitening = _int_or_none(tool_parameters.get("whitening"), "whitening")
        face_lifting = _int_or_none(tool_parameters.get("face_lifting"), "face_lifting")
        eye_enlarging = _int_or_none(tool_parameters.get("eye_enlarging"), "eye_enlarging")

        # Validation per action
        single_image_actions = {"keypoints", "beautify", "age", "gender", "cartoon", "liveness"}
        if action in single_image_actions and not image_url:
            raise ValueError(f"`image_url` is required when action is {action}.")
        if action == "swap":
            if not source_image_url or not target_image_url:
                raise ValueError(
                    "`source_image_url` and `target_image_url` are required when action is swap."
                )

        payload: dict[str, Any] = {}
        if action in single_image_actions:
            payload["image_url"] = image_url
        if action == "swap":
            payload["source_image_url"] = source_image_url
            payload["target_image_url"] = target_image_url

        if action == "beautify":
            for key, val in {
                "smoothing": smoothing,
                "whitening": whitening,
                "face_lifting": face_lifting,
                "eye_enlarging": eye_enlarging,
            }.items():
                if val is not None:
                    payload[key] = val

        if callback_url:
            payload["callback_url"] = callback_url

        client = AceDataFaceClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.invoke(action=action, payload=payload, timeout_s=180)
        except AceDataFaceError as e:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message(
                "error", {"code": e.code, "message": e.message}
            )
            yield self.create_variable_message("trace_id", e.trace_id)
            return

        yield self.create_variable_message("success", True)
        yield self.create_variable_message("task_id", result.task_id)
        yield self.create_variable_message("trace_id", result.trace_id)
        yield self.create_variable_message("data", result.data)
