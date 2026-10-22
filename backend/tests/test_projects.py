from backend.app.models import Experiment
from sqlalchemy.orm import Session


def authenticate(client, email="owner@example.com"):
    account = {"email": email, "password": "a-long-password-2026"}
    assert client.post("/api/auth/register", json=account).status_code == 201
    assert client.post("/api/auth/login", json=account).status_code == 200
    return {"X-CSRF-Token": client.cookies.get("labtrack_csrf")}


def test_projects_crud_ownership_and_conflict(client):
    headers = authenticate(client)
    response = client.post("/api/projects", json={"name": "  Science  "}, headers=headers)
    assert response.status_code == 201
    project = response.json()
    path = f"/api/projects/{project['id']}"
    assert project["name"] == "Science"
    assert client.get(path).json() == project
    assert len(client.get("/api/projects").json()) == 1
    assert (
        client.patch(path, json={"description": "Updated"}, headers=headers).json()["description"]
        == "Updated"
    )
    with Session(client.app.state.engine) as db:
        from uuid import UUID

        experiment = Experiment(
            project_id=UUID(project["id"]), name="Run", dataset_name="Data", model_name="Model"
        )
        db.add(experiment)
        db.commit()
        experiment_id = experiment.id
    assert client.delete(path, headers=headers).status_code == 409
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    other_headers = authenticate(client, "other@example.com")
    assert client.get("/api/projects").json() == []
    for method in ("GET", "PATCH", "DELETE"):
        assert (
            client.request(
                method,
                path,
                headers=other_headers,
                **({"json": {"name": "Stolen"}} if method == "PATCH" else {}),
            ).status_code
            == 404
        )
    assert (
        client.post(
            "/api/auth/login",
            json={"email": "owner@example.com", "password": "a-long-password-2026"},
        ).status_code
        == 200
    )
    headers = {"X-CSRF-Token": client.cookies.get("labtrack_csrf")}
    with Session(client.app.state.engine) as db:
        db.delete(db.get(Experiment, experiment_id))
        db.commit()
    assert client.delete(path, headers=headers).status_code == 204
    assert client.get(path).status_code == 404


def test_project_validation(client):
    headers = authenticate(client)
    for data in (
        {},
        {"name": " "},
        {"name": "x" * 121},
        {"name": "Good", "description": "x" * 2001},
        {"name": "Good", "owner_id": "injected"},
    ):
        assert client.post("/api/projects", json=data, headers=headers).status_code == 422
    project = client.post("/api/projects", json={"name": "Good"}, headers=headers).json()
    for data in ({}, {"name": None}, {"name": " "}):
        assert (
            client.patch(f"/api/projects/{project['id']}", json=data, headers=headers).status_code
            == 422
        )
