import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fisiogenu.db")


def obtener_conexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_bd():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER,
            sexo TEXT,
            dolor TEXT,
            edema TEXT,
            rango_articular TEXT,
            fuerza_muscular TEXT,
            capacidad_funcional TEXT,
            tolerancia_carga TEXT,
            estabilidad_rodilla TEXT,
            fase_detectada TEXT,
            explicacion_tecnica TEXT,
            explicacion_natural TEXT,
            recomendaciones TEXT,
            metodo_evaluacion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def guardar_evaluacion(datos):
    conn = obtener_conexion()
    cursor = conn.cursor()
    recomendaciones = "|".join(datos.get("recomendaciones", []))
    cursor.execute("""
        INSERT INTO evaluaciones (
            nombre, edad, sexo, dolor, edema, rango_articular,
            fuerza_muscular, capacidad_funcional, tolerancia_carga,
            estabilidad_rodilla, fase_detectada, explicacion_tecnica,
            explicacion_natural, recomendaciones, metodo_evaluacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos.get("nombre"),
        datos.get("edad"),
        datos.get("sexo"),
        datos.get("dolor"),
        datos.get("edema"),
        datos.get("rango_articular"),
        datos.get("fuerza_muscular"),
        datos.get("capacidad_funcional"),
        datos.get("tolerancia_carga"),
        datos.get("estabilidad_rodilla"),
        datos.get("fase_detectada"),
        datos.get("explicacion_tecnica"),
        datos.get("explicacion_natural"),
        recomendaciones,
        datos.get("metodo_evaluacion"),
    ))
    evaluacion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return evaluacion_id


def eliminar_evaluacion(evaluacion_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluaciones WHERE id = ?", (evaluacion_id,))
    conn.commit()
    conn.close()


def obtener_historial(limite=None):
    conn = obtener_conexion()
    cursor = conn.cursor()
    if limite:
        cursor.execute(
            "SELECT * FROM evaluaciones ORDER BY fecha DESC LIMIT ?",
            (limite,),
        )
    else:
        cursor.execute("SELECT * FROM evaluaciones ORDER BY fecha DESC")
    filas = cursor.fetchall()
    conn.close()
    resultado = []
    for fila in filas:
        item = dict(fila)
        if item.get("recomendaciones"):
            item["recomendaciones_lista"] = item["recomendaciones"].split("|")
        else:
            item["recomendaciones_lista"] = []
        resultado.append(item)
    return resultado
