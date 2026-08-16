from httpx import Response

from apis.async_http_client import AsyncHttpClient
from apis.result import Result


class GitlabClient:
    """Client for interacting with the GitLab REST API."""
    def __init__(self, http_client: AsyncHttpClient) -> None:
        """Initialize the GitLab client.

        Args:
            http_client: HTTP client used to send requests to the GitLab API.
        """
        self._http_client = http_client

    async def get_commits_async(self, project_id: int) -> Result[Response]:
        """Get commits from a GitLab project.

        Args:
            project_id: Numeric ID of the GitLab project.

        Returns:
            Result containing the HTTP response on success or a Failure
            describing the error.
        """
        return await self._http_client.get_async(url=f"/projects/{project_id}/repository/commits")