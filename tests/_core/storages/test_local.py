from pathlib import Path

from pytest_results import _LocalStorage


class TestLocalStorage:
    def test_copy_with_existing_file(self, tmp_path: Path) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")
        filepath = tmp_path / "current.json"
        filepath.write_bytes(b"Hello")
        destination = tmp_path / "previous.json"

        storage.copy(filepath, destination)

        assert destination.read_bytes() == b"Hello"

    def test_exists_with_existing_file_returns_true(self, tmp_path: Path) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")
        filepath = tmp_path / "result.json"
        filepath.touch()

        assert storage.exists(filepath) is True

    def test_exists_without_file_returns_false(self, tmp_path: Path) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")

        assert storage.exists(tmp_path / "result.json") is False

    def test_get_absolute_path_with_relative_path_returns_path_in_dir(
        self,
        tmp_path: Path,
    ) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")

        path = storage.get_absolute_path(Path("tests/result.json"))

        assert path == tmp_path / "results" / "tests" / "result.json"

    def test_get_temporary_path_with_relative_path_returns_path_in_temporary_dir(
        self,
        tmp_path: Path,
    ) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")

        path = storage.get_temporary_path(Path("tests/result.json"))

        assert path == tmp_path / "temporary" / "tests" / "result.json"

    def test_read_with_existing_file_returns_content(self, tmp_path: Path) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")
        filepath = tmp_path / "result.json"
        filepath.write_bytes(b"Hello")

        assert storage.read(filepath) == b"Hello"

    def test_read_without_file_returns_empty_bytes(self, tmp_path: Path) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")

        assert storage.read(tmp_path / "result.json") == b""

    def test_write_with_missing_parent_dir(self, tmp_path: Path) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")
        filepath = tmp_path / "missing" / "result.json"

        storage.write(filepath, b"Hello")

        assert filepath.read_bytes() == b"Hello"

    def test_write_without_result(self, tmp_path: Path) -> None:
        storage = _LocalStorage(tmp_path / "results", tmp_path / "temporary")
        filepath = tmp_path / "result.json"

        storage.write(filepath)

        assert filepath.read_bytes() == b""
