import pytest
from backend.app.models import Experiment, Project, User
from scripts.seed_demo import seed_demo
from sqlalchemy import func, select
from sqlalchemy.orm import Session


def test_demo_is_opt_in_idempotent_and_private(settings, engine):
    settings.app_env = "development"
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0
    assert seed_demo(settings, " DEMO@example.com ", "demo-test-password-2026") is True
    assert seed_demo(settings, "demo@example.com", "demo-test-password-2026") is False
    with pytest.raises(ValueError, match="credenciales"):
        seed_demo(settings, "demo@example.com", "incorrect-password-2026")
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 1
        assert db.scalar(select(func.count()).select_from(Project)) == 1
        assert db.scalar(select(func.count()).select_from(Experiment)) == 2
        assert db.scalar(select(User)).password_hash != "demo-test-password-2026"


@pytest.mark.parametrize("environment", ["test", "production"])
def test_demo_rejects_non_development_before_database_access(settings, environment):
    settings.app_env = environment
    settings.database_url = "invalid://must-not-connect"
    with pytest.raises(ValueError, match="development"):
        seed_demo(settings, "demo@example.com", "demo-test-password-2026")
