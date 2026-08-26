from typing import ClassVar, Protocol, Self


class Entity(Protocol):
    """Protocol for entities that can be loaded into ClickHouse."""

    DATABASE: ClassVar[str]
    TABLE_NAME: ClassVar[str]
    PATH_TO_TABLE: ClassVar[str]
    COLUMNS: ClassVar[tuple[str, ...]]

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """Create an entity from a dictionary."""
        ...

    def to_tuple(self) -> tuple[object, ...]:
        """Convert the entity to a tuple for database insertion."""
        ...

    @classmethod
    def columns(cls) -> str:
        """Return entity column names as a comma-separated string."""
        return ", ".join(cls.COLUMNS)