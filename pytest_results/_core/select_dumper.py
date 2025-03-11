from functools import singledispatch
from typing import Any

from pytest_results._core.dumpers.abc import Dumper
from pytest_results._core.dumpers.json import SimpleJSONDumper


@singledispatch
def select_json_dumper(value: Any) -> Dumper[Any]:
    return SimpleJSONDumper()


try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    ...
else:
    from pytest_results._core.dumpers.pydantic import PydanticJSONDumper

    @select_json_dumper.register
    def _(value: BaseModel) -> Dumper[BaseModel]:
        return PydanticJSONDumper()
