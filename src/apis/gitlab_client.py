import json

from httpx import Response

from apis.app_logger import AppLogger
from apis.async_http_client import AsyncHttpClient
from apis.error_code import ErrorCode
from apis.result import FailureContext, Result, failure, is_failure, success
from models.gitlab_commit import GitlabCommit


class GitlabClient:
    """Client for interacting with the GitLab REST API."""
    def __init__(self, http_client: AsyncHttpClient) -> None:
        """Initialize the GitLab client.

        Args:
            http_client: HTTP client used to send requests to the GitLab API.
        """
        self._http_client = http_client
        self._logger = AppLogger(self.__class__.__name__)

    async def get_commits_async(self, project_id: int) -> Result[list[GitlabCommit]]:
        """Get commits from a GitLab project.

        Args:
            project_id: Numeric ID of the GitLab project.

        Returns:
            Result containing the list of gitlab commits on success or a Failure
            describing the error.
        """
        response: Result[Response] = await self._http_client.get_async(url=f"/projects/{project_id}/repository/commits")

        if is_failure(response):
            self._logger.log_error(response)
            return response
            
        data = response.value.content

        try:
            commit_data_dict: list[dict] = json.loads(data)
        except Exception as ex:
            self._logger.log_exception(
                "Ошибка при обработке ответа GitLab",
                ex,
            )

            return failure(
                message="Failed to deserialize GitLab response",
                code=ErrorCode.JSON_DESERIALIZATION_ERROR,
                context=FailureContext(
                    operation="get_commits_async",
                    source=self.__class__.__name__,
                ),
                details={
                    "exception": type(ex).__name__,
                    "detail": str(ex),
                },
            )

        commits: list[GitlabCommit] = []
                
        for commit_data in commit_data_dict:
            commits.append(GitlabCommit.from_dict(commit_data))
        
        return success(commits)