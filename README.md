# pytest-results

[![CI](https://github.com/100nm/pytest-results/actions/workflows/ci.yml/badge.svg)](https://github.com/100nm/pytest-results)
[![PyPI](https://img.shields.io/pypi/v/pytest-results.svg?color=blue)](https://pypi.org/project/pytest-results/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Easily spot regressions in your tests.

The package lets you write non-regression tests.

## Installation

⚠️ _Requires Python 3.12 or higher_

```bash
pip install pytest-results
```

## Quick start

First, return the value where you want to check the regression:

```python
def test_function():
    return {"hello": "world"}
```

All results are stored in JSON files at the root of your project in the
`__pytest_results__` folder.

In case of regression, to open the interactive comparison, add the `--ide` parameter
to Pytest with the name of your IDE:

```bash
pytest --ide vscode
```

_At present, the IDEs supported are `cursor`, `pycharm` and `vscode`._

## Resources

* [**Regression fixture**](https://github.com/100nm/pytest-results/tree/prod/documentation/regression-fixture.md)
* [**Configuration**](https://github.com/100nm/pytest-results/tree/prod/documentation/configuration.md)
