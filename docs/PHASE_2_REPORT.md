# F2 · CRUD y dashboard funcional

Fecha: 21 de octubre de 2026 (America/Mexico_City).
Estado: **DONE · gate técnico aprobado**. Entrega: `v0.2.0`.
La comprobación posterior de ramas/tag se registra en
`artifacts/phase_2_release.json` tras ejecutar la liberación; no se incrusta el
hash del propio commit en su contenido. Rama final local prevista: `develop`.

## Tareas y commits

| Tarea | Estado | Commit/ref | Archivos principales | Verificación |
| --- | --- | --- | --- | --- |
| F2-01 | DONE | `be786ea` | api/projects.py, schemas/project.py, test_projects.py, test_foundation.py, test_sandbox.py | CRUD persistente, validación, dueño/404 y borrado protegido 409. Suite de ese punto: 56 passed. |
| F2-02 | DONE | `c8c6042` | api/experiments.py, schemas/experiment.py, test_experiments.py, test_foundation.py | CRUD anidado, autorización en todas las rutas, PATCH parcial, opcionales y métricas finitas fuera de 0..1. 26 pruebas de experimentos/fundamentos aprobadas. |
| F2-03 | DONE | `4fd9f13` | api/summary.py, api/experiments.py, main.py, test_filters_summary.py, API.md | Filtros, búsqueda literal case-insensitive, paginación estable y conteos privados. Prueba dedicada aprobada. |
| F2-04 | DONE | `e836bb7`, `6933679` | frontend/, scripts/smoke_browser.cjs, iniciar.sh, SMOKE_TEST.md | UI real con edición, confirmación, filtros, paginación y totales. Chromium PASS: 14 comprobaciones y capturas revisadas. |
| F2-05 | DONE | `feature/f2-05-qa` | test_user_isolation.py, test_seed_demo.py, seed_demo.py, README.md, docs/ | Integración con dos sesiones y demo opt-in; suite final 65 passed, lint/formato/sintaxis PASS. |

El hash de F2-05 se obtiene con `git rev-parse feature/f2-05-qa` y consta en el
acta posterior. Se conservan las ramas de cada tarea y sus merges `--no-ff`.
F1 estaba completa con tag `v0.1.0` y árbol limpio al iniciar F2.

## Comprobaciones ejecutadas

