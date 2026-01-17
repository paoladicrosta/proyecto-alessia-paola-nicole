import json

class Aircraft:
    def __init__(self, data):
        self.model = data["aircraftModel"]
        self.max_weight = data["maxWeightLb"]
        self.taxi_weight = data["taxiDeduction"]["weight"]
        self.taxi_moment = data["taxiDeduction"]["moment"]
        self.stations = data["stations"]

    @staticmethod
    def load_from_json(path):
        with open(path, "r") as f:
            data = json.load(f)
        return Aircraft(data)

    @staticmethod
    def kg_to_lb(kg):
        return kg * 2.20462