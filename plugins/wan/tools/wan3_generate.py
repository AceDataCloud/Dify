from __future__ import annotations
import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.acedata_client import AceDataWanClient, AceDataWanError

class Wan3GenerateTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage,None,None]:
        prompt=str(tool_parameters.get("prompt") or "").strip()
        raw=tool_parameters.get("media") or "[]"
        media=json.loads(raw) if isinstance(raw,str) else raw
        if not prompt and not media: raise ValueError("prompt or media is required")
        client=AceDataWanClient(bearer_token=str(self.runtime.credentials["acedata_bearer_token"]))
        try:
            result=client.generate_video(model="wan3.0-video",prompt=prompt,media=media,duration=int(tool_parameters.get("duration") or 5),resolution=tool_parameters.get("resolution") or "1080P",ratio=tool_parameters.get("ratio") or "adaptive",audio=tool_parameters.get("audio") is not False,watermark=bool(tool_parameters.get("watermark")),async_mode=bool(tool_parameters.get("async")),timeout_s=1800)
        except AceDataWanError as e:
            yield self.create_variable_message("success",False); yield self.create_variable_message("error",{"code":e.code,"message":e.message}); return
        yield self.create_variable_message("success",True); yield self.create_variable_message("task_id",result.task_id); yield self.create_variable_message("trace_id",result.trace_id); yield self.create_variable_message("data",result.data)
