from validator.oberservation_data import ObservationData
import json


with open("./tests/data/iris.json") as fin:
    iris_data = json.load(fin)

observation_data = ObservationData(**iris_data)

print(
    max([obs.petal_length / obs.petal_width for obs in observation_data.observations])
)
print(
    min([obs.petal_length / obs.petal_width for obs in observation_data.observations])
)


invalid_input = {
    "observations": [
        {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
            "species": "setosao",
        }
    ]
}

try:
    observation_data = ObservationData(**invalid_input)
except Exception as e:
    print(e)

invalid_input = {
    "observations": [
        {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 14,
            "petal_width": 0.2,
            "species": "setosa",
        }
    ]
}

try:
    observation_data = ObservationData(**invalid_input)
except Exception as e:
    print(e)
