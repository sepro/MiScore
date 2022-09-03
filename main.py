from miscore import RecordData
import json

with open("./tests/data/records.json") as f:
    data = json.load(f)

record_data = RecordData(**data)
