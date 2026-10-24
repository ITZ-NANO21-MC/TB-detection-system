# PATTERNS.md — Guía de implementación y convenciones

> Patrones observados en el proyecto legado y patrones objetivo a aplicar en nuevas implementaciones.
> Si una implementación nueva se desvía de esta guía, debe justificarse en `DECISIONS.md`.

## 1. Convenciones generales

- **Idioma de identificadores**: inglés (`predict`, `study_id`, `password_hash`).
- **Idioma de dominio en BD**: español (`pacientes`, `estudios`, `numero_expediente`). Mantener consistencia; no renombrar tablas sin migración y ADR.
- **Idioma de UI, comentarios y documentación**: español.
- **Formato**: PEP 8, 4 espacios, líneas ≤ 100 caracteres.
- **Docstrings**: una línea para funciones simples; estilo Google para lógica compleja.
- **Comentarios**: solo cuando aclaran intención o una restricción; no repetir el código.
- **Secretos**: siempre por variables de entorno; nunca en código, logs, fixtures ni repositorio.
- **Fechas**: almacenar en UTC (`datetime.utcnow()`); formatear en la capa de presentación.
- **IDs**: UUID v4 como string (`generate_uuid()`), mantener el patrón existente.

## 2. Backend — capas

```
routes (HTTP)  →  services (lógica)  →  models (persistencia)
      │                    │
      └── validación de entrada y formato de respuesta
```

### 2.1 Routes / Blueprints

- Un blueprint por área: `main` (vistas), `auth` (sesión), `api` (JSON).
- Las rutas **no** contienen lógica de negocio ni de IA: delegan en servicios.
- Usar `@login_required` en toda ruta clínica.
- Devolver JSON consistente:

```python
return jsonify({'success': True, 'data': payload}), 200
return jsonify({'error': 'Mensaje apto para el usuario'}), 400
```

- Códigos: `400` entrada inválida, `401` no autenticado, `403` sin permiso, `404` no encontrado, `413` archivo grande, `500` error interno.
- No exponer `str(e)` al cliente. Registrar el detalle en servidor y devolver un mensaje genérico.

### 2.2 Services

- Toda lógica de IA, archivos o reglas de negocio vive en `app/services/`.
- El servicio no conoce Flask (`request`, `jsonify`); recibe rutas y datos primitivos.
- Carga perezosa de recursos costosos (modelo Keras) y una única instancia reutilizable.
- Errores de dominio mediante excepciones propias (`InferenceError`, `InvalidImageError`) capturadas en la ruta.

### 2.3 Models

- Un archivo por agregado cuando el volumen lo justifique (objetivo: Fase 2).
- Definir `__tablename__` explícito en español.
- Relaciones con `backref` y `lazy` explícitos.
- Añadir índices a columnas de búsqueda frecuente (`numero_expediente`, `paciente_id`, `fecha_estudio`).
- La validación de datos vive en el servicio o en el esquema de entrada, no solo en la BD.
- No crear tablas en el arranque en producción; usar migraciones (Fase 3).

### 2.4 Transacciones

```python
try:
    db.session.add(entity)
    db.session.flush()
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

- `flush()` cuando se necesita el ID antes del commit.
- Nunca dejar una transacción abierta entre capas.

## 3. Validación de entrada

- Validar en el borde (ruta/servicio) antes de tocar la BD o el modelo.
- Archivos: extensión permitida **y** tipo MIME/magic bytes; tamaño máximo 16 MB.
- DICOM: validar con `pydicom` o rechazar explícitamente con mensaje claro.
- Strings: recortar, limitar longitud y rechazar vacíos donde sean obligatorios.
- Email: validación de formato; contraseña: longitud mínima y no almacenar nunca en claro.
- Autorización: comprobar que el recurso pertenece a `current_user.institucion_id` antes de leer o modificar.

## 4. Manejo de errores y logging

- Registrar en servidor con `logging` (no `print`), incluyendo `request_id` cuando exista.
- Niveles: `INFO` para eventos clínicos, `WARNING` para entradas inválidas, `ERROR` para fallos.
- No registrar datos personales de pacientes, rutas completas ni secretos.
- El cliente recibe un mensaje comprensible y un código HTTP adecuado.

## 5. Seguridad — patrones obligatorios

- **Autenticación**: Flask-Login; `login_user`, `logout_user`, `@login_required`.
- **Contraseñas**: `generate_password_hash`/`check_password_hash` (ya usado). Añadir política mínima y rate limiting.
- **CSRF**: `CSRFProtect` de Flask-WTF en formularios y endpoints mutables; para AJAX, enviar token en cabecera.
- **CORS**: lista blanca explícita de orígenes; nunca `CORS(app)` abierto en producción.
- **Cookies**: `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'`, `SESSION_COOKIE_SECURE=True` en producción.
- **Subidas**: `secure_filename` + UUID (patrón existente), almacenamiento fuera de rutas públicas o servido con autorización.
- **XSS**: escapar todo dato dinámico; preferir `textContent`/`.text()` sobre HTML concatenado; si se usa plantilla, escapar valores.
- **SQL**: usar ORM/consultas parametrizadas; nunca interpolar entrada en SQL.
- **Errores**: no filtrar trazas ni configuración.
- **Producción**: `debug=False`, gunicorn/uWSGI, usuario no root en Docker, HTTPS en el proxy.

