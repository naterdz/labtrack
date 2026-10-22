from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.security import current_user
from backend.app.db import get_db
from backend.app.models import Experiment, Project, User

router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.get("")
def summary(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {
        "projects_count": db.scalar(
            select(func.count()).select_from(Project).where(Project.owner_id == user.id)
        ),
        "experiments_count": db.scalar(
            select(func.count())
            .select_from(Experiment)
            .join(Project)
            .where(Project.owner_id == user.id)
        ),
    }
