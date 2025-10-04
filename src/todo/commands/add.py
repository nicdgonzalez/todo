import argparse
import dataclasses
import json
import logging
import sys
from typing import Self

from ..context import Context
from ..subcommand import Subcommand
from ..task import Priority, Status, Task

log = logging.getLogger(__name__)


@dataclasses.dataclass
class Add(Subcommand):
    """Create a new task."""

    title: str
    priority: Priority
    status: Status

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Self:
        return cls(
            title=args.title,
            priority=Priority[args.priority],
            status=Status[args.status],
        )

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, /) -> None:
        parser.add_argument(
            "title",
            action="store",
            type=str,
            help="Description of the task",
        )
        parser.add_argument(
            "--priority",
            action="store",
            default=Priority.LOW.name,
            type=str,
            choices=[e.name for e in Priority],
            help="Importance of the task",
        )
        parser.add_argument(
            "--status",
            action="store",
            default=Status.PENDING.name,
            type=str,
            choices=[e.name for e in Status],
            help="Current state of the task",
        )

    def run(self, ctx: Context, /) -> None:
        cursor = ctx.connection.cursor()
        cursor.execute(
            """
            INSERT INTO task(title, priority, status)
            VALUES(?, ?, ?);
            """,
            (
                self.title,
                self.priority.value,
                self.status.value,
            ),
        )
        ctx.connection.commit()

        task_id = cursor.lastrowid
        cursor.execute(
            """
            SELECT id, title, priority, status, created_at, updated_at
            FROM task
            WHERE id = ?;
            """,
            (task_id,),
        )

        data = cursor.fetchone()
        task = Task.from_data(*data)

        _ = sys.stderr.write("Task created successfully!\n\n")
        _ = sys.stdout.write(json.dumps(task.as_dict(), indent=2) + "\n")
