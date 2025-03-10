from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class Dumper[T](Protocol):
    __slots__ = ()

    file_format: str

    @abstractmethod
    def dump(self, value: T) -> bytes:
        raise NotImplementedError


class JSONDumper[T](Dumper[T], ABC):
    __slots__ = ()

    file_format: str = "json"
