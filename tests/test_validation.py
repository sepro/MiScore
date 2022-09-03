import json
from miscore import RecordData


def test_on_working_data():
    """
    This will load the golden standard dataset (which should work) and perform a few additional checks to ensure data
    was included correctly.
    """
    with open("./tests/data/records.json") as fin:
        game_data = json.load(fin)

    record_data = RecordData(**game_data)

    assert len(record_data.games) > 0
