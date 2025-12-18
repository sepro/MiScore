import json
import os
import re
from datetime import datetime, timedelta, date
from enum import Enum
from typing import List, Optional, Union, Literal, Annotated

from pydantic import model_validator, BaseModel, FilePath, Field, Discriminator


class CompletedRecordEntry(BaseModel, extra="forbid"):
    """
    Model for tracking when you completed the game (without anything more)
    """

    entry_type: Literal["completed"] = Field(default="completed", frozen=True)
    date: Union[date, datetime]
    description: Optional[str] = None
    screenshot: Optional[FilePath] = None


class CompletedAtDifficultyRecordEntry(CompletedRecordEntry):
    """
    Model for tracking when you completed the game at a specific difficulty
    """

    entry_type: Literal["completed_at_difficulty"] = Field(
        default="completed_at_difficulty", frozen=True
    )
    difficulty: str


class TimeRecordEntry(CompletedRecordEntry):
    """
    Model for tracking when you completed the game in a record time
    """

    entry_type: Literal["time"] = Field(default="time", frozen=True)
    time: timedelta


class ScoreRecordEntry(CompletedRecordEntry):
    """
    Model for tracking when you completed the game with a record score
    """

    entry_type: Literal["score"] = Field(default="score", frozen=True)
    score: float


class RecordTypeOptions(str, Enum):
    completed = "completed"
    completed_at_difficulty = "completed_at_difficulty"
    fastest_time = "fastest_time"
    longest_time = "longest_time"
    high_score = "high_score"
    low_score = "low_score"


class RecordType(BaseModel):
    """
    Model that contains the description and all entries for a certain record type (e.g. speedruns are one,
    completed, ...)
    """

    name: str
    description: Optional[str] = None
    type: RecordTypeOptions
    records: Optional[
        List[
            Annotated[
                Union[
                    CompletedAtDifficultyRecordEntry,
                    TimeRecordEntry,
                    ScoreRecordEntry,
                    CompletedRecordEntry,
                ],
                Discriminator("entry_type"),
            ]
        ]
    ] = None

    @model_validator(mode="after")
    @classmethod
    def check_record_entry_types(cls, values):
        """
        Ensure all entries match the record type.
        """
        records = values.records

        if values.type == "completed":
            for r in records:
                assert isinstance(r, CompletedRecordEntry)
        elif values.type == "completed_at_difficulty":
            for r in records:
                assert isinstance(r, CompletedAtDifficultyRecordEntry)
        elif values.type in ["fastest_time", "longest_time"]:
            for r in records:
                assert isinstance(r, TimeRecordEntry)
        elif values.type in ["high_score", "low_score"]:
            for r in records:
                assert isinstance(r, ScoreRecordEntry)

        return values


class Game(BaseModel):
    """
    Model containing all data for a single game
    """

    name: str
    difficulties: Optional[List[str]] = None
    record_types: Optional[List[RecordType]] = None

    @model_validator(mode="after")
    @classmethod
    def check_record_entry_difficulty(cls, values):
        """
        For record where a difficulty needs to be entered, that difficulty needs to be a valid option in this model.
        """
        difficulties = values.difficulties

        if difficulties is not None and values.record_types is not None:
            record_types = values.record_types
            for rt in record_types:
                if rt.type == "completed_at_difficulty":
                    if rt.records is not None:
                        for entry in rt.records:
                            assert entry.difficulty in difficulties
        return values


