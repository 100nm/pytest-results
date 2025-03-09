from pydantic import BaseModel

from pytest_results._core.dumpers.abc import JSONDumper


class PydanticJSONDumper(JSONDumper[BaseModel]):
    __slots__ = ()

    def dump(self, value: BaseModel) -> bytes:
        return value.model_dump_json(indent=2).encode()
