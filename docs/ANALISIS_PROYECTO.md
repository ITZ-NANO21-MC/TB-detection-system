# Informe de análisis profundo — TB Detection System

> Comando: `/analyze --deep`
> Fecha: 2026-10-24
> Analista: Arquitecto de software / auditor técnico
> Alcance: código, configuración, plantillas, assets, esquema de datos, historial Git y artefactos de despliegue.

> **Nota de vigencia**: este informe describe el estado **previo** a la limpieza y reestructuración del repositorio. El 2026-10-24 se purgaron del historial `.env`, bases SQLite, imágenes médicas, `model_summary.txt` y `models_TB/tb_model.h5`; `Demo/` fue eliminado. El repositorio pasó de ~46 MiB a ~1.3 MiB. Las credenciales fueron rotadas. `requirements.txt` se redujo al stack base de UI/UX; los extras de inferencia local se movieron a `requirements-local-model.txt`. La UI ahora puede arrancar sin TensorFlow. El modelo debe consumirse desde `TB-prediction-model` por API.

---

## 1. Resumen ejecutivo

| Campo | Valor |
|---|---|
| Nombre | Sistema de Detección de Tuberculosis Asistida por IA |
| Tipo | Aplicación web monolítica con inferencia ML (Flask + TensorFlow) |
| Estado general | **Medio**, funcional en local pero no listo para producción clínica |
| Madurez | MVP avanzado / prototipo con funcionalidad de extremo a extremo |
| Deuda técnica | **Alta** |
| Riesgo de seguridad | **Alto** |
| Cobertura de pruebas | 0 % |

El sistema implementa un flujo completo: registro/login de médicos, alta de pacientes, subida de radiografía, inferencia con DenseNet121, generación de Grad-CAM, persistencia de resultados y registro del diagnóstico médico. La arquitectura es comprensible y la separación por blueprints/servicios es adecuada para el tamaño actual.

Los bloqueos principales no son funcionales sino de **seguridad, reproducibilidad y calidad**: secretos y datos clínicos versionados, ausencia de pruebas y migraciones, endpoints sin aislamiento por institución, CORS abierto, falta de CSRF y un pipeline que declara DICOM pero no lo procesa.

---

## 2. Arquitectura

### 2.1 Capas identificadas

```
Navegador (Jinja2 + Bootstrap + jQuery)
        │  HTML / AJAX JSON
        ▼
Flask application factory (app/__init__.py)
        │
        ├── Blueprints
        │   ├── main  → vistas HTML
        │   ├── auth  → sesión (Flask-Login)
        │   └── api   → JSON (predict, studies, diagnosis)
        │
        ├── Servicio de IA (app/services/ai_service.py)
        │   └── TensorFlow/Keras + Grad-CAM + Pillow/Matplotlib
        │
        └── Persistencia (Flask-SQLAlchemy)
            └── SQLite (dev) / PostgreSQL (declarado, no configurado)
```

### 2.2 Patrón de diseño

- **MVC parcial**: rutas + plantillas + modelos ORM. La lógica de IA está extraída a un servicio, pero parte de la lógica de negocio vive en `api.py` (creación de paciente/estudio/resultado/diagnóstico dentro del endpoint `predict`).
- **Application factory** y **blueprints**: correcto y extensible.
- **Repository pattern**: no existe; los modelos se consultan directamente desde las rutas.
- **Service layer**: solo para IA; no hay servicios de dominio para pacientes/estudios/diagnósticos.
- **Dependencias globales**: `inference_service` se instancia y carga el modelo al importar `api.py` (`app/routes/api.py:15-18`), lo que acopla el arranque web a TensorFlow.

### 2.3 Estructura y modularidad

- `app/models/__init__.py` concentra las 7 entidades (~150 líneas). Aceptable hoy, pero conviene dividir cuando se añadan índices, migraciones y auditoría.
- `api.py` concentra validación, persistencia, orquestación y formateo de respuesta. Es el principal candidato a refactor por servicios.
- No hay carpeta `tests/`, `migrations/`, `scripts/` ni configuración de lint/CI.
- Frontend separado por página (`app.js`, `upload.js`, `results.js`) con jQuery y AJAX; consistente pero con concatenación de HTML.

### 2.4 Flujo de una predicción

