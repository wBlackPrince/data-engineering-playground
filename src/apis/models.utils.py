from datetime import datetime
from typing import Any


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_user_id(data: dict[str, Any] | None) -> int | None:
    if data is None:
        return None

    return data.get("id")


def get_user_username(data: dict[str, Any] | None) -> str | None:
    if data is None:
        return None

    return data.get("username")


def get_assignee_ids(data: list[dict[str, Any]]) -> list[int]:
    return [
        assignee["id"]
        for assignee in data
        if assignee.get("id") is not None
    ]