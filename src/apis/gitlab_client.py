from httpx import Response

from apis.async_http_client import AsyncHttpClient


class GtilabClient:
    def __init__(self):
        self._http_client: AsyncHttpClient = AsyncHttpClient()

    async def get_commits_async(self, project_id: int) -> Response:
        return await self._http_client.get_async(url=f"https://gitlab.com/api/v4/projects/{project_id}/repository/commits")