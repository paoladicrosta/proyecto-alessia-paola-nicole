from aircraft import Aircraft
from calculator import WeightBalanceCalculator

def main():
    aircraft = Aircraft.load_from_json("data/cessna172.json")
    calc = WeightBalanceCalculator(aircraft)

    print("\n=== Calculadora de Peso y Balance – Cessna 172 ===\n")

    total_weight = 0
    total_moment = 0

    for station in aircraft.stations:
        w = float(input(f"Ingrese peso en '{station['name']}': "))
        moment = calc.compute_moment(w, station["arm"])

        total_weight += w
        total_moment += moment

    fuel_liters = float(input("Ingrese litros de combustible: "))
    fuel_weight = fuel_liters * aircraft.fuel_density
    fuel_moment = calc.compute_moment(fuel_weight, 48)

    total_weight += fuel_weight
    total_moment += fuel_moment

    cg = calc.compute_cg(total_moment, total_weight)

    print("\n--- Resultados ---")
    print(f"Peso total: {total_weight:.2f} kg")
    print(f"Momento total: {total_moment:.2f}")
    print(f"Centro de Gravedad (CG): {cg:.2f} in")

    if calc.validate_cg(cg):
        print("El avión está dentro de los límites de seguridad.")
    else:
        print("PELIGRO: el CG está fuera de los límites.")

if __name__ == "__main__":
    main()
