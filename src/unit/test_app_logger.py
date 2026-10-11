import logging

import pytest

from src.apis.app_logger import (
    AppLogger,
    Emoji,
    LogEventType,
)
from src.apis.error_code import ErrorCode
from src.apis.result import Failure, FailureContext


class TestAppLoggerSecretMasking:
    """Tests for sensitive data masking in AppLogger."""

    