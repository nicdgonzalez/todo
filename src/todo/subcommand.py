from __future__ import annotations

import abc
import argparse
import string
from typing import TYPE_CHECKING

from .context import Context

if TYPE_CHECKING:
    SubParsersAction = argparse._SubParsersAction[argparse.ArgumentParser]

subcommand_registry: dict[str, type[Subcommand]] = {}


def _camel_case_to_kebab_case(name: str) -> str:
    if len(name) < 1:
        return name

    # The first character in CamelCase is always uppercase. We do it outside
    # of the loop to avoid having to clean up the string afterwards.
    kebab_case = name[0].lower()

    for c in name[1:]:
        if c in string.ascii_uppercase:
            kebab_case += "-" + c.lower()
        else:
            kebab_case += c

    return kebab_case


class Subcommand(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_args(cls, args: argparse.Namespace) -> Subcommand:
        """Construct this type from an [`argparse.Namespace`].

        Parameters
        ----------
        args
            Deserialized command-line arguments. (The specific arguments are
            defined by overriding [`Subcommand.add_arguments`].)

        Returns
        -------
        Subcommand
            An instance of the current type.
        """
        pass

    @classmethod
    def register(cls, parent: SubParsersAction) -> argparse.ArgumentParser:
        """Create a new parser for this subcommand.

        By default, the subcommand's name is the class name converted from
        CamelCase to kebab-case.

        Parameters
        ----------
        parent
            The `subcommands` subparser.

        Returns
        -------
        argparse.ArgumentParser
            The newly created parser.
        """
        name = _camel_case_to_kebab_case(cls.__name__)
        parser = parent.add_parser(
            name=name,
            deprecated=False,
            help=(cls.__doc__ or "").split("\n\n", maxsplit=1)[0],
        )
        subcommand_registry[name] = cls
        cls.add_arguments(parser)
        return parser

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, /) -> None:
        """Define options and arguments for the parser.

        By default, this method has an empty implementation. Override this
        method to define the options and arguments needed to implement
        [`Subcommand.from_args`]. This method is automatically called at
        the end of [`Subcommand.register`].

        Parameters
        ----------
        parser
            Parser that represents this subcommand in the CLI.
        """
        pass

    @abc.abstractmethod
    def run(self, ctx: Context, /) -> None:
        """Execute the subcommand.

        This method contains the logic for the subcommand.

        Parameters
        ----------
        ctx
            Context type containing relevant data and state information.
        """
        pass
