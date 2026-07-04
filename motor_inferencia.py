RECOMENDACIONES_POR_FASE = {
    "aguda": [
        "Reposo relativo y elevacion de la extremidad.",
        "Aplicacion de hielo 15-20 minutos cada 2-3 horas.",
        "Evitar carga completa sobre la rodilla afectada.",
        "Consulta con fisioterapeuta para manejo del dolor y edema.",
        "Ejercicios isometricos suaves segun tolerancia.",
    ],
    "subaguda": [
        "Iniciar movilizacion activa asistida progresiva.",
        "Fortalecimiento isometrico de cuadriceps e isquiotibiales.",
        "Control de edema con compresion y crioterapia intermitente.",
        "Progresion gradual de carga parcial.",
        "Trabajo de propiocepcion en posicion estable.",
    ],
    "funcional": [
        "Ejercicios de fortalecimiento en cadena cerrada.",
        "Entrenamiento de marcha y subida de escaleras.",
        "Progresion a actividades deportivas de bajo impacto.",
        "Ejercicios pliometricos progresivos segun tolerancia.",
        "Programa de retorno funcional supervisado.",
    ],
    "alta funcional": [
        "Mantenimiento de rutina de fortalecimiento.",
        "Actividad deportiva progresiva sin restricciones.",
        "Prevencion de recaidas con calentamiento adecuado.",
        "Evaluacion periodica de biomecanica.",
        "Alta rehabilitativa con seguimiento opcional.",
    ],
}

REGLAS = [
    {
        "fase": "aguda",
        "prioridad": 100,
        "tipo": "cualquiera",
        "condiciones": [
            ("dolor", "severo"),
            ("edema", "severo"),
            ("tolerancia_carga", "no_tolera"),
        ],
        "explicacion": (
            "Fase AGUDA detectada: presencia de dolor severo, edema severo "
            "o incapacidad para tolerar carga. Indica lesion reciente con "
            "respuesta inflamatoria activa y limitacion funcional significativa."
        ),
    },
    {
        "fase": "alta funcional",
        "prioridad": 90,
        "tipo": "todas",
        "condiciones": [
            ("dolor", "leve"),
            ("edema", "ausente"),
            ("rango_articular", "completo"),
            ("fuerza_muscular", "adecuada"),
            ("capacidad_funcional", "independiente"),
            ("tolerancia_carga", "funcional"),
            ("estabilidad_rodilla", "estable"),
        ],
        "explicacion": (
            "Fase ALTA FUNCIONAL detectada: todos los parametros clinicos son optimos "
            "(dolor leve, edema ausente, rango completo, fuerza adecuada, capacidad "
            "independiente, carga funcional, estabilidad estable). Indica recuperacion "
            "completa o cercana al alta rehabilitativa."
        ),
    },
]

PUNTAJES = {
    "funcional": {
        "pesos": {
            ("dolor", "leve"): 25,
            ("rango_articular", "completo"): 25,
            ("fuerza_muscular", "adecuada"): 25,
            ("tolerancia_carga", "funcional"): 25,
        },
        "umbral": 75,
        "explicacion_base": (
            "Fase FUNCIONAL detectada: se cumple {puntaje}% de los criterios "
            "(dolor leve, rango completo, fuerza adecuada, carga funcional). "
            "El paciente presenta capacidad para actividades cotidianas con minimas limitaciones."
        ),
    },
    "subaguda": {
        "pesos": {
            ("dolor", "moderado"): 25,
            ("edema", "leve"): 15,
            ("edema", "moderado"): 15,
            ("rango_articular", "parcial"): 20,
            ("fuerza_muscular", "disminuida"): 20,
            ("tolerancia_carga", "parcial"): 20,
        },
        "umbral": 40,
        "explicacion_base": (
            "Fase SUBAGUDA detectada: se cumple {puntaje}% de los criterios "
            "(dolor moderado, edema leve/moderado, rango parcial, "
            "fuerza disminuida, carga parcial). "
            "Indica transicion hacia la recuperacion con limitaciones moderadas."
        ),
    },
}


def _calcular_puntaje(hechos, pesos):
    total = 0
    acumulado = 0
    for (var, val), peso in pesos.items():
        total += peso
        if hechos.get(var) == val:
            acumulado += peso
    if total == 0:
        return 0
    return int(round(acumulado / total * 100))


def inferir_fase(hechos):
    for regla in sorted(REGLAS, key=lambda r: -r["prioridad"]):
        if regla["tipo"] == "cualquiera":
            if any(hechos.get(var) == val for var, val in regla["condiciones"]):
                return (regla["fase"], regla["explicacion"], RECOMENDACIONES_POR_FASE[regla["fase"]])
        elif regla["tipo"] == "todas":
            if all(hechos.get(var) == val for var, val in regla["condiciones"]):
                return (regla["fase"], regla["explicacion"], RECOMENDACIONES_POR_FASE[regla["fase"]])

    mejor_fase = None
    mejor_puntaje = 0
    mejor_explicacion = ""

    for fase, config in PUNTAJES.items():
        puntaje = _calcular_puntaje(hechos, config["pesos"])
        if puntaje >= config["umbral"] and puntaje > mejor_puntaje:
            mejor_fase = fase
            mejor_puntaje = puntaje
            mejor_explicacion = config["explicacion_base"].format(puntaje=puntaje)

    if mejor_fase:
        return (mejor_fase, mejor_explicacion, RECOMENDACIONES_POR_FASE[mejor_fase])

    return (
        "subaguda",
        "Fase SUBAGUDA (por defecto): los criterios no coinciden claramente con "
        "aguda, funcional o alta funcional. Se asigna subaguda como fase de "
        "transicion mas probable.",
        RECOMENDACIONES_POR_FASE["subaguda"],
    )


def generar_explicacion_natural(hechos, fase):
    nombre = hechos.get("nombre_paciente", "el paciente")
    dolor = hechos.get("dolor", "no especificado")
    edema = hechos.get("edema", "no especificado")
    rango = hechos.get("rango_articular", "no especificado")
    fuerza = hechos.get("fuerza_muscular", "no especificado")
    capacidad = hechos.get("capacidad_funcional", "no especificado")
    carga = hechos.get("tolerancia_carga", "no especificado")
    estabilidad = hechos.get("estabilidad_rodilla", "no especificado")

    fase_texto = {
        "aguda": "fase aguda de rehabilitacion",
        "subaguda": "fase subaguda de rehabilitacion",
        "funcional": "fase funcional de rehabilitacion",
        "alta funcional": "fase de alta funcional",
    }.get(fase, fase)

    return (
        f"Estimado equipo clinico, tras evaluar a {nombre}, el sistema experto "
        f"FisioGenu determina que se encuentra en {fase_texto}. "
        f"Presenta dolor {dolor}, edema {edema}, rango articular {rango}, "
        f"fuerza muscular {fuerza}, capacidad funcional {capacidad}, "
        f"tolerancia a la carga {carga} y "
        f"estabilidad de rodilla {estabilidad}. "
        f"Se recomienda seguir el protocolo de rehabilitacion correspondiente "
        f"a esta fase para optimizar la recuperacion."
    )
