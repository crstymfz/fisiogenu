# FisioGenu

Sistema experto híbrido orientado al apoyo en la evaluación clínica y rehabilitación de rodilla. Combina un motor de inferencia determinista (reglas clínicas y puntuación ponderada) con Procesamiento de Lenguaje Natural (PLN) e Inteligencia Artificial generativa para clasificar la fase de recuperación tisular del paciente y elaborar planes de rehabilitación personalizados.

---

## Características principales

- **Doble modalidad de evaluación clínica:**
  - **Formulario estándar:** captura estructurada de las 7 variables clínicas definidas en el modelo de hechos.
  - **Evaluación mediante texto libre (PLN):** extracción automática de variables clínicas a partir de notas escritas en lenguaje natural mediante modelos de lenguaje, con respaldo determinista basado en sinónimos y expresiones regulares.
- **Motor de inferencia por fases de reparación tisular:** clasifica cada caso en una de cuatro fases clínicas (`aguda`, `subaguda`, `cronica` o `funcional`) y genera tanto la justificación técnica como una explicación en lenguaje natural.
- **Arquitectura de IA híbrida con tolerancia a fallos:** consulta en cascada a **Google Gemini** y **Groq Cloud** para extracción semántica y generación de recomendaciones con dosificación, justificación biomecánica, análisis fisiopatológico y precauciones. Si no hay conexión o credenciales disponibles, el sistema recurre automáticamente a sus módulos locales deterministas.
- **Historial clínico y exportación a PDF:** almacenamiento persistente en SQLite y generación de informes clínicos descargables en formato PDF.

---

## Variables clínicas y fases de rehabilitación

El sistema evalúa 7 variables clínicas normalizadas (`base_hechos.py`):

| Variable | Valores permitidos |
| :--- | :--- |
| `dolor` | `leve`, `moderado`, `severo` |
| `edema` | `ausente`, `leve`, `moderado`, `severo` |
| `rango_articular` | `completo`, `parcial`, `limitado` |
| `fuerza_muscular` | `adecuada`, `disminuida`, `debil` |
| `capacidad_funcional` | `independiente`, `asistida`, `dependiente` |
| `tolerancia_carga` | `funcional`, `parcial`, `no_tolera` |
| `estabilidad_rodilla` | `estable`, `inestable`, `muy_inestable` |

A partir de estas variables, `motor_inferencia.py` determina la fase correspondiente:

1. **Reactiva / Aguda (`aguda`):** prioridad máxima (100). Se activa ante dolor severo, edema severo o incapacidad de tolerar carga.
2. **Funcional / Readaptación (`funcional`):** prioridad 90. Requiere el cumplimiento simultáneo de todos los parámetros en estado óptimo.
3. **Remodelación / Crónica (`cronica`):** evaluada por puntuación ponderada (umbral mínimo de 45 %), enfocada en rigidez articular persistente, debilidad prolongada o inestabilidad.
4. **Proliferación / Subaguda (`subaguda`):** evaluada por puntuación ponderada (umbral mínimo de 45 %) y asignada por defecto cuando el cuadro clínico corresponde a una etapa intermedia o de transición.

---

## Flujo de proveedores de IA

El módulo `ia_client.py` centraliza las peticiones en formato JSON estricto siguiendo un esquema de respaldo en cascada:

