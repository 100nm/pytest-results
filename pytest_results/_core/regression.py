from abc import abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Final, Protocol, Self, runtime_checkable

from pytest_results._core.dump_functions.json import json_dump
from pytest_results._core.storages.abc import Storage
from pytest_results.exceptions import ResultsMismatchError

type DumpFunction[T] = Callable[[T], bytes]
type CommandRunner = Callable[[str], Any]

_DEFAULT_DUMP_FUNCTION: Final[DumpFunction[Any]] = json_dump
_DEFAULT_FILE_FORMAT: Final[str] = "json"


@runtime_checkable
class Regression(Protocol):
    __slots__ = ()

    @abstractmethod
    def check[T](
        self,
        current_result: T,
        /,
        suffix: str | None = ...,
        dump_func: DumpFunction[T] | None = ...,
        file_format: str | None = ...,
    ) -> None:
        raise NotImplementedError


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class BoundedRegression(Regression):
    regression: Regression
    dump_func: DumpFunction[Any]
    file_format: str

    def check[T](
        self,
        current_result: T,
        /,
        suffix: str | None = None,
        dump_func: DumpFunction[T] | None = None,
        file_format: str | None = None,
    ) -> None:
        __tracebackhide__ = True
        return self.regression.check(
            current_result,
            suffix,
            dump_func or self.dump_func,
            file_format or self.file_format,
        )


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class RegressionImpl(Regression):
    testinfo: Sequence[str]
    storage: Storage
    command_runner: CommandRunner

    def check[T](
        self,
        current_result: T,
        /,
        suffix: str | None = None,
        dump_func: DumpFunction[T] | None = None,
        file_format: str | None = None,
    ) -> None:
        __tracebackhide__ = True

        dump_func = dump_func or _DEFAULT_DUMP_FUNCTION
        file_format = file_format or _DEFAULT_FILE_FORMAT
        suffix = suffix or ""

        current_bytes = dump_func(current_result)
        relative_filepath = self.__get_relative_result_filepath(file_format, suffix)
        filepath = self.storage.get_absolute_path(relative_filepath)
        previous_bytes = self.storage.read(filepath)

        try:
            assert current_bytes == previous_bytes

        except AssertionError as exc:
            temporary_filepath = self.storage.get_temporary_path(relative_filepath)
            self.storage.write(temporary_filepath, current_bytes)
            raise ResultsMismatchError(
                current=temporary_filepath,
                previous=filepath,
                storage=self.storage,
                command_runner=self.command_runner,
            ) from exc

    def __get_relative_result_filepath(self, file_format: str, suffix: str) -> Path:
        testinfo = self.testinfo
        filename = f"{testinfo[-1]}{suffix}.{file_format}"
        return Path(*testinfo[:-1], filename)


class RegressionStack(Regression):
    __slots__ = ("__count", "__delegate", "__mismatches")

    __count: int
    __delegate: Regression
    __mismatches: list[ResultsMismatchError]

    def __init__(self, delegate: Regression) -> None:
        self.__count = 0
        self.__delegate = delegate
        self.__mismatches = []

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

    def check[T](
        self,
        current_result: T,
        /,
        suffix: str | None = None,
        dump_func: DumpFunction[T] | None = None,
        file_format: str | None = None,
    ) -> None:
        __tracebackhide__ = True

        if not suffix and (count := self.__count) > 0:
            suffix = f"_{count}"

        self.__count += 1

        try:
            return self.__delegate.check(current_result, suffix, dump_func, file_format)
        except ResultsMismatchError as mismatch:
            self.__mismatches.append(mismatch)
