import json
import os
from datetime import datetime, timedelta, date
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, root_validator, Extra, FilePath


class CompletedRecordEntry(BaseModel, extra=Extra.forbid):
    """
    Model for tracking when you completed the game (without anything more)
    """

    date: Union[date, datetime]
    description: Optional[str]
    screenshot: Optional[FilePath]


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
    description: Optional[str]
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
    ]

    @root_validator()
    def check_record_entry_types(cls, values):
        """
        Ensure all entries match the record type.
        """
        records = values.get("records", [])

        if values.get("type") == "completed":
            for r in records:
                assert isinstance(r, CompletedRecordEntry)
        elif values.get("type") == "completed_at_difficulty":
            for r in records:
                assert isinstance(r, CompletedAtDifficultyRecordEntry)
        elif values.get("type") in ["fastest_time", "longest_time"]:
            for r in records:
                assert isinstance(r, TimeRecordEntry)
        elif values.get("type") in ["high_score", "low_score"]:
            for r in records:
                assert isinstance(r, ScoreRecordEntry)

        return values


class Game(BaseModel):
    """
    Model containing all data for a single game
    """

    name: str
    difficulties: Optional[List[str]]
    record_types: Optional[List[RecordType]]

    @root_validator()
    def check_record_entry_difficulty(cls, values):
        """
        For record where a difficulty needs to be entered, that difficulty needs to be a valid option in this model.
        """
        difficulties = values.get("difficulties", None)

        if difficulties is not None:
            record_types = values.get("record_types", [])
            for rt in record_types:
                if rt.type == "completed_at_difficulty":
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


