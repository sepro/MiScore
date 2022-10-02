from miscore import RecordData
import pytest


def test_successful_load():
    """
    This will load the golden standard dataset (which should work) and perform a few additional checks to ensure data
    was included correctly.
    """
    record_data = RecordData.load("./tests/data/records.json")
    assert len(record_data.games) > 0


def test_failed_load():
    with pytest.raises(Exception):
        _ = RecordData.load("./tests/data/invalid.json")
