import ia_client

SISTEMA = (
    "Eres un extractor de variables clinicas para rehabilitacion de rodilla. "
    "Del texto del paciente, extrae SOLO estas variables con sus valores exactos permitidos:\n"
    "- dolor: leve, moderado, severo\n"
    "- edema: ausente, leve, moderado, severo\n"
    "- rango_articular: completo, parcial, limitado\n"
    "- fuerza_muscular: adecuada, disminuida, debil\n"
    "- capacidad_funcional: independiente, asistida, dependiente\n"
    "- tolerancia_carga: funcional, parcial, no_tolera\n"
    "- estabilidad_rodilla: estable, inestable, muy_inestable\n\n"
    "Usa SIEMPRE los nombres exactos de variable escritos arriba.\n"
    "Devuelve SOLO JSON valido, sin comentarios, sin texto adicional, sin markdown:\n"
    '{"dolor": {"valor": "leve", "confianza": 0.95, "frase_detectada": "..."}, ...}'
)

ULTIMO_RESULTADO = {}
ULTIMO_PROVEEDOR = None


def procesar_texto(texto):
    """
    Extrae las variables clínicas del texto libre usando el cliente de IA híbrido (Gemini / Groq).
    """
    global ULTIMO_RESULTADO, ULTIMO_PROVEEDOR

    if not texto or not texto.strip():
        ULTIMO_RESULTADO = {}
        ULTIMO_PROVEEDOR = None
        return None

    datos, proveedor = ia_client.consultar_ia_json(
        system_prompt=SISTEMA,
        user_prompt=texto,
        orden_preferido=("gemini", "groq")
    )

    if not datos or not isinstance(datos, dict):
        ULTIMO_RESULTADO = {}
        ULTIMO_PROVEEDOR = None
        return None

    # Limpieza y validación de las variables detectadas
    variables_validas = {
        "dolor": ["leve", "moderado", "severo"],
        "edema": ["ausente", "leve", "moderado", "severo"],
        "rango_articular": ["completo", "parcial", "limitado"],
        "fuerza_muscular": ["adecuada", "disminuida", "debil"],
        "capacidad_funcional": ["independiente", "asistida", "dependiente"],
        "tolerancia_carga": ["funcional", "parcial", "no_tolera"],
        "estabilidad_rodilla": ["estable", "inestable", "muy_inestable"],
    }

    resultado_limpio = {}
    for var in list(datos.keys()):
        if var not in variables_validas:
            continue
        info = datos[var]
        if isinstance(info, str):
            info = {"valor": info, "confianza": 0.9, "frase_detectada": ""}
        if not isinstance(info, dict) or "valor" not in info:
            continue
        
        valor = str(info["valor"]).strip().lower().replace(" ", "_")
        if valor in variables_validas[var]:
            resultado_limpio[var] = {
                "valor": valor,
                "confianza": min(1.0, max(0.0, float(info.get("confianza", 0.9)))),
                "frase_detectada": str(info.get("frase_detectada", "")),
            }

    if not resultado_limpio:
        ULTIMO_RESULTADO = {}
        ULTIMO_PROVEEDOR = None
        return None

    ULTIMO_RESULTADO = resultado_limpio
    ULTIMO_PROVEEDOR = proveedor
    return resultado_limpio


def obtener_resultado_formateado():
    if not ULTIMO_RESULTADO:
        return []
    etiquetas = {
        "dolor": "Dolor",
        "edema": "Edema",
        "rango_articular": "Rango articular",
        "fuerza_muscular": "Fuerza muscular",
        "capacidad_funcional": "Capacidad funcional",
        "tolerancia_carga": "Tolerancia a carga",
        "estabilidad_rodilla": "Estabilidad de rodilla",
    }
    resultado = []
    for variable, datos in ULTIMO_RESULTADO.items():
        resultado.append({
            "variable": variable,
            "etiqueta": etiquetas.get(variable, variable),
            "valor": datos["valor"],
            "confianza": datos["confianza"],
            "frase": datos.get("frase_detectada", ""),
        })
    return resultado
