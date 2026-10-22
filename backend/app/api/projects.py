from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.security import current_user, require_csrf
from backend.app.db import get_db
from backend.app.errors import APIError
from backend.app.models import Experiment, Project, User
from backend.app.schemas.project import ProjectCreate, ProjectPatch, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


def owned_project(db: Session, project_id: UUID, user: User) -> Project:
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.owner_id == user.id)
    )
    if project is None:
        raise APIError(404, "not_found", "Proyecto no encontrado.")
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Project).where(Project.owner_id == user.id).order_by(Project.created_at, Project.id)
    ).all()


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate, user: User = Depends(require_csrf), db: Session = Depends(get_db)
):
    project = Project(owner_id=user.id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    return owned_project(db, project_id, user)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    data: ProjectPatch,
    user: User = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    project = owned_project(db, project_id, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: UUID, user: User = Depends(require_csrf), db: Session = Depends(get_db)
):
    project = owned_project(db, project_id, user)
    if db.scalar(select(Experiment.id).where(Experiment.project_id == project.id).limit(1)):
        raise APIError(
            409, "project_has_experiments", "Elimina primero los experimentos del proyecto."
        )
    db.delete(project)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise APIError(
            409, "project_has_experiments", "Elimina primero los experimentos del proyecto."
        ) from None
    return Response(status_code=204)