1. `POST /api/predict` recibe imagen + datos del paciente (requiere login).
2. Guarda el archivo con `secure_filename` + UUID en `app/static/uploads/`.
3. Crea/recupera `Paciente` por `numero_expediente`.
4. Ejecuta `TBInference.predict()` (preproceso 224×224, sigmoide, Grad-CAM).
5. Persiste `Estudio`, `ResultadoIA`, `ModeloIA` (si no existe) y `Diagnostico` inicial.
6. Devuelve `study_id`; el frontend redirige a `/results/<id>`.

---

## 3. Stack tecnológico

### 3.1 Backend

- Python 3.8+ (entorno local observado: 3.12).
- Flask 2.3.3, Flask-SQLAlchemy 3.0.5, Flask-Login 0.6.3, Flask-CORS 4.0.0, Flask-WTF 1.2.2.
- Werkzeug 2.3.7.
- TensorFlow/Keras 2.13.0, NumPy 1.24.3, Pillow 10.0.0, OpenCV 4.8.1.78.
- SQLite (dev). PostgreSQL declarado en README sin driver instalado.

### 3.2 Frontend

- Jinja2, Bootstrap 5.3 (CDN), jQuery 3.6 (CDN), Font Awesome 6.4 (CDN), Google Fonts (Inter).
- Chart.js mencionado en README, no importado en las plantillas.
- JS propio: `app.js` (dashboard), `upload.js` (drag & drop + AJAX), `results.js` (detalle, zoom, heatmap, diagnóstico).

### 3.3 Herramientas de desarrollo

- Docker (`python:3.10-slim`) + `start.sh` local con ruta absoluta.
- Sin CI/CD, sin linter/formatter configurado, sin gestor de migraciones, sin suite de pruebas.
- `requirements.txt` incompleto:
  - `config.py:3` importa `dotenv`, pero `python-dotenv` no está en requirements.
  - `ai_service.py:5` importa `matplotlib.cm`, pero `matplotlib` no está en requirements.
  - No hay driver PostgreSQL (`psycopg2`/`asyncpg`).
  - `Flask-WTF` está instalado pero no se usa (no hay `CSRFProtect` ni `FlaskForm`).

### 3.4 Modelo

- DenseNet121 + GlobalAveragePooling + BatchNorm + Dense/Dropout.
- ~7.18 M parámetros (3.03 M entrenables), entrada 224×224 RGB.
- Artefacto `models_TB/tb_model.h5` (~? MB) versionado en Git.
- No hay script de entrenamiento, dataset, métricas reproducibles ni evaluación en el repositorio.
- Las métricas del README (95 % precisión, 93 % sensibilidad, 96 % especificidad) no tienen evidencia verificable en el código.

---

## 4. Estado del proyecto

- **Fase inferida**: MVP funcional con deuda de hardening.
- **Módulos completados**: autenticación básica, dashboard, carga, inferencia, Grad-CAM, persistencia, perfil, Dockerfile.
- **Módulos parciales**: multi-institución (solo se asigna la primera institución), DICOM (se acepta pero no se procesa), exportación de informes (solo `window.print()`), auditoría (no existe), confianza del modelo (hardcodeada a 0.95).
- **Estado Git observado**:
  - Cambios preparados (staged): `.gitignore` modificado y eliminación de `model_summary.txt` y `tb_detection.db` del índice.
  - `.env` figura como archivo versionado (`git ls-files`).
  - También están versionados `instance/tb_detection.db`, `models_TB/tb_model.h5` y 11 imágenes en `app/static/uploads/`.
- **Base de datos local**:
  - `instance/tb_detection.db`: 7 tablas, 14 estudios, 14 resultados, 14 diagnósticos, 13 pacientes, 2 usuarios, 1 institución, 1 modelo.
  - `tb_detection.db` (raíz): 6 tablas, 2 estudios; parece un artefacto antiguo duplicado.
- **Deuda técnica estimada**: alta.

---

## 5. Funcionalidades

### 5.1 Implementadas

