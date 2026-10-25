from pathlib import Path

from pytest_results import _Storage


class MemoryStorage(_Storage):
    memory: dict[Path, bytes]

    def __init__(self) -> None:
        self.memory = {}

    @property
    def json_memory(self) -> dict[str, str]:
        return {str(key): value.decode() for key, value in self.memory.items()}

    def copy(self, filepath: Path, destination: Path) -> None:
        self.memory[destination] = self.memory[filepath]

    def exists(self, path: Path) -> bool:
        return path in self.memory

    def get_absolute_path(self, relative_path: Path) -> Path:
        return Path("/root") / relative_path

    def get_temporary_path(self, relative_path: Path) -> Path:
        return Path("/tmp") / relative_path

    def read(self, filepath: Path) -> bytes:
        return self.memory.get(filepath, b"")

    def write(self, filepath: Path, result: bytes = b"") -> None:
        self.memory[filepath] = result
