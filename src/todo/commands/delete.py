import argparse
import dataclasses
import json
import logging
import sys
from typing import Self

from ..context import Context
from ..subcommand import Subcommand
from ..task import Task

log = logging.getLogger(__name__)


@dataclasses.dataclass
class Delete(Subcommand):
    """Remove a task from the database (permanently)."""

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
            type=int,
            help="Unique identifier for the task",
        )

    def run(self, ctx: Context, /) -> None:
        cursor = ctx.connection.cursor()

        # TODO: Get the task before deleting so we return it.
        cursor.execute(
            """
            SELECT * FROM task WHERE id = ?;
            """,
            (self.id,),
        )
        data = cursor.fetchone()

        if data is None:
            _ = sys.stderr.write(f"No task with ID {self.id} found\n")
            return

        task = Task.from_data(*data)

        cursor.execute(
            """
            DELETE FROM task WHERE id = ?;
            """,
            (self.id,),
        )
        ctx.connection.commit()

        _ = sys.stderr.write(f"Deleted task with ID {self.id}\n\n")
        _ = sys.stdout.write(json.dumps(task.as_dict(), indent=2) + "\n")
