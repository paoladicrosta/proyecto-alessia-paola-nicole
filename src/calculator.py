class WeightBalanceCalculator:

    def __init__(self, aircraft):
        self.aircraft = aircraft

    def compute_moment(self, weight, arm):
        return weight * arm

    def compute_cg(self, total_moment, total_weight):
        return total_moment / total_weight

    def validate_cg(self, cg):
        return self.aircraft.cg_limits["forward"] <= cg <= self.aircraft.cg_limits["aft"]
