from types import TracebackType
from typing import Any, Self

from httpx import AsyncClient, HTTPError, Response

from apis.app_logger import AppLogger
from apis.result import Result, Success, handle_http_error


class AsyncHttpClient:
    """Asynchronous HTTP client based on httpx.AsyncClient.

    Provides a simplified interface for making HTTP requests and
    converts HTTPX exceptions into application-level Failure results.
    """

    def __init__(self, base_url: str, headers: dict[str, str] | None = None, timeout: int | None = None) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: Base URL prepended to relative request URLs.
            headers: Optional default headers applied to all requests.
            timeout: Optional request timeout in seconds.
        """
        self._client: AsyncClient = AsyncClient(base_url=base_url, headers=headers, timeout=timeout)
        self._logger = AppLogger()

    async def get_async(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> Result[Response]:
        """Perform an asynchronous GET request.

        The response status is checked using ``raise_for_status()``.
        HTTPX exceptions are converted into application-level Failure
        results using ``handle_http_error()``.

        Args:
            url: URL of the resource to request.
            params: Optional query parameters to include in the request.

        Returns:
            Success containing the HTTP response if the request succeeds,
            or Failure containing error information if an HTTP error occurs.
        """
        try:
            response: Response = await self._client.get(url=url, params=params)
            response.raise_for_status()
            return Success(value=response)
        except HTTPError as exc:
            return handle_http_error(exc)


    async def __aenter__(self) -> Self:
        """Enter the asynchronous context manager.

        Returns:
            The current AsyncHttpClient instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Enter the asynchronous context manager.

        Returns:
            The current AsyncHttpClient instance.
        """
        await self._client.aclose()