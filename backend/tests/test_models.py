from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from backend.app.core.config import ROOT
from backend.app.db import make_engine
from backend.app.models import Experiment, Project, User
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_relationships_uuid_utc_and_persistence(engine, database_url):
    with Session(engine) as session:
        user = User(email=" Test@Example.com ", password_hash="test-hash")
        project = Project(name=" Proyecto ", owner=user)
        experiment = Experiment(
            name="Prueba",
            dataset_name="datos.csv",
            model_name="baseline",
            metric_name="RMSE",
            metric_value=15.6,
            project=project,
        )
        session.add(experiment)
        session.commit()
        experiment_id = experiment.id
        assert isinstance(experiment.id, UUID)
        assert experiment.created_at.utcoffset() == timedelta(0)
        assert project.name == "Proyecto"
        assert user.email == "test@example.com"
        created = project.updated_at
        project.description = "Cambio"
        session.commit()
        assert project.updated_at >= created
    engine.dispose()
    reopened = make_engine(database_url)
    with Session(reopened) as session:
        experiment = session.get(Experiment, experiment_id)
        assert experiment.project.owner.email == "test@example.com"
        assert experiment.metric_value == 15.6
    reopened.dispose()


def test_unique_email_and_foreign_key(engine):
    with Session(engine) as session:
        session.add(User(email="a@example.com", password_hash="test"))
        session.commit()
        session.add(User(email="A@example.com", password_hash="test"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        session.add(Project(name="Huérfano", owner_id=uuid4()))
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.parametrize("bad_name", ["", "   ", "x" * 121])
def test_project_name_constraints(engine, bad_name):
    with Session(engine) as session:
        session.add(Project(name=bad_name, owner=User(email="a@example.com", password_hash="x")))
        with pytest.raises(IntegrityError):
            session.commit()


def test_parent_delete_is_restricted(engine):
    with Session(engine) as session:
        project = Project(name="Con hijos", owner=User(email="a@example.com", password_hash="x"))
        session.add(Experiment(name="E", dataset_name="D", model_name="M", project=project))
        session.commit()
        session.delete(project)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        assert session.scalar(select(Experiment)) is not None


def test_schema_and_migration_round_trip(database_url):
    config = Config(str(ROOT / "alembic.ini"))
    config.attributes["database_url"] = database_url
    command.check(config)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    engine = make_engine(database_url)
    schema = inspect(engine)
    assert {"users", "projects", "experiments"}.issubset(schema.get_table_names())
    assert schema.get_foreign_keys("projects")[0]["referred_table"] == "users"
    assert schema.get_foreign_keys("experiments")[0]["referred_table"] == "projects"
    for table in ["users", "projects", "experiments"]:
        assert "status" not in {c["name"] for c in schema.get_columns(table)}
    engine.dispose()
