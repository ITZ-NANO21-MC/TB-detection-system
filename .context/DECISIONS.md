# DECISIONS.md — Registro de decisiones de arquitectura (ADR)

> Cada decisión relevante debe registrarse aquí antes o inmediatamente después de implementarse.
> Formato: contexto → decisión → alternativas → motivación → consecuencias → estado.

## Plantilla

```markdown
## ADR-XXX: Título breve

- **Fecha**: YYYY-MM-DD
- **Estado**: Propuesta | Aceptada | Reemplazada | Deprecada
- **Decisores**: rol(es) implicados

### Contexto
Situación, restricciones y fuerzas en juego.

### Decisión
Qué se decide hacer, en una frase verificable.

### Alternativas consideradas
1. Opción A — pros/contras.
2. Opción B — pros/contras.

### Motivación
Por qué esta opción es la mejor dadas las restricciones.

### Consecuencias
- Positivas:
- Negativas / coste:
- Impacto en seguridad, rendimiento o mantenibilidad:

### Referencias
Archivos, issues o documentación relacionada.
```

---

## ADR-001: Adoptar SDD como metodología de evolución del proyecto

- **Fecha**: 2026-10-24
- **Estado**: Aceptada
- **Decisores**: Arquitecto, Producto

### Contexto
El proyecto es un legado funcional pero sin pruebas, migraciones, contexto documentado ni controles de seguridad sistemáticos. Los cambios futuros necesitan orden y trazabilidad.

### Decisión
Adoptar Spec-Driven Development con los artefactos `.context/{CONTEXT,ROADMAP,STATE,DECISIONS,PATTERNS}.md`, `.prompts/` y fases planificadas mediante `/plan-phase`.

### Alternativas consideradas
1. **Continuar con desarrollo ad hoc** — rápido a corto plazo, pero agrava la deuda y el riesgo clínico.
2. **Reescritura completa** — elimina deuda, pero es costosa, arriesgada y no preserva el conocimiento del dominio.
3. **Adopción incremental de SDD** — bajo riesgo, mejora continua, requiere disciplina documental.

### Motivación
La opción 3 permite estabilizar y documentar sin detener la operación, priorizando seguridad y pruebas.

### Consecuencias
- Positivas: trazabilidad, priorización explícita, base para CI y auditoría.
- Negativas: sobrecarga de documentación si no se mantiene al día.
- Seguridad: obliga a tratar los hallazgos críticos como primera fase.

### Referencias
`.context/CONTEXT.md`, `.context/ROADMAP.md`, `docs/ANALISIS_PROYECTO.md`.

---

## ADR-002: Mantener Flask con application factory y blueprints

- **Fecha**: 2026-10-24 (decisión heredada, documentada)
- **Estado**: Aceptada
- **Decisores**: Arquitecto

### Contexto
La aplicación ya usa `create_app()`, blueprints `main`/`auth`/`api` y una capa de servicio de IA. Es una estructura razonable para el tamaño actual.

### Decisión
Conservar Flask + application factory + blueprints, reforzando la separación rutas/servicios/modelos en lugar de migrar de framework.

### Alternativas consideradas
1. Migrar a FastAPI/Django — mayor coste y riesgo sin beneficio inmediato.
2. Mantener Flask y endurecer la arquitectura — evolutivo y de bajo riesgo.

### Motivación
El stack funciona y el equipo lo conoce. Los problemas actuales son de seguridad, pruebas y persistencia, no del framework.

### Consecuencias
- Positivas: continuidad, menor riesgo, foco en deuda real.
- Negativas: se mantiene la dependencia de Werkzeug/Flask 2.x.
- Mantenibilidad: se debe evitar lógica de negocio en los blueprints.

### Referencias
`app/__init__.py`, `app/routes/`, `app/services/ai_service.py`.

---

## ADR-003: Inferencia Keras con DenseNet121 y Grad-CAM

- **Fecha**: 2026-10-24 (decisión heredada, documentada)
- **Estado**: Aceptada
- **Decisores**: Arquitecto, Ciencia de datos

### Contexto
Se dispone de `models_TB/tb_model.h5` (DenseNet121, ~7.18 M parámetros) y se requiere explicabilidad visual para apoyo clínico.

### Decisión
Mantener la inferencia con TensorFlow/Keras y generar Grad-CAM sobre la última capa convolucional. La versión del modelo se registrará en `modelos_ia`.

### Alternativas consideradas
1. Modelo propietario/API externa — dependencia de terceros y datos clínicos fuera del perímetro.
2. CNN simple entrenada desde cero — menor precisión esperada y más datos necesarios.
3. DenseNet121 + Grad-CAM — buen equilibrio precisión/explicabilidad, ya disponible.

### Motivación
Reutiliza un artefacto existente y ofrece explicabilidad, requisito de confianza clínica.

### Consecuencias
- Positivas: sin reentrenamiento inmediato; heatmap comprensible.
- Negativas: TF 2.13 fija versiones antiguas de Python/NumPy; el modelo no tiene métricas reproducibles en el repo.
- Seguridad: el modelo debe cargarse de forma perezosa y validarse antes de usarse.

### Referencias
`app/services/ai_service.py`, `models_TB/tb_model.h5`, `model_summary.txt`.

---

## ADR-004: SQLite en desarrollo y PostgreSQL en producción (pendiente de completar)

- **Fecha**: 2026-10-24 (decisión heredada, documentada)
- **Estado**: Propuesta
- **Decisores**: Arquitecto, Base de datos

### Contexto
`config.py` permite `DATABASE_URL` y usa SQLite por defecto. El README declara PostgreSQL en producción, pero no hay driver ni migraciones.

### Decisión
Usar SQLite solo para desarrollo y pruebas; PostgreSQL para producción, con migraciones Alembic/Flask-Migrate en la Fase 3.

### Alternativas consideradas
1. SQLite también en producción — simple, pero concurrencia y operación limitadas.
2. PostgreSQL desde ya — requiere driver, migraciones y entorno.
3. SQLite dev + PostgreSQL prod con migraciones — equilibrio recomendado.

### Motivación
Un sistema clínico multi-usuario necesita concurrencia, integridad y respaldo robustos.

### Consecuencias
- Positivas: camino claro a producción.
- Negativas: trabajo de migración y ajuste de tipos (`JSON` de SQLite).
- Seguridad: requiere gestión de credenciales por entorno.

### Referencias
`config.py`, `requirements.txt`, `.context/ROADMAP.md` (Fase 3).
