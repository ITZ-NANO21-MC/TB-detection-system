/**
 * Sistema de Detección de Tuberculosis
 * Script Principal - Gestión Global
 */

const tbApp = {
    // Configuración global
    config: {
        apiUrl: '/api',
        refreshInterval: 30000
    },

    // Notificaciones globales (usando estilo Toast de Bootstrap si está disponible)
    showNotification: function (message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // Implementación básica con alert por ahora
        // alert(message);
    },

    // Utilidades de formateo
    formatters: {
        date: function (dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        probability: function (val) {
            return (val * 100).toFixed(1) + '%';
        }
    }
};

// Manager para el Dashboard
const studiesManager = {
    loadStudies: function () {
        const tbody = $('#studies-tbody');
        if (!tbody.length) return;

        $.ajax({
            url: '/api/studies',
            method: 'GET',
            success: function (response) {
                tbody.empty();

                if (response.studies.length === 0) {
                    tbody.append('<tr><td colspan="7" class="text-center py-4 text-muted">No hay estudios registrados</td></tr>');
                    return;
                }

                response.studies.forEach(study => {
                    const priorityClass = {
                        'rutina': 'bg-success',
                        'urgente': 'bg-warning text-dark',
                        'critico': 'bg-danger'
                    }[study.prioridad] || 'bg-secondary';

                    const row = `
                        <tr>
                            <td>${study.fecha}</td>
                            <td class="fw-bold">${study.paciente}</td>
                            <td><code>${study.expediente}</code></td>
                            <td>${study.diagnostico}</td>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="progress flex-grow-1 me-2" style="height: 6px;">
                                        <div class="progress-bar" style="width: ${study.confianza * 100}%"></div>
                                    </div>
                                    <span>${(study.confianza * 100).toFixed(0)}%</span>
                                </div>
                            </td>
                            <td><span class="badge ${priorityClass}">${study.prioridad.toUpperCase()}</span></td>
                            <td>
                                <a href="/results/${study.id}" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-eye"></i> Detalle
                                </a>
                            </td>
                        </tr>
                    `;
                    tbody.append(row);
                });

                // Actualizar contadores
                $('#total-studies').text(response.studies.length);
                $('#tb-cases').text(response.studies.filter(s => s.diagnostico === 'Tuberculosis').length);
                $('#normal-cases').text(response.studies.filter(s => s.diagnostico === 'Normal').length);
            },
            error: function () {
                tbApp.showNotification('Error al cargar estudios', 'danger');
            }
        });
    }
};
