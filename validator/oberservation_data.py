from enum import Enum
from typing import List

from pydantic import BaseModel, root_validator, validator

MAX_PETAL_LENGTH_WIDTH_RATIO = 15
MIN_PETAL_LENGTH_WIDTH_RATIO = 2


class SpeciesEnum(str, Enum):
    setosa = "setosa"
    virginica = "virginica"
    versicolor = "versicolor"


class Observation(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    species: SpeciesEnum

    @validator("sepal_length")
    def sepal_length_larger_than_zero(cls, value):
        if value <= 0:
            raise ValueError(f"Sepal length {value} smaller than (or equal to) zero")
        return value

    @validator("sepal_width")
    def sepal_width_larger_than_zero(cls, value):
        if value <= 0:
            raise ValueError(f"Sepal width {value} smaller than (or equal to) zero")
        return value

    @validator("petal_length")
    def petal_length_larger_than_zero(cls, value):
        if value <= 0:
            raise ValueError(f"Petal length {value} smaller than (or equal to) zero")
        return value

    @validator("petal_width")
    def petal_width_larger_than_zero(cls, value):
        if value <= 0:
            raise ValueError(f"Petal width {value} smaller than (or equal to) zero")
        return value

    @root_validator
    def check_petal_length_width_ratio(cls, values):
        petal_length, petal_width = values.get("petal_length"), values.get(
            "petal_width"
        )

        if petal_length / petal_width > MAX_PETAL_LENGTH_WIDTH_RATIO:
            raise ValueError(
                f"Petal length width ratio to large (max: {MAX_PETAL_LENGTH_WIDTH_RATIO})"
            )

        if petal_length / petal_width < 2:
            raise ValueError(
                f"Petal length width ratio to small (min: {MIN_PETAL_LENGTH_WIDTH_RATIO})"
            )

        return values


class ObservationData(BaseModel):
    observations: List[Observation]
