"""
This module sets environment variables based on the data in `pyproject.toml`.

Examples
--------
>>> import os
>>> from .pyproject import pyproject_init
>>> pyproject_init()
>>>
>>> assert os.getenv("PYPROJECT_NAME") is not None
>>> assert os.getenv("PYPROJECT_VERSION") is not None

A more involved example:

>>> import io
>>> import os
>>> import tomllib
>>> from typing import Any
>>>
>>> from .pyproject import pyproject_update_env
>>>
>>> file = io.BytesIO(
...     b\"\"\"
...     [project]
...     name = "foo"
...     version = "0.1.0"
...     requires-python = ">= 3.13"
...     \"\"\"
... )
>>>
>>> data = tomllib.load(file)
>>> mock_env: dict[str, Any] = {}
>>> pyproject_update_env(data, mock_env)
>>>
>>> assert mock_env.get("PYPROJECT_NAME") == "foo"
>>> assert mock_env.get("PYPROJECT_VERSION") == "0.1.0"
"""

import os
import pathlib
import tomllib
from typing import Any, Mapping, MutableMapping


def pyproject_init(
    start: pathlib.Path = pathlib.Path.cwd(),
    env: MutableMapping[str, Any] = os.environ,
) -> None:
    """Find and decode the `pyproject.toml` file, then update `env`.

    This is a convenience function for using `find` to get the `pyproject.toml`
    file, deserializing its contents, and then running `update_env`.

    Parameters
    ----------
    start
        The directory to start searching from.
    env
        The environment to mutate.

    Raises
    ------
    FileNotFoundError
        Failed to find the project's `pyproject.toml`.
    tomllib.TOMLDecodeError
        The contents of the `pyproject.toml` file were invalid.
    KeyError
        An expected key was not present in the `pyproject.toml` file.
    """
    path = find_pyproject(start)

    with open(path, mode="rb") as f:
        data = tomllib.load(f)

    pyproject_update_env(data, env)


def find_pyproject(start: pathlib.Path = pathlib.Path.cwd()) -> pathlib.Path:
    """Search upwards for the `pyproject.toml` file.

    Parameters
    ----------
    start
        The directory to start searching from.

    Returns
    -------
    pathlib.Path
        The path to the project's `pyproject.toml` file.

    Raises
    ------
    FileNotFoundError
        Failed to find the project's `pyproject.toml`.
    """
    for parent in (start, *start.parents):
        candidate = parent.joinpath("pyproject.toml")

        if candidate.exists(follow_symlinks=False):
            break
        else:
            pass
    else:
        raise FileNotFoundError("expected pyproject.toml to exist at root")

    return candidate


def pyproject_update_env(
    data: Mapping[str, Any],
    env: MutableMapping[str, Any] = os.environ,
) -> None:
    """Update environment variables based on the contents of `data`.

    Parameters
    ----------
    data
        The deserialized contents of the project's `pyproject.toml` file.
    env
        The environment to mutate.

    Raises
    ------
    KeyError
        An expected key was not present in the `pyproject.toml` file.
    """
    project = data["project"]
    env["PYPROJECT_NAME"] = project["name"]
    env["PYPROJECT_VERSION"] = project["version"]
