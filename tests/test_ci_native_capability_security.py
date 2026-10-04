"""Mocked certificate orchestration; never represents live native security proof."""

import copy
import json
from types import SimpleNamespace

import pytest

from scripts import ci_native_capability_security as ci
from scripts.ci_native_generated import acceptance_spec
from workbench.capability_execution import security_checks_for
from workbench.capability_native_runtime import native_start_command
from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest
from workbench.settings import Settings

IMAGE = "sha256:" + "9" * 64
TABLE = "wb_01234567_device"


@pytest.fixture
def product(tmp_path):
    root = tmp_path / "product"
    plan = acceptance_spec().model_dump()
    metadata = {
        "format": 1,
        "template": "fastapiadmin",
        "contains_user_data": False,
        "bootstrap": "native-seed-then-business-schema-and-menus",
        "spec_digest": digest(plan),
        "plan": plan,
        "targets": [
            {
                "entity": "device",
                "api": "/rnd/device",
                "list": "/rnd/device/list",
                "route": "/module_rnd/device",
                "permission": "module_rnd:device",
                "table": TABLE,
            }
        ],
        "tables": {TABLE: ["id", "name", "quantity", "active"]},
    }
    atomic_text(root / "deployment/manifest.json", json.dumps(metadata))
    for name in (
        "backend/app/__init__.py",
        "backend/app/plugin/module_rnd/device/controller.py",
        "frontend/web/src/views/module_rnd/device/index.vue",
    ):
        atomic_text(root / name, "source-fixture-never-executed")
    return root


def test_authored_native_contract_has_real_captcha_form_login_and_typed_crud(product):
    plan = ci.fixed_plan(product)
    assert plan.selection.model_dump() == ci.selection()
    assert plan.runtime.database_tables == ["sys_user", TABLE]
    assert plan.runtime.prepare == []
    assert native_start_command(plan) == plan.runtime.start
    assert plan.runtime.port == 8000 and plan.runtime.health_path == "/openapi.json"
    signup, devices = plan.scenarios
    assert signup.steps[0].path == "/system/user/register"
    assert signup.steps[0].body["username"] == ci.SIGNUP_USER
    assert len(ci.SIGNUP_USER) <= 32
    for scenario in plan.scenarios:
        login = [step for step in scenario.steps if step.path == "/system/auth/login"]
        assert login and all(step.body_encoding == "form" for step in login)
        assert all("captcha_key" in step.body and "Referer" not in step.headers for step in login)
        challenge = [step for step in scenario.steps if step.path == "/system/auth/captcha/get"]
        complete = [step for step in scenario.steps if step.path.endswith("/slider/complete")]
        assert len(challenge) == len(complete) == len(login)
        assert all(
            step.wait_ms == 300 and step.equals["$.data.verified"] is True for step in complete
        )
        assert scenario.after_restart
    assert {step.method for step in devices.steps} >= {"GET", "POST", "PUT", "DELETE"}
    assert any(step.status == 403 for step in devices.steps)
    assert any(
        step.body
        and isinstance(step.body, dict)
        and step.body.get("active") is False
        and step.body.get("quantity") == 0
        for step in devices.steps
    )
    browser = signup.browser
    assert any(
        step.action == "click" and "login-auth-link-row" in step.selector for step in browser
    )
    assert any(step.action == "viewport" and step.width == 390 for step in browser)
    assert all("Bearer" not in step.value for step in browser)
    assert "CAPTCHA_ENABLE" not in json.dumps(plan.model_dump())


@pytest.mark.parametrize(
    "mutation",
    [
        lambda metadata: metadata.update(template="python-basic"),
        lambda metadata: metadata.update(contains_user_data=True),
        lambda metadata: metadata.update(spec_digest="0" * 64),
        lambda metadata: metadata.update(targets=[]),
        lambda metadata: metadata["targets"][0].update(api="/fake/device"),
        lambda metadata: metadata["targets"][0].update(table="arbitrary_users"),
        lambda metadata: metadata.update(tables={TABLE: ["id"]}),
    ],
)
def test_wrong_native_baseline_cannot_be_certified(product, mutation):
    path = product / "deployment/manifest.json"
    value = json.loads(path.read_text())
    mutation(value)
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        ci.fixed_plan(product)


