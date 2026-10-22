# F2 · CRUD y dashboard funcional

Fecha: 2026-10-21. Estado: **BLOCKED en validación de navegador**.
F1 confirmada mediante informe, tag `v0.1.0` y árbol inicial limpio.
No se creó `v0.2.0`, no se fusionó F2 a main y no se hizo push.

## Tareas

| Tarea | Estado | Commit/ref | Archivos principales | Evidencia |
| --- | --- | --- | --- | --- |
| F2-01 | DONE | `be786ea` | api/projects.py, schemas/project.py, test_projects.py, test_foundation.py, test_sandbox.py | Suite de ese punto: 56 passed. CRUD, validación, dos usuarios y 409; lint PASS. Integrada a develop. |
| F2-02 | DONE | `c8c6042` | api/experiments.py, schemas/experiment.py, test_experiments.py, test_foundation.py | Pruebas de experimentos/fundamentos: 26 passed. CRUD, permisos en todas las rutas, PATCH, opcionales y métricas finitas fuera de 0..1. Integrada a develop. |
| F2-03 | DONE | `4fd9f13` | api/summary.py, api/experiments.py, main.py, test_filters_summary.py, API.md | Prueba de filtros/resumen PASS: cuenta vacía, datos, dos usuarios, paginación, comodines literales e intento de inyección. Integrada a develop. |
| F2-04 | PARTIAL | `feature/f2-04-dashboard` | frontend/index.html, frontend/css/styles.css, frontend/js/app.js, scripts/smoke_browser.cjs, SMOKE_TEST.md, README.md | UI implementada, sintaxis JS y API PASS; smoke y revisión visual bloqueados. Rama sin integrar. api.js existente ya envía sesión y CSRF. |
| F2-05 | NOT_STARTED | — | — | Depende de F2-04 terminada: pendientes test_user_isolation.py de integración consolidada, seed_demo.py opt-in y gate/liberación. Ya hay pruebas de aislamiento en proyectos, experimentos y resumen. |

## Comprobaciones reales

| Comando | Resultado | Evidencia |
| --- | --- | --- |
| `.venv/bin/python scripts/test_sandbox.py -q backend/tests` | PASS | **61 passed, 1 warning, 37.98 s**. SQLite temporal migrada, sin tocar base local. |
| `.venv/bin/python -m ruff check backend scripts migrations` | PASS | All checks passed. |
| `.venv/bin/python -m ruff format --check backend scripts migrations` | PASS | 33 files already formatted. |
| `node --check` en api.js, app.js y smoke_browser.cjs | PASS | Sintaxis válida. |
| `git diff --check` | PASS | Sin errores de whitespace. |
| `.venv/bin/python scripts/verify_browser.py` | BLOCKED | PermissionError al crear socket local; no arrancó servidor ni navegador. |
| Revisión visual y smoke manual F2 | NOT_RUN | Sin Chromium/Playwright disponible; DNS del registro npm bloqueado. |
| `git status --short` | PASS previo al trabajo | Árbol inicial limpio. Verificación final después del commit. |
| Tag v0.2.0 / main | NOT_RUN | Gate de fase pendiente; main permanece en F1. |

## Incidencias y decisiones

- El proyecto fue trasladado desde otro equipo. Se reparó el enlace ignorado
  `.venv/bin/python` hacia el Python 3.12.15 ya incluido en `.tools/python`.
  No se imprimió ni modificó `.env`, la base local ni credenciales.
- Pytest directo quedó bloqueado en el portal entre hilos de TestClient.
  El diagnóstico con faulthandler mostró espera en epoll y Future del portal.
  `scripts/test_sandbox.py` limita la espera de epoll a 10 ms para permitir avanzar
  en este aislamiento. Ejecuta las aserciones originales, sin omitir pruebas ni
  alterar respuestas de la API. Fuera de este entorno se usa pytest normal.
- Un primer intento sobre experimentos aún incluía expectativas 501 históricas
  y falló; se retiraron esas expectativas para las rutas implementadas y se
  ejecutó la suite final completa con el resultado PASS indicado arriba.
- La advertencia de Starlette sobre httpx/TestClient es la misma de F1.
- La UI conserva estilos y autenticación existentes; añade selector/detalle,
  formularios con labels y límites, diálogos nativos de confirmación, mensajes
  de error (incluido 409), filtros, paginación y totales reales. Se usa textContent
  para los datos del usuario. Las mutaciones siguen usando sesión y CSRF.
- Los stubs 501 del CRUD fueron retirados. No se añadió el campo experimental status.
- La prueba de navegador fue actualizada al flujo F2, pero **no se declara PASS**.
  No hay permiso para abrir sockets y no hay navegador local instalado. La descarga
  tampoco es viable: curl al registro npm devuelve error de resolución DNS.
- Se respeta la secuencia del JSON: F2-04 no se integra ni se avanza a F2-05
  mientras falte su acceptance de navegador. No hay remoto ni despliegue nuevo.

## Reanudación

1. Abrir esta rama en un entorno con loopback y Playwright/Chromium disponibles.
2. Ejecutar `scripts/verify_browser.py` y revisión manual de `docs/SMOKE_TEST.md`;
   corregir cualquier fallo, comprobar teclado y tamaños 1366/390/320 px.
3. Integrar F2-04 a develop cuando sus comprobaciones pasen.
4. Crear feature/f2-05-qa desde develop, completar integración consolidada y demo
   opt-in, repetir gate y actualizar este informe.
5. Solo entonces liberar a main, crear v0.2.0 y volver a develop conforme al JSON.

```json
{
  "phase_id": "F2",
  "status": "BLOCKED",
  "completed_tasks": ["F2-01", "F2-02", "F2-03"],
  "commits": ["be786ea", "c8c6042", "4fd9f13", "feature/f2-04-dashboard"],
  "current_branch": "feature/f2-04-dashboard",
  "checks": [
    {"command": ".venv/bin/python scripts/test_sandbox.py -q backend/tests", "result": "PASS", "evidence": "61 passed, 1 warning"},
    {"command": "ruff check / format --check; node --check; git diff --check", "result": "PASS", "evidence": "Sin errores"},
    {"command": ".venv/bin/python scripts/verify_browser.py", "result": "FAIL", "evidence": "PermissionError: sockets locales bloqueados"},
    {"command": "revisión visual F2", "result": "NOT_RUN", "evidence": "Sin Chromium/Playwright"}
  ],
  "tag": "",
  "pending": ["Validar e integrar F2-04", "Completar F2-05", "Liberar v0.2.0 tras gate"],
  "next_step": "Completar smoke y revisión visual F2 en un entorno con loopback y Chromium habilitados"
}
```
