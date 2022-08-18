from validator.oberservation_data import ObservationData
import json


def test_on_working_data():
    """
    This will load the golden standard dataset (which should work) and perform a few additional checks to ensure data
    was included correctly.
    """
    with open("./tests/data/iris.json") as fin:
        iris_data = json.load(fin)

    observation_data = ObservationData(**iris_data)

    assert len(observation_data.observations) == 150
