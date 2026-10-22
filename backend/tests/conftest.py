import pytest
from alembic import command
from alembic.config import Config
from backend.app.core.config import ROOT, Settings
from backend.app.db import make_engine
from backend.app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def database_url(tmp_path):
    url = f"sqlite:///{tmp_path / 'test.db'}"
    config = Config(str(ROOT / "alembic.ini"))
    config.attributes["database_url"] = url
    command.upgrade(config, "head")
    return url


@pytest.fixture
def engine(database_url):
    db_engine = make_engine(database_url)
    yield db_engine
    db_engine.dispose()


@pytest.fixture
def settings(database_url):
    return Settings(_env_file=None, app_env="test", secret_key="t" * 48, database_url=database_url)


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as test_client:
        yield test_client
