

from enum import Enum


class ErrorCode(Enum):
    # General errors
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    TOO_MANY_REDIRECTS = "too_many_redirects"
    HTTP_STATUS_ERROR = "http_status_error"
    VALIDATION_ERROR = "validation_error"
    DECODING_ERROR = "decoding_error"
    PERMISSION_DENIED = "permission_denied"
    INVALID_URL = "invalid_url"
    PROTOCOL_ERROR = "protocol_error"
    PROXY_ERROR = "proxy_error"
    UNKNOWN = "unknown"
    # Authentication errors
    AUTH_REQUIRED = "auth_required"
    AUTH_FAILED = "auth_failed"
    AUTH_EXPIRED = "auth_expired"
    AUTH_CANCELLED = "auth_cancelled"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_REFRESH_FAILED = "token_refresh_failed"
    # Network errors
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    # Configuration errors
    CONFIG_INVALID = "config_invalid"
    CONFIG_MISSING = "config_missing"
    # Skill errors
    SKILL_NOT_FOUND = "skill_not_found"
    SKILL_INVALID = "skill_invalid"
    SKILL_INSTALL_FAILED = "skill_install_failed"
    # Session errors
    SESSION_NOT_FOUND = "session_not_found"
    SESSION_CORRUPTED = "session_corrupted"
    # MCP errors
    MCP_SERVER_NOT_FOUND = "mcp_server_not_found"
    MCP_CONFIG_ERROR = "mcp_config_error"