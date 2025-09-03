import json
import os
from datetime import datetime, timedelta, date
from enum import Enum
from typing import List, Optional, Union

from pydantic import model_validator, BaseModel, FilePath


class CompletedRecordEntry(BaseModel, extra="forbid"):
    """
    Model for tracking when you completed the game (without anything more)
    """

    date: Union[date, datetime]
    description: Optional[str] = None
    screenshot: Optional[FilePath] = None


class CompletedAtDifficultyRecordEntry(CompletedRecordEntry):
    """
    Model for tracking when you completed the game at a specific difficulty
    """

    difficulty: str


class TimeRecordEntry(CompletedRecordEntry):
    """
    Model for tracking when you completed the game in a record time
    """

    time: timedelta


class ScoreRecordEntry(CompletedRecordEntry):
    """
    Model for tracking when you completed the game with a record score
    """

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
            Union[
                CompletedRecordEntry,
                CompletedAtDifficultyRecordEntry,
                TimeRecordEntry,
                ScoreRecordEntry,
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
    def load(cls, filename):
        """
        Will load records from a JSON file.

        For the FilePath validator to work with relative paths, the working directory needs to be set to the loaded
        file. Before the end of the function the working directory is set back to the original.
        """
        old_wd = os.getcwd()
        current_directory = os.path.dirname(filename)
        current_file = os.path.basename(filename)
        os.chdir(current_directory)

        with open(current_file) as fin:
            json_data = json.load(fin)

        record_data = RecordData(**json_data)

        os.chdir(old_wd)

        return record_data

    def save(self, filename):
        """
        Save records to a JSON file.
        """
        with open(filename, "w") as fout:
            json.dump(self.model_dump(), fout, indent=2, default=str)

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
        Create a game with interactive prompts for difficulty levels.
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

        return Game(name=game_name, difficulties=difficulties)

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
