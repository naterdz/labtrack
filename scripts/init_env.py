"""Crear configuración privada local sin sobrescribirla ni mostrar sus valores."""

import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def init_env(root: Path = ROOT) -> bool:
    template = (root / ".env.example").read_text(encoding="utf-8")
    content = template.replace(
        "SECRET_KEY=\n", f"SECRET_KEY={secrets.token_urlsafe(48)}\n"
    )
    try:
        fd = os.open(root / ".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        output.write(content)
    return True


if __name__ == "__main__":
    print(
        "Configuración local creada."
        if init_env()
        else "Configuración existente conservada."
    )
