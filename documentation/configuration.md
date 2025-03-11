# Configuration

## [Pytest](https://github.com/pytest-dev/pytest)

### Accept diff

Automatically saves the new result if `regression.check` fails.

With Pytest command line:

```bash
pytest --accept-diff
```

### Diff

Executes a command line when `regression.check` fails.

Command line parameters:
* `{current}`: path to temporary file containing the current test result.
* `{previous}`: path to reference file containing previous test result.

With [Pytest configuration](https://docs.pytest.org/en/latest/reference/customize.html):

```ini
# pytest.ini

[pytest]
diff = <COMMAND_LINE>
```

With Pytest command line:

```bash
pytest --diff "<COMMAND_LINE>"
```

VSCode command line example:

```bash
code -d -w {current} {previous}
```

### IDE

Executes an interactive comparison based on the chosen IDE when `regression.check`
fails.

_If `diff` is defined, it takes priority._

Possible choices are: `cursor`, `pycharm` and `vscode`.

With [Pytest configuration](https://docs.pytest.org/en/latest/reference/customize.html):

```ini
# pytest.ini

[pytest]
ide = <IDE>
```

With Pytest command line:

```bash
pytest --ide <IDE>
```
