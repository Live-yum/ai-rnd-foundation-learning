"""Preflight failure/cleanup contracts; unit fixtures are not browser evidence."""

import json
from urllib.request import urlopen

import pytest

from scripts import ci_capability_browser_preflight as preflight
from workbench.capability_verification import BrowserFailure


@pytest.fixture
def setup_report(tmp_path, monkeypatch):
    monkeypatch.setattr(preflight, "ROOT", tmp_path)
    monkeypatch.setattr(preflight, "sha", lambda path: "a" * 64)
    monkeypatch.setattr(preflight, "installed_chrome_version", lambda: "141.0.7390.37")
    monkeypatch.setattr(preflight, "readonly_host_facts", lambda: {"apparmor_enabled": "Y"})
    monkeypatch.setenv("PRODUCT_VERIFY_BROWSER_CHANNEL", "chrome")
    return tmp_path / "reports/capability-browser-preflight.json"


@pytest.mark.parametrize("selected_passes", [True, False])
def test_selected_probe_is_mandatory_even_if_bundled_browser_passes(
    setup_report, monkeypatch, selected_passes
):
    calls = []

    def probe(url):
        with urlopen(url, timeout=2) as response:
            assert response.status == 200
            assert b'id="check"' in response.read()
        channel = preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"]
        calls.append((channel, url))
        return {"passed": selected_passes if channel == "chrome" else True}

    monkeypatch.setattr(preflight, "probe", probe)
    if selected_passes:
        preflight.main()
    else:
        with pytest.raises(SystemExit, match="preflight FAILED"):
            preflight.main()
    result = json.loads(setup_report.read_text())
    assert result["passed"] is selected_passes
    assert result["product_acceptance"] is False
    assert result["channel"] == "chrome"
    assert [channel for channel, _ in calls] == ["", "chrome"]
    assert preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] == "chrome"
    with pytest.raises(OSError):
        urlopen(calls[-1][1], timeout=2)


def test_bundled_failure_cannot_hide_selected_success(setup_report, monkeypatch):
    def probe(url):
        if preflight.os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] == "":
            return {"passed": False, "browser_diagnostic": {"error_code": "sandbox-unavailable"}}
        return {"passed": True}

    monkeypatch.setattr(preflight, "probe", probe)
    preflight.main()
    result = json.loads(setup_report.read_text())
    assert result["passed"] is True
    assert result["bundled_probe"]["passed"] is False
    assert result["selected_probe"]["passed"] is True


def test_probe_preserves_safe_browser_failure_without_raw_infrastructure_errors(monkeypatch):
    diagnostic = {"phase": "launch", "error_code": "sandbox-unavailable"}

    def fail(*args):
        raise BrowserFailure(diagnostic)

    monkeypatch.setattr(preflight, "run_browser", fail)
    assert preflight.probe("http://127.0.0.1:1") == {
        "passed": False,
        "browser_diagnostic": diagnostic,
    }

    def infrastructure_failure(*args):
        raise OSError("private-path-and-credential-do-not-print")

    monkeypatch.setattr(preflight, "run_browser", infrastructure_failure)
    assert preflight.probe("http://127.0.0.1:1") == {
        "passed": False,
        "error_code": "preflight-infrastructure",
    }


@pytest.mark.parametrize("version", ["141.0.7390.37\n", "private-token", "141.0.7390.37\nsecret"])
def test_chrome_version_output_is_bounded_and_allowlisted(monkeypatch, version):
    from types import SimpleNamespace

    monkeypatch.setattr(
        preflight.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=version.encode()),
    )
    assert preflight.installed_chrome_version() == (
        "141.0.7390.37" if version == "141.0.7390.37\n" else None
    )


@pytest.mark.parametrize("valid_diagnostic", [True, False])
def test_profile_failure_label_does_not_bypass_or_replace_strict_validation(
    monkeypatch, valid_diagnostic
):
    from scripts import ci_capability_profile as profile
    from workbench.capability_verification import CheckFailure

    calls = []
    proof = {
        "passed": False,
        "browser_diagnostic": {
            "phase": "launch" if valid_diagnostic else "private-credential",
            "error_code": "sandbox-unavailable",
        },
    }

    def reject(receipt, **bindings):
        calls.append((receipt, bindings))
        raise CheckFailure("strict-contract-rejected")

    monkeypatch.setattr(profile, "require_evidence", reject)
    message = "launch/sandbox-unavailable" if valid_diagnostic else "strict-contract-rejected"
    with pytest.raises(CheckFailure, match=message) as failure:
        profile.require_profile_evidence(proof, aggregate=True, source_digest="current-source")
    assert "private-credential" not in str(failure.value)
    assert calls == [(proof, {"aggregate": True, "source_digest": "current-source"})]
    assert proof["passed"] is False
