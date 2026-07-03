import os
import re
import json
import requests

API_URL = os.environ.get("IA_API_URL", "https://api.groq.com/openai/v1/chat/completions")

_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ia_key")
API_KEY = os.environ.get("IA_API_KEY", "")
if not API_KEY and os.path.isfile(_key_file):
    with open(_key_file, "r") as f:
        API_KEY = f.read().strip()

MODELO = os.environ.get("IA_MODELO", "llama-3.3-70b-versatile")

SISTEMA_REC = (
    "Eres un fisioterapeuta especializado en rehabilitacion de rodilla. "
    "Genera recomendaciones de tratamiento personalizadas basadas en las variables clinicas del paciente. "
    "Debes devolver SOLO JSON valido, sin markdown, sin texto adicional. "
    "5 recomendaciones especificas, profesionales y accionables, ordenadas por prioridad clinica. "
    "Cada una debe ser una frase clara y concreta en espanol.\n\n"
    '{"recomendaciones": ["Recomendacion 1", ...], '
    '"explicacion_adicional": "Breve nota clinica sobre el caso"}'
)


def _extraer_json(texto):
    texto = texto.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
    if match:
        texto = match.group(1)
    texto = re.sub(r",\s*}", "}", texto)
    texto = re.sub(r",\s*]", "]", texto)
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio != -1 and fin != -1 and fin > inicio:
        texto = texto[inicio:fin+1]
    return json.loads(texto)


def generar_recomendaciones(hechos, fase, nombre_paciente="el paciente"):
    if not API_KEY:
        return None, None

    vars_texto = ", ".join(f"{k}: {v}" for k, v in sorted(hechos.items()) if v)

    mensaje = (
        f"Paciente: {nombre_paciente}\n"
        f"Fase detectada: {fase}\n"
        f"Variables clinicas: {vars_texto}\n\n"
        "Genera recomendaciones de rehabilitacion especificas para este caso."
    )

    try:
        resp = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODELO,
                "messages": [
                    {"role": "system", "content": SISTEMA_REC},
                    {"role": "user", "content": mensaje},
                ],
                "temperature": 0.3,
                "max_tokens": 1024,
            },
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        datos = _extraer_json(raw)

        recs = datos.get("recomendaciones", [])
        extra = datos.get("explicacion_adicional", "")

        if not isinstance(recs, list) or len(recs) == 0:
            return None, None

        return recs[:7], extra

    except Exception:
        return None, None
