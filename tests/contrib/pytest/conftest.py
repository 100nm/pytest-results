import pytest


@pytest.fixture(autouse=True)
def asyncio_loop_scope(
    monkeypatch: pytest.MonkeyPatch,
    pytester: pytest.Pytester,
) -> None:
    monkeypatch.setenv(
        "PYTEST_ADDOPTS",
        "-o asyncio_default_fixture_loop_scope=function",
    )
