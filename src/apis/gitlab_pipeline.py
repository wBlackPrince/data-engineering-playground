from dataclasses import astuple, dataclass
from datetime import datetime
import os
from typing import Any, ClassVar


from src.apis.error_code import ErrorCode
from src.apis.result import FailureContext, Result, failure, success
from src.models.entity import Entity


@dataclass(slots=True)
class GitlabPipeline(Entity):
    DATABASE = os.getenv("CLICKHOUSE_DATABASE")
    TABLE_NAME = "pipelines"
    PATH_TO_TABLE = f"{DATABASE}.{TABLE_NAME}"

    COLUMNS: ClassVar[tuple[str, ...]] = (
        "id",
        "project_id",
        "status",
        "source",
        "ref",
        "sha",
        "created_at",
        "updated_at",
        "started_at",
        "finished_at",
        "duration",
        "queued_duration",
        "coverage",
        "user_id",
        "user_username",
        "web_url",
    )

    id: int
    project_id: int

    status: str
    source: str | None
    ref: str
    sha: str

    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    duration: float | None
    queued_duration: float | None
    coverage: float | None

    user_id: int | None
    user_username: str | None

    web_url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Result["GitlabPipeline"]:
        try:
            user = data.get("user") or {}

            pipeline = cls(
                id=data["id"],
                project_id=data["project_id"],
                status=data["status"],
                source=data.get("source"),
                ref=data["ref"],
                sha=data["sha"],
                created_at=parse_datetime(data["created_at"]),
                updated_at=parse_datetime(data["updated_at"]),
                started_at=parse_datetime(data.get("started_at")),
                finished_at=parse_datetime(data.get("finished_at")),
                duration=data.get("duration"),
                queued_duration=data.get("queued_duration"),
                coverage=data.get("coverage"),
                user_id=get_user_id(user),
                user_username=get_user_username(user),
                web_url=data["web_url"],
            )

            return success(pipeline)

        except (KeyError, TypeError, ValueError) as ex:
            return failure(
                message="Failed to create GitlabPipeline from dict",
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
        return astuple(self)

    @classmethod
    def columns(cls) -> str:
        return ", ".join(cls.COLUMNS)