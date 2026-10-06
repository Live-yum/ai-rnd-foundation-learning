import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from workbench.api import create_app


@pytest.fixture
def client(settings):
    settings.base_url = "https://model.example.test/v1"
    settings.model = "test-model"
    settings.api_key = SecretStr("dummy-api-test-key")
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


def test_report_exposes_bounded_toolchain_receipts_without_arbitrary_files(client, settings):
    from conftest import new_run

    from workbench.filesystem import write_json

    run_id = new_run(client.app.state.store)
    directory = settings.data_dir / "runs" / run_id
    evidence = {
        "source-context/context-receipt.json": {"source_is_untrusted_data": True},
        "daytona-verification.json": {"passed": False, "cleanup": "deleted"},
        "tool-failure.json": {"passed": False, "log": "redacted diagnostic"},
    }
    for name, value in evidence.items():
        write_json(directory / name, value)
    write_json(directory / "private.json", {"secret": "must-not-be-exposed"})
    response = client.get(f"/runs/{run_id}/report")
    assert response.status_code == 200
    assert response.json() == evidence
    assert "must-not-be-exposed" not in response.text
    assert (
        client.get(f"/runs/{run_id}/report", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )


def test_run_list_pagination_parameters_and_status_filter(client):
    from workbench.store import Run

    store = client.app.state.store
    project = store.create_project("history", "history-project")
    with store.tx() as session:
        session.add_all(
            [
                Run(
                    id="scope-run",
                    project_id=project["id"],
                    template="python-basic",
                    status="WAITING_EXTENSION_SCOPE",
                ),
                Run(
                    id="ready-run",
                    project_id=project["id"],
                    template="python-basic",
                    status="READY",
                ),
            ]
        )
    assert len(client.get("/runs?limit=1").json()) == 1
    assert len(client.get("/runs?limit=1&offset=1").json()) == 1
    assert client.get("/runs?limit=101").status_code == 422
    assert client.get("/runs?offset=-1").status_code == 422
    assert (
        client.get(f"/projects/{project['id']}/runs?status=WAITING_EXTENSION_SCOPE").json()[0]["id"]
        == "scope-run"
    )
    assert client.get("/projects/missing/runs").status_code == 404
