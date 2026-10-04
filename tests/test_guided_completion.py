"""Regression for real news fields and the entire delivered --check lifecycle."""

import ast
import json
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from scripts.ci_guided_browser import news_spec
from workbench.domain import Plan, ResumeInput
from workbench.knowledge import design_pack
from workbench.settings import ROOT


def test_news_design_covers_date_enum_and_selected_postgres(tmp_path):
    plan = Plan.model_validate(news_spec())
    result = design_pack(plan, tmp_path, selection={"database": "postgresql"})
    assert result["tasks"]
    assert "date published_on" in (tmp_path / "design-er.mmd").read_text()
    assert "string category" in (tmp_path / "design-er.mmd").read_text()
    assert "Product PostgreSQL" in (tmp_path / "architecture.mmd").read_text()


@pytest.mark.parametrize("value", ["批准", "“批准”", '"批准"', "拒绝", "智能推荐"])
def test_http_control_words_cannot_turn_into_questions(value):
    with pytest.raises(ValidationError, match="控制指令"):
        ResumeInput(gate_id="a" * 64, action="answer", text=value)


def test_standalone_check_waits_for_frontend_after_backend_success(tmp_path, monkeypatch):
    # Execute the real delivered main with controlled boundaries. Native Actions
    # separately execute its actual SQL, backends and frontends on fresh databases.
    import argparse

    stages = []
    (tmp_path / "manifest.json").write_text(
        json.dumps({"template": "fastapiadmin", "targets": [], "plan": {}})
    )

    @contextmanager
    def backend(template, path, env, reports):
        stages.append("backend-start")
        yield f"http://127.0.0.1:{env['SERVER_PORT']}", "/openapi.json"
        stages.append("backend-stop")

    @contextmanager
    def frontend(*args):
        stages.append("frontend-start")
        yield "http://127.0.0.1:5173"

    writes = []
    from workbench.native_ports import backend_port_lease

    namespace = {
        "backend_port_lease": backend_port_lease,
        "argparse": argparse,
        "json": json,
        "os": SimpleNamespace(getenv=lambda name, default=None: default, environ={}),
        "HERE": tmp_path,
        "PRODUCT": tmp_path,
        "verify_manifest": lambda *a: None,
        "services": lambda: ("unused", 6379),
        "ownership": lambda *a: ("marker", False),
        "native_environment": lambda template, backend, url, port, **k: {"SERVER_PORT": port},
        "install_backend": lambda *a: stages.append("install"),
        "apply_delivery_sql": lambda *a: stages.append("sql"),
        "running_backend": backend,
        "login": lambda *a: "test-token",
        "write_json": lambda p, d: writes.append(dict(d)),
        "frontend_environment": lambda *a: {},
        "build_frontend": lambda *a, **k: stages.append("frontend-build"),
        "frontend_preview": frontend,
        "ExitStack": __import__("contextlib").ExitStack,
    }
    import workbench.portable_checks as probes

    monkeypatch.setattr(probes, "check_restored_product", lambda *a: {"passed": True})
    monkeypatch.setattr("sys.argv", ["run.py", "--check"])
    tree = ast.parse((ROOT / "templates/deployment/run.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "delivered main", "exec"), namespace)
    namespace["main"]()
    assert "frontend-build" in stages and "frontend-start" in stages
    assert writes[-1]["passed"] is True and writes[-1]["frontend_started"] is True
