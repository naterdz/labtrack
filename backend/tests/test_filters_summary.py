from backend.tests.test_projects import authenticate


def test_filters_pagination_and_private_counts(client):
    assert client.get("/api/summary").status_code == 401
    headers = authenticate(client)
    assert client.get("/api/summary").json() == {"projects_count": 0, "experiments_count": 0}
    project = client.post("/api/projects", json={"name": "First"}, headers=headers).json()
    path = f"/api/projects/{project['id']}/experiments"
    for name, model in [("Alpha", "Forest"), ("Beta", "FOREST"), ("100%_literal", "Linear")]:
        assert (
            client.post(
                path,
                json={"name": name, "model_name": model, "dataset_name": "Data", "notes": "A note"},
                headers=headers,
            ).status_code
            == 201
        )
    assert len(client.get(path, params={"model": "forest"}).json()) == 2
    assert len(client.get(path, params={"q": "ALPHA"}).json()) == 1
    assert len(client.get(path, params={"q": "NOTE"}).json()) == 3
    assert len(client.get(path, params={"q": "%_"}).json()) == 1
    assert client.get(path, params={"q": "' OR 1=1 --"}).json() == []
    assert client.get(path, params={"model": "absent"}).json() == []
    assert client.get(path, params={"q": "Alpha", "model": "Linear"}).json() == []
    first = client.get(path, params={"limit": 1}).json()
    second = client.get(path, params={"limit": 1, "offset": 1}).json()
    assert first[0]["id"] != second[0]["id"]
    assert client.get(path, params={"offset": 100}).json() == []
    for params in ({"limit": 0}, {"limit": 101}, {"offset": -1}):
        response = client.get(path, params=params)
        assert response.status_code == 422
        assert {"code", "message", "details"} <= response.json().keys()
    assert client.get("/api/summary").json() == {"projects_count": 1, "experiments_count": 3}
    client.post("/api/auth/logout", headers=headers)
    authenticate(client, "second@example.com")
    assert client.get("/api/summary").json() == {"projects_count": 0, "experiments_count": 0}
    assert client.get(path, params={"q": "Alpha"}).status_code == 404
