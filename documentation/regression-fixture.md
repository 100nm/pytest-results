# Regression fixture

`regression` is a Pytest fixture which compares the result with the result of the
previous run.

All results are stored in JSON files at the root of your project in the
`__pytest_results__` folder.

Example:

```python
from pytest_results import RegressionType

def test_function(regression: RegressionType) -> None:
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
> `result` must be a Python object serializable to JSON or an instance of Pydantic 
> `BaseModel`.

It is possible to call `regression.check` several times in the same test:

```python
from pytest_results import RegressionType

def test_function(regression: RegressionType) -> None:
    for i in range(...):
        result = ...
        regression.check(result)
```
