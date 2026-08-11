from typing import Self
from httpx import AsyncClient, Response

from apis.app_logger import AppLogger



class AsyncHttpClient:
    def __init__(self) -> None:
        self._client: AsyncClient = AsyncClient()
        self._logger = AppLogger()

    async def get_async(self, url: str, params: dict) -> Response:
        return await self._client.get(url=url, params=params)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc, tb) ->  None:
        await self._client.aclose()
        