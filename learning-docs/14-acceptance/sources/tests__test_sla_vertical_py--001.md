# tests/test_sla_vertical.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.sla_fixture`、`workbench.coding.candidates`、`workbench.coding.mini_swe`、`workbench.coding.ports`、`workbench.core.contracts`、`workbench.filesystem`、`workbench.generator`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fixture_product`（L20–L85）：接收`settings`、`tmp_path`。 控制顺序：L29遍历`enumerate(selected.implementation.tasks, 1)`；L83断言`manifest(base) == frozen`；L84断言`(product / "web/index.html").read_bytes() == (base / "web/index.html").read_bytes()`。 调用`design`、`generate_basic`、`selected.outline.selection.model_dump`、`manifest`、`settings.model_copy`、`enumerate`、`run_agent`、`Gateway`、`apply_candidate`等。 返回路径：L85的`product`。
- `fixture_product.Gateway`（L31–L54）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `fixture_product.Gateway.complete`（L34–L54）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L36按`self.calls == 2`分支。 调用`AgentTurn`、`authored_files`、`AgentTurn.model_validate`。 返回路径：L37的`AgentTurn(operation="submit")`；L39的`AgentTurn.model_validate( { "operation": "edit", "edits": { "explanation": "audited author…`。
- `fixture_product.Environment`（L56–L63）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `fixture_product.Environment.write`（L59–L60）：接收`edits`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `fixture_product.Environment.snapshot`（L62–L63）：接收`paths`。 返回路径：L63的`self.contents`。
- `fixture_product.environment`（L66–L67）：接收`*args`。 调用`Environment`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_authored_sla_worker_zip_api_restart`（L88–L170）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L94按`not worker_python().exists()`分支；L95断言`not os.environ.get("RND_REQUIRE_V2_TOOLS")`；L101断言`client.get("/").status_code == 200`；L105断言`registered.status_code == 201`；L108断言`client.post("/api/customers", headers=headers, json={"name": "客户A"}).status_code == 2…`；L112遍历`[ ("逾期紧急", "2000-01-01T00:00:00Z", "open", "urgent"), ("已解决", "20…`；L128断言`result.status_code == 201`；L129断言`client.get("/sla/summary", headers=headers).json() == { "overdue": 1, "urgent_overdue…`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`digest`、`manifest`、`worker_python().exists`、`worker_python`、`os.environ.get`、`pytest.skip`、`fixture_product`、`extract_consumer`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_sla_vertical.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L170。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7120`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_sla_vertical.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "44aafa2c4e56f12290fedfb80bb731d8a0d7aa080f59dc9521c14a01cc810ecd"} -->
````python
# tests/test_sla_vertical.py
"""Authored module fixture with real Worker/API/ZIP/restart; no live-model claim."""

import json
import os
import subprocess
from contextlib import contextmanager

import pytest
from test_capability_consumer import extract_consumer, free_port, running_consumer

from scripts.sla_fixture import authored_files, design
from workbench.coding.candidates import apply_candidate
from workbench.coding.mini_swe import run_agent, worker_python
from workbench.coding.ports import AgentTurn
from workbench.core.contracts import digest
from workbench.filesystem import manifest
from workbench.generator import generate_basic


def fixture_product(settings, tmp_path):
    selected = design()
    base = tmp_path / "baseline"
    generate_basic(selected.baseline, base, selected.outline.selection.model_dump())
    frozen = manifest(base)
    product = base
    settings = settings.model_copy(
        update={"mini_swe_enabled": True, "mini_swe_max_tokens": 2000000}
    )
    for index, task in enumerate(selected.implementation.tasks, 1):

        class Gateway:
            calls = 0

            def complete(self, run_id, key, instruction, payload, schema):
                self.calls += 1
                if self.calls == 2:
                    return AgentTurn(operation="submit")
                source = authored_files(task, payload["context"]["app.py"]["content"])
                return AgentTurn.model_validate(
                    {
                        "operation": "edit",
                        "edits": {
                            "explanation": "audited authored fixture",
                            "files": [
                                {
                                    "path": name,
                                    "before_sha256": payload["context"][name]["sha256"],
                                    "content": source[name],
                                }
                                for name in task.files
                            ],
                        },
                    }
                )

        class Environment:
            contents = {}

            def write(self, edits):
                self.contents = {edit.path: edit.content for edit in edits.files}

            def snapshot(self, paths):
                return self.contents

        @contextmanager
        def environment(*args):
            yield Environment()

        edits = run_agent(
            settings,
            Gateway(),
            "sla-fixture",
            task,
            selected.implementation,
            product,
            tmp_path / f"worker-{index}",
            {},
            environment_factory=environment,
        )
        candidate = tmp_path / f"candidate-{index}"
        apply_candidate(product, edits, task, selected.outline.selection.model_dump(), candidate)
        product = candidate
    assert manifest(base) == frozen
    assert (product / "web/index.html").read_bytes() == (base / "web/index.html").read_bytes()
    return product


def test_authored_sla_worker_zip_api_restart(settings, tmp_path, monkeypatch):
    # Authored local fixture only; real checkpoint isolation is not asserted here.
    monkeypatch.setattr(
        "workbench.coding.mini_swe.check_candidate",
        lambda s, t, p, c, d: {"passed": True, "source_digest": digest(manifest(c))},
    )
    if not worker_python().exists():
        assert not os.environ.get("RND_REQUIRE_V2_TOOLS"), "mandatory Worker missing"
        pytest.skip("locked optional mini-SWE worker not installed")
    product = fixture_product(settings, tmp_path)
    clean = extract_consumer(product, tmp_path)
    port = free_port()
    with running_consumer(clean, tmp_path, port, extra_args=("--port", str(port))) as client:
        assert client.get("/").status_code == 200
        registered = client.post(
            "/auth/register", json={"username": "owner", "password": "authored-fixture-password"}
        )
        assert registered.status_code == 201
        token = registered.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        assert (
            client.post("/api/customers", headers=headers, json={"name": "客户A"}).status_code
            == 201
        )
        for title, due, status, priority in [
            ("逾期紧急", "2000-01-01T00:00:00Z", "open", "urgent"),
            ("已解决", "2000-01-01T00:00:00Z", "resolved", "urgent"),
            ("未来", "2099-01-01T00:00:00Z", "open", "normal"),
        ]:
            result = client.post(
                "/api/tickets",
                headers=headers,
                json={
                    "title": title,
                    "customer": "客户A",
                    "due_at": due,
                    "status": status,
                    "priority": priority,
                },
            )
            assert result.status_code == 201, result.text
        assert client.get("/sla/summary", headers=headers).json() == {
            "overdue": 1,
            "urgent_overdue": 1,
        }
        assert client.get("/sla/summary").status_code == 401
        stranger = client.post(
            "/auth/register", json={"username": "outsider", "password": "authored-fixture-password"}
        ).json()["access_token"]
        assert client.get(
            "/sla/summary", headers={"Authorization": "Bearer " + stranger}
        ).json() == {"overdue": 0, "urgent_overdue": 0}
        assert client.get("/sla-dashboard").status_code == 200
        browser = os.environ.get("PRODUCT_VERIFY_PLAYWRIGHT")
        if browser:
            script = """const {chromium}=require(process.argv[1]);(async()=>{const b=await chromium.launch({headless:true,args:['--no-sandbox']});try{const p=await b.newPage();await p.goto(process.argv[2]+'/sla-dashboard');await p.fill('#username','owner');await p.fill('#password','authored-fixture-password');await p.click('#login');await p.waitForFunction(()=>document.querySelector('#result').textContent==='逾期 1；紧急逾期 1');}finally{await b.close();}})().catch(()=>process.exit(1));"""
            # Synthetic fixture token only, never a model/provider credential.
            run = subprocess.run(
                ["node", "-e", script, browser, f"http://127.0.0.1:{port}", token],
                capture_output=True,
                timeout=30,
            )
            assert run.returncode == 0, "authored browser fixture failed"
    with running_consumer(clean, tmp_path, port, extra_args=("--port", str(port))) as client:
        assert client.get("/sla/summary", headers=headers).json() == {
            "overdue": 1,
            "urgent_overdue": 1,
        }
    (tmp_path / "fixture-evidence.json").write_text(
        json.dumps(
            {
                "authored_fixture": True,
                "real_worker": True,
                "model": "mock",
                "daytona": "mock",
                "api": True,
                "restart": True,
                "zip_new_directory": True,
                "browser": bool(browser),
                "real_model_acceptance": False,
            }
        )
    )
````
