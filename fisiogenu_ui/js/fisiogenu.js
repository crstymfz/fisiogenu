document.addEventListener("DOMContentLoaded", function () {
    initFormularioEstandar();
    initFormularioPln();
});

function initFormularioEstandar() {
    const form = document.getElementById("formEstandar");
    if (!form) return;

    const campos = form.querySelectorAll(".campo-clinico, #nombre, #edad, #sexo");
    const btnEvaluar = document.getElementById("btnEvaluar");
    const progressFill = document.getElementById("progressFill");

    function actualizarProgreso() {
        let completados = 0;
        campos.forEach(function (campo) {
            if (campo.value && campo.value.trim() !== "") {
                completados++;
            }
        });
        const porcentaje = Math.round((completados / campos.length) * 100);
        if (progressFill) {
            progressFill.style.width = porcentaje + "%";
        }
        if (btnEvaluar) {
            btnEvaluar.disabled = porcentaje < 100;
        }
    }

    campos.forEach(function (campo) {
        campo.addEventListener("change", actualizarProgreso);
        campo.addEventListener("input", actualizarProgreso);
    });

    form.addEventListener("reset", function () {
        setTimeout(actualizarProgreso, 0);
    });

    actualizarProgreso();
}

function initFormularioPln() {
    const btnAnalizar = document.getElementById("btnAnalizar");
    const textoClinico = document.getElementById("textoClinico");
    const panel = document.getElementById("panelDetectado");

    if (!btnAnalizar || !textoClinico || !panel) return;

    btnAnalizar.addEventListener("click", function () {
        analizarTextoPln(textoClinico.value, panel);
    });

    let debounceTimer;
    textoClinico.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () {
            if (textoClinico.value.trim().length > 20) {
                analizarTextoPln(textoClinico.value, panel);
            }
        }, 800);
    });
}

function analizarTextoPln(texto, panel) {
    if (!texto || texto.trim() === "") {
        panel.innerHTML =
            '<p class="text-muted mb-0 small"><i class="bi bi-info-circle me-1"></i>Escribe una descripción clínica para analizar.</p>';
        return;
    }

    panel.innerHTML =
        '<p class="text-muted mb-0 small"><i class="bi bi-hourglass-split me-1"></i>Analizando texto…</p>';

    const formData = new FormData();
    formData.append("texto", texto);

    fetch("/procesar-texto", {
        method: "POST",
        body: formData,
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            renderPanelDetectado(data, panel);
            aplicarValoresDetectados(data.detectados || {});
        })
        .catch(function () {
            panel.innerHTML =
                '<p class="text-danger mb-0 small"><i class="bi bi-exclamation-triangle me-1"></i>Error al procesar el texto.</p>';
        });
}

function renderPanelDetectado(data, panel) {
    const formateado = data.formateado || [];
    if (formateado.length === 0) {
        panel.innerHTML =
            '<p class="text-muted mb-0 small"><i class="bi bi-info-circle me-1"></i>No se detectaron variables clínicas. Completa los selects manualmente.</p>';
        return;
    }

    let html = '<p class="small fw-semibold mb-2"><i class="bi bi-check2-circle me-1"></i>Variables detectadas:</p><div>';
    formateado.forEach(function (item) {
        const confPct = Math.round(item.confianza * 100);
        html +=
            '<span class="variable-detectada">' +
            '<strong>' + item.etiqueta + ":</strong> " +
            item.valor +
            '<span class="confianza">' + confPct + "%</span>" +
            "</span>";
    });
    html += "</div>";
    panel.innerHTML = html;
}

function aplicarValoresDetectados(detectados) {
    Object.keys(detectados).forEach(function (variable) {
        const select = document.querySelector(
            '.campo-pln[data-variable="' + variable + '"]'
        );
        if (select && detectados[variable].valor) {
            select.value = detectados[variable].valor;
            select.classList.add("border-success");
        }
    });
}
