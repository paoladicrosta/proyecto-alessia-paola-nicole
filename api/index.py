import flet as ft
import json
import os
from aircraft import Aircraft
from calculator import WBCalculator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime

def generate_pdf_report(filename, model, reg, results, status, limits_text):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_final = os.path.join(current_dir, "..", filename)
    
    c = canvas.Canvas(path_final, pagesize=letter)
    w_p, h_p = letter
    
    # 1. Recuadro exterior grueso
    c.setLineWidth(1.5)
    c.rect(45, h_p - 750, 520, 710) 
    
    # 2. Encabezado
    c.line(45, h_p - 90, 565, h_p - 90)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w_p/2, h_p - 75, f"Take Off Data Card {model}")
    c.line(45, h_p - 60, 565, h_p - 60)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(55, h_p - 110, "Weight & Balance")
    c.drawString(420, h_p - 110, f"N# {reg}")
    
    # 3. Encabezados de columna
    y = h_p - 140
    c.drawString(300, y, "Weight (lb)")
    c.drawString(450, y, "Moment/1000")
    
    # --- LÍNEAS VERTICALES (Divisores de columnas) ---
    c.setLineWidth(0.5)
    c.line(285, h_p - 120, 285, h_p - 650) # Línea entre Item y Weight
    c.line(440, h_p - 120, 440, h_p - 650) # Línea entre Weight y Moment
    
    y -= 30
    for line in results["lines"]:
        if line[0].startswith("-") or line[0].startswith("="):
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 10)
            
        c.drawString(55, y, f"{line[0]}")
        c.drawString(305, y, f"{line[1]:.2f}")
        
        if "Taxi" in line[0] or "Start" in line[0]:
            c.drawString(465, y, "-0.30")
        else:
            momento_reducido = line[2] / 1000
            c.drawString(465, y, f"{momento_reducido:.2f}")
        
        c.line(300, y-2, 400, y-2)
        c.line(460, y-2, 550, y-2)
        y -= 35

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    tow_cg = results['totals']['tow'][2]
    c.drawString(55, y, f"CG: {tow_cg:.2f} in")
    
    c.setFont("Helvetica", 10)
    c.drawString(55, y - 20, f"Límites: {limits_text}")

    c.save()

def main(page: ft.Page):
    page.title = "Cessna 172N W&B Calculator"
    page.theme_mode = ft.ThemeMode.DARK

    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "..", "data", "cessna172.json")

    try:
        avion = Aircraft.load_from_json(json_path)
        calc = WBCalculator(avion)
        with open(json_path, "r") as f:
            bag_lim = json.load(f).get("baggageLimits", {})
    except Exception as e:
        page.add(ft.Text(f"Error: {e}", color="red"))
        return

    # CAMPOS VACÍOS (Sin el parámetro 'value')
    reg_field = ft.TextField(label="Matrícula",value="YV-", width=150,)
    bew_field = ft.TextField(label="BEW (Lb)", hint_text="0", width=150)
    mom_field = ft.TextField(label="Moment (Total)", hint_text="0", width=150)
    
    fields, units = [], []
    for st in avion.stations:
        f_in = ft.TextField(label=st["name"], width=200, hint_text="0")
        u_in = ft.Dropdown(options=[ft.dropdown.Option("Lb"), ft.dropdown.Option("Kg")], 
                          value="Lb", width=80) if st["type"] == "payload" else None
        fields.append(f_in)
        units.append(u_in)

    res_col = ft.Column()
    state = {"res": None, "safe": None, "lim": None, "reg": ""}

    def on_calc(e):
        res_col.controls.clear()
        try:
            b_w = float(bew_field.value or 0)
            b_m = float(mom_field.value or 0)
            p_lb = []
            
            for i, f in enumerate(fields):
                val = float(f.value or 0)
                p = Aircraft.kg_to_lb(val) if (units[i] and units[i].value == "Kg") else (val * 6.0 if units[i] is None else val)
                p_lb.append(p)

            det = calc.calculate_detailed_wb(b_w, b_m, p_lb)
            tow_w, _, tow_cg = det["totals"]["tow"]
            safe, flim = calc.check_safety(tow_w, tow_cg)
            
            mensaje_estado = "Dentro de los límites" if safe else "Fuera de límites"
            state.update({
                "res": det, 
                "safe": mensaje_estado, 
                "lim": f"{flim:.1f} - 47.3 in", 
                "reg": reg_field.value
            })
            
            res_col.controls.append(ft.Text(f"TOW: {tow_w:.1f} lb | CG: {tow_cg:.2f} in", size=20, weight="bold"))
            
            res_col.controls.append(
                ft.Text(
                    mensaje_estado, 
                    color="green" if safe else "red", 
                    size=22, 
                    weight="bold"
                )
            )

            btn_pdf.disabled = False
            page.update()
        except ValueError:
            snack = ft.SnackBar(ft.Text("Error: Llene los campos con números"))
            page.overlay.append(snack)
            snack.open = True
            page.update()

    def pdf_click(e):
        try:
            nombre = f"WB_{state['reg'] if state['reg'] else 'Reporte'}.pdf"
            generate_pdf_report(nombre, avion.model, state["reg"], state["res"], state["safe"], state["lim"])
            
            # RUTA Y APERTURA AUTOMÁTICA
            path_completo = os.path.abspath(os.path.join(current_dir, "..", nombre))
            os.startfile(path_completo) 
            
            snack = ft.SnackBar(ft.Text(f"PDF generado y abierto"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
        except Exception as ex:
            print(f"Error: {ex}")

    btn_calc = ft.ElevatedButton("Calcular", on_click=on_calc)
    btn_pdf = ft.ElevatedButton("PDF", on_click=pdf_click, disabled=True)

    page.add(ft.Column([
        ft.Text("Cessna 172N W&B Calculator", size=24, weight="bold"),
        ft.Row([reg_field, bew_field, mom_field]), 
        ft.Divider(),
        *[ft.Row([fields[i], units[i]]) if units[i] else ft.Row([fields[i]]) for i in range(len(fields))], 
        ft.Row([btn_calc, btn_pdf]), 
        res_col
    ]))

ft.app(target=main)
