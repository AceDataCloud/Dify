from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataGrokClient, AceDataGrokError, parse_image_urls


class GrokGenerateVideoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        prompt = tool_parameters.get("prompt")
        prompt = prompt.strip() if isinstance(prompt, str) and prompt.strip() else None

        image_url = tool_parameters.get("image_url")
        image_url = image_url.strip() if isinstance(image_url, str) and image_url.strip() else None

        reference_image_urls = parse_image_urls(tool_parameters.get("reference_image_urls"))

        model = tool_parameters.get("model")
        model = model.strip() if isinstance(model, str) and model.strip() else None

        aspect_ratio = tool_parameters.get("aspect_ratio")
        aspect_ratio = (
            aspect_ratio.strip() if isinstance(aspect_ratio, str) and aspect_ratio.strip() else None
        )

        resolution = tool_parameters.get("resolution")
        resolution = (
            resolution.strip() if isinstance(resolution, str) and resolution.strip() else None
        )

        duration = tool_parameters.get("duration")
        if duration is not None:
            if isinstance(duration, bool) or not isinstance(duration, (int, float)):
                raise ValueError("`duration` must be a number between 1 and 15.")
            duration = int(duration)
            if duration < 1 or duration > 15:
                raise ValueError("`duration` must be between 1 and 15 seconds.")

        callback_url = tool_parameters.get("callback_url")
        callback_url = (
            callback_url.strip() if isinstance(callback_url, str) and callback_url.strip() else None
        )

        # Text-to-video needs a prompt; image-to-video needs an image_url.
        if not image_url and not prompt:
            raise ValueError("Provide a `prompt` (text-to-video) or an `image_url` (image-to-video).")

        client = AceDataGrokClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_video(
                prompt=prompt,
                model=model,
                image_url=image_url,
                reference_image_urls=reference_image_urls or None,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                duration=duration,
                callback_url=callback_url,
                async_mode=bool(tool_parameters.get("async")),
                timeout_s=1800,
            )
        except AceDataGrokError as e:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error", {"code": e.code, "message": e.message})
            yield self.create_variable_message("trace_id", e.trace_id)
            return

        yield self.create_variable_message("success", True)
        yield self.create_variable_message("task_id", result.task_id)
        yield self.create_variable_message("trace_id", result.trace_id)
        yield self.create_variable_message("data", result.data)
