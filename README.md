# LabTrack · F1

Base independiente del taller: FastAPI, SQLAlchemy 2, Pydantic 2 y frontend nativo.
Requiere Python 3.12. No hay publicación externa ni repositorio remoto.

## Instalación (desde esta carpeta)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
python scripts/init_env.py
alembic upgrade head
uvicorn backend.app.main:create_app --factory --host 127.0.0.1 --port 8765
```

Abrir http://127.0.0.1:8765. La configuración está en `.env` (privada, ignorada por Git).
`init_env.py` genera la clave y conserva intacta una configuración existente.
Siempre ejecutar comandos desde la raíz de LabTrack; SQLite usa `./labtrack.db`.

## Comprobaciones

```bash
python -m pytest -q backend/tests
ruff check backend scripts migrations
curl -i http://127.0.0.1:8765/api/health
```

Las pruebas usan bases temporales y configuración explícita, sin modificar la base local.
Las dependencias exactas se guardan en `backend/requirements*.txt`; los archivos `.in`
registran las dependencias directas. Python 3.12 puede instalarse localmente con uv:

```bash
UV_PYTHON_INSTALL_DIR=.tools/python uv python install 3.12 --no-bin
UV_PYTHON_INSTALL_DIR=.tools/python uv venv --python 3.12 .venv
```

## Alcance

F1 implementa salud, modelos/migración y autenticación; proyectos y experimentos
quedan pendientes con HTTP 501 intencional. Los contadores no muestran cifras inventadas.
CRUD, filtros y resumen corresponden a F2; Docker/PostgreSQL y CI a F3.
El campo experimental `status` no forma parte de los modelos.

Ver `docs/GIT_WORKFLOW.md` para ramas y liberaciones.
