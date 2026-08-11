
from dataclasses import dataclass
from typing import Any

from apis.error_type import ErrorType



@dataclass
class Result:
    value: Any
    error: ErrorType