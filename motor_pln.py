import re


SINONIMOS_CLINICOS = {
    "dolor": {
        "severo": [
            "dolor intenso", "dolor fuerte", "mucho dolor", "dolor severo",
            "dolor agudo", "dolor insoportable", "dolor extremo",
            "intenso dolor", "dolor muy fuerte", "dolor muy intenso",
        ],
        "moderado": [
            "dolor moderado", "dolor medio", "dolor tolerable",
            "algo de dolor", "dolor intermedio", "dolor molesto",
        ],
        "leve": [
            "dolor leve", "poco dolor", "dolor minimo", "dolor suave",
            "ligero dolor", "casi sin dolor", "molestia leve",
            "sin dolor", "no duele", "no presenta dolor",
            "no tiene dolor", "sin molestia",
        ],
    },
    "edema": {
        "severo": [
            "muy hinchado", "hinchazon severa", "edema severo",
            "mucho edema", "hinchazon importante", "muy inflamado",
            "hinchazon grave", "inflamacion severa",
        ],
        "moderado": [
            "hinchazon moderada", "edema moderado", "algo hinchado",
            "inflamacion moderada", "hinchazon notable",
        ],
        "leve": [
            "ligera hinchazon", "edema leve", "poco hinchado",
            "hinchazon leve", "ligero edema", "minima hinchazon",
        ],
        "ausente": [
            "sin hinchazon", "sin edema", "no hay edema", "no hinchado",
            "edema ausente", "sin inflamacion", "no esta inflamado",
            "sin inflamacion", "no hay inflamacion", "no presenta edema",
        ],
    },
    "rango_articular": {
        "completo": [
            "rango completo", "movilidad completa", "flexion completa",
            "extension completa", "movimiento completo",
            "sin limitacion de movimiento", "rango total",
        ],
        "parcial": [
            "rango parcial", "movilidad limitada parcial", "flexion parcial",
            "movimiento restringido parcial", "limitacion parcial",
        ],
        "limitado": [
            "rango limitado", "muy limitado", "poca movilidad",
            "movilidad muy reducida", "bloqueo articular",
            "no puede mover", "rigidez articular", "muy rigido",
        ],
    },
    "fuerza_muscular": {
        "adecuada": [
            "fuerza adecuada", "buena fuerza", "fuerza normal",
            "musculos fuertes", "fuerza conservada",
            "sin perdida de fuerza", "fuerza intacta",
        ],
        "disminuida": [
            "fuerza disminuida", "fuerza reducida", "debilidad moderada",
            "poca fuerza", "musculos debiles", "perdida parcial de fuerza",
        ],
        "debil": [
            "fuerza muy baja", "muy debil", "debilidad severa",
            "sin fuerza", "atrofia muscular", "perdida total de fuerza",
            "no puede contraer", "paralisis",
        ],
    },
    "capacidad_funcional": {
        "independiente": [
            "independiente", "autonomo", "sin ayuda", "camina solo",
            "actividades independientes", "se vale por si mismo",
            "sin asistencia", "no necesita ayuda",
        ],
        "asistida": [
            "con ayuda", "asistido", "necesita apoyo", "muletas",
            "baston", "andadera", "camina con apoyo",
            "asistencia parcial", "supervision",
        ],
        "dependiente": [
            "dependiente", "no puede caminar", "silla de ruedas",
            "necesita asistencia total", "postrado", "encamado",
            "inmovil", "no se moviliza",
        ],
    },
    "tolerancia_carga": {
        "funcional": [
            "tolera carga", "apoya bien", "carga funcional",
            "puede apoyar", "soporta peso", "carga completa",
            "apoya totalmente", "tolera el peso",
        ],
        "parcial": [
            "carga parcial", "apoya parcialmente", "tolera poco peso",
            "apoyo limitado", "media carga", "apoya un poco",
        ],
        "no_tolera": [
            "no puede apoyar", "no tolera carga", "sin apoyo",
            "no apoya el pie", "evita apoyar", "descarga total",
            "no carga peso", "no soporta peso", "sin carga",
        ],
    },
    "estabilidad_rodilla": {
        "estable": [
            "rodilla estable", "estabilidad buena", "sin inestabilidad",
            "firme", "estable", "no se desplaza",
        ],
        "inestable": [
            "rodilla inestable", "sensacion de fallo", "inestabilidad",
            "rodilla que cede", "bloqueos", "cede al caminar",
            "se le dobla", "falso paso",
        ],
        "muy_inestable": [
            "muy inestable", "rodilla que se sale", "luxacion",
            "inestabilidad severa", "fallo articular",
            "se disloca", "se sale de lugar",
        ],
    },
}

