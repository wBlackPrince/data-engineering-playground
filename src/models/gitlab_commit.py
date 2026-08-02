from dataclasses import astuple, dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID


@dataclass(slots=True)
class GitlabCommit:
    DATABASE = "warehouse"
    TABLE_NAME = "commits"
    PATH_TO_TABLE = f"{DATABASE}.{TABLE_NAME}"

    COLUMNS: ClassVar[tuple[str, ...]] = (
        "id",
        "short_id",
        "created_at",
        "parent_ids",
        "title",
        "message",
        "author_name",
        "author_email",
        "authored_date",
        "committer_name",
        "committer_email",
        "committed_date",
        "web_url",
        "trailers",
        "extended_trailers",
    )

    id: UUID
    short_id: str
    created_at: datetime
    parent_ids: list[UUID]

    title: str
    message: str

    author_name: str
    author_email: str
    authored_date: datetime

    committer_name: str
    committer_email: str
    committed_date: datetime

    web_url: str

    trailers: dict[str, str]
    extended_trailers: dict[str, list[str]]

    @classmethod
    def from_dict(cls, data: dict) -> "GitlabCommit":
        return cls(
            id=UUID(data["id"]),
            short_id=data["short_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            parent_ids=[UUID(parent_id) for parent_id in data["parent_ids"]],
            title=data["title"],
            message=data["message"],
            author_name=data["author_name"],
            author_email=data["author_email"],
            authored_date=datetime.fromisoformat(data["authored_date"]),
            committer_name=data["committer_name"],
            committer_email=data["committer_email"],
            committed_date=datetime.fromisoformat(data["committed_date"]),
            web_url=data["web_url"],
            trailers=data["trailers"],
            extended_trailers=data["extended_trailers"],
        )

    def to_tuple(self) -> tuple:
        return astuple(self)

    @classmethod
    def columns(cls) -> str:
        return ", ".join(cls.COLUMNS)