| Funcionalidad | Evidencia |
|---|---|
| Landing pública | `app/templates/index.html` |
| Registro de médicos | `app/routes/auth.py` (`/register`) |
| Login/logout con sesión | `auth.py` + Flask-Login |
| Dashboard con listado de estudios y contadores | `dashboard.html`, `app.js` |
| Perfil de médico editable | `profile.html`, `POST /api/update_profile` |
| Subida con drag & drop y validación de extensión | `upload.js`, `upload.html` |
| Inferencia binaria TB/Normal | `ai_service.py` |
| Grad-CAM semitransparente | `ai_service.py` (`generate_gradcam`) |
| Persistencia de paciente/estudio/resultado/diagnóstico | `api.py` (`predict`) |
| Detalle de estudio con imagen y heatmap | `GET /api/study/<id>`, `results.js` |
| Actualización del diagnóstico médico | `POST /api/update_diagnosis` |
| Prioridad de estudio (rutina/urgente/crítico) | modelo `Estudio`, UI |
| Dockerfile | `Dockerfile` |

### 5.2 Pendientes o anunciadas sin implementar

- Exportación real de reportes PDF (solo impresión del navegador).
- Registro de auditoría de operaciones.
- Roles/permisos (médico, administrador, auditor).
- Aislamiento efectivo multi-institución.
- Soporte real de DICOM.
- Recuperación de contraseña y verificación de email.
- Búsqueda avanzada, filtros y paginación.
- Métricas del modelo y evaluación reproducible.
- Pruebas automatizadas, CI/CD, observabilidad y health checks.
- `Chart.js` anunciado en README, no utilizado.

---

## 6. Estilo de código

### 6.1 Fortalezas

- Nombres claros y consistentes; dominio en español en BD y UI, inglés en código.
- Uso correcto de application factory, blueprints y `@login_required`.
- `secure_filename` + UUID para archivos.
- Hash de contraseñas con Werkzeug (`set_password`/`check_password`).
- Manejo transaccional con `commit`/`rollback` en la mayoría de endpoints.
- Docstrings breves y comentarios en español.

### 6.2 Problemas detectados

- `api.py` mezcla orquestación, persistencia y reglas de negocio (endpoint `predict` ~100 líneas).
- Duplicación en `ai_service.py`: `heatmap_path = None` repetido (`ai_service.py:59-61`).
- `print()` en lugar de `logging` (`ai_service.py`).
- Excepciones genéricas capturadas y devueltas al cliente (`api.py:57`, `api.py:253`).
- Confianza simulada hardcodeada: `confianza_modelo=0.95` (`api.py:132`).
- Umbral de riesgo inconsistente: backend `>0.5` medio (`ai_service.py:71`) vs frontend `>0.4` moderado (`results.js`).
- `debug=True` fijo en `run.py:7`.
- Ruta absoluta de entorno en `start.sh`.
- README desactualizado: describe `app.py`, `model.py`, `database.py` y `static/` en raíz, que no existen; las rutas de la demo son incorrectas.
- Sin LICENSE pese a declarar MIT.
- Sin `.env.example` pese a que el README lo indica.
- CDNs sin integridad (SRI) y dependencia de red externa.

---

## 7. Seguridad

### 7.1 Hallazgos por severidad

| # | Severidad | Hallazgo | Evidencia | Impacto |
|---|---|---|---|---|
| S1 | **Crítica** | `.env` versionado con `SECRET_KEY` y `DATABASE_URL` | `git ls-files` incluye `.env`; `.env` en raíz | Compromiso de sesiones y credenciales de BD |
| S2 | **Crítica** | Clave secreta por defecto en código | `config.py:11` | Falsificación de sesiones si no hay `.env` |
| S3 | **Crítica** | Datos clínicos y BD versionados | `instance/tb_detection.db`, `app/static/uploads/*` en Git | Exposición de datos de pacientes en el historial |
| S4 | **Alta** | Sin autorización por institución (IDOR) | `api.py:184`, `api.py:229` usan `get_or_404` sin filtrar por `institucion_id` | Un médico puede leer/modificar estudios de otra institución |
| S5 | **Alta** | CORS completamente abierto | `app/__init__.py:18` `CORS(app)` | APIs accesibles desde cualquier origen |
| S6 | **Alta** | Sin protección CSRF | `Flask-WTF` instalado pero no integrado; formularios AJAX sin token | Acciones no deseadas en sesión autenticada |
| S7 | **Alta** | Imágenes médicas servidas públicamente | `url_for('static', filename='uploads/...')` | Acceso no autenticado a radiografías |
| S8 | **Alta** | XSS almacenado en dashboard | `app.js:64-78` inserta datos en HTML con template strings | Ejecución de scripts desde nombres/diagnósticos |
| S9 | **Alta** | Validación de subida solo por extensión | `api.py:19-21`, `upload.js` | Archivos maliciosos o no-imagen aceptados |
| S10 | **Media** | Sin rate limiting en login/registro | `auth.py` | Fuerza bruta y abuso |
| S11 | **Media** | Errores internos filtrados al cliente | `api.py:57`, `api.py:253` | Divulgación de detalles de implementación |
| S12 | **Media** | `debug=True` y servidor de desarrollo en contenedor | `run.py:7`, `Dockerfile` | Debugger interactivo / información sensible |
| S13 | **Media** | Validación de contraseña/email insuficiente | `auth.py` | Cuentas débiles; registros inválidos |
| S14 | **Media** | Registro asigna la primera institución sin control | `auth.py` (`Institucion.query.first()`) | Asignación incorrecta y cruce de datos |
| S15 | **Baja** | Cookies sin flags explícitos | `config.py` | Mayor superficie de secuestro de sesión |
| S16 | **Baja** | DICOM aceptado pero no procesado | `config.py:32`, `ai_service.py` (Pillow) | Fallo en tiempo de ejecución percibido como error del sistema |
| S17 | **Baja** | Sin cabeceras de seguridad (CSP, HSTS, X-Frame-Options) | `app/__init__.py` | Clickjacking, inyección de contenido |

