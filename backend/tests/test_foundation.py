"""Contrato transitorio F1: actualizar estas expectativas al implementar cada ruta en F2."""

import pytest
from backend.app.models import Experiment, Project
from sqlalchemy import func, select
from sqlalchemy.orm import Session

PROJECT = "11111111-1111-4111-8111-111111111111"
EXPERIMENT = "22222222-2222-4222-8222-222222222222"
BASE = f"/api/projects/{PROJECT}"
ROUTES = [
    ("GET", "/api/projects"),
    ("POST", "/api/projects"),
    ("GET", BASE),
    ("PATCH", BASE),
    ("DELETE", BASE),
    ("GET", f"{BASE}/experiments"),
    ("POST", f"{BASE}/experiments"),
    ("GET", f"{BASE}/experiments/{EXPERIMENT}"),
    ("PATCH", f"{BASE}/experiments/{EXPERIMENT}"),
    ("DELETE", f"{BASE}/experiments/{EXPERIMENT}"),
]
ACCOUNT = {"email": "foundation@example.com", "password": "fundamentos-2026-segura"}


def login(client):
    assert client.post("/api/auth/register", json=ACCOUNT).status_code == 201
    assert client.post("/api/auth/login", json=ACCOUNT).status_code == 200
    return {"X-CSRF-Token": client.cookies.get("labtrack_csrf")}


@pytest.mark.f1
@pytest.mark.parametrize("method,path", ROUTES)
def test_all_pending_routes_require_authentication(client, method, path):
    response = client.request(method, path)
    assert response.status_code == 401
    assert response.json()["code"] == "unauthenticated"


@pytest.mark.f1
@pytest.mark.parametrize("method,path", [(m, p) for m, p in ROUTES if "experiments" in p])
def test_all_pending_routes_return_explicit_501(client, method, path):
    headers = login(client)
    response = client.request(method, path, headers=headers)
    assert response.status_code == 501
    assert response.json()["code"] == "not_implemented"
    with Session(client.app.state.engine) as session:
        assert session.scalar(select(func.count()).select_from(Project)) == 0
        assert session.scalar(select(func.count()).select_from(Experiment)) == 0


@pytest.mark.f1
@pytest.mark.parametrize("method,path", [(m, p) for m, p in ROUTES if m != "GET"])
def test_pending_mutations_require_csrf(client, method, path):
    login(client)
    assert client.request(method, path).status_code == 403
    assert client.request(method, path, headers={"X-CSRF-Token": "invalid"}).status_code == 403


@pytest.mark.f1
def test_foundation_end_to_end_and_openapi(client):
    assert client.get("/api/health").json() == {"status": "ok", "service": "labtrack"}
    headers = login(client)
    assert client.get("/api/auth/me").json()["email"] == ACCOUNT["email"]
    assert client.get("/api/projects").status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/auth/me").status_code == 401
    spec = client.get("/openapi.json").json()
    assert "/api/summary" not in spec["paths"]  # F2
    route = spec["paths"]["/api/projects/{project_id}/experiments/{experiment_id}"]["get"]
    assert {p["name"] for p in route["parameters"] if p["in"] == "path"} == {
        "project_id",
        "experiment_id",
    }
