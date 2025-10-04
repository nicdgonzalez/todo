import dataclasses
import datetime as dt
import enum
from typing import Any

from dateutil.tz import tzlocal


class Priority(enum.Enum):
    """Describes the importance of the task."""

    LOW = 0
    MEDIUM = 1
    HIGH = 2


class Status(enum.Enum):
    """Describes the current state of the task."""

    PENDING = 0
    ACTIVE = 1
    COMPLETED = 2


@dataclasses.dataclass
class Task:
    """Represents a single task.

    Parameters
    ----------
    id
        A unique identifier.
    title
        A brief description explaining the task.
    priority
        Indicates how important the task is.
    status
        Indicates the current state of the task.
    created_at
        A timestamp indicating when the task was inserted into the database.
    updated_at
        A timestamp indicating when the task was last modified.
    """

    id: int
    title: str
    priority: Priority
    status: Status
    created_at: dt.datetime
    updated_at: dt.datetime

    @classmethod
    def from_data(
        cls,
        id: int,
        title: str,
        priority: int,
        status: int,
        created_at: float,
        updated_at: float,
    ) -> "Task":
        return cls(
            id=id,
            title=title,
            priority=Priority(priority),
            status=Status(status),
            created_at=dt.datetime.fromtimestamp(created_at, tz=tzlocal()),
            updated_at=dt.datetime.fromtimestamp(updated_at, tz=tzlocal()),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.name,
            "status": self.status.name,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "updated_at": self.updated_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
