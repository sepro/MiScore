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
- Whether the game has difficulty levels (y/n)
- If yes, you can enter each difficulty level (press Enter with empty input to finish)

If the game already exists in the file, you'll get a message saying so and the file won't be modified.

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
python -m miscore validate --help
```

## Setting up (for developers)

After cloning the repository, navigate into the MiScore directory and run the command below to create and activate
an environment.

```commandline
python -m venv venv
activate venv/bin/activate
pip install -r docs/dev/requirements.txt
```

Now you can run the test suite using

```commandline
pytest
```

To run tests with coverage reporting:

```commandline
pytest --cov=src --cov-report=term-missing
```

