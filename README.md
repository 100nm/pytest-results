# pytest-results

[![PyPI - Version](https://shieldcn.dev/pypi/v/pytest-results.svg?color=3775A9&size=xs&variant=secondary)](https://pypi.org/project/pytest-results)
[![PyPI - Downloads](https://shieldcn.dev/pypi/dm/pytest-results.svg?color=3775A9&size=xs&variant=secondary)](https://pypistats.org/packages/pytest-results)
[![GitHub Stars](https://shieldcn.dev/github/stars/100nm/pytest-results.svg?size=xs&variant=secondary)](https://github.com/100nm/pytest-results/stargazers)
[![CI](https://shieldcn.dev/github/ci/100nm/pytest-results.svg?size=xs&variant=secondary&workflow=ci.yml)](https://github.com/100nm/pytest-results/actions/workflows/ci.yml)
[![Ruff](https://shieldcn.dev/badge/code_style-Ruff-261230.svg?logo=ruff&size=xs&variant=secondary)](https://github.com/astral-sh/ruff)

Easily spot regressions in your tests.

A [Pytest](https://github.com/pytest-dev/pytest) plugin for snapshot testing: a test
returns a value, the plugin stores it in a snapshot file, and compares the next runs
with it.

## Installation

⚠️ _Requires Python 3.12 or higher_

```bash
pip install pytest-results
```

## Quick start

Return the value to check from your test:

```python
def test_function():
    return {"hello": "world"}
```

The first run fails, since there is no snapshot to compare with yet. Accept the new
results to store them as snapshots:

```bash
pytest --accept-diff
```

The snapshots are stored as JSON files in the `__pytest_results__` folder, at the root
of your project. Commit this folder: from now on, the test fails whenever its result
changes.

When a test fails, open the differences in your IDE with the `--ide` option:

```bash
pytest --ide vscode
```

_The supported IDEs are `cursor`, `pycharm` and `vscode`._

If the changes are expected, update the snapshots with `pytest --accept-diff`.

## Documentation

* [**Regression fixture**](https://github.com/100nm/pytest-results/blob/prod/docs/regression-fixture.md):
  checking results, supported types, snapshot files and custom formats.
* [**Configuration**](https://github.com/100nm/pytest-results/blob/prod/docs/configuration.md):
  command line options and configuration file.
