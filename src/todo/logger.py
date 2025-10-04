"""
This module provides utility functions for configuring the logger.
"""

import logging
from typing import Iterable


def setup_logger(
    level: int,
    handlers: Iterable[logging.Handler],
) -> None:
    """Prepare the logger to start listening for events.

    This function should only be called once at the start of the program.

    Parameters
    ----------
    level
        The minimum level required for events to be recorded.
    handlers
        A collection of event processors (e.g., writing to stderr or file).
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 format
        style="%",
    )

    for handler in handlers:
        handler.setFormatter(fmt=formatter)
        logging.root.addHandler(hdlr=handler)

    logging.root.setLevel(level=level)


def level_from_directive(directive: str) -> int | None:
    """Convert a string level into a valid logging level.

    Parameters
    ----------
    directive
        Should be one of [OFF, DEBUG, INFO, WARNING, ERROR, CRITICAL].

    Returns
    -------
    int
        A logging level from the [`logging`] module.
    None
        Indicates a desire to disable logging.

    Raises
    ------
    ValueError
        An invalid value for `directive` was used.

    Notes
    -----
    It is possible that there are more levels defined in [`logging`][logging]
    than are available here. This function limits the valid directives to
    a subset of known logging levels to ensure we can always return `int`.
    """
    match directive.upper():
        case "OFF":
            return None
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO
        case "WARNING" | "WARN":
            return logging.WARNING
        case "ERROR":
            return logging.ERROR
        case "CRITICAL" | "FATAL":
            return logging.CRITICAL
        case _:
            raise ValueError(f"invalid log level directive: {directive}")
