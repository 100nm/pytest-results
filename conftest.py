import pytest

from pytest_results import Regression, _RegressionImpl, _RegressionStack
from pytest_results._utils import get_testinfo
from tests.testing_impl.command_runner import CommandRunnerHistory
from tests.testing_impl.storage import MemoryStorage


@pytest.fixture(scope="function")
def command_history() -> CommandRunnerHistory:
    return CommandRunnerHistory()


@pytest.fixture(scope="function")
def memory_storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture(scope="function")
def test_regression(
    command_history: CommandRunnerHistory,
    memory_storage: MemoryStorage,
    request: pytest.FixtureRequest,
) -> Regression:
    return _RegressionImpl(
        get_testinfo(request),
        memory_storage,
        command_history.run,
    )


@pytest.fixture(scope="function")
def test_regression_stack(test_regression: Regression) -> _RegressionStack:
    return _RegressionStack(test_regression)
