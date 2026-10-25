from pathlib import Path
from typing import Any

import pytest

from pytest_results import BoundRegression, _RegressionImpl, _RegressionStack
from pytest_results.exceptions import ResultsMismatchError
from tests.impl.command_runner import CommandRunnerHistory
from tests.impl.storage import MemoryStorage

_TESTINFO = ("tests", "test_module", "TestClass", "test_function")


def _repr_dump(value: Any) -> bytes:
    return repr(value).encode()


class TestBoundRegression:
    def test_check_without_arguments_raises_results_mismatch_error(
        self,
    ) -> dict[str, str]:
        storage = MemoryStorage()
        regression = BoundRegression(
            _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run),
            dump_func=_repr_dump,
            file_format="txt",
        )

        with pytest.raises(ResultsMismatchError):
            regression.check({"title": "Hello"})

        return storage.json_memory

    def test_check_with_arguments_raises_results_mismatch_error(
        self,
    ) -> dict[str, str]:
        storage = MemoryStorage()
        regression = BoundRegression(
            _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run),
            dump_func=_repr_dump,
            file_format="txt",
        )

        with pytest.raises(ResultsMismatchError):
            regression.check(
                {"title": "Hello"},
                suffix="_custom",
                dump_func=lambda value: str(value).upper().encode(),
                file_format="log",
            )

        return storage.json_memory


class TestRegressionImpl:
    def test_check_with_same_stored_result(self) -> None:
        storage = MemoryStorage()
        storage.memory[Path("/root/tests/test_module/TestClass/test_function.json")] = (
            b'{\n  "title": "Hello"\n}'
        )
        regression = _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run)

        regression.check({"title": "Hello"})

        assert len(storage.memory) == 1

    def test_check_without_stored_result_raises_results_mismatch_error(
        self,
    ) -> dict[str, str]:
        storage = MemoryStorage()
        regression = _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run)

        with pytest.raises(ResultsMismatchError) as exc_info:
            regression.check({"title": "Hello"})

        assert exc_info.value.previous == Path(
            "/root/tests/test_module/TestClass/test_function.json"
        )
        return storage.json_memory

    def test_check_with_different_stored_result_raises_results_mismatch_error(
        self,
    ) -> dict[str, str]:
        storage = MemoryStorage()
        storage.memory[Path("/root/tests/test_module/TestClass/test_function.json")] = (
            b'{\n  "title": "Hello"\n}'
        )
        regression = _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run)

        with pytest.raises(ResultsMismatchError):
            regression.check({"title": "Goodbye"})

        return storage.json_memory

    def test_check_with_arguments_raises_results_mismatch_error(
        self,
    ) -> dict[str, str]:
        storage = MemoryStorage()
        regression = _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run)

        with pytest.raises(ResultsMismatchError):
            regression.check(
                {"title": "Hello"},
                suffix="_custom",
                dump_func=_repr_dump,
                file_format="txt",
            )

        return storage.json_memory


class TestRegressionStack:
    def test_check_with_several_results_without_suffix(self) -> list[str]:
        storage = MemoryStorage()
        stack = _RegressionStack(
            _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run),
        )

        for index in range(3):
            stack.check({"index": index})

        return sorted(storage.json_memory)

    def test_check_with_suffix(self) -> list[str]:
        storage = MemoryStorage()
        stack = _RegressionStack(
            _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run),
        )

        stack.check({"index": 0})
        stack.check({"index": 1}, suffix="_custom")

        return sorted(storage.json_memory)

    def test_close_without_mismatch(self) -> None:
        storage = MemoryStorage()
        storage.memory[Path("/root/tests/test_module/TestClass/test_function.json")] = (
            b'{\n  "title": "Hello"\n}'
        )
        stack = _RegressionStack(
            _RegressionImpl(_TESTINFO, storage, CommandRunnerHistory().run),
        )
        stack.check({"title": "Hello"})

        stack.close()

    def test_close_with_one_mismatch_raises_results_mismatch_error(self) -> None:
        stack = _RegressionStack(
            _RegressionImpl(_TESTINFO, MemoryStorage(), CommandRunnerHistory().run),
        )
        stack.check({"title": "Hello"})

        with pytest.raises(ResultsMismatchError):
            stack.close()

    def test_close_with_several_mismatches_raises_exception_group(self) -> None:
        stack = _RegressionStack(
            _RegressionImpl(_TESTINFO, MemoryStorage(), CommandRunnerHistory().run),
        )
        stack.check({"index": 0})
        stack.check({"index": 1})

        with pytest.raises(ExceptionGroup) as exc_info:
            stack.close()

        assert len(exc_info.value.exceptions) == 2

    def test_close_with_already_raised_mismatch(self) -> None:
        stack = _RegressionStack(
            _RegressionImpl(_TESTINFO, MemoryStorage(), CommandRunnerHistory().run),
        )
        stack.check({"title": "Hello"})

        with pytest.raises(ResultsMismatchError):
            stack.close()

        stack.close()
