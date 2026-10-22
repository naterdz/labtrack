# F2 · CRUD y dashboard

En curso. F1 verificada: tag v0.1.0 y árbol inicial limpio.

| Tarea | Estado | Commit/ref | Archivos | Evidencia |
| --- | --- | --- | --- | --- |
| F2-01 | DONE | feature/f2-01-projects | api/projects.py, schemas/project.py, test_projects.py, test_foundation.py, scripts/test_sandbox.py | 56 passed; ruff PASS. CRUD, dos usuarios, validación y 409 con SQLite temporal. |

Entorno trasladado desde otro equipo: se reparó el enlace ignorado `.venv/bin/python`.
Pytest normal se bloquea en el portal de TestClient por los wakeups de sockets
restringidos. `python scripts/test_sandbox.py` limita la espera de epoll a 10 ms,
sin cambiar las aserciones ni la aplicación. Resultado real: 56 passed, 1 warning.
Fuera de este aislamiento se usa `python -m pytest -q backend/tests`.

| F2-02 | DONE | feature/f2-02-experiments | api/experiments.py, schemas/experiment.py, test_experiments.py, test_foundation.py | 26 passed; ruff PASS. CRUD, campos opcionales, PATCH, métricas finitas fuera de 0..1 y permisos en todas las rutas. |

Se retiraron las expectativas 501 de F1 para las rutas ya implementadas.