def positive(plan):
    tables = plan.runtime.database_tables
    return {
        "passed": True,
        "cleanup": "deleted",
        "restart_kind": "application_process",
        "security_checks": dict.fromkeys(security_checks_for(ci.selection()), True),
        "restart_security_checks": dict.fromkeys(security_checks_for(ci.selection()), True),
        "browser_image": IMAGE,
        "native_build": {
            name: True
            for name in ("offline_install", "frontend_build", "frontend_typecheck", "source_frozen")
        },
        "native_frontend_started": True,
        "native_frontend_restart": True,
        "database": {
            "baseline": dict.fromkeys(tables, 0),
            "after": dict.fromkeys(tables, 1),
            "after_restart": dict.fromkeys(tables, 1),
        },
    }


@pytest.mark.parametrize(
    "mutation",
    [
        lambda proof: proof.update(restart_kind="container"),
        lambda proof: proof.update(restart_security_checks={}),
        lambda proof: proof["restart_security_checks"].update(raw_socket_denied=1),
        lambda proof: proof.update(browser_image="sha256:" + "8" * 64),
        lambda proof: proof["native_build"].update(frontend_build=1),
        lambda proof: proof["native_build"].update(frontend_typecheck=False),
        lambda proof: proof.update(native_frontend_started=False),
        lambda proof: proof.update(native_frontend_restart=1),
        lambda proof: proof["database"]["after"].update(sys_user=0),
        lambda proof: proof["database"]["after"].update({TABLE: 0}),
    ],
)
def test_native_specific_positive_evidence_cannot_be_omitted_or_truthy(
    product, monkeypatch, mutation
):
    plan = ci.fixed_plan(product)
    proof = positive(plan)
    monkeypatch.setattr(ci, "require_profile_evidence", lambda value, **bindings: None)
    ci.require_native_positive(proof, plan, "a" * 64, IMAGE)
    mutation(proof)
    with pytest.raises(ValueError):
        ci.require_native_positive(proof, plan, "a" * 64, IMAGE)


def test_generic_independent_evidence_validation_is_never_replaced(product, monkeypatch):
    plan = ci.fixed_plan(product)
    calls = []

    def check(value, **bindings):
        calls.append(bindings)
        raise ValueError("explicit missing independent evidence")

    monkeypatch.setattr(ci, "require_profile_evidence", check)
    with pytest.raises(ValueError, match="independent evidence"):
        ci.require_native_positive(positive(plan), plan, "a" * 64, IMAGE)
    assert calls == [
        {
            "aggregate": True,
            "source_digest": "a" * 64,
            "plan_digest": digest(plan.model_dump()),
            "scenarios": plan.scenarios,
            "selection": ci.selection(),
            "database_tables": ["sys_user", TABLE],
        }
    ]


