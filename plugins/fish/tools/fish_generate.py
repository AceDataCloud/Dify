from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataFishClient, AceDataFishError


def _str_or_none(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


class FishGenerateAudioTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        text = _str_or_none(tool_parameters.get("text"))
        if not text:
            raise ValueError("`text` is required.")

        reference_id = _str_or_none(tool_parameters.get("reference_id"))
        model = _str_or_none(tool_parameters.get("model"))
        fmt = _str_or_none(tool_parameters.get("format"))
        latency = _str_or_none(tool_parameters.get("latency"))
        callback_url = _str_or_none(tool_parameters.get("callback_url"))

        sample_rate = tool_parameters.get("sample_rate")
        if sample_rate is not None:
            if isinstance(sample_rate, bool) or not isinstance(sample_rate, (int, float)):
                raise ValueError("`sample_rate` must be a number.")
            sample_rate = int(sample_rate)

        mp3_bitrate = tool_parameters.get("mp3_bitrate")
        if mp3_bitrate is not None:
            if isinstance(mp3_bitrate, bool) or not isinstance(mp3_bitrate, (int, float)):
                raise ValueError("`mp3_bitrate` must be a number.")
            mp3_bitrate = int(mp3_bitrate)

        client = AceDataFishClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.generate_audio(
                text=text,
                reference_id=reference_id,
                model=model,
                format=fmt,
                sample_rate=sample_rate,
                mp3_bitrate=mp3_bitrate,
                latency=latency,
                callback_url=callback_url,
                async_mode=bool(tool_parameters.get("async")),
                timeout_s=300,
            )
        except AceDataFishError as e:
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
