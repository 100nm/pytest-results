from functools import singledispatch
from typing import Any

import orjson


@singledispatch
def json_dump(value: Any) -> bytes:
    return orjson.dumps(value, default=str, option=orjson.OPT_INDENT_2)


try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    ...
else:

    @json_dump.register
    def _(value: BaseModel) -> bytes:
        return value.model_dump_json(indent=2).encode()