_PALABRAS_NEGACION = {"no", "sin", "nunca", "jamas", "tampoco", "ni"}
_VENTANA_NEGACION = 4

_ultimo_resultado = {}


def _tokenizar(texto):
    return re.findall(r"[a-zA-Z\u00C0-\u024F]+(?:'[a-zA-Z\u00C0-\u024F]+)?", texto.lower())


def _stem_es(palabra):
    p = palabra.lower()
    if len(p) <= 4:
        return p
    for suf in [
        "ciones", "ción", "mientos", "miento", "mente",
        "ados", "adas", "ado", "ada",
        "idos", "idas", "ido", "ida",
        "ando", "iendo",
        "aban", "abas", "aba", "abais",
        "ian", "ias", "ia", "iais",
        "amos", "imos",
        "asteis", "isteis", "aste", "iste", "aron", "ieron",
        "arais", "ierais", "aria", "arian", "arias",
        "ariais", "arian", "arias",
        "eses", "esas", "eses", "esa", "eso", "ese",
        "ones", "onas", "ona", "on",
        "oras", "ores", "ora", "or",
        "adas", "ados", "ada", "ado",
        "idas", "idos", "ida", "ido",
        "es", "as", "os",
        "a", "o", "e",
    ]:
        if p.endswith(suf) and len(p) - len(suf) >= 3:
            return p[: -len(suf)]
    return p


def _coincidencia_token(tokens_texto, frase_tokens):
    for i in range(len(tokens_texto) - len(frase_tokens) + 1):
        coincide = True
        for j, ft in enumerate(frase_tokens):
            tt = tokens_texto[i + j]
            if tt != ft and _stem_es(tt) != _stem_es(ft):
                coincide = False
                break
        if coincide:
            return (i, i + len(frase_tokens) - 1)
    return None


def _tiene_negacion(tokens, idx_fin):
    inicio = max(0, idx_fin - _VENTANA_NEGACION + 1)
    for i in range(inicio, idx_fin + 1):
        if tokens[i] in _PALABRAS_NEGACION:
            return True
    return False


def _calcular_confianza(tokens_texto, frase_tokens, idx_inicio, idx_fin, negado):
    total_significativos = sum(1 for t in tokens_texto if len(t) > 2)
    if total_significativos == 0:
        return 0.5
    proporcion = len(frase_tokens) / total_significativos
    coincidencias_exactas = sum(
        1 for j, ft in enumerate(frase_tokens) if tokens_texto[idx_inicio + j] == ft
    )
    calidad = coincidencias_exactas / max(len(frase_tokens), 1)
    confianza = min(1.0, proporcion * 2 + calidad * 0.5)
    if negado:
        confianza *= 0.5
    return max(confianza, 0.3)


def procesar_texto(texto):
    global _ultimo_resultado
    if not texto or not texto.strip():
        _ultimo_resultado = {}
        return {}

    tokens = _tokenizar(texto)
    detectados = {}

    for variable, valores_dict in SINONIMOS_CLINICOS.items():
        mejor_valor = None
        mejor_confianza = 0.0
        mejor_frase = ""
        frase_negada = False

        for valor, frases in valores_dict.items():
            for frase in frases:
                frase_tokens = _tokenizar(frase)
                if not frase_tokens:
                    continue

                match = _coincidencia_token(tokens, frase_tokens)
                if not match:
                    continue

                idx_inicio, idx_fin = match
                negado = _tiene_negacion(tokens, idx_fin)

                es_ausencia = valor in ("ausente", "leve", "no_tolera")
                if negado and not es_ausencia:
                    continue

                confianza = _calcular_confianza(tokens, frase_tokens, idx_inicio, idx_fin, negado)

                if negado and es_ausencia:
                    confianza = min(1.0, confianza + 0.15)

                if confianza > mejor_confianza:
                    mejor_confianza = confianza
                    mejor_valor = valor
                    mejor_frase = frase
                    frase_negada = negado

        if mejor_valor:
            detectados[variable] = {
                "valor": mejor_valor,
                "confianza": round(mejor_confianza, 2),
                "frase_detectada": mejor_frase,
                "negado": frase_negada,
            }

    _ultimo_resultado = detectados
    return detectados


def obtener_resultado_formateado():
    if not _ultimo_resultado:
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
    for variable, datos in _ultimo_resultado.items():
        resultado.append({
            "variable": variable,
            "etiqueta": etiquetas.get(variable, variable),
            "valor": datos["valor"],
            "confianza": datos["confianza"],
            "frase": datos.get("frase_detectada", ""),
        })
    return resultado
