from validator import ObservationData, Observation
import json
import pytest


def test_on_working_data():
    """
    This will load the golden standard dataset (which should work) and perform a few additional checks to ensure data
    was included correctly.
    """
    with open("./tests/data/iris.json") as fin:
        iris_data = json.load(fin)

    observation_data = ObservationData(**iris_data)

    assert len(observation_data.observations) == 150


def test_observation_validation_errors():
    """
    This will load the Observation class with incorrect data and check if an error is correctly raised
    """
    # Missing field
    with pytest.raises(ValueError):
        _ = Observation(
            sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="setosa"
        )

    # Negative value for sepal length
    with pytest.raises(ValueError):
        _ = Observation(
            sepal_length=-1,
            sepal_width=3.5,
            petal_length=1.4,
            petal_width=0.2,
            species="setosa",
        )

    # Negative value for sepal width
    with pytest.raises(ValueError):
        _ = Observation(
            sepal_length=5.1,
            sepal_width=-1,
            petal_length=1.4,
            petal_width=0.2,
            species="setosa",
        )

    # Negative value for petal length
    with pytest.raises(ValueError):
        _ = Observation(
            sepal_length=5.1,
            sepal_width=3.5,
            petal_length=-1,
            petal_width=0.2,
            species="setosa",
        )

    # Negative value for petal width
    with pytest.raises(ValueError):
        _ = Observation(
            sepal_length=5.1,
            sepal_width=3.5,
            petal_length=1.4,
            petal_width=-1,
            species="setosa",
        )

    # Impossible petal length/width (too large)
    with pytest.raises(ValueError):
        _ = Observation(
            sepal_length=5.1,
            sepal_width=3.5,
            petal_length=14,
            petal_width=0.2,
            species="setosa",
        )

    # Impossible petal length/width (too small)
    with pytest.raises(ValueError):
        _ = Observation(
            sepal_length=5.1,
            sepal_width=3.5,
            petal_length=1.4,
            petal_width=2,
            species="setosa",
        )
