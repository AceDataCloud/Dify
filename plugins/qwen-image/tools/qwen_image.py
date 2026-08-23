from __future__ import annotations
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.acedata_client import AceDataQwenImageClient, AceDataQwenImageError, parse_image_inputs

class QwenImageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        prompt=str(tool_parameters.get("prompt") or "").strip()
        if not prompt: raise ValueError("`prompt` is required.")
        image_urls=parse_image_inputs(tool_parameters.get("image_urls"))
        if len(image_urls)>3: raise ValueError("At most three reference images are supported.")
        payload={k:v for k,v in {"model":tool_parameters.get("model") or "qwen-image-3.0","prompt":prompt,"image_urls":image_urls or None,"n":tool_parameters.get("n") or 1,"size":tool_parameters.get("size") or None,"prompt_extend":tool_parameters.get("prompt_extend"),"enable_thinking":tool_parameters.get("enable_thinking"),"negative_prompt":tool_parameters.get("negative_prompt") or None,"seed":tool_parameters.get("seed"),"watermark":tool_parameters.get("watermark"),"async":tool_parameters.get("async") or False}.items() if v is not None}
        client=AceDataQwenImageClient(bearer_token=str(self.runtime.credentials["acedata_bearer_token"]))
        try: result=client.generate_images(payload=payload,timeout_s=1800)
        except AceDataQwenImageError as e:
            yield self.create_variable_message("success",False); yield self.create_variable_message("error",{"code":e.code,"message":e.message}); return
        for url in result.image_urls: yield self.create_image_message(url)
        yield self.create_variable_message("success",True); yield self.create_variable_message("task_id",result.task_id); yield self.create_variable_message("trace_id",result.trace_id); yield self.create_variable_message("data",result.data)
