import datetime as dt
import enum
import json
import pathlib
import sqlite3
from typing import Annotated, Literal

import clap
from colorize import Colorize
from dateutil.tz import tzlocal

__all__ = ("app",)

app = clap.Application(
    brief="",
    after_help="Repository: https://github.com/nicdgonzalez/todo",
)

filepath = pathlib.Path(__file__).resolve().parents[2].joinpath("todo.sqlite3")
connection = sqlite3.connect(
    f"file://{filepath.as_posix()}",
    timeout=5.0,
    detect_types=0,
    isolation_level="DEFERRED",
    check_same_thread=True,
    factory=sqlite3.Connection,
    cached_statements=128,
    uri=True,
    autocommit=True,
)

cursor = connection.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        -- A unique identifier that represents the current task.
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- A brief summary explaining the task.
        task TEXT NOT NULL,
        -- Priority: 0=Low, 1=Medium, 2=High
        priority INTEGER CHECK (priority >= 0 AND priority <= 2) DEFAULT 1,
        -- Status: 0=Pending, 1=Active, 2=Completed
        status INTEGER CHECK (status >= 0 AND status <= 2) DEFAULT 0,
        -- A timestamp indicating when the task was created.
        created_at NUMERIC NOT NULL,
        -- A timestamp indicating the last time the entry was updated.
        updated_at NUMERIC NOT NULL
    );
    """
)


class Priority(enum.IntEnum):
    LOW = 0
    MEDIUM = enum.auto()
    HIGH = enum.auto()

    @classmethod
    def from_int(cls, value: int, /) -> "Priority":
        match value:
            case 0:
                return cls.LOW
            case 1:
                return cls.MEDIUM
            case 2:
                return cls.HIGH
            case int():
                raise ValueError("expected value between 0 and 2, inclusive")
            case _:
                raise TypeError(f"expected type int, got {type(value)}")

        raise AssertionError("unreachable:", value)

    def __str__(self) -> str:
        match self.value:
            case self.LOW:
                return "Low"
            case self.MEDIUM:
                return "Medium"
            case self.HIGH:
                return "High"
            case _:
                raise AssertionError("unreachable:")


class Status(enum.IntEnum):
    PENDING = 0
    ACTIVE = enum.auto()
    COMPLETED = enum.auto()

    @classmethod
    def from_int(cls, value: int, /) -> "Priority":
        match value:
            case 0:
                return cls.PENDING
            case 1:
                return cls.ACTIVE
            case 2:
                return cls.COMPLETED
            case int():
                raise ValueError("expected value between 0 and 2, inclusive")
            case _:
                raise TypeError(f"expected type int, got {type(value)}")

        raise AssertionError("unreachable:", value)

    def __str__(self) -> str:
        match self.value:
            case self.PENDING:
                return "Pending"
            case self.ACTIVE:
                return "Active"
            case self.COMPLETED:
                return "Completed"
            case _:
                raise AssertionError("unreachable:")


class Task:
    def __init__(
        self,
        id: int,
        task: str,
        priority: Literal[0, 1, 2],
        status: Literal[0, 1, 2],
        created_at: float,
        updated_at: float,
    ) -> None:
        self.id = id
        self.task = task
        self.priority = Priority.from_int(priority)
        self.status = Status.from_int(status)
        self.created_at = dt.datetime.fromtimestamp(created_at, tz=tzlocal())
        self.updated_at = dt.datetime.fromtimestamp(updated_at, tz=tzlocal())

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "task": self.task,
            "priority": str(self.priority),
            "status": str(self.status),
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "updated_at": self.updated_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }

    def display(self) -> None:
        print(
            self.id,
            self.task,
            self.priority,
            self.status,
            self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            sep=" | ",
        )


@app.subcommand()
def add(
    task: str,
    *,
    priority: Annotated[Literal["low", "medium", "high"], clap.Short] = "low",
    status: Annotated[
        Literal["pending", "active", "completed"], clap.Short
    ] = "pending",
) -> None:
    """Create a new task.

    Parameters
    ----------
    task
        A brief summary explaining the task.
    priority
        Indicates how important the task is.
    status
        Indicates the state of the task.
    """
    now = dt.datetime.now()
    priority_mapping = {
        "low": 0,
        "medium": 1,
        "high": 2,
    }
    status_mapping = {
        "pending": 0,
        "active": 1,
        "completed": 2,
    }

    # Add task to the database.
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO tasks(task, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            task,
            priority_mapping[priority],
            status_mapping[status],
            now.timestamp(),
            now.timestamp(),
        ),
    )

    task_id = cursor.lastrowid

    # Get the task back from the database so we can display it to the user.
    cursor.execute(
        """
        SELECT * FROM tasks WHERE id = ?;
        """,
        (task_id,),
    )

    result = cursor.fetchone()
    assert len(result) >= 6, len(result)
    new_task = Task(
        id=result[0],
        task=result[1],
        priority=result[2],
        status=result[3],
        created_at=result[4],
        updated_at=result[5],
    )

    print(
        "🎉",
        Colorize("Task added successfully!").bold().green(),
    )
    print()
    _display_field("ID", new_task.id)
    _display_field("Task", new_task.task)
    _display_field("Priority", new_task.priority)
    _display_field("Status", new_task.status)
    _display_field(
        "Created at", new_task.created_at.strftime("%Y-%m-%dT%H:%M:%S%z")
    )


def _display_field(key: str, value: object) -> None:
    print(
        f"{Colorize(key).bold()}: {value}",
    )


@app.subcommand()
def get(*, id: int) -> None:
    pass


@app.subcommand(name="list")
def _list(
    *,
    sort: Literal["id", "priority", "status", "created_at"] = "id",
    reverse: bool = False,
    as_json: bool = False,
) -> None:
    cursor = connection.cursor()
    # NOTE: clap guarantees that `sort` is one of the valid options.
    cursor.execute(
        f"""
        SELECT * FROM tasks ORDER BY {sort} {"DESC" if reverse else ""};
        """
    )
    results = cursor.fetchall()

    if as_json:
        print(
            json.dumps(
                [Task(*result).as_dict() for result in results],
                indent=2,
            )
        )
        return

    id_width = len(str(len(results))) if len(results) > 9 else 2

    task_width = max(
        len("Task"),
        max(
            map(len, [result[1] for result in results]),
            default=len("Task"),
        ),
    )

    priority_width = max(
        len("Priority"),
        max(
            map(
                len, [str(Priority.from_int(result[2])) for result in results]
            ),
            default=len("Priority"),
        ),
    )

    status_width = max(
        len("Status"),
        max(
            map(len, [str(Status.from_int(result[3])) for result in results]),
            default=len("Status"),
        ),
    )

    created_at_width = 24 if len(results) > 0 else len("created at")
    updated_at_width = 24 if len(results) > 0 else len("updated at")

    print(
        "┌",
        "─".center(id_width, "─"),
        "┬",
        "─".center(task_width, "─"),
        "┬",
        "─".center(priority_width, "─"),
        "┬",
        "─".center(status_width, "─"),
        "┬",
        "─".center(created_at_width, "─"),
        "┬",
        "─".center(updated_at_width, "─"),
        "┐",
        sep="─",
    )
    print(
        "│" + " ID".center(id_width),
        "Task".ljust(task_width),
        "Priority".ljust(priority_width),
        "Status".ljust(status_width),
        "Created at".ljust(created_at_width),
        "Updated at".ljust(updated_at_width) + " │",
        sep=" │ ",
    )
    print(
        "├",
        "─".center(id_width, "─"),
        "┼",
        "─".center(task_width, "─"),
        "┼",
        "─".center(priority_width, "─"),
        "┼",
        "─".center(status_width, "─"),
        "┼",
        "─".center(created_at_width, "─"),
        "┼",
        "─".center(updated_at_width, "─"),
        "┤",
        sep="─",
    )

    for result in results:
        task = Task(
            id=result[0],
            task=result[1],
            priority=result[2],
            status=result[3],
            created_at=result[4],
            updated_at=result[5],
        )

        print(
            "│ " + str(task.id).rjust(id_width, "0"),
            task.task.ljust(task_width),
            str(task.priority).ljust(priority_width),
            str(task.status).ljust(status_width),
            task.created_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
            task.updated_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "",
            sep=" │ ",
        )

    print(
        "└",
        "─".center(id_width, "─"),
        "┴",
        "─".center(task_width, "─"),
        "┴",
        "─".center(priority_width, "─"),
        "┴",
        "─".center(status_width, "─"),
        "┴",
        "─".center(created_at_width, "─"),
        "┴",
        "─".center(updated_at_width, "─"),
        "┘",
        sep="─",
    )


@app.subcommand()
def delete(*, id: int) -> None:
    cursor = connection.cursor()

    # TODO: Fetch row before deleting it so we can display to the user what is
    # being deleted.

    cursor.execute(
        """
        DELETE FROM tasks WHERE id = ?;
        """,
        (id,),
    )

    print("💣", Colorize("Task removed successfully!").bold().green())
