/**
 * upload.js
 * Manejo de carga de imágenes y previsualización
 */

$(document).ready(function () {
    const dropZone = $('#drop-zone');
    const input = $('#image-input');
    const form = $('#upload-form');
    const submitBtn = $('#submit-btn');
    const preview = $('#image-preview');
    const prompt = $('#upload-prompt');
    const fileInfo = $('#file-info');
    const overlay = $('.processing-overlay');

    // Trigger click on zone
    dropZone.on('click', function () {
        input.click();
    });

    // Drag and drop events
    dropZone.on('dragover', function (e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });

    dropZone.on('dragleave', function (e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });

    dropZone.on('drop', function (e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files[0]);
        }
    });

    input.on('change', function () {
        if (this.files.length > 0) {
            handleFiles(this.files[0]);
        }
    });

    function handleFiles(file) {
        // Validar tipo
        const allowed = ['image/jpeg', 'image/png', 'application/dicom'];
        // Nota: DCM a veces no tiene mime type en el navegador, validamos extensión
        const ext = file.name.split('.').pop().toLowerCase();

        if (!allowed.includes(file.type) && ext !== 'dcm') {
            alert('Formato de archivo no permitido. Use JPG, PNG o DICOM.');
            return;
        }

        // Mostrar previsualización (solo para imágenes)
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.attr('src', e.target.result).show();
                prompt.hide();
            };
            reader.readAsDataURL(file);
        } else {
            // Para DICOM mostramos un icono genérico
            preview.hide();
            prompt.html('<i class="fas fa-file-medical fa-3x mb-3 text-primary"></i><h5>Archivo DICOM Detectado</h5><p>' + file.name + '</p>').show();
        }

        // Mostrar info
        fileInfo.text(`Archivo: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`).removeClass('d-none');

        // Activar botón
        submitBtn.prop('disabled', false);

        // Adjuntar archivo al input del form (por si se usó drag & drop)
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input[0].files = dataTransfer.files;
    }

    // Submit form
    form.on('submit', function (e) {
        e.preventDefault();

        overlay.css('display', 'flex');

        const formData = new FormData(this);

        $.ajax({
            url: '/api/predict',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.success) {
                    window.location.href = `/results/${response.study_id}`;
                } else {
                    alert('Error: ' + response.error);
                    overlay.hide();
                }
            },
            error: function (xhr) {
                const error = xhr.responseJSON ? xhr.responseJSON.error : 'Error interno del servidor';
                alert('Error en el análisis: ' + error);
                overlay.hide();
            }
        });
    });
});
