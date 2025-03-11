# assert_results_match fixture

`assert_results_match` is a Pytest fixture which compares the result with the result of
the previous run.

All results are stored in JSON files at the root of your project in the
`__pytest_results__` folder.

Example:

```python
from pytest_results import AssertResultsMatchType

def test_function(assert_results_match: AssertResultsMatchType) -> None:
    result = ...
    assert_results_match(result)
```

If you have only one `assert_results_match` at the end of your test, you can use
`return`, and the plugin will take care of it automatically:

```python
def test_function() -> ...:
    result = ...
    return result
```

> [!NOTE]
> `result` must be a Python object serializable to JSON or an instance of Pydantic 
> `BaseModel`.

If `assert_results_match` is called several times in a test, a suffix must be added to
differentiate the results to be checked:

```python
from pytest_results import AssertResultsMatchType

def test_function(assert_results_match: AssertResultsMatchType) -> None:
    for i in range(...):
        result = ...
        assert_results_match(result, file_suffix=f"-{i}")
```
