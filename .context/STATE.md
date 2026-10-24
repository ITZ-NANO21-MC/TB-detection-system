# STATE.md — Estado actual del proyecto

> Última actualización: 2026-10-24
> Metodología: SDD (Spec-Driven Development)

## Ubicación actual

- **Fase actual**: Fase 1 — Hardening y estabilización
- **Módulo actual**: Módulo 1 — Configuración segura, dependencias y limpieza del repositorio
- **Estado de la fase**: En progreso
- **Estado del módulo**: Flujo local con pesos en `models_TB/` documentado

## Última acción

Alineación al flujo correcto (2026-10-24):
- README actualizado: los pesos se colocan en `models_TB/tb_model.h5` desde `TB-prediction-model`.
- `.context/` actualizado para reflejar inferencia local con archivos exportados.
- `ai_service.py` mantiene carga opcional de TensorFlow para arrancar la app, pero el uso requiere el modelo y `requirements-local-model.txt`.

## Siguiente acción

Validar carga del modelo con los pesos colocados y completar hardening (SECRET_KEY sin default, pruebas básicas).

## Bloqueos

- **Alto**: `config.py` mantiene una clave por defecto si falta `SECRET_KEY`.
- **Alto**: ausencia total de pruebas automatizadas y de CI.
- **Medio**: falta el driver PostgreSQL (`psycopg2-binary`) cuando se use en producción.
- **Medio**: sin migraciones de base de datos; `db.create_all()` en el arranque.
- **Medio**: verificar que el archivo en `models_TB/` sea compatible con `TBInference`.

## Métricas de referencia

| Indicador | Valor |
|---|---|
| Archivos versionados | 36 |
| Archivos Python de aplicación | 6 |
| Plantillas HTML | 8 |
| Archivos JS propios | 3 |
| Entidades de datos | 7 |
| Endpoints HTTP | ~12 |
| Entorno base instalado | `.venv` (Python 3.12) |
| Tamaño del historial Git | ~1.3 MiB |
| Pruebas automatizadas | 0 |
| Cobertura estimada | 0 % |
| Deuda técnica | Alta |

## Historial de estado

| Fecha | Acción | Fase | Módulo |
|---|---|---|---|
| 2026-10-24 | Adopción SDD y análisis profundo | 1 | 1 |
| 2026-10-24 | Limpieza de repositorio y purga de historial | 1 | 1 |
| 2026-10-24 | Eliminación de Demo y actualización de README | 1 | 1 |
| 2026-10-24 | Alineación al flujo models_TB + pesos exportados | 1 | 1 |
