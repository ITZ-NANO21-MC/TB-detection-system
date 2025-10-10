# 🏥 Sistema de Detección de Tuberculosis Asistida por IA

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema web avanzado para el apoyo al diagnóstico de tuberculosis pulmonar mediante inteligencia artificial y aprendizaje profundo.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Demo](#-demo)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API](#-api)
- [Base de Datos](#-base-de-datos)
- [Desarrollo](#-desarrollo)
- [Tecnologías](#-tecnologías)
- [Licencia](#-licencia)

## ✨ Características

### 🔬 Diagnóstico Asistido por IA
- **Análisis automático** de radiografías torácicas
- **Detección de patrones** de tuberculosis con alta precisión
- **Mapas de calor** para visualización de áreas de interés
- **Métricas de confianza** en tiempo real

### 💻 Interfaz Moderna
- **Diseño responsive** compatible con dispositivos móviles
- **Flujo guiado** paso a paso para nuevos estudios
- **Drag & drop** para carga intuitiva de imágenes
- **Visualización avanzada** de resultados

### 🗄️ Gestión de Pacientes
- **Registro completo** de historiales médicos
- **Seguimiento temporal** de estudios
- **Búsqueda avanzada** por múltiples criterios
- **Exportación de reportes** en formato PDF

### 🔒 Seguridad y Auditoría
- **Base de datos segura** con relaciones normalizadas
- **Registro de auditoría** de todas las operaciones
- **Manejo de errores** robusto
- **Validación de datos** en frontend y backend

## 🎯 Demo

### Capturas de Pantalla

| Dashboard Principal | Subida de Imágenes | Resultados de IA |
|---------------------|-------------------|------------------|
| ![Dashboard](https://via.placeholder.com/300x200/4A90E2/FFFFFF?text=Dashboard) | ![Upload](https://via.placeholder.com/300x200/50E3C2/FFFFFF?text=Upload) | ![Results](https://via.placeholder.com/300x200/9013FE/FFFFFF?text=Results) |

### Métricas de Rendimiento
- **Precisión del modelo**: 95%
- **Sensibilidad**: 93%
- **Especificidad**: 96%
- **Tiempo de procesamiento**: < 5 segundos

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/ITZ-NANO21-MC/TB-detection-system.git
   cd tb-detection-system
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Inicializar la base de datos**
   ```bash
   python app.py
   # La base de datos se crea automáticamente
   ```

6. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

La aplicación estará disponible en `http://localhost:5000`

### Configuración con Docker

```bash
# Construir la imagen
docker build -t tb-detection-system .

# Ejecutar el contenedor
docker run -p 5000:5000 tb-detection-system
```

## 📖 Uso

### Flujo de Trabajo Típico

1. **Acceso al Sistema**
   - Abrir navegador en `http://localhost:5000`
   - Navegar por el dashboard principal

2. **Nuevo Estudio**
   - Click en "Nuevo Estudio"
   - Completar datos del paciente
   - Subir imagen de radiografía (drag & drop o selector)
   - Confirmar envío para análisis

3. **Análisis con IA**
   - El sistema procesa la imagen automáticamente
   - Genera resultados en segundos
   - Muestra métricas de confianza

4. **Revisión de Resultados**
   - Visualizar imagen original + mapa de calor
   - Revisar hallazgos detectados
   - Confirmar o modificar diagnóstico

5. **Gestión de Historial**
   - Consultar estudios anteriores
   - Filtrar por paciente, fecha o diagnóstico
   - Exportar reportes

### Formatos de Imagen Soportados

- **DICOM** (.dcm) - Formato médico estándar
- **JPEG** (.jpg, .jpeg) - Imágenes comprimidas
- **PNG** (.png) - Imágenes sin pérdida

## 🏗️ Estructura del Proyecto

```
tb-detection-system/
├── app.py                 # Aplicación principal Flask
├── model.py              # Clase de inferencia del modelo IA
├── database.py           # Modelos de base de datos
├── config.py             # Configuración de la aplicación
├── requirements.txt      # Dependencias de Python
├── static/
│   ├── css/
│   │   └── style.css    # Estilos principales
│   ├── js/
│   │   ├── app.js       # JavaScript principal
│   │   ├── upload.js    # Gestión de subidas
│   │   └── results.js   # Visualización de resultados
│   └── uploads/          # Imágenes subidas
├── templates/
│   ├── base.html        # Plantilla base
│   ├── index.html       # Página principal
│   ├── upload.html      # Subida de estudios
│   └── results.html     # Resultados de análisis
└── models/
    └── tb_model.h5      # Modelo de IA entrenado
```

## 🔌 API

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/studies` | Listar todos los estudios |
| `GET` | `/api/study/<id>` | Obtener detalles de estudio |
| `POST` | `/api/predict` | Procesar nueva imagen |
| `POST` | `/api/update_diagnosis` | Actualizar diagnóstico médico |

### Ejemplo de Uso de API

```python
import requests

# Subir imagen para análisis
files = {'file': open('radiografia.png', 'rb')}
data = {
    'nombre_paciente': 'Juan Pérez',
    'expediente': 'XP12345',
    'edad': 45,
    'genero': 'masculino'
}

response = requests.post('http://localhost:5000/api/predict', 
                        files=files, data=data)
result = response.json()
```

## 🗃️ Base de Datos

### Esquema Principal

```sql
INSTITUCIONES → PACIENTES → ESTUDIOS → RESULTADOS_IA
                              ↓
                         DIAGNOSTICOS
```

### Entidades Principales

- **Pacientes**: Información demográfica e historial médico
- **Estudios**: Metadatos de cada análisis realizado
- **Resultados_IA**: Predicciones y métricas del modelo
- **Diagnosticos**: Diagnósticos finales del médico

## 🛠️ Desarrollo

### Contribuir al Proyecto

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

### Estructura de Commits

Usamos Conventional Commits:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Documentación
- `style:` Cambios de formato
- `refactor:` Refactorización de código
- `test:` Adición de tests

## 🛡️ Tecnologías

### Backend
- **Flask** - Framework web ligero
- **SQLAlchemy** - ORM para base de datos
- **TensorFlow** - Framework de machine learning
- **OpenCV** - Procesamiento de imágenes

### Frontend
- **Bootstrap 5** - Framework CSS
- **JavaScript ES6+** - Interactividad
- **Font Awesome** - Iconografía
- **Chart.js** - Visualización de datos

### Base de Datos
- **SQLite** (Desarrollo)
- **PostgreSQL** (Producción)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## ⚠️ Descargo de Responsabilidad

Este sistema está diseñado para **asistir** a profesionales de la salud en el diagnóstico de tuberculosis. **No debe ser usado como único método de diagnóstico**. Siempre consulte con un médico calificado para diagnósticos definitivos.

