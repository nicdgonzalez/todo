"""
This module converts command-line arguments to logging levels.
"""

import enum
import logging


class Verbosity(enum.IntEnum):
    """Convert command-line arguments into a valid logging level.

    Attributes
    ----------
    SILENT
        Supress all logging output.
    QUIET
        Log events up to level [`logging.ERROR`][logging.ERROR].
    DEFAULT
        Log events up to level [`logging.WARNING`][logging.WARNING].
    VERBOSE
        Log events up to level [`logging.INFO`][logging.INFO].
    EXTRA_VERBOSE
        Log events up to level [`logging.DEBUG`][logging.DEBUG].
    """

    SILENT = enum.auto()
    QUIET = enum.auto()
    DEFAULT = enum.auto()
    VERBOSE = enum.auto()
    EXTRA_VERBOSE = enum.auto()

    @classmethod
    def from_args(cls, verbose: int, quiet: int) -> "Verbosity":
        """Construct a new verbosity level from command-line arguments.

        This function takes the values of `verbose` and `quiet` and returns
        the corresponding `Verbosity` level.

        Note: `quiet` has a higher priority than `verbose`.

        Raises
        ------
        ValueError
            Either `verbose` or `quiet` are less than 0.
        """
        match quiet:
            case n if n < 0:
                raise ValueError(f"expected value greater than 0, got {n}")
            case 0:
                pass
            case 1:
                return cls.QUIET
            case _:
                return cls.SILENT

        match verbose:
            case n if n < 0:
                raise ValueError(f"expected value greater than 0, got {n}")
            case 0:
                return cls.DEFAULT
            case 1:
                return cls.VERBOSE
            case _:
                return cls.EXTRA_VERBOSE

    def to_level(self) -> int | None:
        """Convert the verbosity level into a logging level."""
        match self:
            case self.SILENT:
                return None
            case self.QUIET:
                return logging.ERROR
            case self.DEFAULT:
                return logging.WARNING
            case self.VERBOSE:
                return logging.INFO
            case self.EXTRA_VERBOSE:
                return logging.DEBUG
            case level:
                raise NotImplementedError(f"unexpected level: {level}")

    def to_level_name(self) -> str | None:
        """Convert the verbosity level into a logging level."""
        level = self.to_level()

        if level is None:
            return None

        level_name = logging.getLevelName(level)
        # The verbosity levels should map to the levels in logging.
        assert isinstance(level_name, str), repr(level_name)

        return level_name
