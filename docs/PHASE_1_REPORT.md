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
