class WeightBalanceCalculator:
    def __init__(self, aircraft):
        self.aircraft = aircraft

    def es_numero_valido(self, valor):
        try:
            if valor is None or str(valor).strip() == "":
                return False
            n = float(valor)
            return n >= 0
        except ValueError:
            return False

    def compute_moment(self, weight, arm):
        return float(weight) * float(arm)

    def compute_cg(self, total_moment, total_weight):
        if total_weight == 0:
            return 0
        return total_moment / total_weight

    def validate_cg(self, cg):
        limits = self.aircraft.cg_limits
        return limits["forward"] <= cg <= limits["aft"]