# scripts/ci_signup_scope_browser.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：历史FAILED报名运行的真实浏览器恢复协调。** 建立真实SQLite/LangGraph旧设计失败检查点，以显式进程内需求网关夹具启动实际API与Worker；检查同run恢复、原目标、旧审批和仅一次有效澄清模型调用，不启动原生生成或外部供应商。

**对应关系：** 第14站及教材cleanroom → signup_scope_browser.cjs → reports/signup-scope-browser/browser.json及截图。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`、`workbench.domain`、`workbench.filesystem`、`workbench.flow`、`workbench.llm`、`workbench.requirement_intent`、`workbench.runtime`、`workbench.settings`、`workbench.store`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `diagnostic_failed_run`（L37–L95）：接收`settings`。 源码说明：Real adapter/store, offline invalid provider envelope; never a paid request.。 控制顺序：L90抛异常，停止当前正常路径。 调用`Store`、`store.migrate`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`store.claim`、`store.gate`、`store.finish`等。 返回路径：L95的`run_id`。
- `diagnostic_failed_run.invalid_response`（L68–L84）：接收`request`。 调用`httpx.Response`。 返回路径：L69的`httpx.Response( 200, json={ "id": "fixture", "object": "chat.completion", "created": 0, "m…`。
- `ui_snapshot`（L98–L102）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`hashlib.sha256((ROOT / name).read_bytes()).hexdigest`、`hashlib.sha256`、`(ROOT / name).read_bytes`。 返回路径：L99的`{ name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ("workbench/web…`。
- `ScopeFixture`（L105–L122）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ScopeFixture.__init__`（L106–L107）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ScopeFixture.complete`（L109–L122）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L110断言`schema is Requirement`；L111断言`payload["original_request"] == ORIGINAL`；L112断言`len(payload["fresh_user_corrections"]) == 1`；L113断言`AUTHENTICATED_SCOPE in payload["fresh_user_corrections"][0]`；L114断言`ADMIN_SCOPE not in payload["fresh_user_corrections"][0]`。 调用`len`、`self.calls.append`、`Requirement`。 返回路径：L116的`Requirement( summary=ORIGINAL, users=["参赛者", "管理员"], data_scope="shared", features=[AUTHEN…`。
- `legacy_failed_run`（L125–L203）：接收`settings`。 源码说明：Write the real pre-upgrade checkpoint without importing optional drivers.。 控制顺序：L185断言`worker.tick()`；L187断言`snapshot.next == ("design",)`；L188断言`pending_interrupt(snapshot) is None`；L190断言`failed["status"] == "FAILED" and failed["pending"] is None`；L191断言`"ModuleNotFoundError" in failed["error"]`；L200断言`len(initial_approvals) == 1 and initial_approvals[0].actor == "delegated-ai"`。 调用`Store`、`store.migrate`、`Requirement`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`patch.object`、`Runtime`等。 返回路径：L201的`run`。
- `legacy_failed_run.LegacyFixture`（L137–L153）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `legacy_failed_run.LegacyFixture.complete`（L138–L153）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L139断言`schema is Plan and key == "plan:1"`。 调用`Plan.model_validate`。 返回路径：L140的`Plan.model_validate( { "title": "竞赛报名管理", "data_scope": "shared", "entities": [ { "name": …`。
- `legacy_failed_run.old_analyse`（L155–L156）：接收`state`。 调用`requirement.gate_dump`。 返回路径：L156的`{"requirement": requirement.gate_dump()}`。
- `legacy_failed_run.old_requirements`（L158–L165）：接收`state`。 调用`self.gate`。 返回路径：L159的`self.gate( state, "requirements", {"requirement": state["requirement"], "ready": True}, ["…`。
- `legacy_failed_run.old_import_failure`（L167–L168）：接收`state`。 控制顺序：L168抛异常，停止当前正常路径。 调用`ModuleNotFoundError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L206–L340）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L214遍历`( "browser.log", "scope-blocked.png", "scope-blocked-mobile.png",…`；L248在`not server.started`成立时循环；L249按`time.monotonic() >= deadline`分支；L250抛异常，停止当前正常路径；L284断言`result.returncode == 0`；L287断言`run_id == legacy_run_id`；L289断言`run["status"] == "WAITING_REQUIREMENTS"`；L290断言`run["pending"]["can_approve"] and not run["auto_mode"]`。后续分支沿下方源码相同行号继续阅读。 调用`ui_snapshot`、`socket.socket`、`sock.bind`、`sock.getsockname`、`reports.mkdir`、`(reports / name).unlink`、`write_json`、`ScopeFixture`、`tempfile.TemporaryDirectory`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_signup_scope_browser.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L344。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13623`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_signup_scope_browser.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f1d844c9d2c5710e78d99a371f9fe46726c64d8db8aae5f8b4b57453d5803a90"} -->
````python
# scripts/ci_signup_scope_browser.py
"""Real local HTTP/Chromium proof of the registration scope correction UI.

The requirements gateway is an explicit in-process test fixture. The worker,
Store, gates, HTTP API, SSE updates and compiled Vue application are real.
"""

import hashlib
import json
import os
import socket
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path
from unittest.mock import patch

import httpx
import uvicorn
from sqlalchemy import select

from workbench.api import create_app
from workbench.domain import Plan, Requirement
from workbench.filesystem import write_json
from workbench.flow import Workflow
from workbench.llm import ModelFailure, ModelGateway
from workbench.requirement_intent import ADMIN_SCOPE, AUTHENTICATED_SCOPE
from workbench.runtime import Runtime, pending_interrupt
from workbench.settings import ROOT, Settings
from workbench.store import Approval, Revision, Store
from workbench.tools import clean_env

ORIGINAL = "大学生计算机设计大赛报名网站"


def diagnostic_failed_run(settings):
    """Real adapter/store, offline invalid provider envelope; never a paid request."""
    store = Store(settings)
    store.migrate()
    project = store.create_project("模型反馈回归", str(uuid.uuid4()))
    run_id = store.create_run(
        project["id"], {"requirement": ORIGINAL, "template": "fastapiadmin"}, str(uuid.uuid4())
    )["run_id"]
    job = store.claim()
    gate = store.gate(
        run_id,
        "clarification",
        1,
        {
            "requirement": {
                "questions": ["参与者将通过哪种入口报名？"],
                "unsupported": ["模板不支持匿名公开报名页"],
            }
        },
        ["answer"],
        can_approve=False,
    )
    store.finish(job, "WAITING_CLARIFICATION", pending=gate)
    answer = "参赛者注册并登录后，在现有业务界面自行提交报名，仅管理本人报名记录"
    store.submit(
        run_id,
        {"gate_id": gate["gate_id"], "action": "answer", "text": answer},
        "diagnostic-answer",
    )
    job = store.claim()

    def invalid_response(request):
        return httpx.Response(
            200,
            json={
                "id": "fixture",
                "object": "chat.completion",
                "created": 0,
                "model": "fixture",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": '{"summary":123}'},
                    }
                ],
            },
        )

    try:
        ModelGateway(
            settings, store, httpx.MockTransport(invalid_response), streaming=True
        ).complete(run_id, "requirement:2", "JSON fixture", {}, Requirement)
        raise AssertionError("Invalid provider fixture must fail strict validation")
    except ModelFailure:
        store.finish(job, "FAILED", error="模型返回内容不符合结构化契约；两次尝试后停止")
    finally:
        store.engine.dispose()
    return run_id


def ui_snapshot():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in ("workbench/web/index.html", "workbench/web/app.js", "workbench/web/style.css")
    }


