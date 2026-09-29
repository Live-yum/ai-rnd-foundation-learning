"""Exact reviewed repairs; this diagnostic helper is not part of the final PR."""
from pathlib import Path


def replace(name, old, new):
    path = Path(name)
    value = path.read_text(encoding='utf-8')
    if new in value:
        return
    if value.count(old) != 1:
        raise ValueError('Unexpected source shape: ' + name)
    path.write_text(value.replace(old, new), encoding='utf-8')


replace('workbench/knowledge.py', 'def design_pack(plan, destination, template="python-basic"):', 'def design_pack(plan, destination, template="python-basic", selection=None):')
replace('workbench/knowledge.py', "{'text': 'string', 'integer': 'int', 'boolean': 'boolean'}[field.kind]", "{'text': 'string', 'integer': 'int', 'boolean': 'boolean', 'date': 'date', 'enum': 'string'}[field.kind]")
replace('workbench/knowledge.py', '    atomic_text(destination / "architecture.mmd", topology)', '    if selection and selection.get("database") == "postgresql":\n        topology = topology.replace("Product SQLite", "Product PostgreSQL")\n    atomic_text(destination / "architecture.mmd", topology)')
replace('workbench/flow.py', 'pack = design_pack(plan, self.product(state).parent / "design", state["template"])', 'pack = design_pack(plan, self.product(state).parent / "design", state["template"], selection.model_dump())')
replace('templates/deployment/run.py', '        if args.check:\n            return\n    # Full frontend', '    # --check must reach frontend startup; do not report backend-only success.\n    # Full frontend')
replace('templates/deployment/run.py', '''        token = login(template, base)
        from workbench.portable_checks import check_restored_product

        outcome = check_restored_product(
            template, base, token, manifest["targets"], manifest["plan"]
        )
        write_json(reports / "portable-start.json", outcome)''', '''        if args.check or not ready:
            token = login(template, base)
            from workbench.portable_checks import check_restored_product

            outcome = check_restored_product(
                template, base, token, manifest["targets"], manifest["plan"]
            )
        else:
            # A regular restart must not require the seed admin's old password.
            outcome = {"database_initialized": True, "verification_rerun": False}
        write_json(reports / "portable-start.json", outcome)''')
replace('workbench/domain.py', '        if self.action == "approve" and self.approved is not True:', '''        if self.action in {"answer", "revise"}:
            from workbench.conversation import command_word

            if command_word(self.text) in {"批准", "approve", "拒绝", "reject", "智能推荐", "推荐", "smart", "recommend"}:
                raise ValueError("这是控制指令，不是需求回答；请使用对应按钮或 CLI 命令，不消耗澄清轮数")
        if self.action == "approve" and self.approved is not True:''')
replace('workbench/runtime.py', 'import logging\n', 'import logging\nimport traceback\nfrom pathlib import Path\n')
replace('workbench/runtime.py', 'error = f"{type(exc).__name__}：执行失败，请检查本地日志和验收报告"', '''frame = traceback.extract_tb(exc.__traceback__)[-1]
                error = f"{type(exc).__name__}：{Path(frame.filename).name}:{frame.lineno}（{frame.name}），请检查本次运行报告"''')
Path('tests/test_guided_completion.py').write_text('''"""Regression for real news fields and the entire delivered --check lifecycle."""
import ast
from contextlib import contextmanager
from types import SimpleNamespace
import json
import pytest
from pydantic import ValidationError
from workbench.domain import Plan, ResumeInput
from workbench.knowledge import design_pack
from workbench.settings import ROOT
from scripts.ci_guided_browser import news_spec


def test_news_design_covers_date_enum_and_selected_postgres(tmp_path):
    plan = Plan.model_validate(news_spec())
    result = design_pack(plan, tmp_path, selection={"database": "postgresql"})
    assert result["tasks"]
    assert "date published_on" in (tmp_path / "design-er.mmd").read_text()
    assert "string category" in (tmp_path / "design-er.mmd").read_text()
    assert "Product PostgreSQL" in (tmp_path / "architecture.mmd").read_text()


@pytest.mark.parametrize("value", ["批准", "“批准”", '\\"批准\\"', "拒绝", "智能推荐"])
def test_http_control_words_cannot_turn_into_questions(value):
    with pytest.raises(ValidationError, match="控制指令"):
        ResumeInput(gate_id="a"*64, action="answer", text=value)


def test_standalone_check_waits_for_frontend_after_backend_success(tmp_path, monkeypatch):
    # Execute the real delivered main with controlled boundaries. Native Actions
    # separately execute its actual SQL, backends and frontends on fresh databases.
    import argparse
    stages = []
    (tmp_path / "manifest.json").write_text(json.dumps({"template": "fastapiadmin", "targets": [], "plan": {}}))
    @contextmanager
    def backend(*args):
        stages.append("backend-start")
        yield "http://127.0.0.1:8001", "/openapi.json"
        stages.append("backend-stop")
    @contextmanager
    def frontend(*args):
        stages.append("frontend-start")
        yield "http://127.0.0.1:5173"
    writes=[]
    namespace={"argparse": argparse, "json": json, "os": SimpleNamespace(getenv=lambda name, default=None: default, environ={}),
        "HERE": tmp_path, "PRODUCT": tmp_path, "verify_manifest": lambda *a: None,
        "services": lambda: ("unused", 6379), "ownership": lambda *a: ("marker", False),
        "native_environment": lambda *a, **k: {}, "install_backend": lambda *a: stages.append("install"),
        "apply_delivery_sql": lambda *a: stages.append("sql"), "running_backend": backend,
        "login": lambda *a: "test-token", "write_json": lambda p,d: writes.append(dict(d)),
        "frontend_environment": lambda *a: {}, "build_frontend": lambda *a, **k: stages.append("frontend-build"),
        "frontend_preview": frontend, "ExitStack": __import__("contextlib").ExitStack}
    import workbench.portable_checks as probes
    monkeypatch.setattr(probes, "check_restored_product", lambda *a: {"passed": True})
    monkeypatch.setattr("sys.argv", ["run.py", "--check"])
    tree=ast.parse((ROOT/"templates/deployment/run.py").read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="main")
    exec(compile(ast.Module(body=[fn],type_ignores=[]),"delivered main","exec"),namespace)
    namespace["main"]()
    assert "frontend-build" in stages and "frontend-start" in stages
    assert writes[-1]["passed"] is True and writes[-1]["frontend_started"] is True
''',encoding='utf-8')
print('Reviewed guided workflow repairs applied')
