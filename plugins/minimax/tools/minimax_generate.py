from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataMinimaxClient, AceDataMinimaxError


_LEGACY_FIELDS = {"prompt", "image_urls", "audio_urls"}


class MinimaxGenerateVideoTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        legacy_fields = sorted(_LEGACY_FIELDS.intersection(tool_parameters))
        if legacy_fields:
            raise ValueError(
                f"Legacy fields {', '.join(f'`{field}`' for field in legacy_fields)} are no longer accepted. "
                'Migrate to `content`, for example: [{"type":"text","text":"A cat waves"}].'
            )
        content = tool_parameters.get("content")
        if not isinstance(content, list) or not content or not all(isinstance(item, dict) for item in content):
            raise TypeError("`content` must be a non-empty array of content objects.")
        if not any(
            item.get("type") == "text" and isinstance(item.get("text"), str) and item["text"].strip()
            for item in content
        ):
            raise ValueError("`content` must include one non-empty text item.")

        resolution = tool_parameters.get("resolution") or "2K"
        if resolution not in {"768P", "2K"}:
            raise ValueError("`resolution` must be 768P or 2K.")
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
        # `async` is retained by the public API for compatibility; creation is
        # always asynchronous, so the plugin intentionally ignores its value.
        client = AceDataMinimaxClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_video(
                content=content,
                resolution=resolution,
                ratio=ratio,
                duration=duration,
                callback_url=callback_url,
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
