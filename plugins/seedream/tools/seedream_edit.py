from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import (
    AceDataSeedreamClient,
    AceDataSeedreamError,
    parse_image_inputs,
)


class SeedreamEditImageTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        prompt = tool_parameters.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("`prompt` is required.")

        image_urls = parse_image_inputs(tool_parameters.get("image_urls"))
        if not image_urls:
            raise ValueError("`image_urls` must contain at least 1 item.")

        model = tool_parameters.get("model")
        model = model.strip() if isinstance(model, str) and model.strip() else None

        size = tool_parameters.get("size")
        size = size.strip() if isinstance(size, str) and size.strip() else None

        sequential_image_generation = tool_parameters.get("sequential_image_generation")
        sequential_image_generation = (
            sequential_image_generation.strip()
            if isinstance(sequential_image_generation, str) and sequential_image_generation.strip()
            else None
        )


        response_format = tool_parameters.get("response_format")
        response_format = (
            response_format.strip()
            if isinstance(response_format, str) and response_format.strip()
            else None
        )

        watermark = tool_parameters.get("watermark")
        if watermark is not None and not isinstance(watermark, bool):
            raise ValueError("`watermark` must be a boolean.")

        callback_url = tool_parameters.get("callback_url")
        callback_url = (
            callback_url.strip()
            if isinstance(callback_url, str) and callback_url.strip()
            else None
        )

        payload: dict[str, Any] = {"action": "edit", "prompt": prompt.strip(), "image": image_urls}
        if model:
            payload["model"] = model
        if size:
            payload["size"] = size
        if sequential_image_generation:
            payload["sequential_image_generation"] = sequential_image_generation
        if response_format:
            payload["response_format"] = response_format
        if watermark is not None:
            payload["watermark"] = watermark
        output_format = tool_parameters.get("output_format")
        if isinstance(output_format, str) and output_format.strip():
            payload["output_format"] = output_format.strip()
        max_images = tool_parameters.get("max_images")
        if isinstance(max_images, int):
            payload["sequential_image_generation_options"] = {"max_images": max_images}
        optimize_mode = tool_parameters.get("optimize_prompt_mode")
        if isinstance(optimize_mode, str) and optimize_mode.strip():
            payload["optimize_prompt_options"] = {"mode": optimize_mode.strip()}
        if tool_parameters.get("web_search") is True:
            payload["tools"] = [{"type": "web_search"}]
        background = tool_parameters.get("background")
        if isinstance(background, str) and background.strip():
            payload["background"] = background.strip()
        if callback_url:
            payload["callback_url"] = callback_url
        if tool_parameters.get("async"):
            payload["async"] = True

        client = AceDataSeedreamClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_images(payload=payload, timeout_s=150)
        except AceDataSeedreamError as e:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error", {"code": e.code, "message": e.message})
            yield self.create_variable_message("trace_id", e.trace_id)
            return

        for image_url in result.image_urls:
            yield self.create_image_message(image_url)

        yield self.create_variable_message("success", True)
        yield self.create_variable_message("task_id", result.task_id)
        yield self.create_variable_message("trace_id", result.trace_id)
        yield self.create_variable_message("data", result.data)
