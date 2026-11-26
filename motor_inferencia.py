RECOMENDACIONES_POR_FASE = {
    "aguda": [
        "Reposo relativo y elevación de la extremidad afectada.",
        "Protocolo PRICE/POLICE: Crioterapia 15-20 minutos cada 2-3 horas para control de derrame y dolor agudo.",
        "Descarga articular obligatoria (evitar apoyo completo de peso).",
        "Contracciones isométricas suaves de cuádriceps según tolerancia (sin movimiento articular).",
        "Consulta inmediata con el equipo de fisioterapia para contención del proceso inflamatorio.",
    ],
    "subaguda": [
        "Iniciar movilización activo-asistida dentro del arco no doloroso (0°-90°).",
        "Fortalecimiento isométrico e isotónico protegido de cuádriceps, isquiotibiales y glúteo medio.",
        "Manejo de edema en resolución con presoterapia suave, elevación y crioterapia post-ejercicio.",
        "Reeducación de la marcha con progresión gradual de carga parcial con apoyo técnico.",
        "Entrenamiento de propiocepción estática y control neuromuscular en superficie estable.",
    ],
    "cronica": [
        "Fortalecimiento intensivo en cadena cinética cerrada (sentadillas controladas, prensas en ángulos seguros).",
        "Trabajo propioceptivo avanzado en superficies inestables (Bosu, plato de Freeman).",
        "Reeducación biomecánica del patrón de marcha, carrera y subida/bajada de escaleras.",
        "Flexibilidad y cinesiterapia para combatir la rigidez articular y adherencias capsulares.",
        "Ejercicios excéntricos específicos para tendinosis y adaptación tisular.",
        "Prevención de recidivas mediante calentamiento estructurado y acondicionamiento global.",
    ],
    "funcional": [
        "Ejercicios de fuerza y potencia funcional en cadena cerrada.",
        "Ejercicios pliométricos y de agilidad progresiva (saltos, cambios de dirección controlados).",
        "Simulación de gestos deportivos y laborales de impacto moderado a alto.",
        "Test de salto (Hop Tests) y evaluación biomecánica de simetría de miembros inferiores.",
        "Programa de retorno deportivo/laboral supervisado y pautas de mantenimiento.",
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
            "Fase REACTIVA / AGUDA detectada: presencia de respuesta inflamatoria activa "
            "(dolor severo, derrame articular/edema severo o incapacidad total de carga). "
            "Indica lesión reciente o sobrecarga aguda con limitación funcional marcada (0-10 días)."
        ),
    },
    {
        "fase": "funcional",
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
            "Fase FUNCIONAL / READAPTACIÓN detectada: todos los parámetros clínicos son óptimos "
            "(dolor leve/ausente, sin edema, rango articular completo, fuerza conservada, marcha "
            "independiente, carga funcional y rodilla estable). Indica maduración tisular completa "
            "y aptitud para retorno funcional o deportivo."
        ),
    },
]

PUNTAJES = {
    "cronica": {
        "pesos": {
            ("estabilidad_rodilla", "muy_inestable"): 35,
            ("estabilidad_rodilla", "inestable"): 25,
            ("rango_articular", "limitado"): 25,
            ("rango_articular", "parcial"): 10,
            ("fuerza_muscular", "debil"): 20,
            ("fuerza_muscular", "disminuida"): 10,
            ("tolerancia_carga", "no_tolera"): 10,
            ("tolerancia_carga", "parcial"): 10,
            ("capacidad_funcional", "dependiente"): 10,
            ("capacidad_funcional", "asistida"): 5,
            ("dolor", "moderado"): 10,
            ("dolor", "leve"): 5,
            ("edema", "ausente"): 10,
            ("edema", "leve"): 10,
            ("edema", "moderado"): 5,
        },
        "umbral": 45,
        "explicacion_base": (
            "Fase de REMODELACIÓN / CRÓNICA detectada: se cumple {puntaje}% de los criterios "
            "de cronicidad (rigidez articular persistente, debilidad muscular prolongada o inestabilidad "
            "articular debida a adaptación tisular deficiente o fibrosis). "
            "Requiere fortalecimiento intensivo, propiocepción y reeducación biomecánica."
        ),
    },
    "subaguda": {
        "pesos": {
            ("dolor", "moderado"): 25,
            ("rango_articular", "parcial"): 25,
            ("tolerancia_carga", "parcial"): 20,
            ("fuerza_muscular", "disminuida"): 20,
            ("capacidad_funcional", "asistida"): 15,
            ("edema", "leve"): 15,
            ("edema", "moderado"): 10,
            ("estabilidad_rodilla", "estable"): 15,
            ("estabilidad_rodilla", "inestable"): 10,
        },
        "umbral": 45,
        "explicacion_base": (
            "Fase de PROLIFERACIÓN / SUBAGUDA detectada: se cumple {puntaje}% de los criterios "
            "de proliferación tisular (dolor moderado que cede en reposo pero persiste con la carga, "
            "edema en resolución, rango parcial y fuerza en recuperación activa). "
            "Indica proceso activo de reparación tisular (10 días a 6 semanas) que tolera movilización progresiva."
        ),
    },
}


def _calcular_puntaje(hechos, pesos):
    var_max = {}
    for (var, val), peso in pesos.items():
        var_max[var] = max(var_max.get(var, 0), peso)
    total = sum(var_max.values())
    if total == 0:
        return 0

    var_matched = set()
    acumulado = 0
    for (var, val), peso in sorted(pesos.items(), key=lambda x: -x[1]):
        if var not in var_matched and hechos.get(var) == val:
            acumulado += peso
            var_matched.add(var)
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
        "Fase de PROLIFERACIÓN / SUBAGUDA (por defecto): los criterios no coinciden claramente con "
        "reactiva, crónica o funcional. Se asigna subaguda como fase de "
        "reparación y transición más probable.",
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
        "aguda": "fase reactiva / aguda de rehabilitación (control de inflamación y derrame)",
        "subaguda": "fase de proliferación / subaguda de rehabilitación (reparación tisular y carga progresiva)",
        "cronica": "fase de remodelación / crónica de rehabilitación (reeducación neuromuscular y corrección de rigidez/inestabilidad)",
        "funcional": "fase funcional / readaptación (retorno completo a la actividad)",
    }.get(fase, fase)

    return (
        f"Estimado equipo clínico, tras evaluar a {nombre}, el sistema experto "
        f"FisioGenu determina que se encuentra en {fase_texto}. "
        f"Presenta dolor {dolor}, edema {edema}, rango articular {rango}, "
        f"fuerza muscular {fuerza}, capacidad funcional {capacidad}, "
        f"tolerancia a la carga {carga} y "
        f"estabilidad de rodilla {estabilidad}. "
        f"Se recomienda seguir el protocolo de rehabilitación correspondiente "
        f"a esta fase para optimizar la recuperación tisular y funcional."
    )
