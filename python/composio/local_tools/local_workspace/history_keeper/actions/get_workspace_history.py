from pydantic import BaseModel, Field

from composio.core.local import Action
from composio.local_tools.local_workspace.commons.get_logger import get_logger
from composio.workspace.workspace_factory import WorkspaceFactory


STATUS_RUNNING = "running"
STATUS_STOPPED = "stopped"
logger = get_logger("workspace")


class GetWorkspaceHistoryRequest(BaseModel):
    workspace_id: str = Field(
        ..., description="workspace-id will be used to get status of the workspace"
    )


class GetWorkspaceHistoryResponse(BaseModel):
    workspace_history: dict = Field(
        ..., description="history of last n commands on the workspace"
    )


class GetWorkspaceHistory(
    Action[GetWorkspaceHistoryRequest, GetWorkspaceHistoryResponse]
):
    """
    returns history for workspace.
    History includes -
            - state of the environment
            - last executed n commands
            - output from last n commands
    """

    _history_maintains = True
    _display_name = "Get workspace history"
    _request_schema = GetWorkspaceHistoryRequest
    _response_schema = GetWorkspaceHistoryResponse
    _tags = ["workspace"]
    _tool_name = "historykeeper"
    _history_len = 5

    def execute(
        self, request_data: GetWorkspaceHistoryRequest, authorisation_data: dict
    ) -> dict:
        workspace_factory = WorkspaceFactory.get_instance()
        if workspace_factory is None:
            logger.error("Workspace factory is not set")
            raise ValueError("Workspace factory is not set")
        workspace = workspace_factory.get_workspace_by_id(request_data.workspace_id)
        if workspace is None:
            logger.error("Workspace is not set")
            raise ValueError("Workspace is not set")
        return {
            "workspace_history": workspace.get_history(
                request_data.workspace_id, self._history_len
            )
        }
