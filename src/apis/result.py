
from dataclasses import dataclass
from typing import Any, TypeGuard

from httpx import (
    DecodingError,
    HTTPError,
    HTTPStatusError,
    InvalidURL,
    NetworkError,
    ProtocolError,
    ProxyError,
    TimeoutException,
    TooManyRedirects,
    UnsupportedProtocol,
)

from apis.error_code import ErrorCode


@dataclass(frozen=True)
class Success[T]:
    """Successful operation result."""
    value: T
    message: str | None = None

@dataclass(frozen=True)
class Failure:
    """Failed operation result."""
    message: str
    code: ErrorCode
    details: dict[str, Any] | None = None

# The Result type alias
type Result[T] = Success[T] | Failure



def success[T](value: T, message: str | None = None) -> Success[T]:
    """Create a successful operation result.

    Args:
        value: Value returned by the successful operation.
        message: Optional descriptive message.

    Returns:
        A Success instance containing the operation result.
    """
    return Success(value=value, message=message)

def failure(
    message: str,
    code: ErrorCode,
    details: dict[str, Any] | None = None
) -> Failure:
    """Create a failed operation result.

    Args:
        message: Description of the error.
        code: Application-specific error code.
        details: Optional additional information about the error.

    Returns:
        A Failure instance containing error information.
    """
    return Failure(message=message, code=code, details=details)



def is_success[T](result: Result[T]) -> TypeGuard[Success[T]]:
    """Check whether a result represents a successful operation.

    Args:
        result: Operation result to check.

    Returns:
        True if the result is a Success instance, otherwise False.
        TypeGuard narrows the result type to Success[T].
    """
    return isinstance(result, Success)

def is_failure[T](result: Result[T]) -> TypeGuard[Failure]:
    """Check whether a result represents a failed operation.

    Args:
        result: Operation result to check.

    Returns:
        True if the result is a Failure instance, otherwise False.
        TypeGuard narrows the result type to Failure.
    """
    return isinstance(result, Failure)



_EXCEPTION_TO_ERROR = {
    HTTPStatusError: ErrorCode.HTTP_STATUS_ERROR,
    TimeoutException: ErrorCode.TIMEOUT,
    NetworkError: ErrorCode.NETWORK_ERROR,
    ProtocolError: ErrorCode.PROTOCOL_ERROR,
    ProxyError: ErrorCode.PROXY_ERROR,
    TooManyRedirects: ErrorCode.TOO_MANY_REDIRECTS,
    DecodingError: ErrorCode.DECODING_ERROR,
    InvalidURL: ErrorCode.INVALID_URL,
    UnsupportedProtocol: ErrorCode.UNSUPPORTED_PROTOCOL,
}


def _get_error_code(exc: HTTPError) -> ErrorCode:
    """Get an application error code for an HTTPX exception.

    Args:
        exc: HTTPX exception to classify.

    Returns:
        Corresponding application error code, or UNKNOWN if the
        exception type is not explicitly mapped.
    """
    for exception_type, error_code in _EXCEPTION_TO_ERROR.items():
        if isinstance(exc, exception_type):
            return error_code

    return ErrorCode.UNKNOWN

def handle_http_error(exc: HTTPError) -> Failure:
    """Convert an HTTPX exception into a Failure result.

    Args:
        exc: HTTPX exception raised during an HTTP operation.

    Returns:
        Failure containing the mapped error code and exception details.
        HTTPStatusError additionally includes the HTTP response status code.
    """
    details: dict[str, Any] = {
        "exception": type(exc).__name__,
        "detail": str(exc),
    }

    if isinstance(exc, HTTPStatusError):
        details["status_code"] = exc.response.status_code

    return failure(
        message=type(exc).__name__,
        code=_get_error_code(exc),
        details=details,
    )