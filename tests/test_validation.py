from miscore import RecordData, Game
import pytest
import os
import tempfile
import json

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
        result = RecordData.add_game_to_file("New Game", temp_filename)
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
        result = RecordData.add_game_to_file("Second Game", temp_filename)
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
        result = RecordData.add_game_to_file("Duplicate Game", temp_filename)
        assert result is False

        # Verify file still contains only one game
        loaded_data = RecordData.load(temp_filename)
        assert len(loaded_data.games) == 1
        assert loaded_data.games[0].name == "Duplicate Game"

    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
