from types import TracebackType
from typing import Any, Self
from httpx import AsyncClient, DecodingError, HTTPError, HTTPStatusError, InvalidURL, NetworkError, ProtocolError, ProxyError, Response, TimeoutException, TooManyRedirects, UnsupportedProtocol

from apis.app_logger import AppLogger
from apis.error_type import ErrorCode
from apis.result import Failure, Result, Success, failure



class AsyncHttpClient:
    def __init__(self) -> None:
        self._client: AsyncClient = AsyncClient()
        self._logger = AppLogger()

    async def get_async(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> Result[Response]:
        try:
            response: Response = await self._client.get(url=url, params=params)
            response.raise_for_status()
            return Success(value=response)

        except HTTPStatusError as exc:
            return failure(
                error="http status exception",
                code=ErrorCode.HTTP_STATUS_ERROR,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                    "status_code": exc.response.status_code,
                },
            )

        except TimeoutException as exc:
            return failure(
                error="timeout exception",
                code=ErrorCode.TIMEOUT,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except NetworkError as exc:
            return failure(
                error="network exception",
                code=ErrorCode.NETWORK_ERROR,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except ProtocolError as exc:
            return failure(
                error="protocol exception",
                code=ErrorCode.PROTOCOL_ERROR,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except ProxyError as exc:
            return failure(
                error="proxy exception",
                code=ErrorCode.PROXY_ERROR,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except TooManyRedirects as exc:
            return failure(
                error="too many redirects exception",
                code=ErrorCode.TOO_MANY_REDIRECTS,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except DecodingError as exc:
            return failure(
                error="decoding exception",
                code=ErrorCode.DECODING_ERROR,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except InvalidURL as exc:
            return failure(
                error="invalid url exception",
                code=ErrorCode.INVALID_URL,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except UnsupportedProtocol as exc:
            return failure(
                error="unsupported protocol exception",
                code=ErrorCode.UNSUPPORTED_PROTOCOL,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

        except HTTPError as exc:
            return failure(
                error="unexpected http exception",
                code=ErrorCode.UNKNOWN,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self._client.aclose()