"""The delivered process must preserve exact first-process records after restart."""

from copy import deepcopy

import pytest

from workbench import business_probe
from workbench.portable_checks import require_preserved_business_records, snapshot_business_records
from workbench.settings import ROOT


def test_restart_snapshot_uses_real_declared_ids_and_closes_client(monkeypatch):
    closed = []
    rows = {
        "customers": [{"id": "1", "name": "Synthetic customer"}],
        "requests": [{"id": "2", "request_state": "resolved"}],
    }

    class Client:
        def __init__(self, *args):
            pass

        def rows(self, entity, **kwargs):
            return rows[entity]

        def close(self):
            closed.append(True)

    monkeypatch.setattr(business_probe, "BusinessClient", Client)
    args = (
        "fastapiadmin",
        "http://127.0.0.1",
        "synthetic-token",
        [{"entity": entity} for entity in rows],
        {"records": {"customers": "1", "requests": "2"}},
    )
    before = snapshot_business_records(*args)
    assert before["customers"]["id"] == "1" and len(before["customers"]["sha256"]) == 64
    after = snapshot_business_records(*args)
    require_preserved_business_records(before, after)
    rows["requests"][0]["request_state"] = "new"
    changed = snapshot_business_records(*args)
    with pytest.raises(ValueError, match="changed or lost"):
        require_preserved_business_records(before, changed)
    rows["requests"] = []
    with pytest.raises(ValueError, match="lost the original"):
        snapshot_business_records(*args)
    assert len(closed) == 4
    with pytest.raises(ValueError):
        require_preserved_business_records({}, {})
    wrong_identity = deepcopy(after)
    wrong_identity["customers"]["id"] = "8"
    with pytest.raises(ValueError):
        require_preserved_business_records(before, wrong_identity)


def test_delivered_launcher_captures_before_process_exit_and_checks_before_browser():
    source = (ROOT / "templates/deployment/run.py").read_text(encoding="utf-8")
    first = source.index("before_restart = snapshot_business_records(")
    second_process = source.index("base, _ = stack.enter_context(running_backend(")
    checked = source.index("require_preserved_business_records(before_restart, after_restart)")
    browser = source.index('outcome["browser"] = run_business_browser(')
    assert first < second_process < checked < browser
    assert 'outcome["restart"] = True' in source
    assert 'outcome["restart_preserved_records"] = True' in source
