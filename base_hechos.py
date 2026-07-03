VARIABLES_CLINICAS = [
    "dolor",
    "edema",
    "rango_articular",
    "fuerza_muscular",
    "capacidad_funcional",
    "tolerancia_carga",
    "estabilidad_rodilla",
]

VALORES_PERMITIDOS = {
    "dolor": ["leve", "moderado", "severo"],
    "edema": ["ausente", "leve", "moderado", "severo"],
    "rango_articular": ["completo", "parcial", "limitado"],
    "fuerza_muscular": ["adecuada", "disminuida", "debil"],
    "capacidad_funcional": ["independiente", "asistida", "dependiente"],
    "tolerancia_carga": ["funcional", "parcial", "no_tolera"],
    "estabilidad_rodilla": ["estable", "inestable", "muy_inestable"],
}

ETIQUETAS_VARIABLES = {
    "dolor": "Dolor",
    "edema": "Edema",
    "rango_articular": "Rango articular",
    "fuerza_muscular": "Fuerza muscular",
    "capacidad_funcional": "Capacidad funcional",
    "tolerancia_carga": "Tolerancia a carga",
    "estabilidad_rodilla": "Estabilidad de rodilla",
}

GRUPOS_VARIABLES = {
    "signos_vitales": ["dolor", "edema"],
    "funcion_motora": ["rango_articular", "fuerza_muscular"],
    "funcionalidad": ["capacidad_funcional", "tolerancia_carga"],
    "estabilidad": ["estabilidad_rodilla"],
}

PESOS_CLINICOS = {
    "dolor": 20,
    "edema": 15,
    "rango_articular": 15,
    "fuerza_muscular": 15,
    "capacidad_funcional": 15,
    "tolerancia_carga": 10,
    "estabilidad_rodilla": 10,
}


def crear_hechos(datos):
    hechos = {}
    for variable in VARIABLES_CLINICAS:
        valor = datos.get(variable, "")
        if valor is not None:
            valor = str(valor).strip().lower().replace(" ", "_")
        else:
            valor = ""
        hechos[variable] = valor
    return hechos


def validar_hechos(hechos):
    errores = []
    for variable in VARIABLES_CLINICAS:
        valor = hechos.get(variable, "")
        if not valor:
            errores.append(f"El campo '{ETIQUETAS_VARIABLES.get(variable, variable)}' es obligatorio.")
            continue
        permitidos = VALORES_PERMITIDOS.get(variable, [])
        if valor not in permitidos:
            errores.append(
                f"Valor invalido para '{ETIQUETAS_VARIABLES.get(variable, variable)}': '{valor}'. "
                f"Valores permitidos: {', '.join(permitidos)}."
            )
    return (len(errores) == 0, errores)
