from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from pytest_results import _CommandRunner, _Storage

__all__ = ("PytestResultsError", "ResultsMismatchError")


class PytestResultsError(Exception): ...


class ResultsMismatchError(AssertionError, PytestResultsError):
    __slots__ = (
        "__command_runner",
        "__current_filepath",
        "__previous_filepath",
        "__storage",
    )

    __command_runner: _CommandRunner
    __current_filepath: Path
    __previous_filepath: Path
    __storage: _Storage

    def __init__(
        self,
        current: Path,
        previous: Path,
        storage: _Storage,
        command_runner: _CommandRunner,
    ) -> None:
        self.__command_runner = command_runner
        self.__current_filepath = current
        self.__previous_filepath = previous
        self.__storage = storage

    def __str__(self) -> str:
        return self.__to_string(self.current, self.previous)

    @property
    def current(self) -> Path:
        return self.__current_filepath

    @property
    def previous(self) -> Path:
        return self.__previous_filepath

    def accept_diff(self) -> None:
        self.__ensure_file_exists(self.previous)
        self.__storage.copy(self.current, self.previous)

    def show_diff(self, command: str) -> None:
        self.__ensure_file_exists(self.previous)
        command = command.format(current=self.current, previous=self.previous)
        self.__command_runner(command)

    def __ensure_file_exists(self, filepath: Path) -> None:
        if self.__storage.exists(filepath):
            return

        self.__storage.write(filepath)

    @staticmethod
    def __to_string(current: object, previous: object) -> str:
        return f"Results mismatch\n・Current: `{current}`\n・Previous: `{previous}`"
