import pytest
from httpx import (
    DecodingError,
    HTTPStatusError,
    InvalidURL,
    NetworkError,
    ProtocolError,
    ProxyError,
    TimeoutException,
    TooManyRedirects,
    UnsupportedProtocol,
    Request,
    Response,
)

from src.apis.error_code import ErrorCode
from src.apis.result import (
    Failure,
    FailureContext,
    Success,
    Unit,
    create_http_error,
    failure,
    is_failure,
    is_success,
    success,
    unit_success,
)


class TestSuccess:
    """Tests for successful operation results."""

    def test_success_creates_success_result(self):
        """Create a Success result containing the provided value."""
        result = success(42)

        assert isinstance(result, Success)
        assert result.value == 42
        assert result.message is None

    def test_success_with_message(self):
        """Create a Success result with an optional message."""
        result = success(
            value="data",
            message="Operation completed",
        )

        assert result.value == "data"
        assert result.message == "Operation completed"

    def test_success_supports_any_value(self):
        """Allow Success to contain values of arbitrary types."""
        value = {"id": 1, "name": "Eduard"}

        result = success(value)

        assert result.value == value


class TestUnitSuccess:
    """Tests for successful results without a return value."""

    def test_unit_success_returns_unit(self):
        """Create a successful result containing a Unit value."""
        result = unit_success()

        assert isinstance(result, Success)
        assert isinstance(result.value, Unit)
        assert result.message is None

    def test_unit_success_with_message(self):
        """Create a UnitResult with an optional message."""
        result = unit_success("Inserted successfully")

        assert isinstance(result.value, Unit)
        assert result.message == "Inserted successfully"


class TestFailure:
    """Tests for failed operation results."""

    def test_failure_creates_failure_result(self):
        """Create a Failure result with message, code, and context."""
        context = FailureContext(
            operation="insert_query",
            source="ClickHouseRepository",
        )

        result = failure(
            message="Insert failed",
            code=ErrorCode.CLICKHOUSE_INSERT_ERROR,
            context=context,
        )

        assert isinstance(result, Failure)
        assert result.message == "Insert failed"
        assert result.code == ErrorCode.CLICKHOUSE_INSERT_ERROR
        assert result.context == context
        assert result.details is None

    def test_failure_with_details(self):
        """Create a Failure result containing additional error details."""
        context = FailureContext(
            operation="get_async",
            source="AsyncHttpClient",
        )

        details = {
            "exception": "TimeoutException",
            "detail": "Request timed out",
        }

        result = failure(
            message="TimeoutException",
            code=ErrorCode.TIMEOUT,
            context=context,
            details=details,
        )

        assert result.details == details


class TestTypeGuards:
    """Tests for Result type guard functions."""

    def test_is_success_returns_true_for_success(self):
        """Return True when the result is a Success instance."""
        result = success(42)

        assert is_success(result) is True

    def test_is_success_returns_false_for_failure(self):
        """Return False when the result is a Failure instance."""
        context = FailureContext(
            operation="test",
            source="test",
        )

        result = failure(
            message="Failed",
            code=ErrorCode.UNKNOWN,
            context=context,
        )

        assert is_success(result) is False

    def test_is_failure_returns_true_for_failure(self):
        """Return True when the result is a Failure instance."""
        context = FailureContext(
            operation="test",
            source="test",
        )

        result = failure(
            message="Failed",
            code=ErrorCode.UNKNOWN,
            context=context,
        )

        assert is_failure(result) is True

    def test_is_failure_returns_false_for_success(self):
        """Return False when the result is a Success instance."""
        result = success(42)

        assert is_failure(result) is False


class TestCreateHttpError:
    """Tests for converting HTTPX exceptions into Failure results."""

    @pytest.fixture
    def context(self):
        """Provide a standard HTTP operation failure context."""
        return FailureContext(
            operation="get_async",
            source="AsyncHttpClient",
        )

    @pytest.fixture
    def http_request(self):
        """Provide an HTTP request used by HTTPX exceptions."""
        return Request(
            "GET",
            "https://gitlab.com/api/v4/projects",
        )

    def test_http_status_error(self, context, http_request):
        """Map HTTPStatusError to HTTP_STATUS_ERROR with status details."""
        response = Response(
            status_code=404,
            request=http_request,
        )

        exc = HTTPStatusError(
            "404 Not Found",
            request=http_request,
            response=response,
        )

        result = create_http_error(exc, context)

        assert isinstance(result, Failure)
        assert result.message == "HTTPStatusError"
        assert result.code == ErrorCode.HTTP_STATUS_ERROR
        assert result.context == context

        assert result.details is not None
        assert result.details["exception"] == "HTTPStatusError"
        assert result.details["status_code"] == 404

    def test_timeout_error(self, context, request):
        """Map TimeoutException to TIMEOUT with exception details."""
        exc = TimeoutException(
            "Request timed out",
            request=request,
        )

        result = create_http_error(exc, context)

        assert result.code == ErrorCode.TIMEOUT
        assert result.message == "TimeoutException"
        assert result.context == context

        assert result.details is not None
        assert result.details["exception"] == "TimeoutException"
        assert result.details["detail"] == "Request timed out"

    @pytest.mark.parametrize(
        ("exception_type", "expected_code"),
        [
            (NetworkError, ErrorCode.NETWORK_ERROR),
            (ProtocolError, ErrorCode.PROTOCOL_ERROR),
            (ProxyError, ErrorCode.PROXY_ERROR),
            (TooManyRedirects, ErrorCode.TOO_MANY_REDIRECTS),
            (DecodingError, ErrorCode.DECODING_ERROR),
            (InvalidURL, ErrorCode.INVALID_URL),
            (UnsupportedProtocol, ErrorCode.UNSUPPORTED_PROTOCOL),
        ],
    )
    def test_http_exception_mapping(
        self,
        exception_type,
        expected_code,
        context,
        http_request,
    ):
        """Map supported HTTPX exception types to application error codes."""
        exc = exception_type(
            "HTTP error",
            request=http_request,
        )

        result = create_http_error(exc, context)

        assert isinstance(result, Failure)
        assert result.code == expected_code
        assert result.message == exception_type.__name__
        assert result.context == context

        assert result.details is not None
        assert result.details["exception"] == exception_type.__name__
        assert result.details["detail"] == "HTTP error"