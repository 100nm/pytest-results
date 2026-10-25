import pytest

from pytest_results.contrib.pytest.plugin import PytestResultsConfig

_RETURNING_TEST = """
def test_function():
    return {"title": "Hello, World!"}
"""


class TestPytestResultsConfig:
    def test_accept_diff_with_option_returns_true(
        self,
        pytester: pytest.Pytester,
    ) -> None:
        config = PytestResultsConfig(pytester.parseconfig("--accept-diff"))

        assert config.accept_diff is True

    def test_accept_diff_without_option_returns_false(
        self,
        pytester: pytest.Pytester,
    ) -> None:
        config = PytestResultsConfig(pytester.parseconfig())

        assert config.accept_diff is False

    @pytest.mark.parametrize(
        ("args", "expected"),
        [
            (("--diff", "meld {current} {previous}"), "meld {current} {previous}"),
            (("--ide", "cursor"), "cursor -d -r -w {current} {previous}"),
            (("--ide", "PyCharm"), "pycharm diff {current} {previous}"),
            (("--ide", "vscode"), "code -d -r -w {current} {previous}"),
            (
                ("--diff", "meld {current} {previous}", "--ide", "vscode"),
                "meld {current} {previous}",
            ),
        ],
    )
    def test_diff_command_with_option_returns_command(
        self,
        args: tuple[str, ...],
        expected: str,
        pytester: pytest.Pytester,
    ) -> None:
        config = PytestResultsConfig(pytester.parseconfig(*args))

        assert config.diff_command == expected

    @pytest.mark.parametrize(
        ("ini", "expected"),
        [
            ("diff = meld {current} {previous}", "meld {current} {previous}"),
            ("ide = vscode", "code -d -r -w {current} {previous}"),
        ],
    )
    def test_diff_command_with_ini_returns_command(
        self,
        expected: str,
        ini: str,
        pytester: pytest.Pytester,
    ) -> None:
        pytester.makeini(f"[pytest]\n{ini}\n")
        config = PytestResultsConfig(pytester.parseconfig())

        assert config.diff_command == expected

    def test_diff_command_with_unsupported_ide_returns_none(
        self,
        pytester: pytest.Pytester,
    ) -> None:
        config = PytestResultsConfig(pytester.parseconfig("--ide", "notepad"))

        with pytest.warns(UserWarning, match="`notepad` IDE"):
            assert config.diff_command is None

    def test_diff_command_without_option_returns_none(
        self,
        pytester: pytest.Pytester,
    ) -> None:
        config = PytestResultsConfig(pytester.parseconfig())

        assert config.diff_command is None


def test_pytest_collection_modifyitems_with_test_returning_none(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(test_module="def test_function():\n    pass\n")

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "source",
    [
        _RETURNING_TEST,
        """
import pytest

@pytest.mark.asyncio
async def test_function():
    return {"title": "Hello, World!"}
""",
    ],
    ids=["sync", "async"],
)
def test_pytest_collection_modifyitems_with_test_returning_stored_result(
    pytester: pytest.Pytester,
    source: str,
) -> None:
    pytester.makepyfile(test_module=source)
    pytester.runpytest("--accept-diff")

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)


def test_pytest_pyfunc_call_with_new_result(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(test_module=_RETURNING_TEST)

    result = pytester.runpytest()

    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*Results mismatch*"])


def test_pytest_pyfunc_call_with_accept_diff(pytester: pytest.Pytester) -> str:
    pytester.makepyfile(test_module=_RETURNING_TEST)

    result = pytester.runpytest("--accept-diff")

    result.assert_outcomes(skipped=1)
    previous = pytester.path / "__pytest_results__/test_module/test_function.json"
    return previous.read_text()


def test_pytest_pyfunc_call_with_diff_command(pytester: pytest.Pytester) -> str:
    pytester.makepyfile(test_module=_RETURNING_TEST)

    result = pytester.runpytest("--diff", "cp {current} {previous}")

    result.assert_outcomes(failed=1)
    previous = pytester.path / "__pytest_results__/test_module/test_function.json"
    return previous.read_text()


def test_pytest_pyfunc_call_with_several_mismatches_and_accept_diff(
    pytester: pytest.Pytester,
) -> list[str]:
    pytester.makepyfile(
        test_module="""
def test_function(regression):
    regression.check({"index": 0})
    regression.check({"index": 1})
""",
    )

    result = pytester.runpytest("--accept-diff")

    result.assert_outcomes(skipped=1)
    directory = pytester.path / "__pytest_results__/test_module"
    return sorted(path.name for path in directory.iterdir())


def test_pytest_pyfunc_call_with_exception_group_without_mismatch(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        test_module="""
def test_function():
    raise ExceptionGroup("errors", [ValueError("error")])
""",
    )

    result = pytester.runpytest("--accept-diff")

    result.assert_outcomes(failed=1)
