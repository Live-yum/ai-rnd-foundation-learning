import pytest
from fastapi.testclient import TestClient

from workbench.api import create_app


@pytest.fixture
def client(settings):
    app = create_app(settings, start_worker=False)
    with TestClient(app) as c:
        c.headers["Authorization"] = "Bearer " + app.state.token
        yield c


def test_auth_and_host(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200
    assert client.get("/projects", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/health", headers={"Host": "attacker.example"}).status_code == 400


def test_project_run_idempotency_roles(client):
    headers = {"Idempotency-Key": "project-key"}
    project = client.post("/projects", json={"title": "test"}, headers=headers)
    assert project.status_code == 201
    assert (
        client.post("/projects", json={"title": "test"}, headers=headers).json() == project.json()
    )
    assert client.post("/projects", json={"title": "changed"}, headers=headers).status_code == 409
    assert client.post("/projects", json={"title": "x"}).status_code == 422
    url = "/projects/" + project.json()["id"] + "/runs"
    payload = {"requirement": "个人任务 CRUD"}
    run = client.post(url, json=payload, headers={"Idempotency-Key": "run-key"})
    assert run.status_code == 202
    assert (
        client.post(
            url, json={**payload, "role": "system"}, headers={"Idempotency-Key": "bad"}
        ).status_code
        == 422
    )
    run_id = run.json()["run_id"]
    assert client.get("/runs/" + run_id + "/messages").json()[0]["role"] == "user"
    assert client.get("/runs/" + run_id + "/download").status_code == 409
    assert client.get("/runs/missing").status_code == 404
    assert client.get("/templates").status_code == 200