class ScopeFixture:
    def __init__(self):
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        assert schema is Requirement, "Browser correction must stop before native planning"
        assert payload["original_request"] == ORIGINAL
        assert len(payload["fresh_user_corrections"]) == 1
        assert AUTHENTICATED_SCOPE in payload["fresh_user_corrections"][0]
        assert ADMIN_SCOPE not in payload["fresh_user_corrections"][0]
        self.calls.append({"run_id": run_id, "key": key})
        return Requirement(
            summary=ORIGINAL,
            users=["参赛者", "管理员"],
            data_scope="shared",
            features=[AUTHENTICATED_SCOPE],
            acceptance=["参赛者仅可创建和维护本人报名，不能管理其他参赛者报名"],
        )


def legacy_failed_run(settings):
    """Write the real pre-upgrade checkpoint without importing optional drivers."""
    store = Store(settings)
    store.migrate()
    requirement = Requirement(
        summary="管理员维护竞赛报名记录",
        users=["管理员"],
        data_scope="shared",
        features=["管理员录入和维护报名记录"],
        acceptance=["管理员可维护报名记录"],
    )

    class LegacyFixture:
        def complete(self, run_id, key, instruction, payload, schema):
            assert schema is Plan and key == "plan:1"
            return Plan.model_validate(
                {
                    "title": "竞赛报名管理",
                    "data_scope": "shared",
                    "entities": [
                        {
                            "name": "registration",
                            "description": "报名记录",
                            "fields": [{"name": "title", "kind": "text", "max_length": 200}],
                        }
                    ],
                    "acceptance": ["管理员可维护报名记录"],
                }
            )

    def old_analyse(self, state):
        return {"requirement": requirement.gate_dump()}

    def old_requirements(self, state):
        return self.gate(
            state,
            "requirements",
            {"requirement": state["requirement"], "ready": True},
            ["approve", "revise", "reject"],
            True,
        )

    def old_import_failure(self, state):
        raise ModuleNotFoundError("No module named 'psycopg'", name="psycopg")

    try:
        project = store.create_project("旧版报名运行浏览器恢复验收", str(uuid.uuid4()))
        run = store.create_run(
            project["id"],
            {"requirement": ORIGINAL, "template": "fastapiadmin", "intelligent": True},
            str(uuid.uuid4()),
        )["run_id"]
        with (
            patch.object(Workflow, "analyse", old_analyse),
            patch.object(Workflow, "requirements", old_requirements),
            patch.object(Workflow, "source_context", lambda *_: {"code_context": {}}),
            patch.object(Workflow, "design", old_import_failure),
            patch.object(Workflow, "capability_recovery", lambda *a, **kw: None),
        ):
            with Runtime(settings, store, LegacyFixture()) as worker:
                assert worker.tick()
                snapshot = worker.graph.get_state({"configurable": {"thread_id": run}})
                assert snapshot.next == ("design",)
                assert pending_interrupt(snapshot) is None
        failed = store.get_run(run)
        assert failed["status"] == "FAILED" and failed["pending"] is None
        assert "ModuleNotFoundError" in failed["error"]
        with store.tx() as session:
            initial_approvals = list(
                session.scalars(
                    select(Approval)
                    .join(Revision, Revision.gate_id == Approval.gate_id)
                    .where(Revision.run_id == run)
                )
            )
        assert len(initial_approvals) == 1 and initial_approvals[0].actor == "delegated-ai"
        return run
    finally:
        store.engine.dispose()


