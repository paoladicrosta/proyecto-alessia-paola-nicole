import json

class Aircraft:
    def __init__(self, data):
        self.model = data["aircraftModel"]
        self.max_weight = data["maxWeightKg"]
        self.cg_limits = data["cgLimits"]
        self.stations = data["stations"]
        self.fuel_density = data["fuel"]["densityKgPerL"]

    @staticmethod
    def load_from_json(path):
        with open(path, "r") as f:
            data = json.load(f)
        return Aircraft(data)
