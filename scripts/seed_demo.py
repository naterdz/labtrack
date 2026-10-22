"""Opt-in development demo: python -m scripts.seed_demo --email tu@ejemplo.com."""

import argparse
import getpass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.core.security import password_hasher, verify_password
from backend.app.db import make_engine
from backend.app.models import Experiment, Project, User
from backend.app.schemas.auth import RegisterRequest

DEMO_PROJECT = "Demo · Comparación de modelos"


def seed_demo(settings: Settings, email: str, password: str) -> bool:
    """Insert one demo transaction; never overwrite existing accounts/projects."""
    if settings.app_env != "development":
        raise ValueError("La demo solo se permite con APP_ENV=development.")
    account = RegisterRequest(email=email, password=password)
    engine = make_engine(settings.database_url)
    try:
        with Session(engine) as db, db.begin():
            user = db.scalar(select(User).where(User.email == str(account.email)))
            if user is None:
                user = User(
                    email=str(account.email),
                    password_hash=password_hasher.hash(
                        account.password.get_secret_value()
                    ),
                )
                db.add(user)
                db.flush()
            elif not verify_password(
                account.password.get_secret_value(), user.password_hash
            ):
                raise ValueError(
                    "Las credenciales de la cuenta existente no son válidas."
                )
            existing = db.scalar(
                select(Project).where(
                    Project.owner_id == user.id, Project.name == DEMO_PROJECT
                )
            )
            if existing:
                return False
            project = Project(
                owner_id=user.id,
                name=DEMO_PROJECT,
                description="Datos sintéticos de ejemplo; puedes editarlos o eliminarlos.",
            )
            db.add(project)
            db.flush()
            db.add_all(
                [
                    Experiment(
                        project_id=project.id,
                        name="Regresión base",
                        dataset_name="Viviendas sintéticas",
                        model_name="LinearRegression",
                        metric_name="MAE",
                        metric_value=42.5,
                        notes="Datos de demostración.",
                    ),
                    Experiment(
                        project_id=project.id,
                        name="Comparación con bosque",
                        dataset_name="Viviendas sintéticas",
                        model_name="RandomForest",
                        metric_name="MAE",
                        metric_value=31.2,
                    ),
                ]
            )
        return True
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Cargar demo opcional en desarrollo.")
    parser.add_argument("--email", required=True, help="Cuenta para los datos demo.")
    args = parser.parse_args()
    settings = Settings()
    if settings.app_env != "development":
        parser.error("La demo solo se permite con APP_ENV=development.")
    password = getpass.getpass("Contraseña de la cuenta (12–128 caracteres): ")
    try:
        created = seed_demo(settings, args.email, password)
    except ValidationError:
        parser.error("Revisa el correo y la longitud de la contraseña.")
    except ValueError as exc:
        parser.error(str(exc))
    print("Demo creada." if created else "La demo ya existe; datos conservados.")


if __name__ == "__main__":
    main()
