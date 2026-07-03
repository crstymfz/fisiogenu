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

SISTEMA = (
    "Eres un extractor de variables clinicas para rehabilitacion de rodilla. "
    "Del texto del paciente, extrae SOLO estas variables con sus valores exactos:\n"
    "- dolor: leve, moderado, severo\n"
    "- edema: ausente, leve, moderado, severo\n"
    "- rango_articular: completo, parcial, limitado\n"
    "- fuerza_muscular: adecuada, disminuida, debil\n"
    "- capacidad_funcional: independiente, asistida, dependiente\n"
    "- tolerancia_carga: funcional, parcial, no_tolera\n"
    "- estabilidad_rodilla: estable, inestable, muy_inestable\n\n"
    "Usa SIEMPRE los nombres exactos de variable escritos arriba.\n"
    "Devuelve SOLO JSON valido, sin comentarios, sin texto adicional, sin markdown:\n"
    '{"dolor": {"valor": "...", "confianza": 0.95, "frase_detectada": "..."}, ...}'
)

ULTIMO_RESULTADO = {}


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


def procesar_texto(texto):
    global ULTIMO_RESULTADO
    if not API_KEY:
        ULTIMO_RESULTADO = {}
        return None

    if not texto or not texto.strip():
        ULTIMO_RESULTADO = {}
        return None

    try:
        body = {
            "model": MODELO,
            "messages": [
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": texto},
            ],
            "temperature": 0.05,
            "max_tokens": 1024,
        }

        resp = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        datos = _extraer_json(raw)

        for var in list(datos.keys()):
            if not isinstance(datos[var], dict) or "valor" not in datos[var]:
                datos.pop(var)
                continue
            datos[var]["confianza"] = min(1.0, max(0.0, datos[var].get("confianza", 0.5)))
            datos[var]["frase_detectada"] = datos[var].get("frase_detectada", "")

        ULTIMO_RESULTADO = datos
        return datos

    except Exception:
        ULTIMO_RESULTADO = {}
        return None


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
