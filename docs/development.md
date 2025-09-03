# Development Guide

This guide covers how to set up and work with the MiScore development environment.

## Setting up the Development Environment

After cloning the repository, navigate into the MiScore directory and run the commands below to create and activate a virtual environment.

```commandline
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r docs/dev/requirements.txt
```

## Running Tests

You can run the test suite using:

```commandline
pytest
```

To run tests with coverage reporting:

```commandline
pytest --cov=src --cov-report=term-missing
```

This will show you which lines are missing test coverage. The project aims for 100% test coverage.

## Code Structure

The main source code is located in `src/miscore/`:

- `__init__.py` - Package initialization
- `__main__.py` - CLI interface using Click
- `record_data.py` - Core data models and validation using Pydantic

## Testing Structure

Tests are located in the `tests/` directory:

- `test_validation.py` - Tests for data models and validation logic
- `test_cli.py` - Tests for CLI interface functionality

The test suite includes comprehensive coverage of:
- Data validation and model behavior
- Interactive mode functionality with mocked user input
- CLI command behavior and error handling
- Edge cases and error conditions

## Code Quality

The project uses:
- **Black** for code formatting
- **Pydantic v2** for data validation
- **Pytest** for testing with coverage reporting
- **Click** for CLI interface

## Dependencies

Development dependencies are listed in `docs/dev/requirements.txt`:
- `click` - CLI framework
- `pydantic` - Data validation
- `black` - Code formatting
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting