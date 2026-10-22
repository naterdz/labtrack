#!/usr/bin/env bash
set -euo pipefail
labtrack_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$labtrack_root"
if [[ ! -x .venv/bin/python ]]; then
  printf '%s\n' 'Primero instala el entorno siguiendo README.md.' >&2
  exit 1
fi
.venv/bin/python scripts/init_env.py
.venv/bin/python -m alembic upgrade head
exec .venv/bin/python -m uvicorn backend.app.main:create_app --factory --host 127.0.0.1 --port "${LABTRACK_PORT:-8765}"
