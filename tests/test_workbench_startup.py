from fastapi.testclient import TestClient

from workbench.api import create_app


def test_missing_models_serves_shell_but_prevents_new_work(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        assert client.get("/").status_code == 200
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        project = client.post(
            "/projects", json={"title": "尚未配置"}, headers={"Idempotency-Key": "p"}
        )
        assert project.status_code == 201
        result = client.post(
            f"/projects/{project.json()['id']}/runs",
            json={"requirement": "任务管理"},
            headers={"Idempotency-Key": "r"},
        )
        assert result.status_code == 503
        assert "配置" in result.json()["detail"]
        assert client.get("/runs").json() == []


def test_invalid_api_body_never_echoes_private_user_input(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        result = client.post(
            "/projects",
            json={"title": "ok", "api_key": "dummy-secret-private"},
            headers={"Idempotency-Key": "x"},
        )
        assert result.status_code == 422
        assert "dummy-secret-private" not in result.text


def test_corrupt_config_models_endpoint_fails_safely(settings):
    settings.prepare()
    path = settings.data_dir / "model-settings.json"
    path.write_text('{"api_key":"dummy-private-secret",broken}', encoding="utf-8")
    path.chmod(0o600)
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.get("/models")
        assert response.status_code == 503
        assert "dummy-private-secret" not in response.text
        assert client.get("/").status_code == 200


def test_shell_has_local_resource_and_frame_security_policy(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        response = client.get("/")
        assert client.get("/ui").content == response.content
        assert client.get("/ui/").content == response.content
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "script-src 'self'" in response.headers["content-security-policy"]
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
