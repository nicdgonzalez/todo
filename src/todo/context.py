"""
This module implements a dataclass for passing around data between subcommands.
"""

import dataclasses
import sqlite3


@dataclasses.dataclass
class Context:
    """A type for passing around relevant data and state information.

    Parameters
    ----------
    connection
        Handle to the database.
    """

    connection: sqlite3.Connection
