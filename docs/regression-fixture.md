# Regression fixture

The `regression` fixture compares the result of a test with its snapshot: the result
stored in a file by a previous run.

## Checking a result

The simplest way to check a result is to return it from the test:

```python
def test_function() -> dict[str, str]:
    return {"hello": "world"}
```

Async tests work the same way (with an async plugin such as
[pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)):

```python
async def test_function() -> dict[str, str]:
    return {"hello": "world"}
```

A test returning `None` checks nothing.

For more control, use the `regression` fixture and call `regression.check`:

```python
from pytest_results import Regression


def test_function(regression: Regression) -> None:
    result = ...
    regression.check(result)
```

`regression.check` can be called several times in the same test. Every check runs, and
all the mismatches are reported together at the end of the test:

```python
from pytest_results import Regression


def test_function(regression: Regression) -> None:
    for i in range(3):
        regression.check({"index": i})
```

## Supported types

| Type                                                          | Snapshot content                                  |
|---------------------------------------------------------------|---------------------------------------------------|
| `bytes`                                                       | the bytes, as is                                  |
| [`pydantic.BaseModel`](https://github.com/pydantic/pydantic)  | `model_dump_json(indent=2)`                       |
| [`msgspec.Struct`](https://github.com/jcrist/msgspec)         | JSON, indented by 2 spaces                        |
| any other value                                               | JSON with [orjson](https://github.com/ijl/orjson) |

Pydantic and msgspec are supported only when they are installed.

orjson serializes the usual Python types (`dict`, `list`, `str`, `int`, `datetime`,
`UUID`, dataclasses, enums...). Any other object is converted with `str()`: a
`Path("hello")` is stored as `"hello"`.

## Snapshot files

The snapshots are stored in the `__pytest_results__` folder, in the
[root directory](https://docs.pytest.org/en/stable/reference/customize.html#rootdir) of
Pytest. Their path follows the test's module, class and function:

```text
__pytest_results__/
└── tests/
    └── test_orders/
        └── TestOrder/
            ├── test_total.json      # first check
            ├── test_total_1.json    # second check
            └── test_total_2.json    # third check
```

## Parameters of `check`

```python
regression.check(
    result,
    suffix=None,  # appended to the file name
    dump_func=None,  # converts the result to bytes
    file_format=None,  # file extension, "json" by default
)
```

### Suffix

The snapshot file name is based on the test function only. The cases of a parametrized
test would therefore share the same snapshot and overwrite each other: give each case
its own snapshot with `suffix`.

```python
import pytest
from pytest_results import Regression


@pytest.mark.parametrize("quantity", [1, 2, 3])
def test_total(quantity: int, regression: Regression) -> None:
    result = ...
    regression.check(result, suffix=f"[{quantity}]")
```

A suffix also replaces the `_1`, `_2`... numbering of successive checks.

### Custom format

`dump_func` converts the result to the bytes of the snapshot, and `file_format` sets the
extension of the snapshot file:

```python
import yaml
from pytest_results import Regression


def test_function(regression: Regression) -> None:
    result = ...
    regression.check(
        result,
        dump_func=lambda value: yaml.safe_dump(value).encode(),
        file_format="yml",
    )
```

## Custom regression fixture

To reuse a format, bind it to a fixture with `BoundRegression`. Its `check` uses the
bound `dump_func` and `file_format`, unless they are passed explicitly:

```python
# conftest.py

from typing import Any

import pytest
import yaml
from pytest_results import BoundRegression, Regression


def _yaml_dump(value: Any) -> bytes:
    return yaml.safe_dump(value).encode()


@pytest.fixture
def regression_yaml(regression: Regression) -> Regression:
    return BoundRegression(regression, dump_func=_yaml_dump, file_format="yml")
```

```python
from pytest_results import Regression


def test_function(regression_yaml: Regression) -> None:
    result = ...
    regression_yaml.check(result)
```
