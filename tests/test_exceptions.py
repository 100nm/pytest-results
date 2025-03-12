from typing import Any

from pytest_results import Regression
from pytest_results.exceptions import ResultsMismatchError
from tests.testing_impl.command_runner import CommandRunnerHistory
from tests.testing_impl.storage import MemoryStorage


class TestResultsMismatchError:
    def test_str_with_success_return_str(
        self,
        test_regression: Regression,
    ) -> dict[str, str]:
        try:
            test_regression.check({})
        except ResultsMismatchError as mismatch:
            return {"__str__": str(mismatch)}

        raise NotImplementedError

    def test_accept_diff_with_success(
        self,
        test_regression: Regression,
        memory_storage: MemoryStorage,
    ) -> dict[str, str]:
        try:
            test_regression.check({})
        except ResultsMismatchError as mismatch:
            mismatch.accept_diff()

        return memory_storage.json_memory

    def test_show_diff_with_success(
        self,
        test_regression: Regression,
        command_history: CommandRunnerHistory,
    ) -> dict[str, Any]:
        try:
            test_regression.check({})
        except ResultsMismatchError as mismatch:
            mismatch.show_diff("code -d -r -w {current} {previous}")

        return {"commands": command_history.history}
