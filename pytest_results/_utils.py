from collections.abc import Iterator

import pytest

__all__ = ("get_testinfo", "iter_nested_exceptions")


def get_testinfo(request: pytest.FixtureRequest) -> tuple[str, ...]:
    return tuple(__iter_testinfo(request))


def iter_nested_exceptions[T: Exception](
    exception_group: ExceptionGroup[T],
) -> Iterator[T]:
    for exception in exception_group.exceptions:
        if isinstance(exception, ExceptionGroup):
            yield from iter_nested_exceptions(exception)
            continue

        yield exception


def __iter_testinfo(request: pytest.FixtureRequest) -> Iterator[str]:
    yield from request.module.__name__.split(".")

    if cls := request.cls:
        yield cls.__name__

    yield request.function.__name__
