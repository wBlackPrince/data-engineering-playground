from dataclasses import astuple, dataclass
from datetime import date, datetime
from typing import Any, ClassVar

from src.apis.error_code import ErrorCode
from src.apis.result import FailureContext, Result, failure, success
from src.models.entity import Entity


@dataclass(slots=True)
class GitlabIssue(Entity):
    DATABASE = "warehouse"
    TABLE_NAME = "issues"
    PATH_TO_TABLE = f"{DATABASE}.{TABLE_NAME}"

    COLUMNS: ClassVar[tuple[str, ...]] = (
        "id",
        "iid",
        "project_id",
        "title",
        "description",
        "state",
        "created_at",
        "updated_at",
        "closed_at",
        "due_date",
        "author_id",
        "author_username",
        "assignee_ids",
        "labels",
        "milestone_id",
        "confidential",
        "weight",
        "discussion_locked",
        "web_url",
    )

    id: int
    iid: int
    project_id: int

    title: str
    description: str | None
    state: str

    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    due_date: date | None

    author_id: int | None
    author_username: str | None

    assignee_ids: list[int]
    labels: list[str]
    milestone_id: int | None

    confidential: bool
    weight: int | None
    discussion_locked: bool | None

    web_url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Result["GitlabIssue"]:
        try:
            author = data.get("author") or {}

            due_date_value = data.get("due_date")

            issue = cls(
                id=data["id"],
                iid=data["iid"],
                project_id=data["project_id"],
                title=data["title"],
                description=data.get("description"),
                state=data["state"],
                created_at=parse_datetime(data["created_at"]),
                updated_at=parse_datetime(data["updated_at"]),
                closed_at=parse_datetime(data.get("closed_at")),
                due_date=(
                    date.fromisoformat(due_date_value)
                    if due_date_value
                    else None
                ),
                author_id=get_user_id(author),
                author_username=get_user_username(author),
                assignee_ids=get_assignee_ids(data.get("assignees", [])),
                labels=data.get("labels", []),
                milestone_id=(
                    data["milestone"]["id"]
                    if data.get("milestone")
                    else None
                ),
                confidential=data.get("confidential", False),
                weight=data.get("weight"),
                discussion_locked=data.get("discussion_locked"),
                web_url=data["web_url"],
            )

            return success(issue)

        except (KeyError, TypeError, ValueError) as ex:
            return failure(
                message="Failed to create GitlabIssue from dict",
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