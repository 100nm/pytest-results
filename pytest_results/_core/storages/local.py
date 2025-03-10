import os
import shutil
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

from pytest_results._core.storages.abc import Storage


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class LocalStorage(Storage):
    dir: Path
    temporary_dir: Path

    def copy(self, filepath: Path, destination: Path) -> None:
        shutil.copyfile(filepath, destination)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def get_absolute_path(self, relative_path: Path) -> Path:
        return self.__get_absolute_path(relative_path, self.dir)

    def get_temporary_path(self, relative_path: Path) -> Path:
        return self.__get_absolute_path(relative_path, self.temporary_dir)

    def read(self, filepath: Path) -> bytes:
        with suppress(FileNotFoundError):
            with open(filepath, "rb") as reader:
                return reader.read()

        return b""

    def write(self, filepath: Path, result: bytes = b"") -> None:
        os.makedirs(filepath.parent, exist_ok=True)

        with open(filepath, "wb") as writer:
            writer.write(result)

    @staticmethod
    def __get_absolute_path(filepath: Path, directory: Path) -> Path:
        assert not filepath.is_absolute()
        return directory / filepath
