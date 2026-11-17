# TB Detection System

Aplicación web Flask para el apoyo al diagnóstico de tuberculosis pulmonar a partir de radiografías de tórax. Usa los pesos exportados desde [`TB-prediction-model`](https://github.com/ITZ-NANO21-MC/TB-prediction-model).

## Arquitectura

- **TB-prediction-model**: entrenamiento, validación, exportación y versionado de modelos (`.h5`).
- **TB-detection-system** (este repositorio): UI web, gestión de pacientes/estudios, autenticación, resultados, mapa de calor (Grad-CAM) e inferencia usando el modelo colocado en `models_TB/`.

## Características

- Autenticación con Flask-Login (registro/login).
- Gestión de pacientes, estudios, prioridades y notas clínicas.
- Subida de imágenes con validación (`.png`, `.jpg`, `.jpeg`, `.dcm`).
- Inferencia con TensorFlow/Keras usando el peso en `models_TB/`.
- Explicabilidad con Grad-CAM.
- Persistencia con SQLAlchemy (SQLite por defecto).
- API JSON para predecir, listar y actualizar diagnósticos.

## Requisitos

- Python 3.10–3.12
- pip
- Git

## Instalación

### 1) Clonar y crear entorno

```bash
git clone https://github.com/ITZ-NANO21-MC/TB-detection-system.git
cd TB-detection-system

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2) Instalar dependencias para inferencia

El sistema usa el modelo cargado localmente. Instala las dependencias ML:

```bash
pip install -r requirements-local-model.txt
```

### 3) Colocar el peso del modelo

Descarga el modelo entrenado desde `TB-prediction-model` (o el archivo exportado) y colócalo en:

```text
models_TB/tb_model.h5
```

> `models_TB/` está ignorado por Git. No subas los pesos al repositorio. El nombre por defecto esperado es `tb_model.h5`. Puedes ajustar `MODEL_PATH` en `config.py` si usas otro nombre.

### 4) Configurar variables de entorno

```bash
cp .env-example .env
# Edita .env: SECRET_KEY, DATABASE_URL, etc.
```

### 5) Ejecutar

```bash
python run.py
# o
./start.sh
```

La app estará en `http://localhost:5000`. La base de datos se crea en `instance/`.

## Docker

```bash
docker build -t tb-detection-system .
docker run --env-file .env -p 5000:5000 \
  -v "$(pwd)/models_TB:/app/models_TB:ro" \
  -v tb_data:/app/instance \
  tb-detection-system
```

La imagen debe tener las dependencias ML instaladas para usar el contenedor con el modelo montado.

## Uso rápido

1. Regístrate/inicia sesión.
2. `Nuevo Estudio` → completa datos del paciente.
3. Sube radiografía → se ejecuta la inferencia con `models_TB/tb_model.h5`.
4. Revisa resultado + heatmap y registra el diagnóstico médico.

## Estructura

```text
TB-detection-system/
├── app/
│   ├── routes/{main,auth,api}.py
│   ├── services/ai_service.py
│   ├── models/__init__.py
│   ├── templates/
│   └── static/
├── models_TB/        # Pesos exportados desde TB-prediction-model (ignorado)
├── config.py
├── run.py
├── requirements.txt
├── requirements-local-model.txt
└── .env-example
```

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/predict` | Predicción con imagen + datos del paciente |
| `GET` | `/api/studies` | Listado de estudios |
| `GET` | `/api/study/<id>` | Detalle de estudio |
| `POST` | `/api/update_diagnosis` | Actualizar diagnóstico médico |

## Notas

- Si `models_TB/tb_model.h5` no existe o faltan dependencias ML, `TBInference.load_model()` lo indicará y la predicción fallará.
- `.env`, `instance/`, imágenes subidas y pesos están ignorados por Git.
- Este sistema es solo para apoyo diagnóstico; no sustituye el criterio médico.

## Licencia

MIT. Consulta el archivo [LICENSE](LICENSE) para el texto completo.
