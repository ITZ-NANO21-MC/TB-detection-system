# CONTEXT.md — Sistema de Detección de Tuberculosis Asistida por IA

> Documento de contexto generado durante la adopción SDD del proyecto legado.
> Última actualización: 2026-10-24

## 1. Visión del proyecto

Sistema web de apoyo al diagnóstico de tuberculosis pulmonar a partir de radiografías de tórax. Permite registrar pacientes, subir estudios, ejecutar inferencia con un modelo de deep learning, visualizar un mapa de calor (Grad-CAM) y registrar la validación final de un profesional de la salud.

El sistema **no sustituye** el diagnóstico médico. Toda salida de IA es un insumo preliminar sujeto a validación clínica.

## 2. Objetivos

- Reducir el tiempo de triage de radiografías de tórax.
- Ofrecer una probabilidad de TB con nivel de riesgo y explicabilidad visual.
- Mantener trazabilidad entre paciente, estudio, resultado de IA y diagnóstico médico.
- Operar en un entorno clínico con autenticación de médicos y aislamiento por institución.

## 3. Usuarios

- **Médico / usuario clínico**: se registra, inicia sesión, sube estudios, revisa resultados y confirma/corrige el diagnóstico.
- **Institución de salud**: agrupa pacientes, estudios y usuarios (multi-institución previsto, hoy simplificado).
- **Administrador técnico**: despliega, configura el modelo y mantiene la base de datos.

## 4. Stack tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.8+ (entorno local con 3.12) |
| Framework web | Flask | 2.3.3 |
| ORM | Flask-SQLAlchemy | 3.0.5 |
| Autenticación | Flask-Login | 0.6.3 |
| Formularios/CSRF | Flask-WTF | 1.2.2 (instalado, no integrado) |
| CORS | Flask-CORS | 4.0.0 |
| Servidor WSGI | Werkzeug (dev) | 2.3.7 |
| Deep learning | TensorFlow / Keras | 2.13.0 |
| Procesamiento de imagen | OpenCV, Pillow | 4.8.1.78 / 10.0.0 |
| Visualización | Matplotlib (Grad-CAM) | No fijada en requirements |
| Base de datos | SQLite (dev), PostgreSQL (producción prevista) | — |
| Frontend | Jinja2 + Bootstrap 5 + jQuery 3.6 | CDN |
| Iconografía | Font Awesome 6.4 | CDN |
| Contenedores | Docker | python:3.10-slim |

> Nota: `python-dotenv` y `matplotlib` se importan en el código pero no figuran en `requirements.txt`. PostgreSQL no tiene driver instalado.

## 5. Estructura de carpetas

```
TB-detection-system/
├── app/
│   ├── __init__.py              # Application factory, extensiones, blueprints, error handlers
│   ├── models/__init__.py       # SQLAlchemy db + todas las entidades
│   ├── routes/
│   │   ├── main.py              # Vistas: index, dashboard, profile, upload, results
│   │   ├── auth.py              # Registro, login, logout
│   │   └── api.py               # API JSON: predict, studies, study detail, diagnosis, profile
│   ├── services/ai_service.py   # TBInference: carga, preproceso, predicción, Grad-CAM
│   ├── static/css/style.css     # Estilos propios sobre Bootstrap
│   ├── static/js/               # app.js, upload.js, results.js (jQuery + AJAX)
│   ├── static/img/              # Assets de landing
│   ├── static/uploads/          # Solo .gitkeep; contenido local ignorado
│   └── templates/               # base, index, login, register, dashboard, upload, results, profile
├── config.py                    # Config, DevelopmentConfig, ProductionConfig
├── run.py                       # Punto de entrada Flask
├── start.sh                     # Script local con ruta absoluta hardcodeada
├── Dockerfile / .dockerignore
├── requirements.txt
├── models_TB/tb_model.h5        # Modelo local ignorado; pertenece a TB-prediction-model
├── instance/                    # SQLite local ignorado, no versionado
├── Demo/                        # Capturas para README
├── .env                         # Secretos locales ignorados, no versionados
├── .context/                    # Contexto SDD (este directorio)
├── .prompts/                    # Roles de trabajo
└── docs/                        # Informes de análisis
```

## 6. Entidades de datos principales

