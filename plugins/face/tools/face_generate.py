from __future__ import annotations

from collections.abc import Generator
import json
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


def _json_array(value: Any, name: str) -> list[dict[str, Any]] | None:
    if value is None or value == "":
        return None
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
    except json.JSONDecodeError as exc:
        raise ValueError(f"`{name}` must be a valid JSON array.") from exc
    if not isinstance(parsed, list) or not parsed or not all(isinstance(item, dict) for item in parsed):
        raise ValueError(f"`{name}` must be a non-empty JSON array of objects.")
    return parsed


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
        mode = _int_or_none(tool_parameters.get("mode"), "mode")
        need_rotate_detection = _int_or_none(
            tool_parameters.get("need_rotate_detection"), "need_rotate_detection"
        )
        face_model_version = tool_parameters.get("face_model_version")
        age_infos = _json_array(tool_parameters.get("age_infos"), "age_infos")
        gender_infos = _json_array(tool_parameters.get("gender_infos"), "gender_infos")

        # Validation per action
        single_image_actions = {"keypoints", "beautify", "age", "gender", "cartoon", "liveness"}
        if action in single_image_actions and not image_url:
            raise ValueError(f"`image_url` is required when action is {action}.")
        if action == "swap":
            if not source_image_url or not target_image_url:
                raise ValueError(
                    "`source_image_url` and `target_image_url` are required when action is swap."
                )
        if action == "age" and not age_infos:
            raise ValueError("`age_infos` is required when action is age.")
        if action == "gender" and not gender_infos:
            raise ValueError("`gender_infos` is required when action is gender.")
        if action != "swap" and (callback_url or tool_parameters.get("async")):
            raise ValueError("`callback_url` and `async` are only supported when action is swap.")

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
        if action == "keypoints":
            for key, val in {
                "mode": mode,
                "face_model_version": _str_or_none(face_model_version),
                "need_rotate_detection": need_rotate_detection,
            }.items():
                if val is not None:
                    payload[key] = val
        if action == "age":
            payload["age_infos"] = age_infos
        if action == "gender":
            payload["gender_infos"] = gender_infos
        if action == "liveness" and face_model_version is not None:
            payload["face_model_version"] = _int_or_none(face_model_version, "face_model_version")

        if callback_url:
            payload["callback_url"] = callback_url
        if tool_parameters.get("async"):
            payload["async"] = True

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
