from collections.abc import Iterator


def iter_nested_exceptions[T: Exception](
    exception_group: ExceptionGroup[T],
) -> Iterator[T]:
    for exception in exception_group.exceptions:
        if isinstance(exception, ExceptionGroup):
            yield from iter_nested_exceptions(exception)
            continue

        yield exception
