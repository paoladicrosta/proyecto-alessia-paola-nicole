import flet as ft
import pandas as pd
from aircraft import Aircraft
from calculator import WeightBalanceCalculator

def main(page: ft.Page):
    
    page.title = "Calculadora Cessna 172 - Seguridad de Vuelo"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "adaptive"

    try:
        avion = Aircraft.load_from_json("data/cessna172.json")
        calc = WeightBalanceCalculator(avion)
    except Exception as e:
        page.add(ft.Text(f"Error crítico al cargar base de datos: {e}", color="red"))
        return

    inputs = {}
    for st in avion.stations:
        inputs[st['name']] = ft.TextField(
            label=f"Peso en {st['name']} (kg)", 
            value="0", 
            width=350
        )

    txt_fuel = ft.TextField(label="Combustible (Litros)", value="0", width=350)
    lbl_res = ft.Text(size=20, weight="bold")

    def calcular_vuelo(e):
        total_weight = 0
        total_moment = 0
        
        try:
            for st in avion.stations:
                valor = inputs[st['name']].value
               
                if not calc.es_numero_valido(valor):
                    raise ValueError(f"Dato inválido en {st['name']}. Ingrese un número.")
                
                peso = float(valor)
                total_weight += peso
                total_moment += calc.compute_moment(peso, st['arm'])

            if not calc.es_numero_valido(txt_fuel.value):
                raise ValueError("Cantidad de combustible inválida.")
            
            litros = float(txt_fuel.value)
            peso_fuel = litros * avion.fuel_density
            total_weight += peso_fuel
            total_moment += calc.compute_moment(peso_fuel, 48)

            cg = calc.compute_cg(total_moment, total_weight)
            es_seguro = calc.validate_cg(cg)
            peso_ok = total_weight <= avion.max_weight

            if es_seguro and peso_ok:
                lbl_res.value = f"SEGURO: CG {cg:.2f} in | Peso {total_weight:.2f} kg"
                lbl_res.color = "green"
            else:
                msg = "PELIGRO: "
                if not es_seguro: msg += "CG Fuera de Límites "
                if not peso_ok: msg += "Exceso de Peso"
                lbl_res.value = msg
                lbl_res.color = "red"

        except ValueError as err:
            lbl_res.value = str(err)
            lbl_res.color = "orange"
        
        page.update()

    def descargar_excel(e):
        try:
            datos_vuelo = {
                "Concepto": ["Peso Total", "Centro de Gravedad", "Resultado"],
                "Valor": [
                    lbl_res.value.split('|')[-1] if '|' in lbl_res.value else "N/A",
                    lbl_res.value.split('|')[0] if '|' in lbl_res.value else "N/A",
                    "Vuelo Seguro" if lbl_res.color == "green" else "Vuelo No Seguro"
                ]
            }
            df = pd.DataFrame(datos_vuelo)
            df.to_excel("reporte_vuelo_cessna.xlsx", index=False)
            
            page.snack_bar = ft.SnackBar(ft.Text("¡Reporte Excel generado correctamente!"))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al generar Excel: {ex}"))
            page.snack_bar.open = True
        
        page.update()

    page.add(
        ft.Column([
            ft.Text("Calculadora Cessna 172", size=32, weight="bold"),
            ft.Text("Desarrollado por: Paola, Alessia y Nicole", italic=True),
            ft.Divider(),
            *list(inputs.values()),
            txt_fuel,
            ft.Row([
                ft.ElevatedButton("Calcular Balance", on_click=calcular_vuelo, icon=ft.icons.CALCULATE),
                ft.ElevatedButton("Exportar Excel", on_click=descargar_excel, icon=ft.icons.FILE_DOWNLOAD),
            ]),
            lbl_res
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)