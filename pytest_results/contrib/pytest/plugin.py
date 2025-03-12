import os
import warnings
from collections.abc import Awaitable, Callable, Generator, Iterable, Mapping, Sequence
from functools import update_wrapper
from inspect import iscoroutinefunction
from pathlib import Path
from typing import Any, ClassVar

import pytest

from pytest_results import _LocalStorage, _RegressionImpl, _RegressionStack
from pytest_results._utils import get_testinfo, iter_nested_exceptions
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
    def accept_diff(self) -> bool:
        return self.__config.getoption("accept_diff")

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
        "--accept-diff",
        dest="accept_diff",
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
            mismatches = tuple(iter_nested_exceptions(sub_exc_group))
            __on_mismatches(mismatches, pyfuncitem.config)

        raise exc_group

    return result


@pytest.fixture(scope="function")
def regression(request: pytest.FixtureRequest, tmp_path: Path) -> _RegressionStack:
    dirname = "__pytest_results__"
    storage = _LocalStorage(request.config.rootpath / dirname, tmp_path / dirname)
    testinfo = get_testinfo(request)
    delegate = _RegressionImpl(testinfo, storage, os.system)
    return _RegressionStack(delegate)


def __autodetect_result(pyfuncitem: pytest.Function) -> pytest.Function:
    wrapper: Callable[..., None | Awaitable[None]]
    wrapped = pyfuncitem.obj

    if iscoroutinefunction(wrapped):

        async def wrapper(*args: Any, **kwargs: Any) -> None:
            with __get_regression_fixture(pyfuncitem) as regression:
                if (result := await wrapped(*args, **kwargs)) is not None:
                    regression.check(result)

    else:

        def wrapper(*args: Any, **kwargs: Any) -> None:
            with __get_regression_fixture(pyfuncitem) as regression:
                if (result := wrapped(*args, **kwargs)) is not None:
                    regression.check(result)

    pyfuncitem.obj = update_wrapper(wrapper, wrapped)
    return pyfuncitem


def __get_regression_fixture(pyfuncitem: pytest.Function) -> _RegressionStack:
    return pyfuncitem._request.getfixturevalue(regression.__name__)


def __on_mismatches(
    mismatches: Sequence[ResultsMismatchError],
    pytest_config: pytest.Config,
) -> None:
    if not mismatches:
        return

    config = PytestResultsConfig(pytest_config)

    if config.accept_diff:
        for mismatch in mismatches:
            mismatch.accept_diff()

        pytest.skip()

    elif command := config.diff_command:
        for mismatch in mismatches:
            mismatch.show_diff(command)
