# Configuration

| Command line            | Configuration file      | Description                                |
|-------------------------|-------------------------|--------------------------------------------|
| `--accept-diff`         |                         | Updates the snapshots instead of failing.  |
| `--diff <COMMAND_LINE>` | `diff = <COMMAND_LINE>` | Runs a command line on each mismatch.      |
| `--ide <IDE>`           | `ide = <IDE>`           | Opens each mismatch in an IDE.             |

The command line takes priority over the configuration file.

## Configuration file

The options go in the Pytest
[configuration file](https://docs.pytest.org/en/stable/reference/customize.html):

```toml
# pyproject.toml

[tool.pytest]
ide = "vscode"
```

```ini
# pytest.ini

[pytest]
ide = vscode
```

## Accept diff

```bash
pytest --accept-diff
```

Updates the snapshot of each test whose result changed, and creates the missing ones.
These tests are marked as **skipped**: run Pytest again to check that everything passes.

## IDE

```bash
pytest --ide vscode
```

Opens each mismatch in an interactive comparison of the IDE. The test still fails.

| IDE       | Command line                            |
|-----------|-----------------------------------------|
| `cursor`  | `cursor -d -r -w {current} {previous}`  |
| `pycharm` | `pycharm diff {current} {previous}`     |
| `vscode`  | `code -d -r -w {current} {previous}`    |

The IDE name is case-insensitive. An unsupported IDE only emits a warning. The IDE's
command line launcher must be installed (e.g. `code` for VSCode).

## Diff

```bash
pytest --diff "meld {current} {previous}"
```

Runs a command line on each mismatch, with these placeholders:

* `{current}`: path to a temporary file containing the current result;
* `{previous}`: path to the snapshot (an empty file is created if there is none).

The test still fails. The command line runs in a shell, so it may use variables or other
shell features. The paths are inserted as is, without quotes.

_If `diff` is set, it takes priority over `ide`._
