from miscore import RecordData, Game
from miscore.record_data import RecordType
import pytest
import os
import tempfile
import json
from datetime import date, timedelta
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
        result = RecordData.add_game_to_file(
            "New Game", temp_filename, interactive=False
        )
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
        result = RecordData.add_game_to_file(
            "Second Game", temp_filename, interactive=False
        )
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
        result = RecordData.add_game_to_file(
            "Duplicate Game", temp_filename, interactive=False
        )
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
            # Mock user input: yes for difficulties, then Easy, Hard, empty to finish, no record types
            user_inputs = ["y", "Easy", "Hard", "", "n"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):  # Suppress print output during tests
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the game was created with correct difficulties
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 1
            game = loaded_data.games[0]
            assert game.name == "Test Game"
            assert game.difficulties == ["Easy", "Hard"]

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
            # Mock user input: no for difficulties, no record types
            user_inputs = ["n", "n"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

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
            # Mock user input: yes, Normal, Normal (duplicate), Hard, empty to finish, no record types
            user_inputs = ["y", "Normal", "Normal", "Hard", "", "n"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify only unique difficulties were added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties == ["Normal", "Hard"]

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
            # Mock user input: invalid responses, then valid 'yes', then difficulties, no record types
            user_inputs = ["maybe", "invalid", "yes", "Easy", "", "n"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the game was created with difficulties
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties == ["Easy"]

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
            # Mock user input: yes, empty (no difficulties yet), then add one, empty again to finish, no record types
            user_inputs = ["y", "", "Medium", "", "n"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the game was created with the difficulty
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties == ["Medium"]

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
            # Mock user input: yes, empty twice to skip difficulties, no record types
            user_inputs = ["y", "", "", "n"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the game was created without difficulties
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.difficulties is None

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_game_with_record_types(self):
        """Test creating a game with record types through interactive prompts"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, yes record types, add high_score and completed
            user_inputs = [
                "n",
                "y",
                "5",
                "My High Score",
                "Track highest score",
                "1",
                "",
                "First completion",
                "",
            ]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the game was created with correct record types
            loaded_data = RecordData.load(temp_filename)
            assert len(loaded_data.games) == 1
            game = loaded_data.games[0]
            assert game.name == "Test Game"
            assert game.difficulties is None
            assert len(game.record_types) == 2

            # Check first record type (high_score)
            high_score_rt = next(
                rt for rt in game.record_types if rt.type == "high_score"
            )
            assert high_score_rt.name == "My High Score"
            assert high_score_rt.description == "Track highest score"
            assert high_score_rt.records == []

            # Check second record type (completed)
            completed_rt = next(
                rt for rt in game.record_types if rt.type == "completed"
            )
            assert completed_rt.name == "Game Completion"  # Default name
            assert completed_rt.description == "First completion"
            assert completed_rt.records == []

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_game_no_record_types(self):
        """Test creating a game without record types"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, no record types
            user_inputs = ["n", "n"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the game was created without record types
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.record_types is None

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_completed_at_difficulty_validation(self):
        """Test that completed_at_difficulty requires difficulty levels"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, yes record types, try completed_at_difficulty (should fail), then completed
            user_inputs = ["n", "y", "2", "1", "", "Basic completion", ""]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify only the valid record type was added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert len(game.record_types) == 1
            assert game.record_types[0].type == "completed"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_duplicate_record_type_handling(self):
        """Test handling of duplicate record type selections"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, yes record types, add high_score twice, then fastest_time
            user_inputs = [
                "n",
                "y",
                "5",
                "First High Score",
                "",
                "5",
                "3",
                "Speed Run",
                "My fastest runs",
                "",
            ]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify only unique record types were added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert len(game.record_types) == 2
            types = [rt.type for rt in game.record_types]
            assert "high_score" in types
            assert "fastest_time" in types

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_invalid_record_type_choices(self):
        """Test handling of invalid record type number choices"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, yes record types, invalid choices, then valid choice
            user_inputs = ["n", "y", "0", "7", "invalid", "1", "", "", ""]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the valid record type was added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert len(game.record_types) == 1
            assert game.record_types[0].type == "completed"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_skip_record_types_with_double_empty(self):
        """Test skipping record types by pressing enter twice"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, yes record types, empty twice to skip
            user_inputs = ["n", "y", "", ""]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify no record types were added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.record_types is None

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_invalid_record_type_yes_no_responses(self):
        """Test handling of invalid responses to record type yes/no question"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, invalid responses for record types, then no
            user_inputs = ["n", "maybe", "invalid", "no"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the game was created without record types
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert game.record_types is None

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_interactive_empty_then_record_type_choice(self):
        """Test handling empty input followed by actual record type choice"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            temp_filename = temp_file.name

        # File should not exist at this point
        assert not os.path.exists(temp_filename)

        try:
            # Mock user input: no difficulties, yes record types, empty (no types yet), then add one
            user_inputs = ["n", "y", "", "1", "", "", ""]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_game_to_file(
                        "Test Game", temp_filename, interactive=True
                    )

            assert result is True

            # Verify the record type was added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            assert len(game.record_types) == 1
            assert game.record_types[0].type == "completed"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestAddRecord:
    """Test suite for add-record functionality"""

    def test_add_record_to_nonexistent_file(self):
        """Test adding record to non-existent file"""
        result = RecordData.add_record_to_file("nonexistent.json", interactive=False)
        assert result is False

    def test_add_record_to_empty_games_file(self):
        """Test adding record to file with no games"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create empty records file
            empty_data = RecordData(games=[])
            empty_data.save(temp_filename)

            result = RecordData.add_record_to_file(temp_filename, interactive=False)
            assert result is False

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_completed_record_interactive(self):
        """Test adding a completed record interactively"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data with a game that has completed record type
            from miscore.record_data import RecordType

            completed_rt = RecordType(name="Completion", type="completed", records=[])
            test_game = Game(name="Test Game", record_types=[completed_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Mock user input: select game 1, record type 1, use today's date, no description, no screenshot
            user_inputs = ["1", "1", "", "", ""]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True

            # Verify the record was added
            loaded_data = RecordData.load(temp_filename)
            game = loaded_data.games[0]
            record_type = game.record_types[0]
            assert len(record_type.records) == 1
            assert record_type.records[0].date == date.today()

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_completed_at_difficulty_record(self):
        """Test adding a completed_at_difficulty record"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data with difficulties
            from miscore.record_data import RecordType

            diff_rt = RecordType(
                name="Difficulty Completion", type="completed_at_difficulty", records=[]
            )
            test_game = Game(
                name="Test Game", difficulties=["Easy", "Hard"], record_types=[diff_rt]
            )
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Mock user input: select game 1, record type 1, today's date, description, no screenshot, difficulty 2
            user_inputs = ["1", "1", "", "Beat the game on hard", "", "2"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True

            # Verify the record was added correctly
            loaded_data = RecordData.load(temp_filename)
            record = loaded_data.games[0].record_types[0].records[0]
            assert record.difficulty == "Hard"
            assert record.description == "Beat the game on hard"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_time_record_various_formats(self):
        """Test adding time records with various input formats"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data with fastest_time record type
            from miscore.record_data import RecordType

            time_rt = RecordType(name="Speed Run", type="fastest_time", records=[])
            test_game = Game(name="Test Game", record_types=[time_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Test different time formats
            time_formats = [
                ("1:30:45", timedelta(hours=1, minutes=30, seconds=45)),
                ("90:30", timedelta(minutes=90, seconds=30)),
                ("1h30m45s", timedelta(hours=1, minutes=30, seconds=45)),
                ("5400", timedelta(seconds=5400)),
            ]

            for time_input, expected_delta in time_formats:
                # Clear previous records
                test_data = RecordData(
                    games=[
                        Game(
                            name="Test Game",
                            record_types=[
                                RecordType(
                                    name="Speed Run", type="fastest_time", records=[]
                                )
                            ],
                        )
                    ]
                )
                test_data.save(temp_filename)

                user_inputs = ["1", "1", "", "", "", time_input]
                with patch("builtins.input", side_effect=user_inputs):
                    with patch("builtins.print"):
                        result = RecordData.add_record_to_file(
                            temp_filename, interactive=True
                        )

                assert result is True, f"Failed for time format: {time_input}"

                # Verify the time was parsed correctly
                loaded_data = RecordData.load(temp_filename)
                record = loaded_data.games[0].record_types[0].records[0]
                assert (
                    record.time == expected_delta
                ), f"Time mismatch for {time_input}: expected {expected_delta}, got {record.time}"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_add_score_record(self):
        """Test adding score records"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data with high_score record type
            from miscore.record_data import RecordType

            score_rt = RecordType(name="High Score", type="high_score", records=[])
            test_game = Game(name="Test Game", record_types=[score_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Mock user input: game 1, record type 1, today, description, no screenshot, score 12345.5
            user_inputs = ["1", "1", "", "New personal best", "", "12345.5"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True

            # Verify the score record
            loaded_data = RecordData.load(temp_filename)
            record = loaded_data.games[0].record_types[0].records[0]
            assert record.score == 12345.5
            assert record.description == "New personal best"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_time_parsing_edge_cases(self):
        """Test time parsing with various edge cases"""
        from miscore.record_data import RecordData

        # Test valid formats
        valid_cases = [
            ("0:00:01", timedelta(seconds=1)),
            ("23:59:59", timedelta(hours=23, minutes=59, seconds=59)),
            ("0:30", timedelta(minutes=0, seconds=30)),
            ("120:00", timedelta(minutes=120)),
            ("1h", timedelta(hours=1)),
            ("30m", timedelta(minutes=30)),
            ("45s", timedelta(seconds=45)),
            ("2h30m", timedelta(hours=2, minutes=30)),
            ("0", timedelta(seconds=0)),
        ]

        for time_str, expected in valid_cases:
            result = RecordData._parse_time_input(time_str)
            assert (
                result == expected
            ), f"Failed for {time_str}: expected {expected}, got {result}"

        # Test invalid formats
        invalid_cases = ["invalid", "abc", "", "1x2y3z"]

        for time_str in invalid_cases:
            with pytest.raises(ValueError):
                RecordData._parse_time_input(time_str)

    def test_user_cancellation_at_different_steps(self):
        """Test user cancellation at various steps"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data
            from miscore.record_data import RecordType

            test_rt = RecordType(name="Completion", type="completed", records=[])
            test_game = Game(name="Test Game", record_types=[test_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Test cancellation during game selection
            with patch("builtins.input", side_effect=["q"]):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )
            assert result is False

            # Test cancellation during record type selection
            with patch("builtins.input", side_effect=["1", "q"]):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )
            assert result is False

            # Test cancellation during date input
            with patch("builtins.input", side_effect=["1", "1", "q"]):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )
            assert result is False

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_screenshot_path_validation(self):
        """Test screenshot path validation relative to JSON file"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        # Create a test screenshot file in the same directory
        screenshot_path = "test_screenshot.png"
        full_screenshot_path = os.path.join(
            os.path.dirname(temp_filename), screenshot_path
        )

        try:
            # Create the screenshot file
            with open(full_screenshot_path, "w") as f:
                f.write("fake screenshot")

            # Create test data
            from miscore.record_data import RecordType

            test_rt = RecordType(name="Completion", type="completed", records=[])
            test_game = Game(name="Test Game", record_types=[test_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Mock user input with screenshot path
            user_inputs = ["1", "1", "", "", screenshot_path]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True

            # Verify the screenshot path was saved
            loaded_data = RecordData.load(temp_filename)
            record = loaded_data.games[0].record_types[0].records[0]
            assert record.screenshot.name == screenshot_path

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            if os.path.exists(full_screenshot_path):
                os.unlink(full_screenshot_path)

    def test_game_with_no_record_types(self):
        """Test handling game with no record types"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create game with no record types
            test_game = Game(name="Test Game")  # No record_types specified
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # User selects game 1, then it should fail because no record types
            user_inputs = ["1"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print"):
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )
            assert result is False

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_date_input_validation_errors(self):
        """Test date input validation with invalid formats"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data
            from miscore.record_data import RecordType

            test_rt = RecordType(name="Completion", type="completed", records=[])
            test_game = Game(name="Test Game", record_types=[test_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Test invalid date format followed by valid date
            user_inputs = ["1", "1", "invalid-date", "2024-13-40", "2024-01-01", "", ""]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print") as mock_print:
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True
            # Verify error messages were printed
            error_calls = [
                call
                for call in mock_print.call_args_list
                if any("Invalid date format" in str(arg) for arg in call[0])
            ]
            assert (
                len(error_calls) >= 2
            )  # Should have printed error messages for both invalid dates

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_score_input_validation_errors(self):
        """Test score input validation with invalid formats"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data with high_score record type
            from miscore.record_data import RecordType

            score_rt = RecordType(name="High Score", type="high_score", records=[])
            test_game = Game(name="Test Game", record_types=[score_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Test invalid score inputs followed by valid score
            user_inputs = ["1", "1", "", "", "", "not-a-number", "12.34.56", "12345"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print") as mock_print:
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True
            # Verify error messages were printed for invalid scores
            error_calls = [
                call
                for call in mock_print.call_args_list
                if any("Please enter a valid number" in str(arg) for arg in call[0])
            ]
            assert (
                len(error_calls) >= 2
            )  # Should have printed error messages for both invalid scores

            # Verify final score was saved correctly
            loaded_data = RecordData.load(temp_filename)
            record = loaded_data.games[0].record_types[0].records[0]
            assert record.score == 12345.0

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_time_input_validation_errors(self):
        """Test time input validation with invalid formats"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data with fastest_time record type
            from miscore.record_data import RecordType

            time_rt = RecordType(name="Speed Run", type="fastest_time", records=[])
            test_game = Game(name="Test Game", record_types=[time_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Test invalid time inputs followed by valid time
            user_inputs = [
                "1",
                "1",
                "",
                "",
                "",
                "invalid-time",
                "abc123",
                "12:XX:34",
                "1:30:45",
            ]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print") as mock_print:
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True
            # Verify error messages were printed for invalid times
            error_calls = [
                call
                for call in mock_print.call_args_list
                if any("Invalid time format" in str(arg) for arg in call[0])
            ]
            assert (
                len(error_calls) >= 3
            )  # Should have printed error messages for all invalid times

            # Verify final time was saved correctly
            loaded_data = RecordData.load(temp_filename)
            record = loaded_data.games[0].record_types[0].records[0]
            assert record.time == timedelta(hours=1, minutes=30, seconds=45)

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_difficulty_selection_edge_cases(self):
        """Test difficulty selection with invalid inputs"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data with completed_at_difficulty record type
            from miscore.record_data import RecordType

            diff_rt = RecordType(
                name="Difficulty Completion", type="completed_at_difficulty", records=[]
            )
            test_game = Game(
                name="Test Game",
                difficulties=["Easy", "Normal", "Hard"],
                record_types=[diff_rt],
            )
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Test invalid difficulty selections followed by valid selection
            user_inputs = ["1", "1", "", "", "", "invalid", "0", "4", "10", "2"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print") as mock_print:
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True
            # Verify error messages were printed for invalid selections
            error_calls = [
                call
                for call in mock_print.call_args_list
                if any(
                    "Please enter a number between 1 and 3" in str(arg)
                    or "Please enter a valid number" in str(arg)
                    for arg in call[0]
                )
            ]
            assert (
                len(error_calls) >= 4
            )  # Should have printed error messages for all invalid inputs

            # Verify correct difficulty was selected
            loaded_data = RecordData.load(temp_filename)
            record = loaded_data.games[0].record_types[0].records[0]
            assert record.difficulty == "Normal"

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_screenshot_path_nonexistent_file_handling(self):
        """Test screenshot path validation when file doesn't exist"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create test data
            from miscore.record_data import RecordType

            test_rt = RecordType(name="Completion", type="completed", records=[])
            test_game = Game(name="Test Game", record_types=[test_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Test with non-existent screenshot file - should fail due to Pydantic FilePath validation
            user_inputs = ["1", "1", "", "", "nonexistent_screenshot.png", "y"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print") as mock_print:
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            # Should fail because FilePath validation is strict
            assert result is False
            # Verify warning was displayed
            warning_calls = [
                call
                for call in mock_print.call_args_list
                if any(
                    "Warning: File" in str(arg) and "does not exist" in str(arg)
                    for arg in call[0]
                )
            ]
            assert len(warning_calls) >= 1

            # Verify error message was displayed
            error_calls = [
                call
                for call in mock_print.call_args_list
                if any("Error creating record" in str(arg) for arg in call[0])
            ]
            assert len(error_calls) >= 1

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_empty_required_fields_handling(self):
        """Test handling of empty input for required fields"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Test time record with empty time input
            from miscore.record_data import RecordType

            time_rt = RecordType(name="Speed Run", type="fastest_time", records=[])
            test_game = Game(name="Test Game", record_types=[time_rt])
            test_data = RecordData(games=[test_game])
            test_data.save(temp_filename)

            # Try empty time input followed by valid time
            user_inputs = ["1", "1", "", "", "", "", "", "1:30:45"]
            with patch("builtins.input", side_effect=user_inputs):
                with patch("builtins.print") as mock_print:
                    result = RecordData.add_record_to_file(
                        temp_filename, interactive=True
                    )

            assert result is True
            # Verify error message for empty required field
            error_calls = [
                call
                for call in mock_print.call_args_list
                if any(
                    "Time is required for time-based records" in str(arg)
                    for arg in call[0]
                )
            ]
            assert (
                len(error_calls) >= 2
            )  # Should have printed error messages for both empty inputs

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestInteractiveInputValidation:
    """Test coverage for interactive input validation errors"""

    def test_invalid_game_selection_out_of_range(self, monkeypatch, capsys):
        """Test game selection with out-of-range numbers (covers record_data.py:521-522)"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create file with multiple games
            games = [
                Game(name="Game 1", difficulties=[], record_types=[]),
                Game(name="Game 2", difficulties=[], record_types=[]),
            ]
            test_data = RecordData(games=games)
            test_data.save(temp_filename)

            # Mock input: try invalid numbers, then valid selection, then quit
            inputs = ["0", "3", "99", "q"]
            input_iter = iter(inputs)
            monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

            result = RecordData.add_record_to_file(temp_filename, interactive=True)
            assert result is False  # Should return False when user quits

            captured = capsys.readouterr()
            assert "Please enter a number between 1 and 2" in captured.out

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_invalid_game_selection_non_numeric(self, monkeypatch, capsys):
        """Test game selection with non-numeric input (covers record_data.py:523-524)"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create file with games
            games = [Game(name="Test Game", difficulties=[], record_types=[])]
            test_data = RecordData(games=games)
            test_data.save(temp_filename)

            # Mock input: try non-numeric inputs, then quit
            inputs = ["abc", "1.5", "!", "q"]
            input_iter = iter(inputs)
            monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

            result = RecordData.add_record_to_file(temp_filename, interactive=True)
            assert result is False

            captured = capsys.readouterr()
            assert "Please enter a valid number or 'q' to quit" in captured.out

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_invalid_record_type_selection_out_of_range(self, monkeypatch, capsys):
        """Test record type selection with out-of-range numbers (covers record_data.py:561-562)"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create game with multiple record types
            record_types = [
                RecordType(name="Type 1", type="completed", records=[]),
                RecordType(name="Type 2", type="completed", records=[]),
            ]
            games = [Game(name="Test Game", difficulties=[], record_types=record_types)]
            test_data = RecordData(games=games)
            test_data.save(temp_filename)

            # Mock input: select game 1, try invalid record type numbers, then quit
            inputs = ["1", "0", "3", "99", "q"]
            input_iter = iter(inputs)
            monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

            result = RecordData.add_record_to_file(temp_filename, interactive=True)
            assert result is False

            captured = capsys.readouterr()
            assert "Please enter a number between 1 and 2" in captured.out

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_invalid_record_type_selection_non_numeric(self, monkeypatch, capsys):
        """Test record type selection with non-numeric input (covers record_data.py:563-564)"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Create game with record types
            record_types = [RecordType(name="Test Type", type="completed", records=[])]
            games = [Game(name="Test Game", difficulties=[], record_types=record_types)]
            test_data = RecordData(games=games)
            test_data.save(temp_filename)

            # Mock input: select game 1, try non-numeric record type inputs, then quit
            inputs = ["1", "abc", "1.5", "!", "q"]
            input_iter = iter(inputs)
            monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

            result = RecordData.add_record_to_file(temp_filename, interactive=True)
            assert result is False

            captured = capsys.readouterr()
            assert "Please enter a valid number or 'q' to quit" in captured.out

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_file_loading_exception(self, monkeypatch, capsys):
        """Test exception handling during file loading (covers record_data.py:418-420)"""
        # Create an invalid JSON file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(b"invalid json content")

        try:
            result = RecordData.add_record_to_file(temp_filename, interactive=True)
            assert result is False

            captured = capsys.readouterr()
            assert "Error loading file:" in captured.out

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
