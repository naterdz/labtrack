"""Arrancar API y base temporales para probar la UI sin tocar datos locales."""

import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[1]


def main():
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="browser-", dir=artifacts) as directory:
        url = f"sqlite:///{Path(directory) / 'smoke.db'}"
        config = Config(str(ROOT / "alembic.ini"))
        config.attributes["database_url"] = url
        command.upgrade(config, "head")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        env = {
            **os.environ,
            "APP_ENV": "test",
            "DATABASE_URL": url,
            "SECRET_KEY": secrets.token_urlsafe(48),
            "COOKIE_SECURE": "false",
        }
        endpoint = f"http://127.0.0.1:{port}"
        with (artifacts / "browser_server.log").open("w") as logs:
            server = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.app.main:create_app",
                    "--factory",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                ],
                cwd=ROOT,
                env=env,
                stdout=logs,
                stderr=logs,
            )
            try:
                for _ in range(100):
                    if server.poll() is not None:
                        raise RuntimeError("No se pudo iniciar el servidor temporal")
                    try:
                        with urllib.request.urlopen(
                            f"{endpoint}/api/health", timeout=1
                        ):
                            break
                    except (urllib.error.URLError, TimeoutError):
                        time.sleep(0.1)
                else:
                    raise RuntimeError("El servidor temporal no respondió")
                subprocess.run(
                    ["node", "scripts/smoke_browser.cjs"],
                    cwd=ROOT,
                    env={**env, "LABTRACK_TEST_URL": endpoint},
                    check=True,
                )
            finally:
                server.terminate()
                server.wait(timeout=10)


if __name__ == "__main__":
    main()
