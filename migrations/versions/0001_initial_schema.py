"""Usuarios, proyectos y experimentos; esquema inicial portable."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def timestamps():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint(
            "length(email) BETWEEN 3 AND 254", name="ck_users_email_length"
        ),
        sa.CheckConstraint(
            "email = lower(trim(email))", name="ck_users_email_normalized"
        ),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        *timestamps(),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "length(trim(name)) BETWEEN 1 AND 120", name="ck_projects_name"
        ),
        sa.CheckConstraint("name = trim(name)", name="ck_projects_name_trimmed"),
        sa.CheckConstraint(
            "length(description) <= 2000", name="ck_projects_description"
        ),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("dataset_name", sa.String(200), nullable=False),
        sa.Column("model_name", sa.String(120), nullable=False),
        sa.Column("metric_name", sa.String(80)),
        sa.Column("metric_value", sa.Float()),
        sa.Column("notes", sa.Text()),
        *timestamps(),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "length(trim(name)) BETWEEN 1 AND 120", name="ck_experiments_name"
        ),
        sa.CheckConstraint(
            "length(trim(dataset_name)) BETWEEN 1 AND 200",
            name="ck_experiments_dataset",
        ),
        sa.CheckConstraint(
            "length(trim(model_name)) BETWEEN 1 AND 120", name="ck_experiments_model"
        ),
        sa.CheckConstraint(
            "length(metric_name) <= 80", name="ck_experiments_metric_name"
        ),
        sa.CheckConstraint("length(notes) <= 4000", name="ck_experiments_notes"),
        sa.CheckConstraint(
            "metric_value IS NULL OR "
            "metric_value BETWEEN -1.7976931348623157e308 AND 1.7976931348623157e308",
            name="ck_experiments_metric_finite",
        ),
    )
    op.create_index("ix_experiments_project_id", "experiments", ["project_id"])


def downgrade():
    op.drop_table("experiments")
    op.drop_table("projects")
    op.drop_table("users")
