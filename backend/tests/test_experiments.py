import pytest
from backend.tests.test_projects import authenticate

DATA = {"name": " Run ", "dataset_name": " Data ", "model_name": "Forest", "metric_value": 123.4}


def setup_project(client):
    headers = authenticate(client)
    project = client.post("/api/projects", json={"name": "Project"}, headers=headers).json()
    return headers, f"/api/projects/{project['id']}/experiments"


def test_experiments_crud_and_persistence(client):
    headers, path = setup_project(client)
    response = client.post(path, json=DATA, headers=headers)
    assert response.status_code == 201
    experiment = response.json()
    item = f"{path}/{experiment['id']}"
    assert experiment["metric_value"] == 123.4
    assert experiment["name"] == "Run"
    assert client.get(item).json() == experiment
    assert len(client.get(path).json()) == 1
    updated = client.patch(item, json={"metric_value": -50, "notes": "Revised"}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["dataset_name"] == "Data"
    assert (
        client.patch(item, json={"metric_value": None}, headers=headers).json()["metric_value"]
        is None
    )
    other = client.post("/api/projects", json={"name": "Other"}, headers=headers).json()
    assert (
        client.get(f"/api/projects/{other['id']}/experiments/{experiment['id']}").status_code == 404
    )
    client.post("/api/auth/logout", headers=headers)
    stranger = authenticate(client, "stranger@example.com")
    for method, suffix, body in [
        ("GET", "", None),
        ("POST", "", DATA),
        ("GET", "/" + experiment["id"], None),
        ("PATCH", "/" + experiment["id"], {"name": "Stolen"}),
        ("DELETE", "/" + experiment["id"], None),
    ]:
        assert (
            client.request(
                method, path + suffix, headers=stranger, **({"json": body} if body else {})
            ).status_code
            == 404
        )
    client.post(
        "/api/auth/login", json={"email": "owner@example.com", "password": "a-long-password-2026"}
    )
    headers = {"X-CSRF-Token": client.cookies.get("labtrack_csrf")}
    assert client.get(item).json()["notes"] == "Revised"
    assert client.delete(item, headers=headers).status_code == 204
    assert client.get(item).status_code == 404


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", " "),
        ("dataset_name", ""),
        ("model_name", None),
        ("metric_name", "x" * 81),
        ("metric_value", "NaN"),
        ("metric_value", "Infinity"),
        ("notes", "x" * 4001),
        ("project_id", "injected"),
    ],
)
def test_invalid_experiment(client, field, value):
    headers, path = setup_project(client)
    assert client.post(path, json={**DATA, field: value}, headers=headers).status_code == 422
    experiment = client.post(path, json=DATA, headers=headers).json()
    assert (
        client.patch(
            path + "/" + experiment["id"], json={field: value}, headers=headers
        ).status_code
        == 422
    )
