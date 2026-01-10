from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataFluxClient, AceDataFluxError


class FluxTaskRetrieveTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        task_id = tool_parameters.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("`task_id` is required.")

        client = AceDataFluxClient(bearer_token=str(self.runtime.credentials["acedata_bearer_token"]))
        try:
            result = client.retrieve_task(task_id=task_id.strip(), timeout_s=60)
        except AceDataFluxError as e:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error", {"code": e.code, "message": e.message})
            yield self.create_variable_message("trace_id", e.trace_id)
            return

        trace_id = result.get("trace_id") if isinstance(result.get("trace_id"), str) else None
        yield self.create_variable_message("success", True)
        yield self.create_variable_message("trace_id", trace_id)
        yield self.create_variable_message("data", result)

