import pytest
from pydantic import BaseModel

from pytest_results import AssertResultsMatchType


class TestAssertResultsMatch:
    def test_assert_results_match_with_success(self) -> dict[str, str]:
        return {"title": "Hello, World!"}

    async def test_assert_results_match_with_async(self) -> dict[str, str]:
        return {"title": "Hello, World!"}

    async def test_assert_results_match_with_multiple_assert(
        self,
        assert_results_match: AssertResultsMatchType,
    ) -> None:
        for i in range(3):
            result = {"title": i}
            assert_results_match(result, f"_{i}")

    def test_assert_results_match_with_failure_raise_assertion_error(
        self,
        assert_results_match: AssertResultsMatchType,
    ) -> None:
        result = {"title": "Hello, World!"}

        with pytest.raises(AssertionError):
            assert_results_match(result)

    def test_assert_results_match_with_pydantic_base_model(self) -> BaseModel:
        class Model(BaseModel):
            title: str

        return Model(title="Hello, World!")
