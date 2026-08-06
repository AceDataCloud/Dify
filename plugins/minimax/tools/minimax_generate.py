from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataMinimaxClient, AceDataMinimaxError, parse_urls


class MinimaxGenerateVideoTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        prompt_value = tool_parameters.get("prompt")
        prompt = prompt_value.strip() if isinstance(prompt_value, str) and prompt_value.strip() else None
        image_urls = parse_urls(tool_parameters.get("image_urls"), field_name="image_urls", limit=9)
        audio_urls = parse_urls(tool_parameters.get("audio_urls"), field_name="audio_urls", limit=3)
        if not prompt and not image_urls and not audio_urls:
            raise ValueError("At least one of `prompt`, `image_urls`, or `audio_urls` is required.")

        ratio = tool_parameters.get("ratio") or "16:9"
        if ratio not in {"16:9", "9:16"}:
            raise ValueError("`ratio` must be 16:9 or 9:16.")
        duration = tool_parameters.get("duration", 4)
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise TypeError("`duration` must be an integer from 4 to 15.")
        duration = int(duration)
        if duration < 4 or duration > 15:
            raise ValueError("`duration` must be an integer from 4 to 15.")

        callback_value = tool_parameters.get("callback_url")
        callback_url = callback_value.strip() if isinstance(callback_value, str) and callback_value.strip() else None
        async_value = tool_parameters.get("async", False)
        if not isinstance(async_value, bool):
            raise TypeError("`async` must be a boolean.")

        client = AceDataMinimaxClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_video(
                prompt=prompt,
                image_urls=image_urls or None,
                audio_urls=audio_urls or None,
                ratio=ratio,
                duration=duration,
                callback_url=callback_url,
                async_mode=async_value,
                timeout_s=1800,
            )
        except AceDataMinimaxError as exc:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error", {"code": exc.code, "message": exc.message})
            yield self.create_variable_message("trace_id", exc.trace_id)
            return

        yield self.create_variable_message("success", True)
        yield self.create_variable_message("task_id", result.task_id)
        yield self.create_variable_message("trace_id", result.trace_id)
        yield self.create_variable_message("data", result.data)
