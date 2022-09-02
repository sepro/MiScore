import json
from miscore import RecordData


def test_on_working_data():
    """
    This will load the golden standard dataset (which should work) and perform a few additional checks to ensure data
    was included correctly.
    """
    with open("./tests/data/records.json") as fin:
        iris_data = json.load(fin)

    observation_data = RecordData(**iris_data)

    assert len(observation_data.games) > 0