## 6. Frontend

### 6.1 Organización

- Plantillas Jinja2 en `app/templates/`, heredando de `base.html`.
- Bloques disponibles: `title`, `extra_css`, `content`, `extra_js`.
- Scripts específicos por página en `{% block extra_js %}`.
- CSS propio en `app/static/css/style.css`; estilos de página en `{% block extra_css %}` solo si son exclusivos.

### 6.2 JavaScript

- jQuery + AJAX es el patrón existente; mantenerlo hasta que exista una decisión de migración.
- Un archivo por página (`upload.js`, `results.js`) y utilidades globales en `app.js`.
- Llamadas AJAX con manejo explícito de `success` y `error`.
- No construir HTML con datos del servidor sin escapar; usar `.text()` o una función `escapeHtml`.
- Mostrar estados de carga y deshabilitar botones durante operaciones.

### 6.3 UI

- Bootstrap 5 como sistema base; clases utilitarias antes que CSS nuevo.
- Paleta: primario `#0d6efd`, fondos `#f5f7fb`, texto `#334155`.
- Tipografía: Inter (Google Fonts).
- Componentes: cards con `shadow-sm border-0`, badges para prioridad/riesgo, barras de progreso para probabilidad.
- Accesibilidad: `alt` en imágenes, `label` asociado a inputs, foco visible, contraste suficiente.
- Mensajes clínicos: tono sobrio, sin alarmismo; incluir descargo de responsabilidad en resultados.

## 7. Pruebas

### 7.1 Herramientas objetivo

- `pytest` + `pytest-flask` + fixtures de app/cliente.
- `unittest.mock` o `monkeypatch` para el modelo de IA (no cargar TensorFlow en tests unitarios).
- Cobertura con `pytest-cov`.

### 7.2 Estructura

```
tests/
├── conftest.py          # app, client, db en memoria, usuario autenticado
├── test_auth.py
├── test_api.py
├── test_models.py
└── test_ai_service.py
```

### 7.3 Reglas

- Cada bug corregido incorpora una prueba de regresión.
- Los tests no dependen de red, archivos externos ni del modelo real.
- Usar base de datos SQLite en memoria y limpiar entre tests.
- Nombrar: `test_<acción>_<condición>_<resultado esperado>`.
- Un test debe fallar por una razón clara.

## 8. Machine Learning

- Preproceso centralizado en `TBInference.preprocess_image`: RGB, 224×224, escala [0, 1].
- No duplicar lógica de preproceso en rutas ni scripts.
- Umbrales de decisión en configuración, no dispersos en código.
- Registrar versión del modelo y métricas en `modelos_ia`.
- Grad-CAM: última capa convolucional, normalización `max > 0`, salida PNG.
- Mantener separado el código de entrenamiento/evaluación del código de inferencia.
- No afirmar métricas en README sin un artefacto reproducible que las respalde.

## 9. Archivos y almacenamiento

- Nombre único: `{uuid}_{secure_filename(original)}`.
- Guardar en `Config.UPLOAD_FOLDER`.
- El heatmap se guarda junto a la imagen con prefijo `heatmap_`.
- Registrar solo el nombre/ruta relativa en BD.
- No servir imágenes médicas por `/static` sin control de acceso (objetivo de Fase 1/3).
- Limpiar archivos huérfanos mediante tarea programada (Fase 5).

## 10. Base de datos

- SQLite para desarrollo/pruebas; PostgreSQL para producción.
- JSON: usar `sqlalchemy.JSON` (portable) o `JSONB` en PostgreSQL si se requiere consulta.
- Fechas: `DateTime` UTC; `Date` solo para fechas sin hora.
- Migraciones: Alembic/Flask-Migrate, nunca cambios manuales en producción.
- Datos semilla solo en desarrollo; nunca pacientes reales en fixtures.

## 11. Git y commits

- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Un commit = un cambio lógico.
- No commitear `.env`, bases de datos, modelos pesados ni imágenes de pacientes.
- Antes de commit: `git status`, revisar diff y ejecutar lint/tests.

## 12. Ejemplo de endpoint conforme al patrón

```python
@api_bp.route('/api/study/<study_id>')
@login_required
def get_study_detail(study_id):
    study = Estudio.query.get_or_404(study_id)
    if study.institucion_id != current_user.institucion_id:
        return jsonify({'error': 'No autorizado'}), 403
    return jsonify(study_service.serialize_detail(study))
```

## 13. Checklist antes de dar una tarea por terminada

- [ ] Entrada validada y autorizada.
- [ ] Errores controlados y sin fugas de información.
- [ ] Sin secretos ni datos personales en código/logs.
- [ ] Prueba automatizada añadida o actualizada.
- [ ] `STATE.md` actualizado.
- [ ] Decisión relevante registrada en `DECISIONS.md`.
- [ ] Documentación/README afectado actualizado.
