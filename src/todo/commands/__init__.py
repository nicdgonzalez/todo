"""
This module implements the CLI subcommands.
"""

import argparse

from ..subcommand import Subcommand
from .add import Add
from .complete import Complete
from .delete import Delete
from .edit import Edit
from .list import List
from .reopen import Reopen


def register_subcommands(parent: argparse.ArgumentParser) -> None:
    subcommand_parser = parent.add_subparsers(dest="subcommand", required=True)
    subcommand_handlers: list[type[Subcommand]] = [
        Add,
        Complete,
        Delete,
        Edit,
        List,
        Reopen,
    ]

    for subcommand_cls in subcommand_handlers:
        subcommand_cls.register(parent=subcommand_parser)


del argparse
