

import io
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import database
from base_hechos import crear_hechos, validar_hechos
from motor_inferencia import inferir_fase, generar_explicacion_natural
from motor_pln import procesar_texto as procesar_texto_pln
from motor_pln import obtener_resultado_formateado as formatear_pln
from motor_pln_llm import procesar_texto as procesar_texto_llm
from motor_pln_llm import obtener_resultado_formateado as formatear_llm
from generar_pdf import EvaluacionPDF
from motor_recomendaciones_ia import generar_recomendaciones as generar_recomendaciones_ia

app = Flask(
    __name__,
    template_folder="fisiogenu_ui",
    static_folder="fisiogenu_ui",
)

database.inicializar_bd()


def _ejecutar_evaluacion(hechos, datos_paciente, metodo):
    valido, errores = validar_hechos(hechos)
    if not valido:
        return None, errores

    fase, explicacion_tecnica, recomendaciones = inferir_fase(hechos)
    hechos_con_nombre = {**hechos, "nombre_paciente": datos_paciente.get("nombre", "el paciente")}
    explicacion_natural = generar_explicacion_natural(hechos_con_nombre, fase)

    recs_ia, extra_ia = generar_recomendaciones_ia(
        hechos, fase, datos_paciente.get("nombre", "el paciente")
    )
    recomendaciones_finales = recs_ia if recs_ia else recomendaciones
    usa_ia = recs_ia is not None

    datos_guardar = {
        "nombre": datos_paciente.get("nombre"),
        "edad": datos_paciente.get("edad"),
        "sexo": datos_paciente.get("sexo"),
        **hechos,
        "fase_detectada": fase,
        "explicacion_tecnica": explicacion_tecnica,
        "explicacion_natural": explicacion_natural,
        "recomendaciones": recomendaciones_finales,
        "metodo_evaluacion": metodo,
    }
    evaluacion_id = database.guardar_evaluacion(datos_guardar)

    return {
        "id": evaluacion_id,
        "nombre": datos_paciente.get("nombre"),
        "edad": datos_paciente.get("edad"),
        "sexo": datos_paciente.get("sexo"),
        "hechos": hechos,
        "fase": fase,
        "explicacion_tecnica": explicacion_tecnica,
        "explicacion_natural": explicacion_natural,
        "recomendaciones": recomendaciones_finales,
        "recomendaciones_ia": usa_ia,
        "explicacion_ia": extra_ia if extra_ia else None,
        "metodo_evaluacion": metodo,
    }, None


@app.route("/")
def index():
    ultimas = database.obtener_historial(5)
    return render_template("index.html", evaluaciones=ultimas)


@app.route("/formulario-estandar")
def formulario_estandar():
    return render_template("formulario_estandar.html")


@app.route("/formulario-pln")
def formulario_pln():
    return render_template("formulario_pln.html")


@app.route("/historial")
def historial():
    todas = database.obtener_historial()
    return render_template("historial.html", evaluaciones=todas)


@app.route("/evaluar", methods=["POST"])
def evaluar():
    datos_paciente = {
        "nombre": request.form.get("nombre", "").strip(),
        "edad": request.form.get("edad"),
        "sexo": request.form.get("sexo", "").strip(),
    }
    hechos = crear_hechos(request.form)
    resultado, errores = _ejecutar_evaluacion(hechos, datos_paciente, "estandar")
    if errores:
        return render_template(
            "formulario_estandar.html",
            errores=errores,
            datos=request.form,
        ), 400
    return render_template("resultado.html", evaluacion=resultado)


@app.route("/evaluar-pln", methods=["POST"])
def evaluar_pln():
    texto = request.form.get("texto_clinico", "")

    datos_paciente = {
        "nombre": request.form.get("nombre", "").strip(),
        "edad": request.form.get("edad"),
        "sexo": request.form.get("sexo", "").strip(),
    }

    hechos_pln = procesar_texto_llm(texto) or procesar_texto_pln(texto)
    hechos_form = crear_hechos(request.form)

    hechos = {}
    for variable in hechos_form:
        if hechos_form.get(variable):
            hechos[variable] = hechos_form[variable]
        elif variable in hechos_pln:
            hechos[variable] = hechos_pln[variable]["valor"]
        else:
            hechos[variable] = ""

    resultado, errores = _ejecutar_evaluacion(hechos, datos_paciente, "pln")
    if errores:
        return render_template(
            "formulario_pln.html",
            errores=errores,
            datos=request.form,
            texto_clinico=texto,
        ), 400
    return render_template("resultado.html", evaluacion=resultado)


@app.route("/eliminar/<int:evaluacion_id>", methods=["POST"])
def eliminar(evaluacion_id):
    database.eliminar_evaluacion(evaluacion_id)
    return redirect(url_for("historial"))


@app.route("/descargar-pdf/<int:evaluacion_id>")
def descargar_pdf(evaluacion_id):
    todas = database.obtener_historial()
    ev = next((e for e in todas if e["id"] == evaluacion_id), None)
    if not ev:
        return "Evaluacion no encontrada", 404
    pdf_buffer = io.BytesIO(bytes(EvaluacionPDF().generar(ev).output()))
    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"fisiogenu_{evaluacion_id}.pdf",
    )


@app.route("/procesar-texto", methods=["POST"])
def procesar_texto_endpoint():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        texto = data.get("texto", "")
    else:
        texto = request.form.get("texto", "")
    detectados = procesar_texto_llm(texto)
    if detectados is not None:
        formateado = formatear_llm()
        metodo = "ia"
    else:
        detectados = procesar_texto_pln(texto)
        formateado = formatear_pln()
        metodo = "patrones"
    return jsonify({
        "detectados": detectados,
        "formateado": formateado,
        "metodo": metodo,
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
