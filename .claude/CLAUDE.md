# Project Instructions for cepces

## Testing
- **ALWAYS run tests after making code modifications**
- Run `pytest tests/ -v` to execute the test suite
- Ensure all tests pass before considering a task complete
- If tests fail, fix the issues before moving on

## Python Code Standards
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Maintain existing code structure and patterns

## Code Quality Checks
- **ALWAYS run linting after making code modifications**
- Run `tox -e lint` to check with ruff linter
- Run `tox -e format` to check code formatting with black
- Run `tox -e type` to run mypy type checking
- Run `tox -e pycodestyle` to check PEP 8 compliance with pycodestyle
- Fix all linting errors and warnings before considering a task complete
- Alternatively, run `tox -e lint,format,type,pycodestyle` to run all checks at once
