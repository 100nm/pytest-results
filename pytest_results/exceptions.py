from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_results import Storage

__all__ = ("PytestResultsError", "ResultsMismatchError")


class PytestResultsError(Exception): ...


@dataclass(slots=True)
class ResultsMismatchError(AssertionError, PytestResultsError):
    current_filepath: Path
    previous_filepath: Path
    storage: Storage = field(repr=False)

    def __str__(self) -> str:
        return self.__to_string(self.current_filepath, self.previous_filepath)

    def accept_diff(self) -> None:
        self.__ensure_file_exists(self.previous_filepath)
        shutil.copyfile(self.current_filepath, self.previous_filepath)

    def show_diff(self, command: str) -> None:
        self.__ensure_file_exists(self.previous_filepath)
        command = command.format(
            current=self.current_filepath,
            previous=self.previous_filepath,
        )
        os.system(command)
        time.sleep(1)

    def __ensure_file_exists(self, filepath: Path) -> None:
        if self.storage.exists(filepath):
            return

        self.storage.write(filepath)

    @staticmethod
    def __to_string(current: object, previous: object) -> str:
        return f"Results mismatch\n・Current: `{current}`\n・Previous: `{previous}`"
