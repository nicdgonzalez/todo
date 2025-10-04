"""
This module implements the command-line argument parser.
"""

import argparse

from .commands import register_subcommands


def setup_parser() -> argparse.ArgumentParser:
    """Configure the command-line argument parser."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        required=False,
        help="Use verbose output (or `-vv` for more verbose output)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        required=False,
        help="Use quiet output (or `-qq` for silent output)",
    )

    register_subcommands(parent=parser)
    return parser
