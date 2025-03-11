from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Any, Protocol, Self, runtime_checkable

import pytest

from pytest_results._core.dumpers.abc import Dumper
from pytest_results._core.select_dumper import select_json_dumper
from pytest_results._core.storages.abc import Storage
from pytest_results.exceptions import ResultsMismatchError

type AssertResultsMatchType = _AssertResultsMatch[Any]


@runtime_checkable
class _AssertResultsMatch[T](Protocol):
    __slots__ = ()

    @abstractmethod
    def __call__(self, current_result: T, /, suffix: str = ...) -> None:
        raise NotImplementedError


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class AssertResultsMatch[T](_AssertResultsMatch[T]):
    request: pytest.FixtureRequest
    storage: Storage
    dumper: Dumper[T] | None = field(default=None)

    def __call__(self, current_result: T, /, suffix: str = "") -> None:
        __tracebackhide__ = True

        dumper = self.dumper or select_json_dumper(current_result)
        storage = self.storage

        current_bytes = dumper.dump(current_result)
        relative_filepath = self.__get_relative_result_filepath(
            dumper.file_format,
            suffix,
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


class AssertResultsMatchGroup[T](_AssertResultsMatch[T]):
    __slots__ = ("__call", "__count", "__exceptions")

    __call: _AssertResultsMatch[T]
    __count: int
    __exceptions: list[ResultsMismatchError]

    def __init__(self, call: _AssertResultsMatch[T]) -> None:
        self.__call = call
        self.__count = 0
        self.__exceptions = []

    def __call__(self, current_result: T, /, suffix: str = "") -> None:
        __tracebackhide__ = True

        if not suffix and (count := self.__count) > 0:
            suffix = f"_{count}"

        self.__count += 1

        try:
            return self.__call(current_result, suffix)
        except ResultsMismatchError as exc:
            self.__exceptions.append(exc)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        __tracebackhide__ = True

        if exceptions := self.__exceptions:
            raise (
                exceptions[0]
                if len(exceptions) == 1
                else ExceptionGroup("", exceptions)
            )
