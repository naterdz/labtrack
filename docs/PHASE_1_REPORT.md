# Informe F1 — en ejecución

## F1-01 — DONE

- Archivos: `.gitignore`, `README.md`, carpetas base y `docs/GIT_WORKFLOW.md`.
- Commit: `7b6f4d3`.
- PASS: `git branch --list`, repositorio independiente y `git diff --check`.
- PASS: árbol limpio tras integrar en `develop`.

## F1-02 — DONE

- Archivos: configuración, aplicación/API de salud, conexión SQLAlchemy, dependencias,
  script de configuración privada, pruebas de salud/configuración y README.
- PASS: Python 3.12.15 local, dependencias exactas instaladas en `.venv`.
- PASS: `python scripts/init_env.py`; archivo privado idempotente.
- PASS: `python -m pytest -q backend/tests`: **3 passed**, 1 aviso de deprecación
  de Starlette sobre httpx (sin fallas).
- PASS: `ruff check backend` y formato.
- PASS: `curl -i http://127.0.0.1:8765/api/health`: 200 y JSON esperado.
- El puerto 8000 estaba ocupado; se utiliza 8765 para las verificaciones reales.
- El aislamiento del entorno impide sockets y bloquea TestClient; las pruebas y
  el servidor se ejecutan con permisos aprobados, solo en loopback.

- Commit F1-02: `fe05304`.

## F1-03 — DONE

- Archivos: `models.py`, Alembic/env/plantilla/revisión 0001, fixtures, pruebas
  de modelo y `docs/DATA_MODEL.md`.
- PASS: `alembic upgrade head`, `alembic current`: `0001 (head)`.
- PASS: suite completa: **10 passed**, 1 aviso de Starlette/httpx.
- PASS: migración desde vacío, downgrade/upgrade/reaplicación, `alembic check`,
  UUID, UTC, claves foráneas, correo único, restricciones y reapertura de SQLite.
- PASS: `ruff check backend scripts migrations`.

- Commit F1-03: `178e0a0`.

## F1-04 — DONE

- Archivos: `api/auth.py`, `core/security.py`, `schemas/auth.py`, manejadores
  de errores, integración en `main.py`, `test_auth.py` y `docs/API.md`.
- PASS: suite completa: **27 passed**, 1 aviso de Starlette/httpx.
- PASS: registro/correo normalizado/duplicados, hash Argon2id, login/me/logout,
  cookies HttpOnly/SameSite/Secure, rotación y expiración de sesión.
- PASS: 401 sin sesión o credenciales incorrectas; 403 sin CSRF, con nonce
  sustituido o con Origin ajeno; 422 sin revelar contraseñas.
- PASS: cuenta utilizable tras reiniciar la aplicación sobre la misma SQLite.
- PASS: `ruff check backend scripts migrations`.

- Commit F1-04: `9e63773`.

## F1-05 — DONE

- Archivos: interfaz HTML/CSS/JS, icono SVG, rutas stub protegidas, integración
  de estáticos, pruebas de recursos y scripts de arranque/smoke de navegador.
- PASS: suite completa: **29 passed**, 1 aviso de Starlette/httpx.
- PASS: `node --check` en ambos módulos JS y el script de navegador.
- PASS: Chromium real: registro -> login fallido -> login válido -> dashboard
  -> POST proyecto con CSRF y 501 -> recarga -> logout -> recarga sin sesión.
- PASS: enlace de salto por teclado, labels, foco de dashboard y controles de contraseña.
- PASS: login/dashboard sin desbordamiento global en escritorio y móvil;
  dashboard también verificado a 320px. Tabla móvil con scroll interno.
- PASS: capturas revisadas visualmente; no hay datos ni contadores simulados.
- PASS: no hay excepciones JavaScript. Informe de navegador: `artifacts/browser_smoke.json`.
- El navegador MCP no comparte el loopback del equipo (404), por lo que se
  verificó con Chromium/Playwright local contra una base temporal independiente.
