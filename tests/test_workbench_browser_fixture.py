"""The actual Chromium driver lives in scripts/ci_guided_browser.py.

These fast tests guard the explicit fixture's streaming proof and preserved guided
regression independently of optional local Chromium installation.
"""

import json
import uuid

import httpx
from pydantic import SecretStr

from scripts.ci_guided_browser import STREAM_SUMMARY, stream_packets
from scripts.news_fixture import news_requirement, news_spec
from workbench.domain import ModelReview, Plan, Requirement
from workbench.llm import ModelGateway
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
