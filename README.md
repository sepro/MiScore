[![Run Pytest](https://github.com/sepro/MiScore/actions/workflows/autopytest.yml/badge.svg)](https://github.com/sepro/MiScore/actions/workflows/autopytest.yml)
[![Coverage](https://raw.githubusercontent.com/sepro/MiScore/main/docs/coverage-badge.svg)](https://github.com/sepro/MiScore/actions/workflows/autopytest.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# MiScore - The anti-social leaderboard

Are you tired of seeing your high scores appear in online leaderboards and being discouraged to see how low you rank ? 
Or maybe you simply enjoy retro games that have no high scores? MiScore is the answer, this tool allows you to set up
a leaderboard to track scores across different games just for YOU! 

## Planning 

This is very much a work in progress, here is a rough sketch of the steps planned.

  - [X] Work out json schema and Pydantic code to load and validate data
  - [ ] Interface (textual ?) to add data
  - [ ] Front-end (Svelte?) to show result on a static webpage

## Using MiScore

MiScore provides a command-line interface for managing your gaming records.

### Adding Games

To create a new records file or add a game to an existing one:

```commandline
python -m miscore add-game "Game Name" records.json
```

By default, the command will interactively ask if the game has difficulty levels and prompt you to enter them. To skip the interactive setup, use the `--no-interactive` flag:

```commandline
python -m miscore add-game "Game Name" records.json --no-interactive
```

**Examples:**
```commandline
# Create a new records file with interactive difficulty setup
python -m miscore add-game "Doom (2016)" my_games.json

# Add a game without interactive prompts (useful for scripts)
python -m miscore add-game "Simple Puzzle Game" my_games.json --no-interactive

# Add a game with difficulty levels (interactive mode will guide you)
python -m miscore add-game "Zelda: Breath of the Wild" my_games.json
```

During interactive mode, you'll be asked:
- **Difficulty levels**: Whether the game has difficulty levels (y/n)
  - If yes, you can enter each difficulty level (press Enter with empty input to finish)
- **Record types**: Whether you want to add record types (y/n)
  - If yes, choose from 6 available types:
    1. **completed** - Track when you completed the game
    2. **completed_at_difficulty** - Track completions at specific difficulties (requires difficulty levels)
    3. **fastest_time** - Track your best speed runs
    4. **longest_time** - Track your longest playthroughs
    5. **high_score** - Track your highest scores
    6. **low_score** - Track your lowest scores (for golf-style games)
  - For each record type, you can customize the name and add an optional description
  - Press Enter with empty input to finish adding record types

If the game already exists in the file, you'll get a message saying so and the file won't be modified.

### Adding Records

Once you have games with record types configured, you can add records to track your achievements:

```commandline
python -m miscore add-record records.json
```

The command will guide you through an interactive process:

1. **Game Selection**: Choose which game to add a record for
2. **Record Type Selection**: Choose which type of record to add
3. **Record Details**: Enter the specific information based on the record type

**Examples:**
```commandline
# Add a record to your games file
python -m miscore add-record my_games.json

# Add a record using just the filename (works in current directory)
python -m miscore add-record records.json
```

**Record Information Collected:**
- **Date**: When the achievement occurred (defaults to today, format: YYYY-MM-DD)
- **Description**: Optional description of the achievement
- **Screenshot**: Optional path to a screenshot file (relative to the JSON file location)
- **Type-specific fields**:
  - **Difficulty**: For `completed_at_difficulty` records, select from the game's difficulty levels
  - **Time**: For `fastest_time`/`longest_time` records, enter time in various formats:
    - `HH:MM:SS` (e.g., `1:23:45`)
    - `MM:SS` (e.g., `23:45`)
    - Human-readable (e.g., `1h30m45s`, `90m`, `5400s`)
  - **Score**: For `high_score`/`low_score` records, enter a numeric value

You can cancel at any step by typing `q` and pressing Enter.

**Note**: The `add-record` command currently only supports interactive mode. You must have at least one game with configured record types before you can add records.

### Validating a records file

You can validate a json file containing records data using:

```commandline
python -m miscore validate records.json
```

**Examples:**
```commandline
# Validate your records file
python -m miscore validate my_games.json

# Validate and see detailed error information
python -m miscore validate my_games.json --raise_error
```

### Getting Help

For more information about available commands:

```commandline
# See all available commands
python -m miscore --help

# Get help for a specific command
python -m miscore add-game --help
python -m miscore add-record --help
python -m miscore validate --help
```

## Development

For developers who want to contribute to MiScore, please see the [Development Guide](docs/development.md) for setup instructions, testing guidelines, and code structure information.

