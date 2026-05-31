from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataWanClient, AceDataWanError


def _str_or_none(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


class WanGenerateVideoTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        action = _str_or_none(tool_parameters.get("action"))
        if not action:
            raise ValueError("`action` is required.")

        model = _str_or_none(tool_parameters.get("model"))
        prompt = _str_or_none(tool_parameters.get("prompt"))
        image_url = _str_or_none(tool_parameters.get("image_url"))
        negative_prompt = _str_or_none(tool_parameters.get("negative_prompt"))
        resolution = _str_or_none(tool_parameters.get("resolution"))
        size = _str_or_none(tool_parameters.get("size"))
        audio_url = _str_or_none(tool_parameters.get("audio_url"))
        shot_type = _str_or_none(tool_parameters.get("shot_type"))
        reference_video_urls = _str_or_none(tool_parameters.get("reference_video_urls"))
        callback_url = _str_or_none(tool_parameters.get("callback_url"))

        duration = tool_parameters.get("duration")
        if duration is not None:
            if isinstance(duration, bool) or not isinstance(duration, (int, float)):
                raise ValueError("`duration` must be a number.")
            duration = int(duration)

        audio = tool_parameters.get("audio")
        if audio is not None and not isinstance(audio, bool):
            raise ValueError("`audio` must be a boolean.")

        prompt_extend = tool_parameters.get("prompt_extend")
        if prompt_extend is not None and not isinstance(prompt_extend, bool):
            raise ValueError("`prompt_extend` must be a boolean.")

        if action in {"text2video", "image2video"} and not prompt:
            raise ValueError("`prompt` is required when action is text2video or image2video.")
        if action == "image2video" and not image_url:
            raise ValueError("`image_url` is required when action is image2video.")

        client = AceDataWanClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_video(
                action=action,
                model=model,
                prompt=prompt,
                image_url=image_url,
                negative_prompt=negative_prompt,
                resolution=resolution,
                duration=duration,
                size=size,
                audio=audio,
                audio_url=audio_url,
                prompt_extend=prompt_extend,
                shot_type=shot_type,
                reference_video_urls=reference_video_urls,
                callback_url=callback_url,
                timeout_s=1800,
            )
        except AceDataWanError as e:
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
