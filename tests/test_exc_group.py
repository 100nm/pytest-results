from pytest_results._exc_group import iter_nested_exceptions


def test_iter_nested_exceptions_with_nested_groups_returns_leaf_exceptions() -> None:
    first, second, third = ValueError("first"), KeyError("second"), TypeError("third")
    exception_group = ExceptionGroup(
        "root",
        [first, ExceptionGroup("nested", [second, ExceptionGroup("deep", [third])])],
    )

    exceptions = tuple(iter_nested_exceptions(exception_group))

    assert exceptions == (first, second, third)
