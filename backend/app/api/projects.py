from uuid import UUID

from fastapi import APIRouter, Depends

from backend.app.core.security import current_user, require_csrf
from backend.app.errors import APIError

router = APIRouter(prefix="/api/projects", tags=["projects · pendiente F2"])


def pending():
    raise APIError(
        501, "not_implemented", "La gestión de proyectos estará disponible en la siguiente etapa."
    )


def pending_item(project_id: UUID):
    pending()


for path, method in [
    ("", "GET"),
    ("", "POST"),
    ("/{project_id}", "GET"),
    ("/{project_id}", "PATCH"),
    ("/{project_id}", "DELETE"),
]:
    router.add_api_route(
        path,
        pending_item if path else pending,
        methods=[method],
        dependencies=[Depends(current_user if method == "GET" else require_csrf)],
        name=f"pending_projects_{method}_{'item' if path else 'list'}",
    )
