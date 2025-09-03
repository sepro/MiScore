# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r docs/dev/requirements.txt
```

### Testing
```bash
pytest                                    # Run all tests
pytest --exitfirst --verbose --failed-first --cov=src tests/ --cov-report=term-missing --cov-report=xml  # Full test suite with coverage
```

### Code Formatting
```bash
black .                                   # Format all Python code
black --check .                          # Check formatting without making changes
```

### Validation
```bash
python -m miscore <path_to_json_file>    # Validate a records JSON file
python -m miscore <path_to_json_file> --raise_error  # Validate and raise error on failure
```

## Architecture Overview

MiScore is a personal gaming leaderboard system built around JSON data validation and management using Pydantic v2. The core architecture follows these principles:

### Core Models (src/miscore/record_data.py)
- **RecordData**: Top-level container for all gaming records
- **Game**: Individual game with difficulties and record types
- **RecordType**: Categories of records (completion, times, scores) with validation
- **Record Entry Types**: Hierarchical models for different record types:
  - `CompletedRecordEntry`: Base completion tracking
  - `CompletedAtDifficultyRecordEntry`: Difficulty-specific completion
  - `TimeRecordEntry`: Time-based records (fastest/longest)
  - `ScoreRecordEntry`: Score-based records (high/low)

### Validation System
The system uses Pydantic's validation with custom validators:
- Record types must match their entry types (enforced by `check_record_entry_types`)
- Difficulty references must be valid for the game (enforced by `check_record_entry_difficulty`)
- File paths for screenshots are validated relative to the JSON file location

### CLI Interface (src/miscore/__main__.py)
Simple Click-based command for JSON validation with optional error raising.

## Key Dependencies
- **Pydantic >=2.0.0**: Core data validation and modeling
- **Click >=8.1.3**: CLI interface
- **Black**: Code formatting (enforced via GitHub Actions)
- **Pytest**: Testing framework with coverage reporting

## Testing Configuration
- Python path: `src` (configured in pytest.ini)
- Coverage excludes: `src/miscore/__main__.py` (configured in .coveragerc)
- CI runs on Python 3.8-3.12 with automatic coverage badge updates