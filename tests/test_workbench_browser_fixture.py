"""The actual Chromium driver lives in scripts/ci_guided_browser.py.

These fast tests guard the explicit fixture's streaming proof and preserved guided
regression independently of optional local Chromium installation.
"""

import asyncio
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi import FastAPI
from pydantic import SecretStr

from scripts.ci_guided_browser import (
    CATALOG_KEY,
    CATALOG_MODELS,
    SETTINGS_READ_FAILURE,
    STREAM_SUMMARY,
    CatalogFixture,
    SettingsReadControl,
    SettingsReadFixture,
    stream_packets,
)
from scripts.news_fixture import news_requirement, news_spec
from workbench.domain import ModelReview, Plan, Requirement
from workbench.llm import ModelGateway
from workbench.model_settings import ModelSettingsRepository, register_model_settings_routes
from workbench.streaming import root_string_prefix


def fragments(value):
    packets = list(stream_packets(value, "explicit-fixture"))
    content = []
    for boundary, packet in packets:
        assert packet.startswith(b"data: ") and packet.endswith(b"\r\n\r\n")
        if packet == b"data: [DONE]\r\n\r\n":
            continue
        item = json.loads(packet[6:].decode("utf-8"))
        assert item["object"] == "chat.completion.chunk"
        choice = item["choices"][0]
        content.append((boundary, choice["delta"].get("content", "")))
    return packets, content


def test_browser_provider_holds_real_terminal_bytes_until_a_visible_draft():
    value = news_requirement()
    value["summary"] = STREAM_SUMMARY
    packets, content = fragments(value)
    raw = ""
    before_release = []
    for boundary, fragment in content:
        if boundary:
            assert root_string_prefix(raw, "summary") == STREAM_SUMMARY
            # A visible summary cannot masquerade as a complete validated object.
            try:
                json.loads(raw)
            except ValueError:
                pass
            else:
                raise AssertionError("Fixture must withhold part of the model JSON")
        raw += fragment
        before_release.append(root_string_prefix(raw, "summary"))
    assert json.loads(raw) == value
    assert len(set(before_release)) >= 3, "The fixture yields genuinely distinct partial text"
    assert any(fragment.endswith(r"\ud8") for _, fragment in content)
    assert packets[-1][1] == b"data: [DONE]\r\n\r\n"
    assert sum(boundary for boundary, _ in packets) == 1
    Requirement.model_validate_json(raw)


def test_browser_fixture_preserves_strict_planning_and_review_contracts():
    values = [
        (news_spec(), Plan),
        ({"summary": "审阅结果", "observations": [], "uncovered_requirements": []}, ModelReview),
    ]
    for value, schema in values:
        packets, content = fragments(value)
        schema.model_validate_json("".join(text for _, text in content))
        finish = json.loads(packets[-2][1][6:])
        assert finish["choices"][0]["finish_reason"] == "stop"


def test_browser_provider_packets_pass_the_actual_structured_model_gateway(store):
    store.settings.base_url = "http://127.0.0.1:8888/v1"
    store.settings.model = "requirements-fixture"
    store.settings.api_key = SecretStr("explicit-ci-only")
    project = store.create_project("Browser fixture", str(uuid.uuid4()))
    run = store.create_run(
        project["id"], {"requirement": "fixture", "template": "python-basic"}, str(uuid.uuid4())
    )["run_id"]
    value = news_requirement()
    value["summary"] = STREAM_SUMMARY
    raw = b"".join(packet for _, packet in stream_packets(value, "requirements-fixture"))

    class Bytes(httpx.SyncByteStream):
        def __iter__(self):
            for offset in range(0, len(raw), 2):
                yield raw[offset : offset + 2]

    gateway = ModelGateway(
        store.settings,
        store,
        httpx.MockTransport(
            lambda _: httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=Bytes()
            )
        ),
        streaming=True,
    )
    assert (
        gateway.complete(run, "requirement:fixture", "JSON", {}, Requirement).summary
        == STREAM_SUMMARY
    )
    assert store.transcript(run)["messages"][-1]["validation"] == "validated"


