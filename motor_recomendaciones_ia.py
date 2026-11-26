import ia_client

SISTEMA_REC = (
    "Eres un fisioterapeuta especialista en rehabilitación ortopédica y traumatológica de rodilla. "
    "Tu objetivo es elaborar un plan de tratamiento y recomendaciones clínicas de ALTO NIVEL, PROFUNDAS, ESPECÍFICAS Y ACCIONABLES, "
    "adaptadas estrictamente a las variables clínicas del paciente y a su fase de recuperación.\n\n"
    "Para cada recomendación debes incluir:\n"
    "1. Categoría o Tipo de intervención (ej. Cinesiterapia, Fortalecimiento, Agentes Físicos, Propiocepción, Reeducación de Marcha, Terapia Manual, etc.).\n"
    "2. Descripción técnica detallada con dosificación clínica exacta (series, repeticiones, tiempos de mantenimiento, frecuencia diaria/semanal, ángulos de movimiento seguros).\n"
    "3. Justificación biomecánica y fisiológica (por qué se prescribe en este caso particular y qué objetivo terapéutico cumple).\n\n"
    "Debes devolver SOLO JSON válido con la siguiente estructura exacta:\n"
    "{\n"
    '  "recomendaciones": [\n'
    '    "Categoría/Nombre: Descripción técnica detallada con dosificación precisa... Justificación: ...",\n'
    '    ...\n'
    "  ],\n"
    '  "analisis_clinico_profundo": "Análisis fisiopatológico detallado del caso, correlacionando dolor, edema, rango, fuerza, carga y estabilidad con la fase diagnóstica.",\n'
    '  "precauciones_contraindicaciones": "Movimientos contraindicados, límites de angulación articular a evitar y signos de alarma clínicos para suspender el ejercicio."\n'
    "}"
)


def generar_recomendaciones(hechos, fase, nombre_paciente="el paciente"):
    """
    Genera recomendaciones clínicas profundas y personalizadas usando el cliente de IA híbrido (Gemini / Groq).
    """
    vars_texto = ", ".join(f"{k}: {v}" for k, v in sorted(hechos.items()) if v)

    mensaje = (
        f"Paciente: {nombre_paciente}\n"
        f"Fase detectada: {fase}\n"
        f"Variables clínicas evaluadas: {vars_texto}\n\n"
        "Genera un plan de recomendaciones clínicas detallado, con dosificación exacta, justificación biomecánica, "
        "análisis fisiopatológico profundo y precauciones específicas para este paciente."
    )

    datos, proveedor = ia_client.consultar_ia_json(
        system_prompt=SISTEMA_REC,
        user_prompt=mensaje,
        orden_preferido=("gemini", "groq")
    )

    if not datos or not isinstance(datos, dict):
        return None, None

    recs = datos.get("recomendaciones", [])
    analisis = datos.get("analisis_clinico_profundo", datos.get("explicacion_adicional", ""))
    precauciones = datos.get("precauciones_contraindicaciones", "")

    if not isinstance(recs, list) or len(recs) == 0:
        return None, None

    # Estructuramos la nota clínica con la profundidad y precauciones recibidas
    nota_completa = ""
    if analisis:
        nota_completa += f"Análisis Fisiopatológico: {analisis}\n\n"
    if precauciones:
        nota_completa += f"Precauciones y Contraindicaciones: {precauciones}\n\n"
    if proveedor:
        nota_completa += f"Plan generado con {proveedor}"

    return recs[:8], nota_completa.strip()
