from abc import abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Protocol, Self, runtime_checkable

from pytest_results._core.storages.abc import Storage
from pytest_results.exceptions import ResultsMismatchError

type DumpFunction[T] = Callable[[T], bytes]
type RegressionType = _Regression[Any]


@runtime_checkable
class _Regression[T](Protocol):
    __slots__ = ()

    @abstractmethod
    def check(self, current_result: T, /, suffix: str = ...) -> None:
        raise NotImplementedError


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class Regression[T](_Regression[T]):
    dump: DumpFunction[T]
    file_format: str
    storage: Storage
    testinfo: Sequence[str]

    def check(self, current_result: T, /, suffix: str = "") -> None:
        __tracebackhide__ = True

        storage = self.storage
        current_bytes = self.dump(current_result)
        relative_filepath = self.__get_relative_result_filepath(suffix)
        filepath = storage.get_absolute_path(relative_filepath)
        previous_bytes = storage.read(filepath)

        try:
            assert current_bytes == previous_bytes

        except AssertionError as exc:
            temporary_filepath = storage.get_temporary_path(relative_filepath)
            storage.write(temporary_filepath, current_bytes)
            raise ResultsMismatchError(temporary_filepath, filepath, storage) from exc

    def __get_relative_result_filepath(self, suffix: str) -> Path:
        testinfo = self.testinfo
        filename = f"{testinfo[-1]}{suffix}.{self.file_format}"
        return Path(*testinfo[:-1], filename)


class RegressionGroup[T](_Regression[T]):
    __slots__ = ("__count", "__mismatches", "__regression")

    __count: int
    __mismatches: list[ResultsMismatchError]
    __regression: _Regression[T]

    def __init__(self, regression: _Regression[T]) -> None:
        self.__count = 0
        self.__mismatches = []
        self.__regression = regression

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        __tracebackhide__ = True

        if mismatches := self.__mismatches:
            raise (
                mismatches[0]
                if len(mismatches) == 1
                else ExceptionGroup("", mismatches)
            )

    def check(self, current_result: T, /, suffix: str = "") -> None:
        __tracebackhide__ = True

        if not suffix and (count := self.__count) > 0:
            suffix = f"_{count}"

        self.__count += 1

        try:
            return self.__regression.check(current_result, suffix)
        except ResultsMismatchError as mismatch:
            self.__mismatches.append(mismatch)
