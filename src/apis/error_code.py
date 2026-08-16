from enum import Enum


class ErrorCode(Enum):
    """Application-level error codes."""

    # General
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_DENIED = "permission_denied"
    UNKNOWN = "unknown"

    # HTTP
    HTTP_STATUS_ERROR = "http_status_error"
    TOO_MANY_REDIRECTS = "too_many_redirects"
    DECODING_ERROR = "decoding_error"
    INVALID_URL = "invalid_url"
    PROTOCOL_ERROR = "protocol_error"
    PROXY_ERROR = "proxy_error"
    UNSUPPORTED_PROTOCOL = "unsupported_protocol"

    # Authentication
    AUTH_REQUIRED = "auth_required"
    AUTH_FAILED = "auth_failed"
    TOKEN_EXPIRED = "token_expired"

    # Network
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"

    # Configuration
    CONFIG_INVALID = "config_invalid"
    CONFIG_MISSING = "config_missing"