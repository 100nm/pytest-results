# pytest-results

[![PyPI - Version](https://shieldcn.dev/pypi/v/pytest-results.svg?color=3775A9&size=xs&variant=secondary)](https://pypi.org/project/pytest-results)
[![PyPI - Downloads](https://shieldcn.dev/pypi/dm/pytest-results.svg?color=3775A9&size=xs&variant=secondary)](https://pypistats.org/packages/pytest-results)
[![GitHub Stars](https://shieldcn.dev/github/stars/100nm/pytest-results.svg?size=xs&variant=secondary)](https://github.com/100nm/pytest-results/stargazers)
[![CI](https://shieldcn.dev/github/ci/100nm/pytest-results.svg?size=xs&variant=secondary&workflow=ci.yml)](https://github.com/100nm/pytest-results/actions/workflows/ci.yml)
[![Ruff](https://shieldcn.dev/badge/code_style-Ruff-261230.svg?logo=ruff&size=xs&variant=secondary)](https://github.com/astral-sh/ruff)

Easily spot regressions in your tests.

[Pytest](https://github.com/pytest-dev/pytest) plugin for writing non-regression tests.

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
