import argparse
import dataclasses
import logging
from typing import Self

from ..context import Context
from ..subcommand import Subcommand

log = logging.getLogger(__name__)


@dataclasses.dataclass
class Reopen(Subcommand):
    """Mark a task as incomplete."""

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
        print("Not implemented yet!")