1. **Google Gemini** (`gemini-3.1-flash-lite`, con respaldo `gemini-3.6-flash`).
2. **Groq Cloud** (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`).
3. **Respaldo local determinista:**
   - Para PLN: `motor_pln.py` (coincidencia por patrones y diccionario clínico).
   - Para recomendaciones: `RECOMENDACIONES_POR_FASE` en `motor_inferencia.py`.

---

## Estructura del proyecto

```text
Fisiogenu/
├── app.py                        # Servidor Flask y enrutamiento principal
├── base_hechos.py                # Definición y validación de variables clínicas
├── motor_inferencia.py           # Reglas clínicas, puntuación por fase y explicación
├── ia_client.py                  # Cliente híbrido Gemini / Groq con fallback en cascada
├── motor_pln_llm.py              # Extractor clínico basado en LLM
├── motor_pln.py                  # Extractor clínico determinista (sinónimos y regex)
├── motor_recomendaciones_ia.py   # Generador de planes terapéuticos detallados con IA
├── database.py                   # Persistencia SQLite (fisiogenu.db)
├── generar_pdf.py                # Generación de reportes PDF con fpdf2
├── fisiogenu_ui/                 # Plantillas HTML y recursos estáticos (CSS, JS, imágenes)
│   ├── index.html
│   ├── formulario_estandar.html
│   ├── formulario_pln.html
│   ├── resultado.html
│   └── historial.html
├── requirements.txt              # Dependencias de Python
└── Procfile                      # Configuración de despliegue con Gunicorn
```

---

## Requisitos e instalación

- **Python:** 3.10 o superior recomendado.
- **Dependencias:** listadas en `requirements.txt` (`Flask`, `requests`, `fpdf2`, `gunicorn`).

### Pasos de instalación

1. Clonar el repositorio y acceder al directorio del proyecto:
   ```bash
   git clone <url-del-repositorio>
   cd Fisiogenu
   ```

2. Crear y activar un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/macOS:
   source venv/bin/activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

> **Nota sobre la exportación a PDF:** `generar_pdf.py` utiliza las fuentes del sistema de Windows (`C:\Windows\Fonts\arial.ttf` y `arialbd.ttf`). Si se despliega en Linux o macOS, es necesario ajustar dichas rutas a una fuente TrueType disponible en el entorno.

---

## Configuración de claves de IA

Las credenciales pueden definirse mediante variables de entorno o a través de un archivo `.ia_key` en la raíz del proyecto (este archivo está excluido en `.gitignore`).

### Opción 1: Variables de entorno

```bash
export GEMINI_API_KEY="tu_clave_de_google_gemini"
export GROQ_API_KEY="tu_clave_de_groq"
```

También se admite `GOOGLE_API_KEY` como alternativa a `GEMINI_API_KEY`.

### Opción 2: Archivo `.ia_key`

Crear el archivo `.ia_key` en la raíz con el siguiente formato:

```ini
GEMINI=tu_clave_de_google_gemini
GROQ=tu_clave_de_groq
```

Si no se configura ninguna clave, la aplicación continuará funcionando con el extractor PLN por patrones y las recomendaciones clínicas base del motor de inferencia.

---

## Ejecución

### Entorno local (desarrollo)

```bash
python app.py
```

El servidor se iniciará en `http://127.0.0.1:5000` (el puerto puede modificarse mediante la variable de entorno `PORT`). Al arrancar, `database.inicializar_bd()` crea automáticamente el archivo `fisiogenu.db` si aún no existe.

### Entorno de producción

Conforme al archivo `Procfile`:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

---

## Rutas principales de la aplicación

| Ruta | Método | Descripción |
| :--- | :--- | :--- |
| `/` | `GET` | Página de inicio con acceso a evaluaciones recientes |
| `/formulario-estandar` | `GET` | Formulario clínico estructurado |
| `/formulario-pln` | `GET` | Formulario de evaluación mediante texto libre |
| `/evaluar` | `POST` | Procesa la evaluación estándar y muestra el resultado |
| `/procesar-texto` | `POST` | Endpoint JSON para extraer variables clínicas desde texto |
| `/evaluar-pln` | `POST` | Ejecuta la evaluación clínica a partir del análisis PLN |
| `/historial` | `GET` | Listado completo de evaluaciones almacenadas |
| `/descargar-pdf/<evaluacion_id>` | `GET` | Descarga el informe clínico en formato PDF |
| `/eliminar/<evaluacion_id>` | `GET`, `POST` | Elimina un registro del historial |

---

## Aviso clínico

FisioGenu está diseñado como sistema de apoyo académico y de asistencia en la toma de decisiones fisioterapéuticas. Los resultados, clasificaciones de fase y planes sugeridos no sustituyen la valoración presencial ni el criterio diagnóstico de un profesional de la salud.
