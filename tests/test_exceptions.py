from pathlib import Path

from pytest_results.exceptions import ResultsMismatchError
from tests.impl.command_runner import CommandRunnerHistory
from tests.impl.storage import MemoryStorage

_CURRENT = Path("/tmp/result.json")
_PREVIOUS = Path("/root/result.json")


class TestResultsMismatchError:
    def test_str_with_success_returns_str(self) -> str:
        mismatch = ResultsMismatchError(
            current=_CURRENT,
            previous=_PREVIOUS,
            storage=MemoryStorage(),
            command_runner=CommandRunnerHistory().run,
        )

        return str(mismatch)

    def test_accept_diff_with_previous_file(self) -> dict[str, str]:
        storage = MemoryStorage()
        storage.memory[_CURRENT] = b"current"
        storage.memory[_PREVIOUS] = b"previous"
        mismatch = ResultsMismatchError(
            current=_CURRENT,
            previous=_PREVIOUS,
            storage=storage,
            command_runner=CommandRunnerHistory().run,
        )

        mismatch.accept_diff()

        return storage.json_memory

    def test_accept_diff_without_previous_file(self) -> dict[str, str]:
        storage = MemoryStorage()
        storage.memory[_CURRENT] = b"current"
        mismatch = ResultsMismatchError(
            current=_CURRENT,
            previous=_PREVIOUS,
            storage=storage,
            command_runner=CommandRunnerHistory().run,
        )

        mismatch.accept_diff()

        return storage.json_memory

    def test_show_diff_without_previous_file(self) -> dict[str, object]:
        storage = MemoryStorage()
        storage.memory[_CURRENT] = b"current"
        command_history = CommandRunnerHistory()
        mismatch = ResultsMismatchError(
            current=_CURRENT,
            previous=_PREVIOUS,
            storage=storage,
            command_runner=command_history.run,
        )

        mismatch.show_diff("diff {current} {previous}")

        return {"commands": command_history.history, "memory": storage.json_memory}
