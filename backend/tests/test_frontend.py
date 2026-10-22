def test_frontend_and_assets_share_origin(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'lang="es-MX"' in response.text
    assert 'id="auth-form"' in response.text
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    for path, content_type in [
        ("/static/css/styles.css", "text/css"),
        ("/static/css/tokens.css", "text/css"),
        ("/static/js/api.js", "javascript"),
        ("/static/js/app.js", "javascript"),
        ("/static/favicon.svg", "image/svg+xml"),
    ]:
        asset = client.get(path)
        assert asset.status_code == 200
        assert content_type in asset.headers["content-type"]


def test_unknown_api_route_is_not_spa_html(client):
    response = client.get("/api/missing")
    assert response.status_code == 404
    assert response.json()["code"] == "http_404"