- **instituciones**: institución médica (nombre, dirección, contacto).
- **usuarios**: médicos (`User`), credenciales hasheadas, especialidad, institución.
- **pacientes**: expediente único, datos demográficos, historial médico JSON.
- **estudios**: estudio radiológico, prioridad, estado, ruta de imagen, notas clínicas.
- **resultados_ia**: probabilidad, detección booleana, nivel de riesgo, hallazgos, heatmap, versión y confianza del modelo.
- **diagnosticos**: diagnóstico final del médico, concordancia con IA, razones de desacuerdo, notas.
- **modelos_ia**: registro de versiones de modelos, arquitectura, métricas y estado activo.

Relaciones: `Institucion 1—N Paciente/Estudio/User`; `Paciente 1—N Estudio`; `Estudio 1—1 ResultadoIA`; `Estudio 1—N Diagnostico`; `Diagnostico N—1 ResultadoIA`.

## 7. Modelo de IA

- Arquitectura: DenseNet121 preentrenado + GlobalAveragePooling + BatchNormalization + Dense/Dropout.
- Parámetros: ~7.18 M totales, ~3.03 M entrenables.
- Entrada: imagen RGB redimensionada a 224×224, normalizada a [0, 1].
- Salida: probabilidad binaria de tuberculosis (sigmoide de 1 neurona o segunda clase).
- Explicabilidad: Grad-CAM sobre la última capa convolucional; heatmap PNG semitransparente.
- Umbrales funcionales actuales: `> 0.5` positivo; `> 0.8` riesgo alto; `> 0.5` riesgo medio.
- El artefacto `tb_model.h5` ya **no está versionado** en este repositorio. El modelo se desarrolla y exporta en `TB-prediction-model`; aquí se conserva una copia local ignorada solo como respaldo temporal hasta migrar a la API remota.

## 8. Reglas de negocio fijas

1. El expediente del paciente es único.
2. Un estudio pertenece a un paciente y a una institución.
3. Cada estudio puede tener un único resultado de IA y uno o más diagnósticos.
4. El diagnóstico final siempre lo registra un profesional autenticado.
5. El resultado de IA nunca se presenta como diagnóstico definitivo; la UI debe mostrar el descargo de responsabilidad.
6. Formatos de imagen admitidos: `.png`, `.jpg`, `.jpeg`, `.dcm` (DICOM está declarado pero no procesado realmente por el pipeline actual).
7. Tamaño máximo de archivo: 16 MB.
8. Las rutas de archivos subidos deben sanearse y almacenarse en `app/static/uploads/`.
9. Las operaciones de escritura deben ser transaccionales (`commit`/`rollback`).
10. Código en inglés para identificadores; textos de interfaz, comentarios y documentación en español.
11. Las credenciales y secretos nunca deben versionarse.
12. Toda funcionalidad nueva debe incluir pruebas automatizadas (regla SDD adoptada).

## 9. Alcance actual y limitaciones conocidas

Implementado: autenticación básica, dashboard, carga de imágenes, inferencia local heredada, Grad-CAM, persistencia de estudios/resultados/diagnósticos, perfil de usuario, Dockerfile.

No implementado o incompleto: cliente HTTP del modelo remoto, recuperación de contraseña, roles/permisos finos, aislamiento multi-institución, exportación PDF, auditoría real, soporte DICOM, migraciones de BD, pruebas automatizadas, CI/CD, observabilidad, métricas verificables del modelo.

Estado del repositorio tras la limpieza del 2026-10-24:
- `.env`, bases SQLite, imágenes médicas, `model_summary.txt` y `tb_model.h5` fueron eliminados del índice y purgados del historial.
- El historial se redujo de ~46 MiB a ~1.2 MiB.
- El modelo y `.env` siguen existiendo solo en local y están ignorados.
- Pendiente: rotar los secretos expuestos y migrar la inferencia local a la API de `TB-prediction-model`.

## 10. Riesgos principales

- Secretos que estuvieron versionados: rotación pendiente aunque ya se purgaran del historial.
- Clave por defecto en `config.py` si falta `SECRET_KEY`.
- Ausencia de pruebas y de migraciones.
- CORS abierto, sin CSRF, sin rate limiting.
- Posible acceso cruzado a estudios entre instituciones (IDOR).
- XSS almacenado en renderizado de datos con plantillas de string en jQuery.
- `debug=True` en el punto de entrada y servidor de desarrollo en Docker.
