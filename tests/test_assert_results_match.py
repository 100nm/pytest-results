import pytest
from pydantic import BaseModel

from pytest_results import AssertResultsMatchType


class TestAssertResultsMatch:
    def test_assert_results_match_with_success(
        self,
        assert_results_match: AssertResultsMatchType,
    ) -> None:
        result = {"title": "Hello, World!"}
        assert_results_match(result)

    def test_assert_results_match_with_failure_raise_(
        self,
        assert_results_match: AssertResultsMatchType,
    ) -> None:
        result = {"title": "Hello, World!"}

        with pytest.raises(AssertionError):
            assert_results_match(result)

    def test_assert_results_match_with_pydantic_base_model(
        self,
        assert_results_match: AssertResultsMatchType,
    ) -> None:
        class Model(BaseModel):
            title: str

        result = Model(title="Hello, World!")
        assert_results_match(result)
