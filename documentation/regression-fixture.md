# Regression fixture

`regression` is a Pytest fixture which compares the result with the result of the
previous run.

All results are stored in JSON files at the root of your project in the
`__pytest_results__` folder.

Example:

```python
from pytest_results import Regression

def test_function(regression: Regression) -> None:
    result = ...
    regression.check(result)
```

If you have only one `regression.check` at the end of your test, you can use
`return`, and the plugin will take care of it automatically:

```python
def test_function() -> ...:
    result = ...
    return result
```

> [!NOTE]
> Supported `result` types:
> * Python serializable objects in JSON
> * bytes (directly for JSON file)
> * [pydantic.BaseModel](https://github.com/pydantic/pydantic)
> * [msgspec.Struct](https://github.com/jcrist/msgspec)

It is possible to call `regression.check` several times in the same test:

```python
from pytest_results import Regression

def test_function(regression: Regression) -> None:
    for i in range(...):
        result = ...
        regression.check(result)
```

## Custom regression fixture

Here's how to write a custom regression fixture:

```python
# conftest.py

from typing import Any

import pytest
from pytest_results import BoundRegression, Regression

def _yaml_dump(value: Any) -> bytes:
    """ Python to yaml """

@pytest.fixture
def regression_yaml(regression: Regression) -> Regression:
    return BoundRegression(regression, dump_func=_yaml_dump, file_format="yml")
```
