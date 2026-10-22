# F1 · Fundamentos y autenticación

Fecha: 21 de octubre de 2026 (America/Mexico_City).
Entrega: `v0.1.0` · rama final: `develop` · estado de comprobaciones: **PASS**.
El tag y el árbol limpio se comprueban después de integrar; véase el procedimiento
al final y el acta local `artifacts/phase_1_release.json` generada tras liberar.

## Tareas y commits

| Tarea | Estado | Commit/ref | Archivos principales | Verificación |
| --- | --- | --- | --- | --- |
| F1-01 · repositorio | DONE | `7b6f4d3` | `.gitignore`, `README.md`, carpetas y `docs/GIT_WORKFLOW.md` | Repo independiente, main/develop, diff correcto y árbol limpio tras integrar. |
| F1-02 · entorno/API | DONE | `fe05304` | `requirements*`, `config.py`, `db.py`, `main.py`, `init_env.py`, pruebas | Python 3.12.15, entorno instalado, .env privado/idempotente, health 200; 3 pruebas pasaron. |
| F1-03 · datos | DONE | `178e0a0` | `models.py`, Alembic/revisión 0001, fixtures, pruebas y `DATA_MODEL.md` | Migración, UUID/UTC, restricciones, relaciones y persistencia; 10 pruebas pasaron. |
| F1-04 · autenticación | DONE | `9e63773` | `auth.py`, `security.py`, schemas, errores, pruebas y `API.md` | Registro/login/me/logout, Argon2id, cookies y CSRF; 27 pruebas pasaron. |
| F1-05 · interfaz/stubs | DONE | `dcfd75a` | `frontend/`, rutas CRUD pendientes, pruebas, lanzador y scripts de navegador | Interfaz funcional con API real, responsive, teclado y errores visibles; 29 pruebas pasaron. |
| F1-06 · cierre | DONE | `feature/f1-06-qa` | `test_foundation.py`, pruebas de métricas, informes y documentación | Suite final, navegador, lint, revisión Git y liberación conforme al gate. |

El hash de F1-06 se obtiene con `git rev-parse feature/f1-06-qa` y consta en
el acta local de liberación; no se incrusta en su propio commit.
Cada tarea se realizó en su rama feature y se integra con `--no-ff` tras pasar
sus comprobaciones. Las ramas se conservan para revisión.

## Comprobaciones ejecutadas

| Comando/comprobación | Resultado | Evidencia |
| --- | --- | --- |
| `.venv/bin/python --version` | PASS | Python 3.12.15 instalado localmente; sistema sin cambios. |
| `python scripts/init_env.py` | PASS | Genera SECRET_KEY sin mostrarla; .env 0600, idempotente. |
| `python -m pytest -q backend/tests` | PASS | **59 passed, 1 warning**, 3.97 s en el gate final. |
| `alembic upgrade head` / `alembic current` | PASS | SQLite local migrada a `0001 (head)`. |
| `alembic check` | PASS | No new upgrade operations detected. |
| Pruebas sobre SQLite temporal | PASS | Base vacía, downgrade/upgrade/reaplicación, FK, correo único, UUID y UTC; reapertura conserva datos. |
| `ruff check backend scripts migrations` | PASS | All checks passed. |
| `ruff format --check backend scripts migrations` | PASS | 26 archivos ya formateados. |
| `node --check` en módulos y smoke | PASS | Sintaxis válida. |
| `bash -n iniciar.sh` | PASS | Sintaxis válida del lanzador. |
| `curl -i http://127.0.0.1:8765/api/health` | PASS | HTTP 200, `{"status":"ok","service":"labtrack"}`. |
| `python scripts/verify_browser.py` | PASS | Chromium real, 13 comprobaciones; servidor y SQLite temporales. |
| Revisión visual | PASS | Login y dashboard en escritorio/móvil; cuatro capturas locales. |
| Revisión de Git y secretos | PASS | Sin clave real, .env, DB, entornos o artefactos rastreados; sin remoto. |

La suite final cubre las diez rutas CRUD pendientes: 401 sin sesión; 403
sin CSRF o con CSRF inválido en las seis mutaciones; 501 con sesión/CSRF válidos,
sin insertar proyectos o experimentos. También cubre hashes, duplicados,
credenciales incorrectas, firma/caducidad/rotación, origen ajeno, atributos de
cookies, validación sin exponer contraseñas, recursos estáticos y esquema.
En QA se añadió rechazo explícito de NaN/infinito para evitar su conversión a
NULL por SQLite; se conservan métricas finitas fuera de 0..1.

El navegador probó registro -> error de login -> login -> panel -> POST con CSRF
-> recarga -> logout -> recarga sin sesión. Se comprobó foco, enlace de salto,
contraseña no conservada, sesión HttpOnly y ausencia de excepciones JavaScript.
No hay desbordamiento global a 1366px/390px ni en el panel a 320px; la tabla
móvil tiene scroll interno. Los contadores muestran guiones y no hay datos demo.

## Incidencias y decisiones

- Se creó `/home/natterdz/Downloads/labtrack`: no existía carpeta `Github`.
  No se modificaron otros proyectos ni el JSON original.
- Python del sistema: 3.14.4. Se instaló Python 3.12.15 en `.tools/python`
  y dependencias exactas en `.venv`; ambos ignorados por Git.
- La red y los sockets están bloqueados dentro del aislamiento. Descargas,
  servidor local, TestClient y Chromium se ejecutaron con permisos aprobados.
  Un intento inicial de pytest dentro del aislamiento se interrumpió al quedar
  bloqueado; no se contó como PASS. Las ejecuciones válidas completaron normalmente.
- El puerto 8000 estaba ocupado. Se verificó salud con curl en 8765 y el
  navegador en un puerto temporal libre.
- El navegador MCP no comparte el loopback del equipo (404). Se utilizó
  Playwright/Chromium local y una base temporal independiente.
- Starlette emite un aviso de deprecación sobre el uso de httpx en TestClient.
  No hubo pruebas fallidas; se conserva httpx por el contrato de tecnología.
- El gate del plan contiene el tag que autoriza crear. Se separó en gate técnico
  previo y comprobación Git posterior, documentado en `GIT_WORKFLOW.md`.
- Los informes se registraron en commits antes de liberar. Las expectativas 501
  son específicas de F1 y deben actualizarse por endpoint al realizar F2.
- Las sesiones son cookies firmadas sin revocación central; logout elimina las
  cookies del navegador. Las copias previas vencen con su TTL. Detalle en `API.md`.

## Liberación y acta posterior

Tras aprobar el gate técnico: commit F1-06, merge a develop, merge a main,
tag anotado `v0.1.0`, vuelta a develop y `merge --ff-only main`.
Comprobar que main/develop/tag apuntan al mismo commit y `git status --short`
no produce salida. El resultado real se registra en `artifacts/phase_1_release.json`
(después de crear el tag, sin autorreferencia ni cambios al contenido etiquetado).

## Pendientes fuera de F1

- F2: CRUD real, autorización por dueño, filtros, regla HTTP 409, resumen y UI completa.
- F3: PostgreSQL/Docker, persistencia de contenedores, CI y guía de despliegue.
- NOT_RUN: Docker/PostgreSQL, CI remota y despliegue; corresponden a otras fases.
- No se agregó `status` a las entidades, no se creó remoto ni se hizo push.

Próxima instrucción: «Ejecuta solo F2 del JSON; verifica primero F1 y v0.1.0».
No se avanza a F2 automáticamente.
