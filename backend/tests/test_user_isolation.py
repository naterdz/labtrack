from backend.tests.test_projects import authenticate
from fastapi.testclient import TestClient


def test_two_users_full_workflow_and_persistence(client):
    headers_a = authenticate(client, "a@example.com")
    project_a = client.post("/api/projects", json={"name": "A"}, headers=headers_a).json()
    project_path = f"/api/projects/{project_a['id']}"
    path = project_path + "/experiments"
    experiment = client.post(
        path,
        json={"name": "Trial A", "dataset_name": "Private data", "model_name": "Forest"},
        headers=headers_a,
    ).json()
    item = f"{path}/{experiment['id']}"
    # A separate browser session on the same application/database.
    with TestClient(client.app) as other:
        headers_b = authenticate(other, "b@example.com")
        project_b = other.post("/api/projects", json={"name": "B"}, headers=headers_b).json()
        assert other.get("/api/projects").json() == [project_b]
        assert other.get("/api/summary").json() == {"projects_count": 1, "experiments_count": 0}
        for method, url, body in [
            ("GET", project_path, None),
            ("PATCH", project_path, {"name": "Stolen"}),
            ("DELETE", project_path, None),
            ("GET", path + "?model=FOREST&q=Trial", None),
            ("POST", path, {"name": "X", "dataset_name": "X", "model_name": "X"}),
            ("GET", item, None),
            ("PATCH", item, {"metric_value": 99}),
            ("DELETE", item, None),
        ]:
            response = other.request(
                method, url, headers=headers_b, **({"json": body} if body is not None else {})
            )
            assert response.status_code == 404
            assert response.json()["code"] == "not_found"
        assert client.get(path, params={"model": "FOREST", "q": "trial"}).json() == [experiment]
        assert client.delete(project_path, headers=headers_a).status_code == 409
        assert client.get("/api/summary").json() == {"projects_count": 1, "experiments_count": 1}
        assert client.get(item).json() == experiment
        assert client.delete(item, headers=headers_a).status_code == 204
        assert client.delete(project_path, headers=headers_a).status_code == 204
        assert client.get("/api/summary").json() == {"projects_count": 0, "experiments_count": 0}
        assert other.get("/api/projects").json() == [project_b]
        assert other.post("/api/auth/logout", headers=headers_b).status_code == 204
        assert other.get("/api/summary").status_code == 401
    assert client.post("/api/auth/logout", headers=headers_a).status_code == 204