class RecordData(BaseModel):
    """
    Top Level Model that will contain all games (each with their own records)
    """

    games: List[Game]

    @classmethod
    def _preprocess_json_data(cls, json_data):
        """
        Preprocess JSON data to:
        1. Normalize path separators (backslash to forward slash) for cross-platform compatibility
        2. Add entry_type field to records based on RecordType.type for discriminated unions
        """
        if "games" not in json_data:
            return json_data

        for game in json_data["games"]:
            if "record_types" not in game or game["record_types"] is None:
                continue

            for record_type in game["record_types"]:
                if "records" not in record_type or not record_type["records"]:
                    continue

                # Determine the entry_type based on record_type.type
                record_type_value = record_type.get("type")
                if record_type_value == "completed":
                    entry_type = "completed"
                elif record_type_value == "completed_at_difficulty":
                    entry_type = "completed_at_difficulty"
                elif record_type_value in ["fastest_time", "longest_time"]:
                    entry_type = "time"
                elif record_type_value in ["high_score", "low_score"]:
                    entry_type = "score"
                else:
                    continue

                # Process each record
                for record in record_type["records"]:
                    # Add entry_type if not present
                    if "entry_type" not in record:
                        record["entry_type"] = entry_type

                    # Normalize screenshot path separators
                    if "screenshot" in record and record["screenshot"]:
                        record["screenshot"] = record["screenshot"].replace("\\", "/")

        return json_data

    @classmethod
    def load(cls, filename):
        """
        Will load records from a JSON file.

        For the FilePath validator to work with relative paths, the working directory needs to be set to the loaded
        file. Before the end of the function the working directory is set back to the original.
        """
        old_wd = os.getcwd()
        # Convert to absolute path to ensure proper directory handling
        abs_filename = os.path.abspath(filename)
        current_directory = os.path.dirname(abs_filename)
        current_file = os.path.basename(abs_filename)

        # Change to the directory containing the JSON file
        os.chdir(current_directory)

        with open(current_file) as fin:
            json_data = json.load(fin)

        # Preprocess JSON data for cross-platform compatibility and discriminated unions
        json_data = cls._preprocess_json_data(json_data)

        record_data = RecordData(**json_data)

        # Restore original directory
        os.chdir(old_wd)

        return record_data

    @classmethod
    def _normalize_paths_for_save(cls, data):
        """
        Normalize all path separators to forward slashes (Unix-style) for cross-platform compatibility.
        This ensures that even on Windows, paths are saved with forward slashes.
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == "screenshot" and isinstance(value, str):
                    # Normalize screenshot paths to Unix-style
                    result[key] = value.replace("\\", "/")
                else:
                    result[key] = cls._normalize_paths_for_save(value)
            return result
        elif isinstance(data, list):
            return [cls._normalize_paths_for_save(item) for item in data]
        else:
            return data

    def save(self, filename):
        """
        Save records to a JSON file with Unix-style path separators.
        """
        data = self.model_dump()
        # Normalize all paths to Unix-style (forward slashes)
        data = self._normalize_paths_for_save(data)
        with open(filename, "w") as fout:
            json.dump(data, fout, indent=2, default=str)

    @classmethod
    def add_game_to_file(cls, game_name, filename, interactive=True):
        """
        Add a new game to a JSON file, or create the file if it doesn't exist.
        Validates the data before writing to avoid corruption.
        Returns True if game was added, False if game already exists.
        """
        # Check if file exists and load existing data
        if os.path.exists(filename):
            record_data = cls.load(filename)

            # Check if game already exists
            for game in record_data.games:
                if game.name == game_name:
                    return False

            # Create new game with optional interactive setup
            new_game = (
                cls._create_game_interactive(game_name)
                if interactive
                else Game(name=game_name)
            )
            record_data.games.append(new_game)
        else:
            # Create new data structure with the game
            new_game = (
                cls._create_game_interactive(game_name)
                if interactive
                else Game(name=game_name)
            )
            record_data = RecordData(games=[new_game])

        # Validate the new data structure before saving
        # This will raise an exception if invalid, preventing file corruption
        validated_data = RecordData(**record_data.model_dump())

        # Only save if validation passes
        validated_data.save(filename)

        return True

    @classmethod
    def _create_game_interactive(cls, game_name):
        """
        Create a game with interactive prompts for difficulty levels and record types.
        """
        print(f"\n📋 Setting up '{game_name}'")
        print("=" * (len(game_name) + 15))

        # Ask if the game has difficulty levels
        while True:
            has_difficulties = (
                input("\n❓ Does this game have difficulty levels? (y/n): ")
                .strip()
                .lower()
            )
            if has_difficulties in ["y", "yes"]:
                difficulties = cls._get_difficulty_levels()
                break
            elif has_difficulties in ["n", "no"]:
                difficulties = None
                break
            else:
                print("⚠️  Please enter 'y' for yes or 'n' for no.")

        # Ask if the user wants to add record types
        while True:
            has_record_types = (
                input("\n❓ Do you want to add record types? (y/n): ").strip().lower()
            )
            if has_record_types in ["y", "yes"]:
                record_types = cls._get_record_types(difficulties)
                break
            elif has_record_types in ["n", "no"]:
                record_types = None
                break
            else:
                print("⚠️  Please enter 'y' for yes or 'n' for no.")

        return Game(
            name=game_name, difficulties=difficulties, record_types=record_types
        )

    @classmethod
    def _get_difficulty_levels(cls):
        """
        Interactive prompt to collect difficulty levels from the user.
        """
        print("\n🎯 Enter difficulty levels (one per line)")
        print("   Press Enter with empty input to finish")
        print("   Examples: Easy, Normal, Hard, Nightmare")

        difficulties = []
        while True:
            print(
                f"\n   Current difficulties: {difficulties if difficulties else 'None yet'}"
            )
            difficulty = input("   Enter difficulty level: ").strip()

            if not difficulty:
                if difficulties:
                    break
                else:
                    print(
                        "   ⚠️  No difficulties added. Press Enter again to skip difficulties."
                    )
                    empty_again = input("   Enter difficulty level: ").strip()
                    if not empty_again:
                        return None
                    else:
                        difficulties.append(empty_again)
                        print(f"   ✅ Added '{empty_again}'")
            elif difficulty in difficulties:
                print(
                    f"   ⚠️  '{difficulty}' is already added. Please enter a different one."
                )
                continue
            else:
                difficulties.append(difficulty)
                print(f"   ✅ Added '{difficulty}'")

        print(f"\n✨ Final difficulty levels: {', '.join(difficulties)}")
        return difficulties

    @classmethod
    def _get_record_types(cls, difficulties):
        """
        Interactive prompt to collect record types from the user.
        """
        print("\n🏆 Setting up record types")
        print("   Available record types:")
        print("   1. completed - Track when you completed the game")
        print(
            "   2. completed_at_difficulty - Track completions at specific difficulties"
        )
        print("   3. fastest_time - Track your best speed runs")
        print("   4. longest_time - Track your longest playthroughs")
        print("   5. high_score - Track your highest scores")
        print("   6. low_score - Track your lowest scores (for golf-style games)")
        print("\n   Press Enter with empty input to finish adding record types")

        record_types = []
        available_types = {
            "1": "completed",
            "2": "completed_at_difficulty",
            "3": "fastest_time",
            "4": "longest_time",
            "5": "high_score",
            "6": "low_score",
        }

        used_types = set()

        while True:
            print(
                f"\n   Current record types: {[rt.name for rt in record_types] if record_types else 'None yet'}"
            )
            choice = input("   Enter record type number (1-6): ").strip()

            if not choice:
                if record_types:
                    break
                else:
                    print(
                        "   ⚠️  No record types added. Press Enter again to skip record types."
                    )
                    empty_again = input("   Enter record type number (1-6): ").strip()
                    if not empty_again:
                        return None
                    else:
                        choice = empty_again

            if choice not in available_types:
                print("   ⚠️  Please enter a number between 1-6.")
                continue

            record_type_key = available_types[choice]

            if record_type_key in used_types:
                print(f"   ⚠️  Record type '{record_type_key}' is already added.")
                continue

            # Validate difficulty requirement
            if record_type_key == "completed_at_difficulty" and not difficulties:
                print(
                    "   ⚠️  'completed_at_difficulty' requires the game to have difficulty levels."
                )
                continue

            used_types.add(record_type_key)

            # Get name and description for the record type
            name = cls._get_record_type_name(record_type_key)
            description = cls._get_record_type_description()

            record_type = RecordType(
                name=name, description=description, type=record_type_key, records=[]
            )

            record_types.append(record_type)
            print(f"   ✅ Added '{name}' ({record_type_key})")

        print(
            f"\n✨ Final record types: {[f'{rt.name} ({rt.type})' for rt in record_types]}"
        )
        return record_types

    @classmethod
    def _get_record_type_name(cls, record_type_key):
        """
        Get a custom name for the record type.
        """
        default_names = {
            "completed": "Game Completion",
            "completed_at_difficulty": "Difficulty Completion",
            "fastest_time": "Speed Run",
            "longest_time": "Marathon Run",
            "high_score": "High Score",
            "low_score": "Low Score",
        }

        default_name = default_names.get(
            record_type_key, record_type_key.replace("_", " ").title()
        )
        name = input(
            f"   📝 Enter name for this record type (default: {default_name}): "
        ).strip()

        return name if name else default_name

    @classmethod
    def _get_record_type_description(cls):
        """
        Get an optional description for the record type.
        """
        description = input("   📄 Enter description (optional): ").strip()
        return description if description else None

    @classmethod
    def add_record_to_file(cls, filename, interactive=True):
        """
        Add a new record entry to a game in the JSON file.
        Returns True if record was added, False if cancelled/failed.
        """
        if not os.path.exists(filename):
            print(
                f"❌ File '{filename}' does not exist. Please create it first using 'add-game'."
            )
            return False

        try:
            record_data = cls.load(filename)
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False

        if not record_data.games:
            print(
                "❌ No games found in the file. Please add a game first using 'add-game'."
            )
            return False

        if not interactive:
            print("❌ Non-interactive mode not yet implemented for add-record.")
            return False

        print(f"\n🎮 Adding record to '{filename}'")
        print("=" * (len(filename) + 20))

        # Step 1: Select game
        selected_game = cls._select_game_interactive(record_data.games)
        if not selected_game:
            return False

        # Step 2: Select record type
        if not selected_game.record_types:
            print(f"\n❌ Game '{selected_game.name}' has no record types configured.")
            print(
                "   Please add record types first using 'add-game' in interactive mode."
            )
            return False

        selected_record_type = cls._select_record_type_interactive(selected_game)
        if not selected_record_type:
            return False

        # Step 3: Collect record details
        record_details = cls._collect_record_details_interactive(
            selected_record_type, selected_game, filename
        )
        if not record_details:
            return False

        # Step 4: Create and add the record (maintain working directory context for FilePath validation)
        old_wd = os.getcwd()
        current_directory = os.path.dirname(os.path.abspath(filename))
        if current_directory:
            os.chdir(current_directory)

        try:
            new_record = cls._create_record_entry(
                selected_record_type.type.value, record_details
            )

            # Add the record to the selected record type
            if selected_record_type.records is None:
                selected_record_type.records = []
            selected_record_type.records.append(new_record)

            # Validate and save
            validated_data = RecordData(**record_data.model_dump())
            validated_data.save(
                os.path.basename(filename) if current_directory else filename
            )

            print(
                f"\n✅ Record added successfully to '{selected_game.name}' - '{selected_record_type.name}'!"
            )
            return True

        except Exception as e:
            print(f"\n❌ Error creating record: {e}")
            return False
        finally:
            if current_directory:
                os.chdir(old_wd)

    @classmethod
    def _select_game_interactive(cls, games):
        """Present game selection interface"""
        print(f"\n🎯 Select a game ({len(games)} available):")
        for i, game in enumerate(games, 1):
            record_count = sum(
                len(rt.records or []) for rt in (game.record_types or [])
            )
            print(f"   {i}. {game.name} ({record_count} records)")

        while True:
            try:
                choice = (
                    input(f"\nEnter game number (1-{len(games)}) or 'q' to quit: ")
                    .strip()
                    .lower()
                )

                if choice == "q":
                    print("Cancelled by user.")
                    return None

                game_index = int(choice) - 1
                if 0 <= game_index < len(games):
                    selected_game = games[game_index]
                    print(f"✅ Selected: {selected_game.name}")
                    return selected_game
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(games)}")

            except ValueError:
                print("⚠️  Please enter a valid number or 'q' to quit")

    @classmethod
    def _select_record_type_interactive(cls, game):
        """Present record type selection interface"""
        record_types = game.record_types
        print(
            f"\n🏆 Select record type for '{game.name}' ({len(record_types)} available):"
        )

        for i, rt in enumerate(record_types, 1):
            record_count = len(rt.records or [])
            description = f" - {rt.description}" if rt.description else ""
            print(
                f"   {i}. {rt.name} ({rt.type.value}){description} [{record_count} records]"
            )

        while True:
            try:
                choice = (
                    input(
                        f"\nEnter record type number (1-{len(record_types)}) or 'q' to quit: "
                    )
                    .strip()
                    .lower()
                )

                if choice == "q":
                    print("Cancelled by user.")
                    return None

                rt_index = int(choice) - 1
                if 0 <= rt_index < len(record_types):
                    selected_rt = record_types[rt_index]
                    print(f"✅ Selected: {selected_rt.name} ({selected_rt.type.value})")
                    return selected_rt
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(record_types)}")

            except ValueError:
                print("⚠️  Please enter a valid number or 'q' to quit")

    @classmethod
    def _collect_record_details_interactive(cls, record_type, game, filename):
        """Collect record details based on record type"""
        details = {}

        print(f"\n📝 Enter details for '{record_type.name}' record:")

        # Get date (all record types)
        details["date"] = cls._get_date_input()
        if details["date"] is None:
            return None

        # Get description (optional for all)
        details["description"] = cls._get_optional_description()

        # Get screenshot (optional for all)
        details["screenshot"] = cls._get_optional_screenshot(filename)

        # Get type-specific fields
        if record_type.type == "completed_at_difficulty":
            details["difficulty"] = cls._get_difficulty_input(game)
            if details["difficulty"] is None:
                return None
        elif record_type.type in ["fastest_time", "longest_time"]:
            details["time"] = cls._get_time_input(record_type.type)
            if details["time"] is None:
                return None
        elif record_type.type in ["high_score", "low_score"]:
            details["score"] = cls._get_score_input(record_type.type)
            if details["score"] is None:
                return None

        return details

    @classmethod
    def _create_record_entry(cls, record_type, details):
        """Create appropriate record entry model"""
        base_data = {
            "date": details["date"],
            "description": details.get("description"),
            "screenshot": details.get("screenshot"),
        }

        if record_type == "completed":
            return CompletedRecordEntry(**base_data)
        elif record_type == "completed_at_difficulty":
            return CompletedAtDifficultyRecordEntry(
                **base_data, difficulty=details["difficulty"]
            )
        elif record_type in ["fastest_time", "longest_time"]:
            return TimeRecordEntry(**base_data, time=details["time"])
        elif record_type in ["high_score", "low_score"]:
            return ScoreRecordEntry(**base_data, score=details["score"])
        else:
            raise ValueError(f"Unknown record type: {record_type}")

    @classmethod
    def _get_date_input(cls):
        """Get date input from user with smart defaults"""
        today = date.today().strftime("%Y-%m-%d")
        print(f"📅 Date (default: {today}, format: YYYY-MM-DD):")

        while True:
            date_input = input("   Enter date or press Enter for today: ").strip()

            if not date_input:
                return date.today()

            if date_input.lower() == "q":
                return None

            # Try to parse the date
            try:
                parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()
                return parsed_date
            except ValueError:
                print(
                    "   ⚠️  Invalid date format. Please use YYYY-MM-DD or press Enter for today"
                )

    @classmethod
    def _get_optional_description(cls):
        """Get optional description"""
        description = input("📝 Description (optional): ").strip()
        return description if description else None

    @classmethod
    def _get_optional_screenshot(cls, json_filename):
        """Get optional screenshot path (relative to JSON file)"""
        screenshot_path = input(
            "📸 Screenshot path (optional, relative to JSON file): "
        ).strip()

        if not screenshot_path:
            return None

        # Check if file exists relative to JSON file directory
        json_dir = os.path.dirname(os.path.abspath(json_filename))
        full_path = os.path.join(json_dir, screenshot_path)

        if not os.path.exists(full_path):
            print(f"   ⚠️  Warning: File '{full_path}' does not exist")
            confirm = input("   Continue anyway? (y/n): ").strip().lower()
            if confirm not in ["y", "yes"]:
                return cls._get_optional_screenshot(json_filename)

        return screenshot_path

    @classmethod
    def _get_difficulty_input(cls, game):
        """Get difficulty selection for completed_at_difficulty records"""
        if not game.difficulties:
            print("❌ This game has no difficulty levels configured.")
            return None

        print(f"🎯 Select difficulty ({len(game.difficulties)} available):")
        for i, difficulty in enumerate(game.difficulties, 1):
            print(f"   {i}. {difficulty}")

        while True:
            try:
                choice = (
                    input(
                        f"Enter difficulty number (1-{len(game.difficulties)}) or 'q' to quit: "
                    )
                    .strip()
                    .lower()
                )

                if choice == "q":
                    return None

                diff_index = int(choice) - 1
                if 0 <= diff_index < len(game.difficulties):
                    selected_difficulty = game.difficulties[diff_index]
                    print(f"✅ Selected difficulty: {selected_difficulty}")
                    return selected_difficulty
                else:
                    print(
                        f"⚠️  Please enter a number between 1 and {len(game.difficulties)}"
                    )

            except ValueError:
                print("⚠️  Please enter a valid number or 'q' to quit")

    @classmethod
    def _get_time_input(cls, record_type):
        """Get time input with flexible format parsing"""
        type_name = "fastest" if record_type == "fastest_time" else "longest"
        print(f"⏱️  Enter {type_name} time:")
        print("   Formats: HH:MM:SS, MM:SS, 1h30m45s, 90m, 5400s")

        while True:
            time_input = input("   Time: ").strip()

            if time_input.lower() == "q":
                return None

            if not time_input:
                print("   ⚠️  Time is required for time-based records")
                continue

            try:
                parsed_time = cls._parse_time_input(time_input)
                # Format back to HH:MM:SS for display
                total_seconds = int(parsed_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                print(f"✅ Parsed time: {formatted_time}")
                return parsed_time
            except ValueError as e:
                print(f"   ⚠️  {e}")

    @classmethod
    def _parse_time_input(cls, time_input):
        """Parse various time input formats to timedelta"""
        time_input = time_input.strip()

        # Try HH:MM:SS format
        if re.match(r"^\d{1,2}:\d{2}:\d{2}$", time_input):
            parts = time_input.split(":")
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # Try MM:SS format
        if re.match(r"^\d{1,3}:\d{2}$", time_input):
            parts = time_input.split(":")
            minutes, seconds = int(parts[0]), int(parts[1])
            return timedelta(minutes=minutes, seconds=seconds)

        # Try human readable format (1h30m45s, 90m, 5400s)
        pattern = r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
        match = re.match(pattern + "$", time_input.lower())

        if match and any(match.groups()):
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            seconds = int(match.group(3)) if match.group(3) else 0
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # Try pure seconds
        if re.match(r"^\d+$", time_input):
            return timedelta(seconds=int(time_input))

        raise ValueError(
            f"Invalid time format: '{time_input}'. Use HH:MM:SS, MM:SS, 1h30m45s, 90m, or 5400s"
        )

    @classmethod
    def _get_score_input(cls, record_type):
        """Get score input (numeric)"""
        type_name = "highest" if record_type == "high_score" else "lowest"
        print(f"🎯 Enter {type_name} score (number):")

        while True:
            score_input = input("   Score: ").strip()

            if score_input.lower() == "q":
                return None

            if not score_input:
                print("   ⚠️  Score is required for score-based records")
                continue

            try:
                score = float(score_input)
                print(f"✅ Score: {score}")
                return score
            except ValueError:
                print("   ⚠️  Please enter a valid number")
