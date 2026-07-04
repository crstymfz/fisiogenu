import os
from fpdf import FPDF

_FUENTES = {}


def _fuente(ruta, estilo=""):
    if estilo not in _FUENTES:
        _FUENTES[estilo] = ruta
    return estilo


class EvaluacionPDF(FPDF):
    def __init__(self):
        super().__init__()
        arial = "C:\\Windows\\Fonts\\arial.ttf"
        arialb = "C:\\Windows\\Fonts\\arialbd.ttf"
        self.add_font("Arial", "", arial, uni=True)
        self.add_font("Arial", "B", arialb, uni=True)
        self.set_auto_page_break(auto=True, margin=20)

    def _header(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(44, 72, 122)
        self.cell(0, 10, "FisioGenu", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Arial", "", 9)
        self.set_text_color(100)
        self.cell(0, 5, "Sistema experto para rehabilitacion de rodilla", new_x="LMARGIN", new_y="NEXT", align="C")
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def _footer(self):
        self.set_y(-15)
        self.set_font("Arial", "", 8)
        self.set_text_color(130)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def _celda_color(self, w, h, texto, color_texto, color_fondo):
        self.set_fill_color(*color_fondo)
        self.set_text_color(*color_texto)
        self.set_font("Arial", "", 10)
        self.cell(w, h, f"  {texto}", fill=True, new_x="END")
        self.set_text_color(0)

    def generar(self, ev):
        self.alias_nb_pages()
        self.add_page()

        # Titulo
        self.set_font("Arial", "B", 14)
        self.set_text_color(44, 72, 122)
        self.cell(0, 8, "Evaluacion Clinica", new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(3)

        # Datos paciente
        self.set_font("Arial", "", 10)
        self.set_text_color(50)
        nombre = ev.get("nombre", "No especificado")
        edad = ev.get("edad", "")
        sexo = ev.get("sexo", "")
        fecha = ev.get("fecha", "")
        metodo = ev.get("metodo_evaluacion", "")
        paciente = nombre
        if edad:
            paciente += f" - {edad} anos"
        if sexo:
            paciente += f" - {sexo}"
        self.cell(0, 6, f"Paciente: {paciente}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"Fecha: {fecha}", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"Metodo: {metodo}", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # Fase detectada
        fase = ev.get("fase_detectada", "")
        colores = {
            "aguda": ((180, 40, 40), (255, 230, 230)),
            "subaguda": ((200, 120, 30), (255, 245, 230)),
            "funcional": ((30, 100, 180), (230, 245, 255)),
            "alta funcional": ((30, 130, 70), (230, 255, 240)),
        }
        color_texto, color_fondo = colores.get(fase, ((80,), (240,)))
        self._celda_color(60, 8, fase.upper(), color_texto, color_fondo)
        self.ln(12)

        # Variables clinicas
        self.set_font("Arial", "B", 11)
        self.set_text_color(44, 72, 122)
        self.cell(0, 7, "Variables clinicas:", new_x="LMARGIN", new_y="NEXT")
        vars_map = {
            "dolor": "Dolor", "edema": "Edema",
            "rango_articular": "Rango articular", "fuerza_muscular": "Fuerza muscular",
            "capacidad_funcional": "Capacidad funcional",
            "tolerancia_carga": "Tolerancia a carga",
            "estabilidad_rodilla": "Estabilidad de rodilla",
        }
        self.set_font("Arial", "", 10)
        for var_clave, var_etiqueta in vars_map.items():
            val = ev.get(var_clave, "")
            if val:
                self.cell(0, 6, f"  {var_etiqueta}: {val}", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # Explicacion tecnica
        self.set_font("Arial", "B", 11)
        self.set_text_color(44, 72, 122)
        self.cell(0, 7, "Analisis tecnico:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Arial", "", 10)
        self.set_text_color(50)
        exp_tec = ev.get("explicacion_tecnica", "")
        self.multi_cell(0, 5, exp_tec)
        self.ln(4)

        # Explicacion natural
        self.set_font("Arial", "B", 11)
        self.set_text_color(44, 72, 122)
        self.cell(0, 7, "Resumen clinico:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Arial", "", 10)
        self.set_text_color(50)
        exp_nat = ev.get("explicacion_natural", "")
        self.multi_cell(0, 5, exp_nat)
        self.ln(4)

        # Recomendaciones
        self.set_font("Arial", "B", 11)
        self.set_text_color(44, 72, 122)

        if ev.get("recomendaciones_ia"):
            self.cell(0, 7, "Recomendaciones personalizadas (IA):", new_x="LMARGIN", new_y="NEXT")
        else:
            self.cell(0, 7, "Recomendaciones:", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Arial", "", 10)
        self.set_text_color(50)
        recs = ev.get("recomendaciones", []) if isinstance(ev.get("recomendaciones"), list) else ev.get("recomendaciones_lista", [])
        for i, rec in enumerate(recs, 1):
            self.cell(5, 6, "")
            self.cell(0, 6, f"{i}. {rec}", new_x="LMARGIN", new_y="NEXT")

        if ev.get("explicacion_ia"):
            self.ln(4)
            self.set_font("Arial", "I", 9)
            self.set_text_color(100)
            self.multi_cell(0, 5, f"Nota clinica: {ev['explicacion_ia']}")

        return self