@pytest.mark.parametrize("mode,status", [("success", 200), ("unsupported", 404), ("denied", 401)])
def test_browser_catalog_fixture_uses_explicit_safe_catalog_responses(mode, status):
    fixture = CatalogFixture()
    fixture.arm(mode)
    code, payload = fixture.response("/catalog-v1/models", "Bearer " + CATALOG_KEY)
    assert code == status
    if mode == "success":
        assert [row["id"] for row in payload["data"]] == CATALOG_MODELS
    assert fixture.status() == {
        "calls": [{"method": "GET", "path": "/catalog-v1/models"}],
        "started": True,
    }
    assert CATALOG_KEY not in json.dumps(payload) + json.dumps(fixture.status())


def test_browser_catalog_fixture_holds_response_until_browser_releases():
    fixture = CatalogFixture()
    fixture.arm("success", hold=True)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fixture.response, "/catalog-v1/models", "Bearer " + CATALOG_KEY)
        try:
            assert fixture.started.wait(2)
            assert not future.done(), "The UI must observe a genuinely pending provider response"
            assert len(fixture.calls) == 1
        finally:
            fixture.release.set()
        assert future.result(timeout=2)[0] == 200


@pytest.mark.parametrize(
    "path,key", [("/wrong-destination/models", CATALOG_KEY), ("/catalog-v1/models", "wrong-key")]
)
def test_browser_catalog_fixture_fails_closed_on_wrong_destination_or_key(path, key):
    fixture = CatalogFixture()
    with pytest.raises(AssertionError):
        fixture.response(path, "Bearer " + key)
    assert fixture.calls == [{"method": "GET", "path": path}]
    assert key not in json.dumps(fixture.status())


def test_browser_settings_read_faults_preserve_real_saves_and_manual_retry(settings):
    app = FastAPI()
    register_model_settings_routes(app, settings, lambda: None)
    control = SettingsReadControl()
    fixture = SettingsReadFixture(app, control)
    repository = ModelSettingsRepository(settings)

    async def exercise():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=fixture), base_url="http://fixture.local"
        ) as client:
            original = (await client.get("/settings/models")).json()
            control.arm("hold")
            pending = asyncio.create_task(client.get("/settings/models"))
            try:
                for _ in range(100):
                    if control.started.is_set():
                        break
                    await asyncio.sleep(0.01)
                assert control.started.is_set() and not pending.done()
            finally:
                control.release.set()
            assert (await asyncio.wait_for(pending, timeout=2)).json() == original

            control.arm("fail")
            # A read failure must not intercept PATCH or fabricate the persisted result.
            saved = await client.patch(
                "/settings/models",
                json={
                    "expected_revision": original["revision"],
                    "default": {
                        "base_url": "http://127.0.0.1:8888/catalog-v1",
                        "model": "manual-model",
                        "api_key": CATALOG_KEY,
                    },
                },
            )
            assert saved.status_code == 200
            assert saved.json()["default"]["model"] == "manual-model"
            persisted = repository.path.read_bytes()
            failure = await client.get("/settings/models")
            assert failure.status_code == 503
            assert failure.json() == {"detail": SETTINGS_READ_FAILURE}
            assert repository.path.read_bytes() == persisted
            retried = await client.get("/settings/models")
            assert retried.status_code == 200 and retried.json() == saved.json()
            assert repository.path.read_bytes() == persisted
            assert CATALOG_KEY not in saved.text + failure.text + retried.text
            assert sum(request["method"] == "PATCH" for request in control.requests) == 1

    asyncio.run(exercise())


def test_browser_read_fault_does_not_intercept_real_discovery_validation(settings):
    app = FastAPI()
    register_model_settings_routes(app, settings, lambda: None)
    control = SettingsReadControl()
    control.arm("fail")

    async def exercise():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=SettingsReadFixture(app, control)),
            base_url="http://fixture.local",
        ) as client:
            response = await client.post("/settings/models/discover", json={})
            assert response.status_code == 422
            assert not control.started.is_set()
            assert (await client.get("/settings/models")).status_code == 503
            assert (await client.get("/settings/models")).status_code == 200

    asyncio.run(exercise())
