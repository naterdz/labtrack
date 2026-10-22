# LabTrack · F2 en validación

Base independiente del taller: FastAPI, SQLAlchemy 2, Pydantic 2 y frontend nativo.
Requiere Python 3.12. No hay publicación externa ni repositorio remoto.

## Abrir el entorno ya preparado

```bash
./iniciar.sh
```

Abrir http://127.0.0.1:8765. Para detener el servidor: Ctrl+C.
El lanzador conserva `.env`, aplica las migraciones y arranca usando `.venv`.
Cambiar el puerto, si es necesario: `LABTRACK_PORT=8766 ./iniciar.sh`.

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
uv pip sync --python .venv/bin/python backend/requirements-dev.txt
```

En este equipo uv está instalado en `.tools/bootstrap/bin/uv` y Python 3.12.15
en `.tools/python`; no se cambió el Python del sistema. El entorno creado por
uv no necesita pip: usar `uv pip sync` como arriba o el ejecutable local de uv.

## Alcance

Implementa autenticación, CRUD de proyectos y experimentos, permisos por dueño,
filtros por modelo/búsqueda, paginación y resumen privado. El dashboard consume
la API y permite crear, editar y eliminar registros con confirmación.
No se carga información demo automáticamente.

F2-01 a F2-04 verificadas: 61 pruebas de API y smoke Chromium con 14 comprobaciones.
El cierre y tag de fase se documentan en `docs/PHASE_2_REPORT.md`.
Docker/PostgreSQL y CI corresponden a F3. El campo experimental `status` no forma
parte de los modelos.

En este entorno restringido se pueden ejecutar las mismas aserciones de pytest con:

```bash
.venv/bin/python scripts/test_sandbox.py -q backend/tests
```

Este ejecutor limita la espera de epoll para resolver el bloqueo de wakeups entre
hilos de TestClient. En un equipo normal usar pytest directamente.
Ver `docs/GIT_WORKFLOW.md` para ramas y liberaciones.

La API de F1 y las cookies están descritas en `docs/API.md`; el modelo y la
migración en `docs/DATA_MODEL.md`. El informe de fase incluye los resultados reales.

## Comprobación de interfaz con Chromium

La prueba requiere Node.js y Playwright con Chromium (instalación independiente
de las dependencias del backend):

```bash
npm install --prefix .tools/browser playwright
./.tools/browser/node_modules/.bin/playwright install chromium
PLAYWRIGHT_MODULE="$PWD/.tools/browser/node_modules/playwright" .venv/bin/python scripts/verify_browser.py
```

También se puede indicar `CHROMIUM_EXECUTABLE` para usar un navegador local.
El script crea una SQLite temporal, arranca otro servidor en un puerto libre,
prueba la UI, guarda capturas en `artifacts/` y elimina la base al terminar.
No modifica cuentas de la base local. Las capturas y logs se excluyen de Git.
