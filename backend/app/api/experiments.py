from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.projects import owned_project
from backend.app.core.security import current_user, require_csrf
from backend.app.db import get_db
from backend.app.errors import APIError
from backend.app.models import Experiment, User
from backend.app.schemas.experiment import ExperimentCreate, ExperimentPatch, ExperimentResponse

router = APIRouter(prefix="/api/projects/{project_id}/experiments", tags=["experiments"])


def owned_experiment(db, project_id, experiment_id, user):
    owned_project(db, project_id, user)
    experiment = db.scalar(
        select(Experiment).where(
            Experiment.project_id == project_id, Experiment.id == experiment_id
        )
    )
    if experiment is None:
        raise APIError(404, "not_found", "Experimento no encontrado.")
    return experiment


@router.get("", response_model=list[ExperimentResponse])
def list_experiments(
    project_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    owned_project(db, project_id, user)
    return db.scalars(
        select(Experiment)
        .where(Experiment.project_id == project_id)
        .order_by(Experiment.created_at, Experiment.id)
    ).all()


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(
    project_id: UUID,
    data: ExperimentCreate,
    user: User = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    owned_project(db, project_id, user)
    experiment = Experiment(project_id=project_id, **data.model_dump())
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(
    project_id: UUID,
    experiment_id: UUID,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return owned_experiment(db, project_id, experiment_id, user)


@router.patch("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(
    project_id: UUID,
    experiment_id: UUID,
    data: ExperimentPatch,
    user: User = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    experiment = owned_experiment(db, project_id, experiment_id, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(experiment, field, value)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(
    project_id: UUID,
    experiment_id: UUID,
    user: User = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    experiment = owned_experiment(db, project_id, experiment_id, user)
    db.delete(experiment)
    db.commit()
    return Response(status_code=204)
