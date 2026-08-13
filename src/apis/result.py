
from dataclasses import dataclass
from typing import Any

from apis.error_type import ErrorCode, ErrorType



@dataclass(frozen=True)
class Success[T]:
    """Failed operation result."""
    value: T
    message: str | None = None

@dataclass(frozen=True)
class Failure[T]:
    """Failed operation result."""
    error: str
    code: ErrorCode
    details: dict[str, Any] | None = None

# The Result type alias
type Result[T] = Success[T] | Failure



def success[T](value: T, message: str | None = None) -> Success[T]:
    """Create a Success result."""
    return Success(value=value, message=message)

def failure(
    error: str,
    code: ErrorCode,
    details: dict[str, Any] | None = None
) -> Failure:
    """Create a Failure result."""
    return Failure(error=error, code=code, details=details)



def is_success[T](result: Result[T]) -> bool:
    """Check if a result is a Success."""
    return isinstance(result, Success)

def is_failure[T](result: Result[T]) -> bool:
    """Check if a result is a Failure."""
    return isinstance(result, Failure)