| Comando/comprobación | Resultado | Evidencia |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q backend/tests` | PASS | **65 passed, 1 warning, 7.14 s**; bases SQLite temporales con Alembic. |
| `.venv/bin/python -m ruff check backend scripts migrations` | PASS | All checks passed. |
| `.venv/bin/python -m ruff format --check backend scripts migrations` | PASS | 36 files already formatted. |
| `node --check` en api.js, app.js y smoke_browser.cjs | PASS | Sintaxis válida. |
| `bash -n iniciar.sh` | PASS | Sintaxis válida. |
| `PLAYWRIGHT_MODULE="$PWD/.tools/browser/node_modules/playwright" .venv/bin/python scripts/verify_browser.py` | PASS | Chromium real, 14 comprobaciones, servidor y BD temporales; sin excepciones JS. |
| Revisión visual de capturas | PASS | Login/panel en escritorio y móvil; controles, foco y tabla con scroll interno. Sin overflow global a 1366, 390 y 320 px. |
| Arranque real con `./iniciar.sh` y SQLite temporal | PASS | Health, migración, registro, proyecto y experimento; tras detener y reiniciar servidor, login y conteos 1/1 y experimento conservados. |
| `python -m scripts.seed_demo --help` y pruebas de demo | PASS | CLI disponible; idempotencia, hash, credenciales existentes y rechazo test/production antes de acceder a BD. |
| Revisión de Git/archivos privados | PASS | Sin .env, DB, .venv, .tools ni artifacts rastreados; diff sin errores. |
| Ramas/tag/árbol limpio | Comprobación posterior | Se valida después de commit/merge/tag y se guarda en acta local. |

## Cobertura y comportamiento

- Proyectos y experimentos: crear 201, leer/listar, PATCH 200 y eliminar 204;
  no hay stubs 501 en el CRUD previsto. Los campos desconocidos y datos inválidos
  devuelven 422. Se conservan valores omitidos y se permite limpiar opcionales.
- Aislamiento: dos sesiones independientes sobre la misma base. La cuenta B no
  puede leer, crear, editar ni borrar recursos de A (404), no ve su listado ni
  sus conteos y tampoco afecta sus registros. La sesión y CSRF siguen exigidos.
- Filtros: modelo exacto sin distinguir mayúsculas; búsqueda literal por nombre,
  dataset, modelo o notas, con comodines escapados y parámetros SQL; paginación
  limit/offset, casos vacíos y consultas sin coincidencias.
- Proyecto con experimentos devuelve 409 y conserva ambos. El borrado de hijo
  permite borrar después el proyecto. Conteos siempre calculados desde BD.
- UI: registro/login, crear/seleccionar proyecto, crear experimento, filtrar,
  editar, confirmar/cancelar borrados, 409 visible, recargar y logout. Los datos
  se insertan como texto y no se inventan contadores. Diálogos con labels,
  foco y Escape; revisión responsive con tabla desplazable en móvil.
- Demo: solo por invocación explícita, solo desarrollo, contraseña solicitada con
  getpass. No hay contraseñas fijas, carga automática ni cambios a otras cuentas.

## Incidencias resueltas

El primer intento se detuvo en F2-04 porque el aislamiento impedía sockets/DNS y
no había navegador. No se liberó ni se simuló PASS. Tras habilitar permisos se
instalaron Playwright y Chromium localmente y se completó la verificación real.
Pytest normal también funciona; el adaptador `test_sandbox.py` queda como
herramienta de diagnóstico histórica, no como requisito de ejecución.

La copia del proyecto conservaba rutas del equipo anterior: se repararon enlaces,
configuración y scripts ignorados del venv sin cambiar dependencias. El lanzador
versionado usa `python -m alembic` / `python -m uvicorn`, y se comprobó arranque y
reinicio real sin tocar la base local ni imprimir secretos. La advertencia de
Starlette sobre httpx/TestClient ya existía en F1 y no afecta los resultados.

Las capturas y reportes de navegador están en `artifacts/` (ignorados). En QA se
ajustaron espaciado de tabla, selector y filtros móviles y se repitió el smoke.

## Liberación y pendientes

Tras pasar el gate: commit F2-05, merge a develop, merge a main, tag anotado
`v0.2.0`, vuelta a develop y `merge --ff-only main`. Verificar después que las
ramas locales y el tag coinciden y que el árbol está limpio; guardar el acta local.

No quedan tareas técnicas pendientes de F2. F3 (Docker/PostgreSQL, persistencia
Compose, CI y guía de despliegue) no se ejecutó. No se añadió status experimental.
La publicación de una rama en naterdz/labtrack y su merge a develop fue solicitada
expresamente por el usuario después; su resultado se informa por separado.

```json
{
  "phase_id": "F2",
  "status": "DONE",
  "completed_tasks": ["F2-01", "F2-02", "F2-03", "F2-04", "F2-05"],
  "commits": ["be786ea", "c8c6042", "4fd9f13", "e836bb7", "6933679", "feature/f2-05-qa"],
  "current_branch": "develop",
  "checks": [
    {"command": "python -m pytest -q backend/tests", "result": "PASS", "evidence": "65 passed, 1 warning"},
    {"command": "ruff check; ruff format --check; node --check; bash -n", "result": "PASS", "evidence": "Sin errores"},
    {"command": "scripts/verify_browser.py", "result": "PASS", "evidence": "Chromium: 14 comprobaciones; capturas revisadas"},
    {"command": "iniciar.sh con SQLite temporal; detener y reiniciar", "result": "PASS", "evidence": "Persisten cuenta, proyecto y experimento"}
  ],
  "tag": "v0.2.0",
  "pending": [],
  "next_step": "Publicar la rama solicitada y hacer merge a develop remoto; F3 requiere instrucción posterior"
}
```
