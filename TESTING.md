# Testing Guide

This document explains how to run tests for the cepces project.

## Test Framework

The project uses [pytest](https://pytest.org/) for running tests. All tests have been migrated from unittest to pytest style.

## Running Tests

### Using Tox

The recommended way to run tests is using [tox](https://tox.wiki/), which tests against multiple Python versions:

```bash
# Run tests for all configured Python versions
tox

# Run tests for a specific Python version
tox -e 3.11
tox -e 3.12
tox -e 3.13
```

Run linting:

```bash
tox -e lint
```

Run formatting checks:

```bash
tox -e format
```

Run type checking:

```bash
tox -e type
```

### Using pytest

Run all tests using pytest:

```bash
pytest tests/
```

Run tests with verbose output:

```bash
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/cepces_test/keyctl.py -v
```

Run a specific test function:

```bash
pytest tests/cepces_test/keyctl.py::test_keyctl_handler_initialization_with_keyctl_available -v
```

### Test Configuration

Test configuration is in `pyproject.toml` under the `[tool.pytest.ini_options]` section.

Default pytest options include:
- `-v`: Verbose output
- `--strict-markers`: Strict marker checking
- `--tb=short`: Short traceback format

## Test Structure

Tests are organized in the `tests/cepces_test/` directory:

```
tests/
├── cepces_test/
│   ├── certmonger/      # Certmonger operation tests
│   ├── keyctl.py        # Keyctl handler tests
│   ├── xcep/            # XCEP converter tests
│   └── xml/             # XML-related tests
```

## Writing Tests

### Test Function Naming

All test functions must start with `test_`:

```python
def test_my_feature():
    assert True
```

### Using Fixtures

pytest fixtures can be used for test setup:

```python
import pytest

@pytest.fixture
def my_fixture():
    return "test_data"

def test_with_fixture(my_fixture):
    assert my_fixture == "test_data"
```

### Testing Exceptions

Use `pytest.raises()` to test exceptions:

```python
import pytest

def test_exception():
    with pytest.raises(ValueError):
        raise ValueError("error message")
```

### Mocking

The project uses `unittest.mock` for mocking:

```python
from unittest.mock import patch

@patch("module.function")
def test_with_mock(mock_function):
    mock_function.return_value = "mocked"
    assert module.function() == "mocked"
```

## CI/CD

Tests are automatically run on GitHub Actions for multiple Python versions (3.10-3.14).
