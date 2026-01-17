class WBCalculator:
    def __init__(self, aircraft):
        self.aircraft = aircraft

    def calculate_detailed_wb(self, bew, bew_moment, inputs_lb):
        results = {"lines": [], "totals": {}}
        
        cw, cm = bew, bew_moment
        results["lines"].append(["Basic Empty Weight", cw, cm])

        p_w, p_m = 0, 0
        for i, st in enumerate(self.aircraft.stations):
            if st["type"] == "payload":
                w = inputs_lb[i]
                m = w * st["arm"]
                results["lines"].append([st["name"], w, m])
                p_w += w
                p_m += m
        
        zfw_w, zfw_m = cw + p_w, cm + p_m
        results["lines"].append(["--- Zero Fuel Weight ---", zfw_w, zfw_m])
        results["totals"]["zfw"] = (zfw_w, zfw_m)

        f_w, f_m = 0, 0
        for i, st in enumerate(self.aircraft.stations):
            if st["type"] == "fuel":
                w = inputs_lb[i]
                m = w * st["arm"]
                results["lines"].append([st["name"], w, m])
                f_w += w
                f_m += m

        rw, rm = zfw_w + f_w, zfw_m + f_m
        results["lines"].append(["--- Ramp Weight ---", rw, rm])
        
        tw, tm = self.aircraft.taxi_weight, self.aircraft.taxi_moment
        results["lines"].append(["Start/Taxi/Run-up", tw, tm])

        tow_w, tow_m = rw + tw, rm + tm
        tow_cg = tow_m / tow_w if tow_w > 0 else 0
        
        results["lines"].append(["=== TAKE OFF WEIGHT ===", tow_w, tow_m])
        results["totals"]["tow"] = (tow_w, tow_m, tow_cg)
        return results

    def check_safety(self, weight, cg):
        aft_limit = 47.3
        fwd_limit = 35.0 if weight <= 1950 else 35.0 + (0.01 * (weight - 1950))
        is_safe = (weight <= self.aircraft.max_weight) and (fwd_limit <= cg <= aft_limit)
        return is_safe, fwd_limit