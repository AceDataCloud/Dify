from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataSeedreamClient, AceDataSeedreamError, parse_image_inputs


class SeedreamDecomposeImageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        images = parse_image_inputs(tool_parameters.get("image_url"))
        if len(images) != 1:
            raise ValueError("`image_url` must contain exactly one PNG or JPEG image.")

        payload: dict[str, Any] = {
            "model": "doubao-seedream-5-0-pro-260628",
            "image": images[0],
            "layer_decomposition": True,
            "size": tool_parameters.get("size") or "auto",
            "output_format": tool_parameters.get("output_format") or "jpeg",
        }
        prompt = tool_parameters.get("prompt")
        if isinstance(prompt, str) and prompt.strip():
            payload["prompt"] = prompt.strip()
        watermark = tool_parameters.get("watermark")
        if isinstance(watermark, bool):
            payload["watermark"] = watermark
        if tool_parameters.get("async") is True:
            payload["async"] = True

        client = AceDataSeedreamClient(bearer_token=str(self.runtime.credentials["acedata_bearer_token"]))
        try:
            result = client.generate_images(payload=payload, timeout_s=150)
        except AceDataSeedreamError as error:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error", {"code": error.code, "message": error.message})
            yield self.create_variable_message("trace_id", error.trace_id)
            return

        for image_url in result.image_urls:
            yield self.create_image_message(image_url)
        yield self.create_variable_message("success", True)
        yield self.create_variable_message("task_id", result.task_id)
        yield self.create_variable_message("trace_id", result.trace_id)
        yield self.create_variable_message("data", result.data)
