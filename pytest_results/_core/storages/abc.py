from abc import abstractmethod
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class Storage(Protocol):
    __slots__ = ()

    @abstractmethod
    def exists(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_absolute_path(self, relative_path: Path) -> Path:
        raise NotImplementedError

    @abstractmethod
    def get_temporary_path(self, relative_path: Path) -> Path:
        raise NotImplementedError

    @abstractmethod
    def read(self, filepath: Path) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def write(self, filepath: Path, result: bytes = ...) -> None:
        raise NotImplementedError
