import os
import re
import json
import logging
import requests

logger = logging.getLogger("fisiogenu.ia")

# Carga de credenciales
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_KEY_FILE = os.path.join(_BASE_DIR, ".ia_key")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

if os.path.isfile(_KEY_FILE):
    try:
        with open(_KEY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip().upper(), v.strip()
                    if k in ("GROQ", "GROQ_API_KEY", "IA_API_KEY") and not GROQ_API_KEY:
                        GROQ_API_KEY = v
                    elif k in ("GEMINI", "GEMINI_API_KEY", "GOOGLE", "GOOGLE_API_KEY") and not GEMINI_API_KEY:
                        GEMINI_API_KEY = v
                else:
                    if line.startswith("gsk_") and not GROQ_API_KEY:
                        GROQ_API_KEY = line
                    elif (line.startswith("AIza") or line.startswith("AQ.")) and not GEMINI_API_KEY:
                        GEMINI_API_KEY = line
    except Exception as e:
        logger.warning(f"No se pudo leer el archivo de claves: {e}")

# Modelos por defecto ordenados por velocidad y disponibilidad activa
GEMINI_MODELS = ["gemini-3.1-flash-lite", "gemini-3.6-flash"]
GROQ_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.6-27b"]


def extraer_json(texto):
    """Limpia y extrae un diccionario o lista JSON a partir de la respuesta del modelo."""
    if not texto:
        return None
    texto = texto.strip()
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL).strip()
    
    match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", texto, re.DOTALL)
    if match:
        texto = match.group(1)
        
    texto = re.sub(r",\s*}", "}", texto)
    texto = re.sub(r",\s*]", "]", texto)
    
    inicio_obj = texto.find("{")
    fin_obj = texto.rfind("}")
    inicio_arr = texto.find("[")
    fin_arr = texto.rfind("]")
    
    if inicio_obj != -1 and fin_obj != -1 and fin_obj > inicio_obj:
        if inicio_arr == -1 or inicio_obj < inicio_arr:
            texto = texto[inicio_obj:fin_obj+1]
        elif inicio_arr != -1 and fin_arr != -1 and fin_arr > inicio_arr:
            texto = texto[inicio_arr:fin_arr+1]
    elif inicio_arr != -1 and fin_arr != -1 and fin_arr > inicio_arr:
        texto = texto[inicio_arr:fin_arr+1]
        
    try:
        return json.loads(texto)
    except Exception:
        return None


def _llamar_gemini(system_prompt, user_prompt):
    """Llama a la API de Google Gemini."""
    if not GEMINI_API_KEY:
        return None, "Sin clave Gemini"

    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"INSTRUCCIONES DEL SISTEMA:\n{system_prompt}\n\nENTRADA:\n{user_prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        try:
            resp = requests.post(url, json=body, timeout=15)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                data = extraer_json(raw_text)
                if data is not None:
                    return data, f"Google Gemini ({model})"
            else:
                logger.warning(f"Gemini {model} respondió con error {resp.status_code}: {resp.text[:120]}")
        except Exception as e:
            logger.warning(f"Excepción al llamar a Gemini ({model}): {e}")
            
    return None, "Error en llamada a Gemini"


def _llamar_groq(system_prompt, user_prompt):
    """Llama a la API de Groq Cloud."""
    if not GROQ_API_KEY:
        return None, "Sin clave Groq"

    url = "https://api.groq.com/openai/v1/chat/completions"
    for model in GROQ_MODELS:
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt + "\nResponde exclusivamente en formato JSON válido."},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=15)
            if resp.status_code == 200:
                raw_text = resp.json()["choices"][0]["message"]["content"]
                data = extraer_json(raw_text)
                if data is not None:
                    return data, f"Groq ({model})"
            else:
                logger.warning(f"Groq {model} respondió con error {resp.status_code}: {resp.text[:120]}")
        except Exception as e:
            logger.warning(f"Excepción al llamar a Groq ({model}): {e}")

    return None, "Error en llamada a Groq"


def consultar_ia_json(system_prompt, user_prompt, orden_preferido=("gemini", "groq")):
    """
    Ejecuta una consulta a la IA con tolerancia a fallos en cascada (Fallback).
    Devuelve (datos_json, proveedor_utilizado).
    """
    for proveedor in orden_preferido:
        if proveedor == "gemini" and GEMINI_API_KEY:
            datos, fuente = _llamar_gemini(system_prompt, user_prompt)
            if datos is not None:
                print(f"[FisioGenu IA] Respuesta generada exitosamente con {fuente}")
                return datos, fuente
        elif proveedor == "groq" and GROQ_API_KEY:
            datos, fuente = _llamar_groq(system_prompt, user_prompt)
            if datos is not None:
                print(f"[FisioGenu IA] Respuesta generada exitosamente con {fuente}")
                return datos, fuente

    print("[FisioGenu IA] No se pudo obtener respuesta de ningún proveedor de IA.")
    return None, None