### 7.2 Observaciones adicionales

- El uso de ORM reduce el riesgo de inyección SQL; no se detectaron consultas SQL construidas con interpolación.
- `secure_filename` + UUID mitiga path traversal en la subida.
- El heatmap se guarda en la misma carpeta pública que la imagen original.
- No hay gestión de secretos por entorno ni rotación documentada.
- El historial de Git conserva los secretos y datos aunque se eliminen del árbol actual; se requiere rotación y, idealmente, reescritura del historial.

---

## 8. Plan de continuación

### 8.1 Prioridad inmediata (Fase 1)

1. **Rotar secretos** y sacar `.env` del control de versiones; añadir `.env.example`.
2. **Eliminar datos clínicos, BD y modelo del repositorio**; documentar su obtención.
3. Corregir `requirements.txt` (`python-dotenv`, `matplotlib`, driver PostgreSQL; separar dev/prod).
4. Restringir CORS, integrar CSRF, añadir rate limiting y flags de cookies.
5. Implementar autorización por institución en todos los endpoints de estudio/diagnóstico.
6. Validar archivos por contenido y resolver DICOM de forma explícita.
7. Escapar datos en el frontend y eliminar confianza hardcodeada.
8. Poner `debug=False` en producción y usar gunicorn en Docker.
9. Añadir una prueba de humo y un health check.

### 8.2 Siguiente (Fases 2–5)

- **Fase 2**: suite `pytest`, fixtures, mocks del modelo, CI con lint + tests.
- **Fase 3**: Flask-Migrate/Alembic, PostgreSQL, índices, auditoría, aislamiento multi-institución.
- **Fase 4**: métricas reproducibles del modelo, umbrales configurables, versión/registro de modelo, soporte DICOM real.
- **Fase 5**: PDF real, roles, observabilidad, Docker hardening, OpenAPI y manual de usuario.

### 8.3 Refactorizaciones recomendadas

- Extraer `EstudioService`/`PacienteService`/`DiagnosticoService` y adelgazar `api.py`.
- Dividir `app/models/__init__.py` por agregado al introducir migraciones.
- Centralizar constantes de umbrales y configuración del modelo.
- Sustituir `print` por `logging` estructurado.
- Unificar el cálculo de riesgo entre backend y frontend.

### 8.4 Mejoras del flujo de desarrollo

- Adoptar Conventional Commits (ya documentado en README).
- Ejecutar `/plan-phase --phase 1` y trabajar por tareas en `.tasks/`.
- Usar los roles de `.prompts/` para separar diseño, implementación y validación.
- Registrar cada decisión relevante en `.context/DECISIONS.md`.
- Revisar seguridad con `/audit` antes de cada release.

---

## 9. Conclusión

El proyecto tiene una base funcional sólida y un flujo clínico completo, pero **no está listo para manejar datos reales de pacientes**. La adopción SDD debe comenzar por la Fase 1 (seguridad y estabilidad), sin añadir funcionalidad nueva hasta cerrar los hallazgos críticos y altos. La inversión en pruebas y migraciones en las fases siguientes permitirá evolucionar el sistema con bajo riesgo.
