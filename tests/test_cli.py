import pytest
import os
import tempfile
import json
from click.testing import CliRunner
from miscore.__main__ import cli
from miscore import RecordData, Game

# Get the test data directory path
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestCLI:
    """Test suite for CLI functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test the CLI main help functionality"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "add-game" in result.output
        assert "validate" in result.output
        assert "MiScore - Personal gaming leaderboard system" in result.output

    def test_validate_command_help(self):
        """Test validate command help"""
        result = self.runner.invoke(cli, ['validate', '--help'])
        assert result.exit_code == 0
        assert "Validate a records JSON file" in result.output
        assert "FILENAME" in result.output
        assert "--raise_error" in result.output

    def test_add_game_command_help(self):
        """Test add-game command help"""
        result = self.runner.invoke(cli, ['add-game', '--help'])
        assert result.exit_code == 0
        assert "Add a new game to a records file" in result.output
        assert "GAME_NAME" in result.output
        assert "FILENAME" in result.output

    def test_validate_valid_file(self):
        """Test validating a valid records file"""
        result = self.runner.invoke(cli, ['validate', os.path.join(TEST_DATA_DIR, 'records.json')])
        assert result.exit_code == 0
        assert "is valid" in result.output

    def test_validate_invalid_file(self):
        """Test validating an invalid records file"""
        result = self.runner.invoke(cli, ['validate', os.path.join(TEST_DATA_DIR, 'invalid.json')])
        assert result.exit_code == 0
        assert "is not valid" in result.output
        assert "The following error occurred:" in result.output

    def test_validate_nonexistent_file(self):
        """Test validating a non-existent file"""
        result = self.runner.invoke(cli, ['validate', 'nonexistent.json'])
        assert result.exit_code == 0
        assert "is not valid" in result.output

    def test_validate_with_raise_error_flag(self):
        """Test validate command with --raise_error flag"""
        result = self.runner.invoke(cli, ['validate', os.path.join(TEST_DATA_DIR, 'invalid.json'), '--raise_error'])
        assert result.exit_code != 0  # Should exit with error code

    def test_add_game_to_new_file(self):
        """Test adding a game to a non-existent file via CLI"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=True) as temp_file:
            temp_filename = temp_file.name

        try:
            # Add game to non-existent file
            result = self.runner.invoke(cli, ['add-game', 'CLI Test Game', temp_filename])
            assert result.exit_code == 0
            assert "Game 'CLI Test Game' added" in result.output

            # Verify file was created correctly
            assert os.path.exists(temp_filename)
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 1
            assert loaded_data.games[0].name == "CLI Test Game"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_game_to_existing_file(self):
        """Test adding a game to an existing file via CLI"""
        # Create initial file with one game
        initial_game = Game(name="Initial Game")
        record_data = RecordData(games=[initial_game])

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            record_data.save(temp_filename)

            # Add second game via CLI
            result = self.runner.invoke(cli, ['add-game', 'Second CLI Game', temp_filename])
            assert result.exit_code == 0
            assert "Game 'Second CLI Game' added" in result.output

            # Verify both games are present
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 2
            game_names = [game.name for game in loaded_data.games]
            assert "Initial Game" in game_names
            assert "Second CLI Game" in game_names

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_duplicate_game_via_cli(self):
        """Test adding a duplicate game via CLI"""
        # Create initial file with one game
        initial_game = Game(name="Duplicate Game")
        record_data = RecordData(games=[initial_game])

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            record_data.save(temp_filename)

            # Try to add same game again via CLI
            result = self.runner.invoke(cli, ['add-game', 'Duplicate Game', temp_filename])
            assert result.exit_code == 0
            assert "already exists" in result.output

            # Verify file still contains only one game
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 1
            assert loaded_data.games[0].name == "Duplicate Game"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_game_with_special_characters(self):
        """Test adding a game with special characters in the name"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=True) as temp_file:
            temp_filename = temp_file.name

        try:
            game_name = "Zelda: Breath of the Wild & The Legend Continues!"
            result = self.runner.invoke(cli, ['add-game', game_name, temp_filename])
            assert result.exit_code == 0
            assert f"Game '{game_name}' added" in result.output

            # Verify game was added correctly
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 1
            assert loaded_data.games[0].name == game_name

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_game_error_handling(self):
        """Test error handling in add-game command"""
        # Test with an invalid directory path
        result = self.runner.invoke(cli, ['add-game', 'Test Game', '/invalid/path/file.json'])
        assert result.exit_code == 0
        assert "Error adding game:" in result.output

    def test_validate_and_add_game_workflow(self):
        """Test a complete workflow: add game, then validate"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=True) as temp_file:
            temp_filename = temp_file.name

        try:
            # Add a game
            add_result = self.runner.invoke(cli, ['add-game', 'Workflow Test Game', temp_filename])
            assert add_result.exit_code == 0
            assert "added" in add_result.output

            # Validate the created file
            validate_result = self.runner.invoke(cli, ['validate', temp_filename])
            assert validate_result.exit_code == 0
            assert "is valid" in validate_result.output

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_cli_missing_arguments(self):
        """Test CLI commands with missing arguments"""
        # Test validate without filename
        result = self.runner.invoke(cli, ['validate'])
        assert result.exit_code != 0

        # Test add-game without arguments
        result = self.runner.invoke(cli, ['add-game'])
        assert result.exit_code != 0

        # Test add-game with only one argument
        result = self.runner.invoke(cli, ['add-game', 'Game Name'])
        assert result.exit_code != 0

    def test_cli_invalid_command(self):
        """Test CLI with invalid command"""
        result = self.runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0
        assert "No such command" in result.output