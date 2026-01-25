/**
 * results.js
 * Gestión de la visualización de resultados de estudio
 */

$(document).ready(function () {
    loadStudyDetails();

    // Manejo de visibilidad de razones de desacuerdo
    $('#concordance').on('change', function () {
        if ($(this).is(':checked')) {
            $('#disagreement-reasons').addClass('d-none');
        } else {
            $('#disagreement-reasons').removeClass('d-none');
        }
    });

    // Envío del formulario de diagnóstico
    $('#diagnosis-form').on('submit', function (e) {
        e.preventDefault();

        const data = {
            study_id: studyId,
            diagnostico_final: $('#diag-final').val(),
            concordancia_ia: $('#concordance').is(':checked'),
            razones_desacuerdo: $('textarea[name="razones_desacuerdo"]').val(),
            notas_medico: $('#diag-notes').val()
        };

        $.ajax({
            url: '/api/update_diagnosis',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                alert('Diagnóstico guardado correctamente');
            },
            error: function () {
                alert('Error al guardar el diagnóstico');
            }
        });
    });

    // Controles de imagen (Zoom y Reset)
    let currentZoom = 1;
    const zoomStep = 0.2;
    const maxZoom = 3;
    const minZoom = 0.5;

    $('#zoom-in').on('click', function () {
        if (currentZoom < maxZoom) {
            currentZoom += zoomStep;
            updateImageTransform();
        }
    });

    $('#zoom-out').on('click', function () {
        if (currentZoom > minZoom) {
            currentZoom -= zoomStep;
            updateImageTransform();
        }
    });

    $('#zoom-reset').on('click', function () {
        currentZoom = 1;
        updateImageTransform();
    });

    function updateImageTransform() {
        $('.study-image, .heatmap-overlay').css('transform', `scale(${currentZoom})`);
    }

    // Toggle Mapa de Calor
    $('#toggle-heatmap').on('click', function () {
        const overlay = $('.heatmap-overlay');
        $(this).toggleClass('active btn-primary btn-outline-primary');
        overlay.toggle();
    });
});

function loadStudyDetails() {
    $.ajax({
        url: `/api/study/${studyId}`,
        method: 'GET',
        success: function (data) {
            // Info Paciente
            $('#patient-name').text(data.paciente.nombre);
            $('#patient-id').text(data.paciente.expediente);
            $('#patient-gender').text(data.paciente.genero === 'M' ? 'Masculino' : 'Femenino');
            $('#patient-age').text(data.paciente.edad + ' años');

            // Resultado IA
            $('#ai-results-content').removeClass('d-none');
            $('#ai-status-container').addClass('d-none');

            const prob = data.resultado_ia.probabilidad_tb;
            const probPct = (prob * 100).toFixed(1) + '%';

            $('#ai-probability').text(probPct);
            $('#ai-risk-bar').css('width', probPct);

            const badge = $('#ai-badge');
            const card = $('#ai-result-card');

            if (prob > 0.8) {
                badge.text('ALTO RIESGO').addClass('bg-danger');
                card.addClass('border-danger');
                $('#ai-risk-bar').addClass('bg-danger');
            } else if (prob > 0.4) {
                badge.text('RIESGO MODERADO').addClass('bg-warning text-dark');
                card.addClass('border-warning');
                $('#ai-risk-bar').addClass('bg-warning');
            } else {
                badge.text('NORMAL / BAJO RIESGO').addClass('bg-success');
                card.addClass('border-success');
                $('#ai-risk-bar').addClass('bg-success');
            }

            $('#model-version').text(data.resultado_ia.version_modelo);
            $('#model-confidence').text(data.resultado_ia.confianza_modelo);
            $('#ai-findings').text(data.resultado_ia.deteccion_tb ? 'Hallazgos sugerentes de TB' : 'Sin hallazgos significativos');

            // Imagen
            const imgContainer = $('#image-viewer');
            imgContainer.empty();
            imgContainer.append(`
                <img src="${data.estudio.imagen_url}" class="study-image" id="main-xray" alt="Radiografía del paciente">
                ${data.resultado_ia.mapa_calor_url ? `<img src="${data.resultado_ia.mapa_calor_url}" class="heatmap-overlay" id="heatmap-img">` : ''}
            `);

            // Mostrar botón de heatmap si existe
            if (data.resultado_ia.mapa_calor_url) {
                $('#toggle-heatmap').removeClass('d-none');
            }

            // Diagnóstico existente
            if (data.diagnostico) {
                $('#diag-final').val(data.diagnostico.final);
                $('#concordance').prop('checked', data.diagnostico.concordancia_ia).trigger('change');
                $('textarea[name="razones_desacuerdo"]').val(data.diagnostico.razones_desacuerdo);
                $('#diag-notes').val(data.diagnostico.notas_medico);
            }
        },
        error: function () {
            alert('Error al cargar los detalles del estudio');
        }
    });
}
