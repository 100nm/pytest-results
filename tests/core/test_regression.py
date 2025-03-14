from typing import Any

import pytest

from pytest_results import BoundRegression, Regression, _RegressionStack
from pytest_results.exceptions import ResultsMismatchError
from tests.testing_impl.storage import MemoryStorage


def _save_result(regression: Regression, result: Any) -> None:
    try:
        regression.check(result)
    except ResultsMismatchError as mismatch:
        mismatch.accept_diff()


def _fake_yaml_dump(value: Any) -> bytes:
    return repr(value).encode()


class TestRegression:
    def test_check_with_failure(
        self,
        test_regression: Regression,
        memory_storage: MemoryStorage,
    ) -> dict[str, str]:
        with pytest.raises(ResultsMismatchError):
            test_regression.check({"hello": "world"})

        return memory_storage.json_memory


class TestBoundRegression:
    def test_check_with_success(
        self,
        test_regression: Regression,
        memory_storage: MemoryStorage,
    ) -> dict[str, str]:
        regression = BoundRegression(
            test_regression,
            dump_func=_fake_yaml_dump,
            file_format="yml",
        )

        result = {"hello": "world"}
        _save_result(regression, result)

        regression.check(result)
        return memory_storage.json_memory

    def test_check_with_failure(
        self,
        test_regression: Regression,
        memory_storage: MemoryStorage,
    ) -> dict[str, str]:
        regression = BoundRegression(
            test_regression,
            dump_func=_fake_yaml_dump,
            file_format="yml",
        )

        with pytest.raises(ResultsMismatchError):
            regression.check({"hello": "world"})

        return memory_storage.json_memory


class TestRegressionStack:
    def test_check_with_failure(
        self,
        test_regression_stack: _RegressionStack,
        memory_storage: MemoryStorage,
    ) -> dict[str, str]:
        with pytest.raises(ExceptionGroup):
            with test_regression_stack:
                test_regression_stack.check({"hello": 1})
                test_regression_stack.check({"hello": 2})
                test_regression_stack.check({"hello": 3})

        return memory_storage.json_memory
