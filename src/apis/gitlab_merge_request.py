from dataclasses import astuple, dataclass
from datetime import datetime
from typing import Any, ClassVar

from src.apis.error_code import ErrorCode
from src.apis.result import FailureContext, Result, failure, success
from src.models.entity import Entity

@dataclass(slots=True)
class GitlabMergeRequest(Entity):
    DATABASE = "warehouse"
    TABLE_NAME = "merge_requests"
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
        "merged_at",
        "closed_at",
        "target_branch",
        "source_branch",
        "author_id",
        "author_username",
        "assignee_ids",
        "labels",
        "milestone_id",
        "draft",
        "merge_status",
        "sha",
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
    merged_at: datetime | None
    closed_at: datetime | None

    target_branch: str
    source_branch: str

    author_id: int | None
    author_username: str | None

    assignee_ids: list[int]
    labels: list[str]
    milestone_id: int | None

    draft: bool
    merge_status: str | None
    sha: str
    web_url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Result["GitlabMergeRequest"]:
        try:
            author = data.get("author") or {}

            merge_request = cls(
                id=data["id"],
                iid=data["iid"],
                project_id=data["project_id"],
                title=data["title"],
                description=data.get("description"),
                state=data["state"],
                created_at=parse_datetime(data["created_at"]),
                updated_at=parse_datetime(data["updated_at"]),
                merged_at=parse_datetime(data.get("merged_at")),
                closed_at=parse_datetime(data.get("closed_at")),
                target_branch=data["target_branch"],
                source_branch=data["source_branch"],
                author_id=get_user_id(author),
                author_username=get_user_username(author),
                assignee_ids=get_assignee_ids(data.get("assignees", [])),
                labels=data.get("labels", []),
                milestone_id=(
                    data["milestone"]["id"]
                    if data.get("milestone")
                    else None
                ),
                draft=data.get("draft", False),
                merge_status=data.get("merge_status"),
                sha=data["sha"],
                web_url=data["web_url"],
            )

            return success(merge_request)

        except (KeyError, TypeError, ValueError) as ex:
            return failure(
                message="Failed to create GitlabMergeRequest from dict",
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