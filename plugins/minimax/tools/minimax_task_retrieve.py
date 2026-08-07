from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataMinimaxClient, AceDataMinimaxError


class MinimaxTaskRetrieveTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        task_id = tool_parameters.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("`task_id` is required.")
        client = AceDataMinimaxClient(
            bearer_token=str(self.runtime.credentials["acedata_bearer_token"])
        )
        try:
            result = client.retrieve_task(task_id=task_id.strip())
        except AceDataMinimaxError as exc:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error", {"code": exc.code, "message": exc.message})
            return
        yield self.create_variable_message("success", True)
        yield self.create_variable_message("data", result)
