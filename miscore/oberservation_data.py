from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, root_validator, validator


class Game(BaseModel):
    name: str
    difficulties: Optional[List[str]]


class RecordData(BaseModel):
    games: List[Game]
