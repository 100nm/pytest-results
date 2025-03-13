from contextlib import suppress
from functools import singledispatch
from typing import Any

import orjson


@singledispatch
def json_dump(value: Any) -> bytes:
    return orjson.dumps(value, default=str, option=orjson.OPT_INDENT_2)


@json_dump.register
def _(value: bytes) -> bytes:
    return value


with suppress(ImportError):
    import msgspec

    @json_dump.register
    def _(value: msgspec.Struct) -> bytes:
        b = msgspec.json.encode(value)
        return msgspec.json.format(b, indent=2)


with suppress(ImportError):
    import pydantic

    @json_dump.register
    def _(value: pydantic.BaseModel) -> bytes:
        return value.model_dump_json(indent=2).encode()
