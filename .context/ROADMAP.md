# ROADMAP.md — Plan de evolución SDD

> Proyecto: Sistema de Detección de Tuberculosis Asistida por IA
> Metodología: Spec-Driven Development
> Última actualización: 2026-10-24

## Criterios de priorización

1. **Seguridad clínica y de datos** antes que funcionalidad nueva.
2. **Estabilidad y reproducibilidad** antes que optimización.
3. **Pruebas automatizadas** como condición de cierre de cada fase.
4. **Cambios pequeños y verificables**, documentados en `DECISIONS.md`.

---

## Fase 1 — Hardening y estabilización (PRIORITARIA)

**Objetivo**: cerrar los riesgos críticos de seguridad, configuración y dependencias sin alterar el comportamiento funcional.

**Módulos / archivos**
- `requirements.txt`: añadir `python-dotenv`, `matplotlib`, driver PostgreSQL (`psycopg2-binary`) y separar dependencias de desarrollo.
- `config.py`: eliminar `SECRET_KEY` por defecto; fallar de forma segura si falta en producción; añadir configuración de `SESSION_COOKIE_*`.
- `app/__init__.py`: restringir `CORS` a orígenes permitidos; integrar `CSRFProtect`; manejador de errores sin filtrar detalles.
- `app/routes/auth.py`: validación de entrada, política mínima de contraseña, rate limiting de login, registro con institución explícita.
- `app/routes/api.py`: autorización por institución en `get_study_detail` y `update_diagnosis`; validación real de archivos (extensión + MIME/magic bytes); manejo explícito de DICOM; eliminar confianza hardcodeada.
- `app/services/ai_service.py`: carga perezosa del modelo, eliminar duplicación, manejo de errores controlado, soporte o rechazo explícito de DICOM.
- `run.py`, `Dockerfile`, `start.sh`: `debug` solo en desarrollo, servidor WSGI de producción, eliminar rutas absolutas.
- `.gitignore` / historial Git: **parcialmente completado (2026-10-24)**: `.env`, SQLite, imágenes, modelo y `model_summary.txt` purgados del historial; queda rotar secretos y migrar la inferencia local a la API.
- `README.md`: corregir estructura y rutas de demo.
- `tests/`: prueba de humo mínima de la aplicación y de carga de configuración.

**Entregable**: aplicación arrancable, sin secretos activos en el árbol de trabajo, con controles básicos de seguridad y una prueba de humo.

**Dependencias**: ninguna. Es la base para el resto.

---

## Fase 2 — Calidad y pruebas automatizadas

**Objetivo**: cubrir los flujos críticos y establecer una red de seguridad antes de refactorizar.

**Módulos / archivos**
- `tests/conftest.py`: fixtures de app, cliente, base de datos en memoria y usuario autenticado.
- `tests/test_auth.py`: registro, login, logout, credenciales inválidas, accesos no autenticados.
- `tests/test_api.py`: `predict` (mock del modelo), `studies`, `study_detail`, `update_diagnosis`; casos de autorización.
- `tests/test_ai_service.py`: preproceso, umbrales, Grad-CAM con modelo mockeado, archivo inválido.
- `tests/test_models.py`: relaciones, unicidad de expediente, cascadas.
- Configuración de `pytest`, cobertura y lint (`ruff`/`black` o equivalente).
- Workflow de CI (GitHub Actions) con lint + tests.
- Refactor de `app/models/__init__.py` en módulos si el volumen lo justifica (solo tras cobertura).

**Entregable**: suite verde, cobertura mínima acordada (≥70 % en rutas/servicio) y CI obligatorio.

**Dependencias**: Fase 1 completada.

---

## Fase 3 — Datos, migraciones y multi-institución

**Objetivo**: hacer la persistencia evolutiva, segura y consistente en producción.

**Módulos / archivos**
- Integrar Flask-Migrate/Alembic y versionar el esquema.
- Migrar de `db.create_all()` a migraciones controladas.
- Configurar PostgreSQL en producción y SQLite solo para desarrollo/pruebas.
- Índices en `pacientes.numero_expediente`, `estudios.paciente_id`, `estudios.fecha_estudio`, `resultados_ia.estudio_id`.
- Aislamiento por institución en consultas y endpoints.
- Modelo de auditoría (`auditoria`) para operaciones clínicas.
- Revisar borrado lógico/confidencialidad y retención de imágenes.

**Entregable**: esquema versionado, consultas acotadas por institución y migración reproducible.

**Dependencias**: Fase 2 (pruebas que validen la migración).

---

## Fase 4 — IA, evaluación y explicabilidad

**Objetivo**: convertir el modelo en un componente medible, versionado y configurable.

**Módulos / archivos**
- `app/services/ai_service.py`: umbrales configurables, calibración de confianza, registro de versión del modelo.
- `models_TB/`: pipeline documentado de entrenamiento/evaluación fuera de la app.
- Métricas verificables: accuracy, sensibilidad, especificidad, AUC, matriz de confusión.
- Evaluación de Grad-CAM y criterios de calidad del heatmap.
- Soporte real de DICOM (pydicom) o rechazo explícito en API y UI.
- Registro de `modelos_ia` con métricas y activación controlada.
- Pruebas de regresión del modelo con imágenes de referencia.

**Entregable**: modelo versionado con métricas reproducibles y umbrales configurables.

**Dependencias**: Fase 2. Puede ejecutarse en paralelo parcial con Fase 3.

---

## Fase 5 — Producto, operación y documentación

**Objetivo**: completar la experiencia clínica y la operabilidad.

**Módulos / archivos**
- Exportación de reportes PDF (funcionalidad anunciada en README, no implementada).
- Búsqueda/filtros avanzados de estudios y paginación.
- Roles y permisos (médico, administrador, auditor).
- Observabilidad: logging estructurado, health check, métricas.
- Endurecimiento de Docker (usuario no root, gunicorn, healthcheck).
- Documentación de API (OpenAPI) y manual de usuario.
- Internacionalización / accesibilidad de la interfaz.

**Entregable**: versión operable y documentada para un piloto clínico controlado.

**Dependencias**: Fases 1–4.

---

## Resumen de dependencias

```
Fase 1 ──► Fase 2 ──► Fase 3 ──► Fase 5
                   └──► Fase 4 ──┘
```

## Definición de terminado (global)

- Código y configuración revisados contra la checklist de seguridad.
- Pruebas automatizadas relevantes en verde.
- Sin secretos ni datos de pacientes en el repositorio.
- `STATE.md` y `DECISIONS.md` actualizados.
- Documentación de usuario/API afectada actualizada.
