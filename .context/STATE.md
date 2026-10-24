# STATE.md — Estado actual del proyecto

> Última actualización: 2026-10-24
> Metodología: SDD (Spec-Driven Development)

## Ubicación actual

- **Fase actual**: Fase 1 — Hardening y estabilización
- **Módulo actual**: Módulo 1 — Configuración segura y dependencias
- **Estado de la fase**: No iniciada
- **Estado del módulo**: Pendiente de planificación

## Última acción

Adopción SDD completada:
- Análisis profundo del proyecto legado.
- Creación de `.context/` (CONTEXT, ROADMAP, STATE, DECISIONS, PATTERNS).
- Creación de `.prompts/` con roles Arquitecto, Desarrollador y Tester.
- Informe en `docs/ANALISIS_PROYECTO.md`.

## Siguiente acción

Ejecutar `/plan-phase --phase 1` para descomponer la Fase 1 en tareas ejecutables y generar `.tasks/TASKS.md`.

## Bloqueos

- **Crítico**: `.env` versionado con `SECRET_KEY` y `DATABASE_URL`, y clave por defecto en `config.py`. Requiere rotación de secretos y limpieza del historial de Git (coordinado con el usuario).
- **Crítico**: imágenes médicas y base de datos SQLite versionadas en Git; privacidad y tamaño del repositorio comprometidos.
- **Alto**: ausencia total de pruebas automatizadas y de CI.
- **Alto**: `requirements.txt` incompleto (`python-dotenv`, `matplotlib`, driver PostgreSQL ausentes).
- **Medio**: sin migraciones de base de datos; `db.create_all()` en el arranque.

## Métricas de referencia

| Indicador | Valor |
|---|---|
| Archivos Python de aplicación | 6 |
| Plantillas HTML | 8 |
| Archivos JS propios | 3 |
| Entidades de datos | 7 |
| Endpoints HTTP | ~12 |
| Pruebas automatizadas | 0 |
| Cobertura estimada | 0 % |
| Deuda técnica | Alta |

## Historial de estado

| Fecha | Acción | Fase | Módulo |
|---|---|---|---|
| 2026-10-24 | Adopción SDD y análisis profundo | 1 | 1 |
