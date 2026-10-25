from pathlib import Path
from typing import Any

import msgspec
import pydantic
import pytest

from pytest_results import Regression
from pytest_results._core.dump_functions.json import json_dump


class _Struct(msgspec.Struct):
    title: str


class _Model(pydantic.BaseModel):
    title: str


def test_json_dump_with_bytes_returns_same_bytes() -> None:
    value = b"Hello, World!"

    dumped = json_dump(value)

    assert dumped is value


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("dict", {"title": "Hello, World!"}),
        ("msgspec", _Struct(title="Hello, World!")),
        ("pydantic", _Model(title="Hello, World!")),
        ("unserializable", {"path": Path("hello/world")}),
    ],
)
def test_json_dump_with_value_returns_indented_json(
    label: str,
    regression: Regression,
    value: Any,
) -> None:
    dumped = json_dump(value)

    regression.check(dumped, suffix=f"({label})")
