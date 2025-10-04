import argparse
import dataclasses
import datetime
import json
import logging
import sys
from typing import Self

from ..context import Context
from ..subcommand import Subcommand
from ..task import Status, Task

log = logging.getLogger(__name__)


@dataclasses.dataclass
class Complete(Subcommand):
    """Mark a task as complete."""

    id: int

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Self:
        return cls(
            id=args.id,
        )

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, /) -> None:
        parser.add_argument(
            "id",
            action="store",
            type=str,
            help="Unique identifier for the task",
        )

    def run(self, ctx: Context, /) -> None:
        now = datetime.datetime.now()
        cursor = ctx.connection.cursor()
        cursor.execute(
            f"""
            UPDATE task
            SET
                status = {Status.COMPLETED.value},
                updated_at = {now.timestamp()}
            WHERE id = ?;
            """,
            (self.id,),
        )
        ctx.connection.commit()

        cursor.execute(
            """
            SELECT id, title, priority, status, created_at, updated_at
            FROM task
            WHERE id = ?
            """,
            (self.id,),
        )
        data = cursor.fetchone()
        task = Task.from_data(*data)

        _ = sys.stderr.write(f"Completed task with ID {self.id}\n\n")
        _ = sys.stdout.write(json.dumps(task.as_dict(), indent=2) + "\n")
