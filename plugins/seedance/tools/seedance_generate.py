from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import (
    AceDataSeedanceClient,
    AceDataSeedanceError,
    parse_image_urls,
)


class SeedanceGenerateVideoTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        prompt = tool_parameters.get("prompt")
        prompt = prompt.strip() if isinstance(prompt, str) else ""

        model = tool_parameters.get("model")
        model = (
            model.strip()
            if isinstance(model, str) and model.strip()
            else "doubao-seedance-2-0-260128"
        )

        first_frame_url = tool_parameters.get("first_frame_url")
        first_frame_url = (
            first_frame_url.strip()
            if isinstance(first_frame_url, str) and first_frame_url.strip()
            else None
        )

        last_frame_url = tool_parameters.get("last_frame_url")
        last_frame_url = (
            last_frame_url.strip()
            if isinstance(last_frame_url, str) and last_frame_url.strip()
            else None
        )

        reference_image_urls = parse_image_urls(
            tool_parameters.get("reference_image_urls"),
            field_name="reference_image_urls",
        )
        reference_audio_urls = parse_image_urls(
            tool_parameters.get("reference_audio_urls"),
            field_name="reference_audio_urls",
        )
        reference_video_urls = parse_image_urls(
            tool_parameters.get("reference_video_urls"),
            field_name="reference_video_urls",
        )
        has_reference_media = bool(
            first_frame_url
            or last_frame_url
            or reference_image_urls
            or reference_audio_urls
            or reference_video_urls
        )
        if not prompt and not (
            model == "doubao-seedance-2-5-260628" and has_reference_media
        ):
            raise ValueError(
                "`prompt` is required unless Seedance 2.5 uses reference media."
            )

        return_last_frame = tool_parameters.get("return_last_frame")
        if return_last_frame is not None and not isinstance(return_last_frame, bool):
            raise ValueError("`return_last_frame` must be a boolean.")

        task_type = tool_parameters.get("omni_reference_task_type")
        task_type = (
            task_type.strip()
            if isinstance(task_type, str) and task_type.strip()
            else None
        )
        output_format = tool_parameters.get("output_format")
        output_format = (
            output_format.strip()
            if isinstance(output_format, str) and output_format.strip()
            else None
        )
        tools = tool_parameters.get("tools")
        if tools is not None:
            allowed_tool_fields = {
                "type",
                "limit",
                "max_keyword",
                "sources",
                "user_location",
            }
            if (
                not isinstance(tools, list)
                or len(tools) > 1
                or any(
                    not isinstance(tool, dict)
                    or tool.get("type") != "web_search"
                    or not set(tool).issubset(allowed_tool_fields)
                    for tool in tools
                )
            ):
                raise ValueError("`tools` accepts at most one valid web_search object.")

        execution_expires_after = tool_parameters.get("execution_expires_after")
        if execution_expires_after is not None:
            if isinstance(execution_expires_after, bool) or not isinstance(
                execution_expires_after, int
            ):
                raise ValueError("`execution_expires_after` must be an integer.")

        callback_url = tool_parameters.get("callback_url")
        callback_url = (
            callback_url.strip()
            if isinstance(callback_url, str) and callback_url.strip()
            else None
        )

        resolution = tool_parameters.get("resolution")
        resolution = (
            resolution.strip()
            if isinstance(resolution, str) and resolution.strip()
            else None
        )

        ratio = tool_parameters.get("ratio")
        ratio = ratio.strip() if isinstance(ratio, str) and ratio.strip() else None

        duration = tool_parameters.get("duration")
        if duration is not None:
            if isinstance(duration, bool) or not isinstance(duration, (int, float)):
                raise ValueError("`duration` must be a number.")
            duration = int(duration)

        seed = tool_parameters.get("seed")
        if seed is not None:
            if isinstance(seed, bool) or not isinstance(seed, (int, float)):
                raise ValueError("`seed` must be a number.")
            seed = int(seed)

        camerafixed = tool_parameters.get("camerafixed")
        if camerafixed is not None and not isinstance(camerafixed, bool):
            raise ValueError("`camerafixed` must be a boolean.")

        watermark = tool_parameters.get("watermark")
        if watermark is not None and not isinstance(watermark, bool):
            raise ValueError("`watermark` must be a boolean.")

        generate_audio = tool_parameters.get("generate_audio")
        if generate_audio is not None and not isinstance(generate_audio, bool):
            raise ValueError("`generate_audio` must be a boolean.")
        priority = tool_parameters.get("priority")
        if priority is not None and (
            isinstance(priority, bool)
            or not isinstance(priority, int)
            or priority < 0
            or priority > 9
        ):
            raise ValueError("`priority` must be an integer from 0 to 9.")
        safety_identifier = tool_parameters.get("safety_identifier")
        if safety_identifier is not None and (
            not isinstance(safety_identifier, str)
            or not safety_identifier
            or len(safety_identifier) > 64
        ):
            raise ValueError("`safety_identifier` must contain 1-64 characters.")

        client = AceDataSeedanceClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_video(
                model=model,
                prompt=prompt,
                first_frame_url=first_frame_url,
                last_frame_url=last_frame_url,
                reference_image_urls=reference_image_urls or None,
                reference_audio_urls=reference_audio_urls or None,
                reference_video_urls=reference_video_urls or None,
                resolution=resolution,
                ratio=ratio,
                duration=duration,
                seed=seed,
                camerafixed=camerafixed,
                watermark=watermark,
                generate_audio=generate_audio,
                return_last_frame=return_last_frame,
                omni_reference_task_type=task_type,
                output_format=output_format,
                tools=tools,
                priority=priority,
                safety_identifier=safety_identifier,
                execution_expires_after=execution_expires_after,
                callback_url=callback_url,
                async_mode=bool(tool_parameters.get("async")),
                timeout_s=600,
            )
        except AceDataSeedanceError as e:
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