@pytest.fixture
def setup_certification(tmp_path, product, monkeypatch):
    directory = tmp_path / "installation"
    directory.mkdir()
    settings = Settings(
        _env_file=None,
        sandbox_provider="daytona",
        daytona_allow_local_execution=True,
        daytona_api_key="local-fixture-key",
        daytona_snapshot="native-fixture-snapshot",
        capability_browser_image=IMAGE,
        capability_profile_directory=directory,
    )
    record = {
        "profile": "native-fastapiadmin-postgresql-v1",
        "selection": ci.selection(),
        "recipe_identity": "a" * 64,
        "runner": {"image_id": "sha256:" + "b" * 64},
        "snapshot": {
            "snapshot": "native-fixture-snapshot",
            "image_id": "sha256:" + "c" * 64,
            "digest": "registry:6000/rnd-native-fastapiadmin@sha256:" + "d" * 64,
        },
        "inputs": {"product": str(product), "source_identity": digest(manifest(product))},
    }
    proof = positive(ci.fixed_plan(product))
    events = []
    client = SimpleNamespace()
    monkeypatch.setattr(ci, "ROOT", tmp_path)
    monkeypatch.setattr(ci, "Settings", lambda **kwargs: settings)
    monkeypatch.setattr(ci, "install_loopback_guard", lambda: events.append("loopback"))
    monkeypatch.setattr(ci, "require_native_profile", lambda *args: copy.deepcopy(record))
    monkeypatch.setattr(ci, "require_browser_acceptance", lambda image: IMAGE)
    monkeypatch.setattr(ci, "client_for", lambda setting: client)
    monkeypatch.setattr(ci, "close_client", lambda value: events.append("close"))
    monkeypatch.setattr(
        ci, "require_profile_evidence", lambda value, **bindings: events.append("evidence")
    )
    monkeypatch.setattr(ci, "verifier_identity", lambda: "e" * 64)
    monkeypatch.setattr(
        ci, "security_probe_for_profile", lambda path, value: "native-security-probe"
    )
    monkeypatch.setattr(
        ci, "inspect_created_sandbox", lambda *args, **kwargs: events.append((args, kwargs))
    )

    def verify(*args, **kwargs):
        assert kwargs["client"] is client and kwargs["aggregate"] is True
        assert kwargs["security_probe"] == "native-security-probe"
        assert args[4] == ci.selection()
        kwargs["control_observer"]("owned-native-sandbox")
        events.append("verify")
        return copy.deepcopy(proof)

    monkeypatch.setattr(ci, "_verify", verify)
    # Preserve the actual strict receipt contract but stabilize its source digest.
    import workbench.capability_execution as execution

    monkeypatch.setattr(execution, "verifier_identity", lambda: "e" * 64)
    return directory, product, record, proof, events


def test_certificate_publishes_only_native_receipt_after_cleanup_and_revalidation(
    setup_certification,
):
    directory, product, record, _, events = setup_certification
    base = directory / "capability-security-acceptance.json"
    atomic_text(base, "base-receipt-unchanged")
    result = ci.certify(product, directory)
    assert result["passed"] is True and result["paid_model_calls"] == 0
    assert result["profile"] == ci.profile_binding(record)
    assert result["browser_image"] == IMAGE
    assert result["checks"].keys() == security_checks_for(ci.selection())
    saved = json.loads((directory / ci.receipt_name(ci.selection())).read_text())
    assert saved == result
    assert events[-1] == "close"
    observer = next(event for event in events if isinstance(event, tuple))
    assert observer[1] == {"require_resources": True, "selection": ci.selection()}
    assert base.read_text() == "base-receipt-unchanged"


@pytest.mark.parametrize(
    "failure",
    [
        "wrong-baseline",
        "wrong-browser",
        "missing-security",
        "restart",
        "close",
        "source-drift",
        "profile-drift",
    ],
)
def test_certification_failure_invalidates_old_receipt_and_never_publishes_success(
    setup_certification, monkeypatch, failure
):
    directory, product, record, proof, events = setup_certification
    receipt = directory / ci.receipt_name(ci.selection())
    atomic_text(receipt, '{"passed":true,"stale":true}')
    if failure == "wrong-baseline":
        record["inputs"]["source_identity"] = "f" * 64
    elif failure == "wrong-browser":
        proof["browser_image"] = "sha256:" + "f" * 64
    elif failure == "missing-security":
        proof["security_checks"].pop("native_egress_denied_same_ports")
    elif failure == "restart":
        proof["native_frontend_restart"] = False
    elif failure == "close":

        def close(value):
            events.append("close-failed")
            raise RuntimeError("explicit transport cleanup failure")

        monkeypatch.setattr(ci, "close_client", close)
    elif failure == "source-drift":

        def close(value):
            events.append("close")
            atomic_text(product / "changed.py", "changed during certification")

        monkeypatch.setattr(ci, "close_client", close)
    elif failure == "profile-drift":

        def close(value):
            events.append("close")
            record["recipe_identity"] = "f" * 64

        monkeypatch.setattr(ci, "close_client", close)
    with pytest.raises((ValueError, RuntimeError)):
        ci.certify(product, directory)
    assert json.loads(receipt.read_text())["passed"] is False
    assert (
        json.loads((ci.ROOT / "reports/native-capability-security.json").read_text())["passed"]
        is False
    )
    if failure == "wrong-baseline":
        assert "verify" not in events


