# tests/test_guided_completion.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_guided_browser`、`workbench.domain`、`workbench.knowledge`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_news_design_covers_date_enum_and_selected_postgres`（L17–L23）：接收`tmp_path`。 控制顺序：L20断言`result["tasks"]`；L21断言`"date published_on" in (tmp_path / "design-er.mmd").read_text()`；L22断言`"string category" in (tmp_path / "design-er.mmd").read_text()`；L23断言`"Product PostgreSQL" in (tmp_path / "architecture.mmd").read_text()`。 调用`Plan.model_validate`、`news_spec`、`design_pack`、`(tmp_path / "design-er.mmd").read_text`、`(tmp_path / "architecture.mmd").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_control_words_cannot_turn_into_questions`（L27–L29）：接收`value`。 调用`pytest.raises`、`ResumeInput`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standalone_check_waits_for_frontend_after_backend_success`（L32–L86）：接收`tmp_path`、`monkeypatch`。 控制顺序：L85断言`"frontend-build" in stages and "frontend-start" in stages`；L86断言`writes[-1]["passed"] is True and writes[-1]["frontend_started"] is True`。 调用`(tmp_path / "manifest.json").write_text`、`json.dumps`、`SimpleNamespace`、`stages.append`、`writes.append`、`dict`、`__import__`、`monkeypatch.setattr`、`ast.parse`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standalone_check_waits_for_frontend_after_backend_success.backend`（L43–L46）：接收`template`、`path`、`env`、`reports`。 调用`stages.append`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_standalone_check_waits_for_frontend_after_backend_success.frontend`（L49–L51）：接收`*args`。 调用`stages.append`。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `tests/test_guided_completion.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L86。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3619`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_guided_completion.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5b63c2937e5a9185a3e90bb48c2587efbe7306b3372a01cf8df761de5ae385e2"} -->
````python
# tests/test_guided_completion.py
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
````
