from datetime import UTC, datetime
from math import isfinite
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import TypeDecorator

from backend.app.db import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """Mantener datetimes conscientes de UTC también al leer desde SQLite."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Se requiere una fecha con zona horaria")
        return value.astimezone(UTC)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(email) BETWEEN 3 AND 254", name="ck_users_email_length"),
        CheckConstraint("email = lower(trim(email))", name="ck_users_email_normalized"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, nullable=False)
    projects: Mapped[list["Project"]] = relationship(back_populates="owner", passive_deletes="all")

    @validates("email")
    def normalize_email(self, key, value):
        return value.strip().lower()


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("length(trim(name)) BETWEEN 1 AND 120", name="ck_projects_name"),
        CheckConstraint("name = trim(name)", name="ck_projects_name_trimmed"),
        CheckConstraint("length(description) <= 2000", name="ck_projects_description"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
    owner: Mapped[User] = relationship(back_populates="projects")
    experiments: Mapped[list["Experiment"]] = relationship(
        back_populates="project", passive_deletes="all"
    )

    @validates("name")
    def trim_name(self, key, value):
        return value.strip()


class Experiment(Base):
    __tablename__ = "experiments"
    __table_args__ = (
        CheckConstraint("length(trim(name)) BETWEEN 1 AND 120", name="ck_experiments_name"),
        CheckConstraint(
            "length(trim(dataset_name)) BETWEEN 1 AND 200", name="ck_experiments_dataset"
        ),
        CheckConstraint("length(trim(model_name)) BETWEEN 1 AND 120", name="ck_experiments_model"),
        CheckConstraint("length(metric_name) <= 80", name="ck_experiments_metric_name"),
        CheckConstraint("length(notes) <= 4000", name="ck_experiments_notes"),
        CheckConstraint(
            "metric_value IS NULL OR "
            "metric_value BETWEEN -1.7976931348623157e308 AND 1.7976931348623157e308",
            name="ck_experiments_metric_finite",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    metric_name: Mapped[str | None] = mapped_column(String(80))
    metric_value: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
    project: Mapped[Project] = relationship(back_populates="experiments")

    @validates("metric_value")
    def finite_metric(self, key, value):
        if value is not None and not isfinite(value):
            raise ValueError("La métrica debe ser un número finito")
        return value
