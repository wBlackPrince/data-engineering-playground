import httpx
import pytest

from src.apis.async_http_client import AsyncHttpClient
from src.apis.error_code import ErrorCode
from src.apis.result import Failure, Success, is_failure, is_success


class TestAsyncHttpClient:
    """Tests for AsyncHttpClient."""

   