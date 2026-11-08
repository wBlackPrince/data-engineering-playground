from dataclasses import astuple, dataclass
from decimal import Decimal
import json
from typing import Any, ClassVar
from uuid import UUID

from src.apis.error_code import ErrorCode
from src.apis.result import FailureContext, Result, failure, success
from src.models.entity import Entity


from typing import Any
from uuid import UUID

def parse_uuid_array(value: Any) -> list[UUID] | None:
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "{}":
            return []

        if value.startswith("{") and value.endswith("}"):
            value = value[1:-1]

        value = [
            item.strip().strip('"')
            for item in value.split(",")
        ]

    return [UUID(str(item)) for item in value]


@dataclass(slots=True)
class Question(Entity):
    DATABASE = "warehouse"
    TABLE_NAME = "questions"
    PATH_TO_TABLE = f"{DATABASE}.{TABLE_NAME}"

    COLUMNS: ClassVar[tuple[str, ...]] = (
        "id",
        "description",
        '"Type"',
        "points_cost",
        "test_id",
        "position_index",
        "match_ids",
        "option_ids",
        "right_answer",
    )

    id: UUID
    description: str
    Type: int
    points_cost: Decimal
    test_id: UUID
    position_index: int
    match_ids: list[UUID] | None
    option_ids: list[UUID] | None
    right_answer: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Result["Question"]:
        try:
            question = cls(
                id=UUID(str(data["id"])),
                description=data["description"],
                Type=data["Type"],
                points_cost=Decimal(str(data["points_cost"])),
                test_id=UUID(str(data["test_id"])),
                position_index=data["position_index"],
                match_ids=parse_uuid_array(data["match_ids"]),
                option_ids=parse_uuid_array(data["option_ids"]),
                right_answer=data["right_answer"],
            )

            return success(question)

        except (KeyError, TypeError, ValueError) as ex:
            return failure(
                message="Failed to create Question from dict",
                code=ErrorCode.PARSE_ERROR,
                context=FailureContext(
                    operation="from_dict",
                    source=cls.__name__,
                ),
                details={
                    "exception": type(ex).__name__,
                    "detail": str(ex),
                },
            )

    def to_tuple(self) -> tuple:
        return (
            self.id,
            self.description,
            self.Type,
            self.points_cost,
            self.test_id,
            self.position_index,
            self.match_ids or [],
            self.option_ids or [],
            self.right_answer,
        )

    @classmethod
    def columns(cls) -> str:
        return ", ".join(cls.COLUMNS)

    @classmethod
    def from_tuple(cls, row: tuple) -> Result["Question"]:
        try:
            def parse_uuid(value: Any, field: str) -> UUID:
                try:
                    return UUID(str(value))
                except (ValueError, TypeError, AttributeError) as ex:
                    raise ValueError(
                        f"Invalid UUID in {field}: "
                        f"value={value!r}, type={type(value).__name__}"
                    ) from ex

            question = cls(
                id=parse_uuid(row[0], "id"),
                description=row[1],
                Type=row[2],
                points_cost=Decimal(str(row[3])),
                test_id=parse_uuid(row[4], "test_id"),
                position_index=row[5],
                match_ids=parse_uuid_array(row[6]),
                option_ids=parse_uuid_array(row[7]),
                right_answer=row[8],
            )

            return success(question)

        except (IndexError, TypeError, ValueError) as ex:
            return failure(
                message="Failed to create Question from tuple",
                code=ErrorCode.PARSE_ERROR,
                context=FailureContext(
                    operation="from_tuple",
                    source=cls.__name__,
                ),
                details={
                    "exception": type(ex).__name__,
                    "detail": str(ex),
                },
            )