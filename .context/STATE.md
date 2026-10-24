# STATE.md — Estado actual del proyecto

> Última actualización: 2026-10-24
> Metodología: SDD (Spec-Driven Development)

## Ubicación actual

- **Fase actual**: Fase 1 — Hardening y estabilización
- **Módulo actual**: Módulo 1 — Configuración segura, dependencias y limpieza del repositorio
- **Estado de la fase**: En progreso
- **Estado del módulo**: Limpieza completada; rotación de secretos y refactor pendientes

## Última acción

Limpieza y purga del repositorio (2026-10-24):
- `.env`, `instance/`, bases SQLite, 11 imágenes médicas, `model_summary.txt` y `models_TB/tb_model.h5` eliminados del índice.
- Historial reescrito con `git-filter-repo` y force-push a `origin/main`.
- Repositorio reducido de ~46 MiB a ~1.2 MiB.
- `.gitignore` actualizado (`session-*.md`, `models_TB/`, excepción de `.gitkeep`).
- Modelo y `.env` conservados solo en local e ignorados.

## Siguiente acción

Rotar `SECRET_KEY` y credenciales de `.env`, y planificar el resto de la Fase 1 con `/plan-phase --phase 1`.

## Bloqueos

- **Crítico**: secretos que estuvieron versionados; rotación pendiente aunque ya se purgaran del historial.
- **Alto**: `config.py` mantiene una clave por defecto si falta `SECRET_KEY`.
- **Alto**: ausencia total de pruebas automatizadas y de CI.
- **Alto**: `requirements.txt` incompleto (`python-dotenv`, `matplotlib`, driver PostgreSQL ausentes).
- **Medio**: sin migraciones de base de datos; `db.create_all()` en el arranque.
- **Medio**: la app aún depende de inferencia local y de `models_TB/tb_model.h5`; falta el cliente HTTP hacia `TB-prediction-model`.

## Métricas de referencia

| Indicador | Valor |
|---|---|
| Archivos versionados | 39 |
| Archivos Python de aplicación | 6 |
| Plantillas HTML | 8 |
| Archivos JS propios | 3 |
| Entidades de datos | 7 |
| Endpoints HTTP | ~12 |
| Tamaño del historial Git | ~1.2 MiB |
| Pruebas automatizadas | 0 |
| Cobertura estimada | 0 % |
| Deuda técnica | Alta |

## Historial de estado

| Fecha | Acción | Fase | Módulo |
|---|---|---|---|
| 2026-10-24 | Adopción SDD y análisis profundo | 1 | 1 |
| 2026-10-24 | Limpieza de repositorio y purga de historial | 1 | 1 |
