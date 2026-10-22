from uuid import UUID

from fastapi import APIRouter, Depends

from backend.app.core.security import current_user, require_csrf
from backend.app.errors import APIError

router = APIRouter(
    prefix="/api/projects/{project_id}/experiments", tags=["experiments · pendiente F2"]
)


def pending(project_id: UUID):
    raise APIError(
        501,
        "not_implemented",
        "La gestión de experimentos estará disponible en la siguiente etapa.",
    )


def pending_item(project_id: UUID, experiment_id: UUID):
    pending(project_id)


for path, method in [
    ("", "GET"),
    ("", "POST"),
    ("/{experiment_id}", "GET"),
    ("/{experiment_id}", "PATCH"),
    ("/{experiment_id}", "DELETE"),
]:
    router.add_api_route(
        path,
        pending_item if path else pending,
        methods=[method],
        dependencies=[Depends(current_user if method == "GET" else require_csrf)],
        name=f"pending_experiments_{method}_{'item' if path else 'list'}",
    )
