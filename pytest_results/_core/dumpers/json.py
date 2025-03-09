from typing import Any

import orjson

from pytest_results._core.dumpers.abc import JSONDumper


class SimpleJSONDumper(JSONDumper[Any]):
    __slots__ = ()

    def dump(self, value: Any) -> bytes:
        return orjson.dumps(value, default=str, option=orjson.OPT_INDENT_2)
