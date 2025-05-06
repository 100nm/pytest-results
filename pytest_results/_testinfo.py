from collections.abc import Iterator

import pytest

__all__ = ("get_testinfo",)


def get_testinfo(request: pytest.FixtureRequest) -> tuple[str, ...]:
    return tuple(__iter_testinfo(request))


def __iter_testinfo(request: pytest.FixtureRequest) -> Iterator[str]:
    yield from request.module.__name__.split(".")

    if cls := request.cls:
        yield cls.__name__

    yield request.function.__name__