def main():
    build_before = ui_snapshot()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    reports = ROOT / "reports/signup-scope-browser"
    reports.mkdir(parents=True, exist_ok=True)
    # A failed rerun must never leave a prior successful receipt/screenshot.
    for name in (
        "browser.log",
        "scope-blocked.png",
        "scope-blocked-mobile.png",
        "scope-options-mobile.png",
        "scope-corrected.png",
        "scope-failed.png",
    ):
        (reports / name).unlink(missing_ok=True)
    write_json(
        reports / "browser.json",
        {"passed": False, "status": "started", "fixture_mode": "in-process-requirement-gateway"},
    )
    fixture = ScopeFixture()
    with tempfile.TemporaryDirectory(prefix="signup-scope-browser-") as directory:
        directory = Path(directory)
        settings = Settings(
            data_dir=directory / "platform",
            base_url="http://127.0.0.1:1/v1",
            api_key="explicit-in-process-fixture-only",
            model="explicit-in-process-fixture",
            install_products=False,
            _env_file=None,
        )
        legacy_run_id = legacy_failed_run(settings)
        diagnostic_run_id = diagnostic_failed_run(settings)
        application = create_app(settings, gateway_factory=lambda _: fixture)
        server = uvicorn.Server(
            uvicorn.Config(application, host="127.0.0.1", port=port, log_level="error")
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Local browser fixture did not start")
                time.sleep(0.05)
            inputs = directory / "input.json"
            write_json(
                inputs,
                {
                    "platform": f"http://127.0.0.1:{port}",
                    "token": application.state.token,
                    "reports": str(reports),
                    "original": ORIGINAL,
                    "admin_scope": ADMIN_SCOPE,
                    "authenticated_scope": AUTHENTICATED_SCOPE,
                    "legacy_run_id": legacy_run_id,
                    "diagnostic_run_id": diagnostic_run_id,
                },
            )
            browser = os.getenv(
                "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
            )
            result = subprocess.run(
                ["node", str(ROOT / "scripts/signup_scope_browser.cjs"), str(inputs), browser],
                cwd=ROOT,
                env=clean_env(
                    {
                        "PLAYWRIGHT_BROWSERS_PATH": os.getenv("PLAYWRIGHT_BROWSERS_PATH", "0"),
                        "PRODUCT_VERIFY_CHROMIUM": os.getenv("PRODUCT_VERIFY_CHROMIUM", ""),
                    }
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=90,
            )
            (reports / "browser.log").write_text(result.stdout + result.stderr, encoding="utf-8")
            assert result.returncode == 0, result.stdout + result.stderr
            evidence = json.loads((reports / "browser.json").read_text(encoding="utf-8"))
            run_id = evidence["run_id"]
            assert run_id == legacy_run_id
            run = application.state.store.get_run(run_id)
            assert run["status"] == "WAITING_REQUIREMENTS"
            assert run["pending"]["can_approve"] and not run["auto_mode"]
            assert len(fixture.calls) == 1
            with application.state.store.tx() as session:
                approval_rows = list(
                    session.scalars(
                        select(Approval)
                        .join(Revision, Revision.gate_id == Approval.gate_id)
                        .where(Revision.run_id == run_id)
                    )
                )
            assert len(approval_rows) == 1 and approval_rows[0].actor == "delegated-ai"
            messages = application.state.store.messages(run_id)
            assert len(messages) == 2 and messages[0]["content"] == ORIGINAL
            assert AUTHENTICATED_SCOPE in messages[1]["content"]
            assert ADMIN_SCOPE not in messages[1]["content"]
            assert not (settings.data_dir / "runs" / run_id / "product").exists()
            assert ui_snapshot() == build_before, "UI assets changed during browser verification"
            screenshot_names = (
                "scope-blocked.png",
                "scope-blocked-mobile.png",
                "scope-options-mobile.png",
                "scope-corrected.png",
            )
            assert set(evidence["screenshots"]) == set(screenshot_names)
            evidence.update(
                passed=True,
                fixture_model_calls=fixture.calls,
                same_run_id=True,
                original_request_preserved=True,
                no_default_scope_selection=True,
                discarded_admin_selection_not_submitted=True,
                authenticated_entrant_goal_preserved=True,
                native_generation_attempted=False,
                legacy_failed_import_checkpoint=True,
                original_approval_count=1,
                recovered_approval_count=len(approval_rows),
                fixture_mode="in-process-requirement-gateway",
                external_provider_calls=False,
                ui_bundle_sha256=build_before,
                screenshot_sha256={
                    name: hashlib.sha256((reports / name).read_bytes()).hexdigest()
                    for name in screenshot_names
                },
            )
            write_json(reports / "browser.json", evidence)
            print(json.dumps(evidence, ensure_ascii=False, indent=2))
        finally:
            server.should_exit = True
            thread.join(timeout=15)
            if thread.is_alive():
                raise RuntimeError("Local browser fixture did not stop")


if __name__ == "__main__":
    main()
````
