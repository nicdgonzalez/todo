import io
import tomllib
import unittest
from typing import Any

from todo.pyproject import pyproject_update_env


class TestPyProject(unittest.TestCase):
    def test_set_env(self) -> None:
        file = io.BytesIO(b"""
            [project]
            name = "foo"
            version = "0.1.0"
            requires-python = ">= 3.13"
        """)
        data = tomllib.load(file, parse_float=float)
        mock_env: dict[str, Any] = {}

        pyproject_update_env(data, mock_env)

        self.assertEqual(mock_env.get("PYPROJECT_NAME"), "foo")
        self.assertEqual(mock_env.get("PYPROJECT_VERSION"), "0.1.0")
