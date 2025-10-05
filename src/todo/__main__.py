"""
The main entry point to the application.
"""

import enum
import logging
import os
import pathlib
import sqlite3
import sys
from importlib.metadata import metadata, packages_distributions, version
from typing import Sequence

from .args import setup_parser
from .context import Context
from .logger import level_from_directive, setup_logger
from .pyproject import pyproject_init
from .subcommand import subcommand_registry
from .verbosity import Verbosity

log = logging.getLogger(__name__)


class ExitCode(enum.IntEnum):
    """Describes the status of the program after it has terminated.

    Attributes
    ----------
    SUCCESS
        Terminated without any errors.
    FAILURE
        Terminated due to an unrecoverable error.
    USAGE
        Terminated due to invalid command-line arguments.
    """

    SUCCESS = 0
    FAILURE = 1
    USAGE = 2


def main(argv: Sequence[str] = sys.argv[1:]) -> ExitCode:
    """The main entry point to the program.

    This function is intended to be wrapped by [`sys.exit`][sys.exit] so that
    its return value becomes the program's exit code.

    Parameters
    ----------
    argv
        Command-line arguments.

    Returns
    -------
    ExitCode
        Zero indicates success; non-zero indicates failure.

    Notes
    -----
    The `args` parameter is primarily intended for testing. In normal usage,
    the program is installed with a wrapper script on `PATH` that calls this
    function without arguments.
    """
    parser = setup_parser()
    args = parser.parse_args(argv)

    verbosity = Verbosity.from_args(args.verbose, args.quiet)
    handlers = [logging.StreamHandler(sys.stderr)]
    assert all(map(lambda h: isinstance(h, logging.Handler), handlers))

    match verbosity:
        case Verbosity.SILENT:
            logging.disable()
        case Verbosity.DEFAULT:
            fallback = Verbosity.DEFAULT.to_level_name()
            assert fallback is not None
            assert __package__ is not None
            directive = os.getenv(f"{__package__.upper()}_LOG", fallback)

            if (level := level_from_directive(directive)) is None:
                logging.disable()
            else:
                setup_logger(level, handlers)
        case _:
            level = verbosity.to_level()
            assert level is not None
            setup_logger(level, handlers)

    if sys.platform == "linux":
        data_dir = pathlib.Path.home().joinpath(".local", "share", "todo")
    else:
        # TODO: Update to use the proper paths on each platform.
        data_dir = pathlib.Path.home().joinpath(".todo")

    data_dir.mkdir(parents=True, exist_ok=True)

    database = data_dir.joinpath("todo.sqlite3")
    connection = sqlite3.connect(database)
    ctx = Context(connection)

    assert hasattr(args, "subcommand")
    assert isinstance(args.subcommand, str), type(args.subcommand)
    assert args.subcommand in subcommand_registry, subcommand_registry.keys()
    subcommand = subcommand_registry[args.subcommand]
    subcommand.from_args(args).run(ctx)

    return ExitCode.SUCCESS


if __name__ == "__main__":
    sys.exit(main())
