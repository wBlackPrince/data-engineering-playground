from enum import Enum
import logging
import re
from typing import ClassVar

from apis.result import Failure

stream_format = (
    "{asctime} | {emoji} | {levelname} | {name} | "
    "{code} | {context} | {message} | {details}"
)

_SECRETS_PATTERN = re.compile(
    r"""
    (?P<key>password|token|secret|api_key|authorization|bearer|basic)
    \s*[:=]\s*
    (?:"(?P<quoted>[^"]*)"|'(?P<single>[^']*)'|(?P<plain>\S+))
    """,
    re.IGNORECASE | re.VERBOSE,
)

_URL_CREDENTIALS_PATTERN = re.compile(
    r"(https?://)([^:]+):([^@]+)@",
    re.IGNORECASE,
)

class LogEventType(Enum):
    """Logging event types mapped to standard Python logging levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class Emoji(Enum):
    """Emoji representations associated with logging severity levels."""
    DEBUG = "🐛"
    INFO = "ℹ️"
    WARNING = "⚠️"
    ERROR = "❌"
    FATAL = "💀"


_EMOJI_MAP: dict[int, str] = {
    logging.DEBUG: Emoji.DEBUG.value,
    logging.INFO: Emoji.INFO.value,
    logging.WARNING: Emoji.WARNING.value,
    logging.ERROR: Emoji.ERROR.value,
    logging.CRITICAL: Emoji.FATAL.value,
}

class AppLogger:
    """Application logger with structured failure context and secret masking.

    Provides a simplified interface over Python's standard logging module.
    Application-level failures are represented by ``Failure`` objects and
    logged with their error code, context, and details. Unexpected exceptions
    can be logged separately with their traceback.
    """
    _logger_names: ClassVar[list[str]] = []

    def __init__(self, name: str) -> None:
        """Initialize an application logger.

        Args:
            name: Name of the logger used by the underlying logging system.
                Logger configuration is initialized only once for each name.
        """
        self._logger = logging.getLogger(name)

        if name not in AppLogger._logger_names:
            self._logger.setLevel(logging.DEBUG)

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_formatter = logging.Formatter(stream_format, style="{")
            stream_handler.setFormatter(stream_formatter)

            self._logger.addHandler(stream_handler)
            AppLogger._logger_names.append(name)

    @staticmethod
    def _make_secret(message: str) -> str:
        """Mask sensitive credentials in a log message.

        Replaces values associated with common secret-related keys and masks
        credentials embedded in HTTP URLs.

        Args:
            message: Log message that may contain sensitive information.

        Returns:
            The message with detected credentials replaced by ``***``.
        """
        message = _SECRETS_PATTERN.sub(lambda m: f"{m.group('key')}=***", message)
        message = _URL_CREDENTIALS_PATTERN.sub(r"\1\2:***@", message)
        return message

    @staticmethod
    def _make_extra(event_type: LogEventType, failure: Failure | None = None) -> dict[str, str]:
        """Build structured logging fields for a log record.

        The returned dictionary contains fields required by the configured
        log formatter. When a failure is provided, its error code, context,
        and details are included in the record.

        Args:
            event_type: Type and severity of the logging event.
            failure: Optional application-level failure associated with the event.

        Returns:
            A dictionary containing emoji, error code, context, and details.
        """
        emoji: str = _EMOJI_MAP.get(event_type.value, Emoji.INFO.value)

        extra: dict[str, str] = {
            "emoji": emoji,
            "code": "",
            "context": "",
            "details": "",
        }

        if failure is not None:
            extra["code"] = failure.code.value
            extra["context"] = f"{failure.context.source}.{failure.context.operation}"

            details = (
                ", ".join(
                    f"{key}:{value}"
                    for key, value in failure.details.items()
                )
                if failure.details
                else ""
            )
            details = AppLogger._make_secret(f"{{{details}}}")
            extra["details"] = details

        return extra

    def _log_event(self, event_type: LogEventType, message: str, failure: Failure | None = None) -> None:
        """Write a structured log event.

        Args:
            event_type: Type and severity of the logging event.
            message: Message to write to the log.
            failure: Optional application-level failure associated with the event.
        """
        extra = self._make_extra(event_type, failure)
        self._logger.log(
            event_type.value,
            self._make_secret(message),
            extra=extra
        )

    def log_debug(self, message: str) -> None:
        """Log a debug-level message.

        Args:
            message: Message to write to the log.
        """
        self._log_event(LogEventType.DEBUG, message)

    def log_info(self, message: str) -> None:
        """Log an informational message.

        Args:
            message: Message to write to the log.
        """
        self._log_event(LogEventType.INFO, message)

    def log_warning(self, message: str) -> None:
        """Log a warning-level message.

        Args:
            message: Message to write to the log.
        """
        self._log_event(LogEventType.WARNING, message)

    def log_error(self, failure: Failure) -> None:
        """Log an application-level failure at error severity.

        The failure message, error code, context, and details are included
        in the structured log record.

        Args:
            failure: Application-level failure to log.
        """
        self._log_event(LogEventType.ERROR, failure.message, failure)

    def log_critical(self, failure: Failure) -> None:
        """Log an application-level failure at critical severity.

        The failure message, error code, context, and details are included
        in the structured log record.

        Args:
            failure: Application-level failure to log.
        """
        self._log_event(LogEventType.CRITICAL, failure.message, failure)

    def log_exception(self, message: str, ex: Exception) -> None:
        """Log an unexpected exception with its traceback.

        Unlike ``log_error()``, this method is intended for unexpected
        exceptions rather than application-level ``Failure`` results.

        Args:
            message: Message describing the operation that failed.
            ex: Exception to log, including its traceback information.
        """
        self._logger.error(
            self._make_secret(message),
            exc_info=(type(ex), ex, ex.__traceback__),
            extra=self._make_extra(LogEventType.ERROR)
        )