def test_fixed_http_protocol_replays_captures_form_bodies_crud_and_restart(product, monkeypatch):
    from urllib.parse import parse_qs

    import httpx

    from workbench import capability_verification as verifier

    # This is an in-memory protocol fixture, never native runtime/PG evidence.
    plan = ci.fixed_plan(product)
    records, users, observed_forms = {}, {"super": True}, []
    counter = 0

    def transport(request):
        nonlocal counter
        path = request.url.path
        data = {}
        if request.content:
            if request.headers.get("content-type") == "application/x-www-form-urlencoded":
                form = parse_qs(request.content.decode())
                observed_forms.append(form)
                data = {key: value[0] for key, value in form.items()}
            else:
                data = json.loads(request.content)
        status = 200
        payload = None
        if path.endswith("/captcha/get"):
            payload = {"key": "captcha-key", "enable": True}
        elif path.endswith("/slider/complete"):
            assert data == {"captcha_key": "captcha-key"}
            payload = {"verified": True}
        elif path == "/system/user/register":
            users[data["username"]] = False
            payload = {"username": data["username"], "is_superuser": False}
        elif path == "/system/auth/login":
            assert data["captcha_key"] == "captcha-key" and data["login_type"] == "PC端"
            assert data["username"] in users
            payload = {
                "access_token": data["username"],
                "user_info": {"username": data["username"]},
            }
        elif path == "/system/user/current/info":
            payload = {"username": ci.SIGNUP_USER, "is_superuser": False}
        elif request.headers.get("authorization") != "Bearer super":
            status = 403
        elif path == "/rnd/device/create":
            counter += 1
            records[counter] = {"id": counter, **data}
            payload = records[counter]
        elif "/detail/" in path:
            payload = records[int(path.rsplit("/", 1)[1])]
        elif "/update/" in path:
            key = int(path.rsplit("/", 1)[1])
            records[key].update(data)
            payload = records[key]
        elif path == "/rnd/device/delete":
            assert all(type(key) is int for key in data)
            for key in data:
                del records[key]
        elif path == "/rnd/device/list":
            payload = {
                "items": [
                    row for row in records.values() if row["name"] == request.url.params.get("name")
                ]
            }
        else:
            raise AssertionError("unexpected authored endpoint: " + path)
        return httpx.Response(
            status,
            stream=httpx.ByteStream(
                json.dumps(
                    {"code": 0 if status == 200 else 403, "data": payload, "success": status == 200}
                ).encode()
            ),
        )

    monkeypatch.setattr(verifier.time, "sleep", lambda value: None)
    with httpx.Client(
        transport=httpx.MockTransport(transport), base_url="http://127.0.0.1"
    ) as client:
        initial, captured = verifier.run_scenarios(client, plan.scenarios)
        restarted, _ = verifier.run_scenarios(
            client, plan.scenarios, saved=captured, after_restart=True
        )
    assert len(observed_forms) == 3
    assert len(records) == 1 and next(iter(records.values()))["quantity"] == 7
    assert {row["phase"] for row in initial} == {"initial"}
    assert {row["phase"] for row in restarted} == {"restart"}
    assert {row["id"] for row in restarted} == {"native_signup", "native_device_crud"}
