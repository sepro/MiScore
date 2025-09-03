from miscore import RecordData, Game
import pytest
import os
import tempfile
import json
from unittest.mock import patch, call

# Get the test data directory path
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def test_successful_load():
    """
    This will load the golden standard dataset (which should work) and perform a few additional checks to ensure data
    was included correctly.
    """

    record_data = RecordData.load(os.path.join(TEST_DATA_DIR, "records.json"))
    assert len(record_data.games) > 0


def test_failed_load():
    with pytest.raises(Exception):
        _ = RecordData.load(os.path.join(TEST_DATA_DIR, "invalid.json"))


def test_save_method():
    """Test the save method creates valid JSON files"""
    # Create test data
    game = Game(name="Test Game")
    record_data = RecordData(games=[game])

    # Save to temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        temp_filename = temp_file.name

    try:
        record_data.save(temp_filename)

        # Verify file was created and contains expected content
        assert os.path.exists(temp_filename)

        with open(temp_filename, "r") as f:
            saved_data = json.load(f)

        assert "games" in saved_data
        assert len(saved_data["games"]) == 1
        assert saved_data["games"][0]["name"] == "Test Game"

        # Verify saved file can be loaded back
        loaded_data = RecordData.load(temp_filename)
        assert len(loaded_data.games) == 1
        assert loaded_data.games[0].name == "Test Game"

    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_add_game_to_new_file():
    """Test adding a game to a non-existent file"""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
        temp_filename = temp_file.name

    # File should not exist at this point
    assert not os.path.exists(temp_filename)

    try:
        # Add game to non-existent file
        result = RecordData.add_game_to_file("New Game", temp_filename, interactive=False)
        assert result is True

        # Verify file was created and contains the game
        assert os.path.exists(temp_filename)
        loaded_data = RecordData.load(temp_filename)
        assert len(loaded_data.games) == 1
        assert loaded_data.games[0].name == "New Game"

    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_add_game_to_existing_file():
    """Test adding a game to an existing file"""
    # Create initial file with one game
    initial_game = Game(name="Initial Game")
    record_data = RecordData(games=[initial_game])

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        temp_filename = temp_file.name

    try:
        record_data.save(temp_filename)

        # Add second game
        result = RecordData.add_game_to_file("Second Game", temp_filename, interactive=False)
        assert result is True

        # Verify both games are present
        loaded_data = RecordData.load(temp_filename)
        assert len(loaded_data.games) == 2
        game_names = [game.name for game in loaded_data.games]
        assert "Initial Game" in game_names
        assert "Second Game" in game_names

    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_add_duplicate_game():
    """Test that adding a duplicate game returns False and doesn't modify the file"""
    # Create initial file with one game
    initial_game = Game(name="Duplicate Game")
    record_data = RecordData(games=[initial_game])

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        temp_filename = temp_file.name

    try:
        record_data.save(temp_filename)

        # Try to add same game again
        result = RecordData.add_game_to_file("Duplicate Game", temp_filename, interactive=False)
        assert result is False

        # Verify file still contains only one game
        loaded_data = RecordData.load(temp_filename)
        assert len(loaded_data.games) == 1
        assert loaded_data.games[0].name == "Duplicate Game"

    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


class TestInteractiveMode:
    """Test suite for interactive difficulty level functionality"""

    def test_interactive_game_with_difficulties(self):
        """Test creating a game with difficulties through interactive prompts"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: yes for difficulties, then Easy, Hard, empty to finish
            user_inputs = ['y', 'Easy', 'Hard', '']
            with patch('builtins.input', side_effect=user_inputs):
                with patch('builtins.print'):  # Suppress print output during tests
                    result = RecordData.add_game_to_file("Test Game", temp_filename, interactive=True)
            
            assert result is True
            
            # Verify the game was created with correct difficulties
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 1
            game = loaded_data.games[0]
            assert game.name == "Test Game"
            assert game.difficulties == ['Easy', 'Hard']

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_game_no_difficulties(self):
        """Test creating a game without difficulties through interactive prompts"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no for difficulties
            user_inputs = ['n']
            with patch('builtins.input', side_effect=user_inputs):
                with patch('builtins.print'):
                    result = RecordData.add_game_to_file("Test Game", temp_filename, interactive=True)
            
            assert result is True
            
            # Verify the game was created without difficulties
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 1
            game = loaded_data.games[0]
            assert game.name == "Test Game"
            assert game.difficulties is None

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_duplicate_difficulty_handling(self):
        """Test handling of duplicate difficulty entries"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: yes, Normal, Normal (duplicate), Hard, empty to finish
            user_inputs = ['y', 'Normal', 'Normal', 'Hard', '']
            with patch('builtins.input', side_effect=user_inputs):
                with patch('builtins.print'):
                    result = RecordData.add_game_to_file("Test Game", temp_filename, interactive=True)
            
            assert result is True
            
            # Verify only unique difficulties were added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties == ['Normal', 'Hard']

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_invalid_yes_no_responses(self):
        """Test handling of invalid responses to yes/no question"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: invalid responses, then valid 'yes', then difficulties
            user_inputs = ['maybe', 'invalid', 'yes', 'Easy', '']
            with patch('builtins.input', side_effect=user_inputs):
                with patch('builtins.print'):
                    result = RecordData.add_game_to_file("Test Game", temp_filename, interactive=True)
            
            assert result is True
            
            # Verify the game was created with difficulties
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties == ['Easy']

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_empty_then_difficulty(self):
        """Test handling empty input followed by actual difficulty"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: yes, empty (no difficulties yet), then add one, empty again to finish
            user_inputs = ['y', '', 'Medium', '']
            with patch('builtins.input', side_effect=user_inputs):
                with patch('builtins.print'):
                    result = RecordData.add_game_to_file("Test Game", temp_filename, interactive=True)
            
            assert result is True
            
            # Verify the game was created with the difficulty
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties == ['Medium']

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_skip_difficulties_with_double_empty(self):
        """Test skipping difficulties by pressing enter twice when no difficulties added"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: yes, empty twice to skip difficulties
            user_inputs = ['y', '', '']
            with patch('builtins.input', side_effect=user_inputs):
                with patch('builtins.print'):
                    result = RecordData.add_game_to_file("Test Game", temp_filename, interactive=True)
            
            assert result is True
            
            # Verify the game was created without difficulties
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties is None

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
