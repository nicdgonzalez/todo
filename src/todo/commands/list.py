import argparse
import dataclasses
import enum
import json
import logging
import sys
from typing import Self, Sequence

from ..context import Context
from ..subcommand import Subcommand
from ..task import Priority, Status, Task

log = logging.getLogger(__name__)


class SortBy(enum.IntEnum):
    """Indicates which column name to sort by."""

    ID = enum.auto()
    PRIORITY = enum.auto()
    STATUS = enum.auto()
    CREATED_AT = enum.auto()


@dataclasses.dataclass
class List(Subcommand):
    """Show tasks."""

    sort_by: SortBy
    reverse: bool
    as_json: bool
    show_all: bool

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Self:
        return cls(
            sort_by=args.sort_by,
            reverse=args.reverse,
            as_json=args.json,
            show_all=args.all,
        )

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, /) -> None:
        parser.add_argument(
            "--sort-by",
            action="store",
            default=SortBy.PRIORITY,
            type=SortBy,
            choices=[e.name.lower() for e in SortBy],
            help="",
        )
        parser.add_argument(
            "--reverse",
            action="store_true",
            help="Display output in reverse order",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Display output in JSON format",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Include completed tasks",
        )

    def run(self, ctx: Context, /) -> None:
        if self.sort_by == SortBy.PRIORITY:
            # When sorting by priority, we want to see important tasks first.
            self.reverse = not self.reverse

        desc = "DESC" if self.reverse else "ASC"

        cursor = ctx.connection.cursor()
        cursor.execute(
            f"""
            SELECT id, title, priority, status, created_at, updated_at
            FROM task
            {f"WHERE status != {Status.COMPLETED.value}" if not self.show_all else ""}
            ORDER BY
                {self.sort_by.name.lower()} {desc},
                CASE
                    WHEN status = {Status.COMPLETED.value} THEN 3
                    WHEN priority = {Priority.HIGH.value} AND status != {Status.COMPLETED.value} THEN 1
                    ELSE 2
                END {desc},
                priority {desc},
                status {desc}
            """,
            (),
        )

        tasks = [Task.from_data(*data) for data in cursor.fetchall()]

        if self.as_json:
            content = json.dumps([task.as_dict() for task in tasks], indent=2)
            _ = sys.stdout.write(content + "\n")
            return
        else:
            _ = sys.stdout.write("\n".join(render_table(tasks=tasks)) + "\n")


def render_table(tasks: Sequence[Task]) -> list[str]:
    width_id = max(2, len(str(len(tasks))))
    # Doubling the initial value handles the case where `tasks` is empty
    # since `*[]` resolves into `` (nothing) and the `int` by itself is not
    # a valid argument for `max` because it's not an iterable.
    width_title = max(5, 5, *[len(t.title) for t in tasks])
    width_priority = max(8, 8, *[len(t.priority.name) for t in tasks])
    width_status = max(6, 6, *[len(t.status.name) for t in tasks])
    # Length of datetime in ISO-8601 format else length of "Created at".
    width_created_at = 24 if len(tasks) > 0 else 10
    # Length of datetime in ISO-8601 format else length of "Updated at".
    width_updated_at = 24 if len(tasks) > 0 else 10

    lines = [
        # Line 1
        "┌"
        + "─" * (width_id + 2)
        + "┬"
        + "─" * (width_title + 2)
        + "┬"
        + "─" * (width_priority + 2)
        + "┬"
        + "─" * (width_status + 2)
        + "┬"
        + "─" * (width_created_at + 2)
        + "┬"
        + "─" * (width_updated_at + 2)
        + "┐",
        # Line 2
        "│ "
        + "ID".center(width_id)
        + " │ "
        + "Title".ljust(width_title)
        + " │ "
        + "Priority".ljust(width_priority)
        + " │ "
        + "Status".ljust(width_status)
        + " │ "
        + "Created at".ljust(width_created_at)
        + " │ "
        + "Updated at".ljust(width_updated_at)
        + " │",
        # Line 3
        "├"
        + "─" * (width_id + 2)
        + "┼"
        + "─" * (width_title + 2)
        + "┼"
        + "─" * (width_priority + 2)
        + "┼"
        + "─" * (width_status + 2)
        + "┼"
        + "─" * (width_created_at + 2)
        + "┼"
        + "─" * (width_updated_at + 2)
        + "┤",
    ]

    for task in tasks:
        created_at = task.created_at.strftime("%Y-%m-%dT%H:%M:%S%z")
        updated_at = task.updated_at.strftime("%Y-%m-%dT%H:%M:%S%z")

        lines.append(
            "│ "
            + str(task.id).center(width_id)
            + " │ "
            + task.title.ljust(width_title)
            + " │ "
            + task.priority.name.ljust(width_priority)
            + " │ "
            + task.status.name.ljust(width_status)
            + " │ "
            + created_at.ljust(width_created_at)
            + " │ "
            + updated_at.ljust(width_updated_at)
            + " │"
        )

    lines.append(
        "└"
        + "─" * (width_id + 2)
        + "┴"
        + "─" * (width_title + 2)
        + "┴"
        + "─" * (width_priority + 2)
        + "┴"
        + "─" * (width_status + 2)
        + "┴"
        + "─" * (width_created_at + 2)
        + "┴"
        + "─" * (width_updated_at + 2)
        + "┘",
    )

    return lines
