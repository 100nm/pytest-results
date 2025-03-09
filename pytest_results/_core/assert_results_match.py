from abc import abstractmethod
from dataclasses import dataclass, field
from functools import singledispatch
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import pytest

from pytest_results._core.dumpers.abc import Dumper
from pytest_results._core.dumpers.json import SimpleJSONDumper
from pytest_results._core.storages.abc import Storage
from pytest_results.exceptions import ResultsMismatchError

type AssertResultsMatchType = _AssertResultsMatch[Any]


@runtime_checkable
class _AssertResultsMatch[T](Protocol):
    __slots__ = ()

    @abstractmethod
    def __call__(self, current_result: T, file_suffix: str = ...) -> None:
        raise NotImplementedError


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class AssertResultsMatch[T](_AssertResultsMatch[T]):
    request: pytest.FixtureRequest
    storage: Storage
    dumper: Dumper[T] | None = field(default=None)

    def __call__(self, current_result: T, file_suffix: str = "") -> None:
        dumper = self.dumper or select_dumper_from(current_result)
        storage = self.storage

        current_bytes = dumper.dump(current_result)
        relative_filepath = self.__get_relative_result_filepath(
            dumper.file_format,
            file_suffix,
        )
        filepath = storage.get_absolute_path(relative_filepath)
        previous_bytes = storage.read(filepath)

        try:
            assert current_bytes == previous_bytes

        except AssertionError as exc:
            temporary_filepath = storage.get_temporary_path(relative_filepath)
            storage.write(temporary_filepath, current_bytes)
            raise ResultsMismatchError(temporary_filepath, filepath, storage) from exc

    def __get_relative_result_filepath(self, file_format: str, suffix: str) -> Path:
        request = self.request
        segments = request.module.__name__.split(".")

        if cls := request.cls:
            segments.append(cls.__name__)

        segments.append(f"{request.function.__name__}{suffix}.{file_format}")
        return Path(*segments)


@singledispatch
def select_dumper_from(value: Any) -> Dumper[Any]:
    return SimpleJSONDumper()


try:
    from pydantic import BaseModel
except ImportError:
    ...
else:
    from pytest_results._core.dumpers.pydantic import PydanticJSONDumper

    @select_dumper_from.register
    def _(value: BaseModel) -> Dumper[BaseModel]:
        return PydanticJSONDumper()
