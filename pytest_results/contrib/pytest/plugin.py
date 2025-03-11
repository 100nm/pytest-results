import warnings
from collections.abc import (
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from functools import update_wrapper
from inspect import iscoroutinefunction
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, ClassVar, ContextManager

import pytest

from pytest_results import (
    AssertResultsMatch,
    AssertResultsMatchGroup,
    AssertResultsMatchType,
    LocalStorage,
)
from pytest_results.exceptions import ResultsMismatchError

__all__ = ()


class PytestResultsConfig:
    __slots__ = ("__config",)

    __diff_commands: ClassVar[Mapping[str, str]] = {
        "cursor": "cursor -d -r -w {current} {previous}",
        "pycharm": "pycharm diff {current} {previous}",
        "vscode": "code -d -r -w {current} {previous}",
    }

    def __init__(self, pytest_config: pytest.Config) -> None:
        self.__config = pytest_config

    @property
    def accept_all_diff(self) -> bool:
        return self.__config.getoption("accept_all_diff")

    @property
    def diff_command(self) -> str | None:
        if diff := self.__get_option_or_ini("diff"):
            return diff

        if ide := self.__get_option_or_ini("ide"):
            lowercase_ide = ide.lower()

            try:
                return self.__diff_commands[lowercase_ide]
            except KeyError:
                warnings.warn(f"pytest-results doesn't yet support the `{ide}` IDE.")

        return None

    def __get_option_or_ini[T](self, key: str) -> T | None:
        config = self.__config
        return config.getoption(key, default=config.getini(key))


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("pytest-results")

    group.addoption(
        "--accept-all-diff",
        dest="accept_all_diff",
        action="store_true",
        help="Parameter for accepting new differences between results.",
        default=False,
    )

    diff_help = "Command line to open an interactive comparison. Example: `code -d -w {current} {previous}`."
    group.addoption(
        "--diff",
        dest="diff",
        metavar="COMMAND_LINE",
        help=diff_help,
        default=None,
    )
    parser.addini(
        "diff",
        type="string",
        help=diff_help,
        default=None,
    )

    ide_help = "The IDE to open for interactive comparison."
    group.addoption(
        "--ide",
        dest="ide",
        metavar="IDE",
        help=ide_help,
        default=None,
    )
    parser.addini(
        "ide",
        type="string",
        help=ide_help,
        default=None,
    )


@pytest.hookimpl
def pytest_collection_modifyitems(items: Iterable[pytest.Item]) -> None:
    for item in items:
        if isinstance(item, pytest.Function):
            __autodetect_result(item)


@pytest.hookimpl(trylast=True, wrapper=True)
def pytest_pyfunc_call(
    pyfuncitem: pytest.Function,
) -> Generator[None, object | None, object | None]:
    __tracebackhide__ = True

    try:
        result = yield

    except ResultsMismatchError as mismatch:
        __on_mismatches((mismatch,), pyfuncitem.config)
        raise mismatch

    except ExceptionGroup as exc_group:
        if sub_exc_group := exc_group.subgroup(ResultsMismatchError):
            mismatches = tuple(__iter_nested_exceptions(sub_exc_group))
            __on_mismatches(mismatches, pyfuncitem.config)

        raise exc_group

    return result


@pytest.fixture(scope="session")
def _pytest_results_tmpdir() -> Iterator[Path]:
    with TemporaryDirectory(prefix="pytest-temporary-results@") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="function")
def assert_results_match(
    request: pytest.FixtureRequest,
    _pytest_results_tmpdir: Path,
) -> AssertResultsMatchType:
    results_dir = request.config.rootpath / "__pytest_results__"
    storage = LocalStorage(results_dir, _pytest_results_tmpdir)
    assert_function: AssertResultsMatchType = AssertResultsMatch(request, storage)
    return AssertResultsMatchGroup(assert_function)


def __autodetect_result(pyfuncitem: pytest.Function) -> pytest.Function:
    wrapper: Callable[..., None | Awaitable[None]]
    wrapped = pyfuncitem.obj

    if iscoroutinefunction(wrapped):

        async def wrapper(*args: Any, **kwargs: Any) -> None:
            with get_assert_results_match_fixture(pyfuncitem) as assert_function:
                if (result := await wrapped(*args, **kwargs)) is not None:
                    assert_function(result)

    else:

        def wrapper(*args: Any, **kwargs: Any) -> None:
            with get_assert_results_match_fixture(pyfuncitem) as assert_function:
                if (result := wrapped(*args, **kwargs)) is not None:
                    assert_function(result)

    pyfuncitem.obj = update_wrapper(wrapper, wrapped)
    return pyfuncitem


def __iter_nested_exceptions[T: Exception](
    exception_group: ExceptionGroup[T],
) -> Iterator[T]:
    for exception in exception_group.exceptions:
        if isinstance(exception, ExceptionGroup):
            yield from __iter_nested_exceptions(exception)
            continue

        yield exception


def get_assert_results_match_fixture(
    pyfuncitem: pytest.Function,
) -> ContextManager[AssertResultsMatchType]:
    fixture_name = assert_results_match.__name__
    return pyfuncitem._request.getfixturevalue(fixture_name)


def __on_mismatches(
    mismatches: Sequence[ResultsMismatchError],
    pytest_config: pytest.Config,
) -> None:
    if not mismatches:
        return

    config = PytestResultsConfig(pytest_config)

    if config.accept_all_diff:
        for mismatch in mismatches:
            mismatch.accept_diff()

        pytest.skip()

    elif command := config.diff_command:
        for mismatch in mismatches:
            mismatch.show_diff(command)
