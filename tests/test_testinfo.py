import pytest

from pytest_results._testinfo import get_testinfo


def test_get_testinfo_without_class_returns_tuple(
    request: pytest.FixtureRequest,
) -> tuple[str, ...]:
    return get_testinfo(request)


class TestWithinClass:
    def test_get_testinfo_with_class_returns_tuple(
        self,
        request: pytest.FixtureRequest,
    ) -> tuple[str, ...]:
        return get_testinfo(request)
