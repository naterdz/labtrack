from backend.app.core.config import Settings
from backend.app.main import create_app
from fastapi.testclient import TestClient


def test_health(tmp_path):
    settings = Settings(
        _env_file=None,
        app_env="test",
        secret_key="t" * 48,
        database_url=f"sqlite:///{tmp_path / 'health.db'}",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "labtrack"}
