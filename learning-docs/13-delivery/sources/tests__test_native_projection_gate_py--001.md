# tests/test_native_projection_gate.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `execution`（L14–L82）：接收`tmp_path`、`monkeypatch`。 调用`gate.approved_customer_replay`、`product.mkdir`、`(product / "start.py").write_text`、`digest`、`plan.model_dump`、`dict.fromkeys`、`write_json`、`monkeypatch.setattr`。 返回路径：L82的`plan, product, reports, report, calls`。
- `execution.style`（L60–L64）：接收`saved`、`receipt`、`files`。 控制顺序：L61断言`saved == report`；L62断言`receipt == {"template": "fastapiadmin", "spec_digest": digest(plan.model_dump())}`；L63断言`files == manifest(product)`。 调用`digest`、`plan.model_dump`、`manifest`、`calls.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `execution.business`（L66–L69）：接收`saved`、`receipt`、`spec_path`。 控制顺序：L67断言`saved == report`；L68断言`spec_path == reports / "approved-spec.json"`。 调用`calls.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `execution.projection`（L71–L77）：接收`saved`、`actual_plan`、`files`、`evidence_sha256`。 控制顺序：L72断言`saved == report`；L73断言`actual_plan == plan`；L74断言`files == manifest(product)`；L75断言`evidence_sha256 == sha(reports / "acceptance.json")`。 调用`manifest`、`sha`、`calls.append`。 返回路径：L77的`{"version": 2, "test_wiring_only": True}`。
- `invoke`（L85–L87）：接收`execution`。 调用`gate.verify_review_projection`。 返回路径：L87的`gate.verify_review_projection("fastapiadmin", plan, product, reports, report)`。
- `status`（L90–L91）：接收`execution`。 调用`json.loads`、`(execution[2] / "review-projection-status.json").read_text`。 返回路径：L91的`json.loads((execution[2] / "review-projection-status.json").read_text(encoding="utf-8"))`。
- `test_gate_calls_strict_production_checks_with_actual_saved_hash_and_sources`（L94–L101）：接收`execution`。 控制顺序：L96断言`execution[4] == ["style", "business", "projection"]`；L97断言`result == {"version": 2, "test_wiring_only": True}`；L98断言`status(execution)["passed"] is True`；L99断言`status(execution)["phase"] == "complete"`；L100断言`status(execution)["model_calls"] == 0`；L101断言`status(execution)["source_digest"] == digest(manifest(execution[1]))`。 调用`invoke`、`status`、`digest`、`manifest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gate_rejects_unbound_artifact_before_projector`（L105–L121）：接收`execution`、`monkeypatch`、`kind`。 控制顺序：L107按`kind == "missing"`分支；L109按`kind == "oversize"`分支；L111按`kind == "different"`分支；L119断言`execution[4] == []`；L120断言`status(execution)["passed"] is False`；L121断言`status(execution)["phase"] == "saved-execution-evidence"`。 调用`path.unlink`、`monkeypatch.setattr`、`write_json`、`pytest.raises`、`invoke`、`status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_retains_actual_report_and_safe_phase_without_stale_pass`（L127–L149）：接收`execution`、`monkeypatch`、`step`。 控制顺序：L140断言`path.read_bytes() == before`；L141断言`not (execution[2] / "review-projection.json").exists()`；L143断言`current["passed"] is False`；L144断言`current["phase"] == ( "production-review-projection" if step == "native_review_eviden…`；L149断言`"secret-test-canary" not in json.dumps(current)`。 调用`path.read_bytes`、`write_json`、`monkeypatch.setattr`、`pytest.raises`、`invoke`、`(execution[2] / "review-projection.json").exists`、`status`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_retains_actual_report_and_safe_phase_without_stale_pass.fail`（L134–L135）：接收`*args`。 控制顺序：L135抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gate_rejects_changes_during_projection`（L153–L165）：接收`execution`、`monkeypatch`、`kind`。 控制顺序：L164断言`status(execution)["passed"] is False`；L165断言`not (execution[2] / "review-projection.json").exists()`。 调用`monkeypatch.setattr`、`pytest.raises`、`invoke`、`status`、`(execution[2] / "review-projection.json").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gate_rejects_changes_during_projection.mutate`（L154–L159）：接收`*args`。 控制顺序：L155按`kind == "source"`分支。 调用`(execution[1] / "start.py").write_text`、`write_json`。 返回路径：L159的`{"version": 2}`。
- `test_main_never_stops_after_run_acceptance`（L168–L173）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L172断言`"report = run_acceptance(" in source`；L173断言`"verify_review_projection(args.template, plan, output, reports, report)" in source`。 调用`inspect.getsource`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shared_production_runtime_gates_cannot_be_bypassed`（L212–L226）：接收`execution`、`location`、`key`、`required`、`mutation`。 控制顺序：L217按`mutation == "missing"`分支；L224断言`execution[4] == []`；L225断言`status(execution)["phase"] == "native-runtime-deployment"`；L226断言`status(execution)["passed"] is False`。 调用`target.pop`、`int`、`write_json`、`pytest.raises`、`invoke`、`status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_parse_and_hash_are_bound_to_the_same_read_bytes`（L229–L251）：接收`execution`、`monkeypatch`。 控制顺序：L249断言`observed == [original_sha]`；L251断言`status(execution)["passed"] is False`。 调用`sha`、`monkeypatch.setattr`、`pytest.raises`、`invoke`、`status`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_parse_and_hash_are_bound_to_the_same_read_bytes.swap_after_read`（L235–L238）：接收`raw`。 调用`loads`、`write_json`。 返回路径：L238的`value`。
- `test_parse_and_hash_are_bound_to_the_same_read_bytes.projection`（L240–L243）：接收`saved`、`plan`、`files`、`evidence_sha256`。 控制顺序：L242断言`evidence_sha256 == original_sha`。 调用`observed.append`。 返回路径：L243的`{"version": 2}`。

</details>

**创建路径：** `tests/test_native_projection_gate.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L251。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9034`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_projection_gate.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "88d7ef06747e6d838276cd11e65f5985396060aabb0d96a9a2d98a1cf9dedb19"} -->
````python
# tests/test_native_projection_gate.py
"""Zero-model CI must pass production projection, not stop at a boolean acceptance."""

import json

import pytest

from scripts import ci_native_bundled as gate
from workbench.domain import digest
from workbench.filesystem import manifest, sha, write_json
from workbench.generator import PrerequisiteError


@pytest.fixture
def execution(tmp_path, monkeypatch):
    # This fixture tests gate wiring only. Real producer/projector validation is
    # covered separately and the Actions replay requires actual native execution.
    plan = gate.approved_customer_replay("fastapi-0e8", "fastapiadmin")
    reports, product = tmp_path / "reports", tmp_path / "product"
    product.mkdir()
    (product / "start.py").write_text("# generated product\n", encoding="utf-8")
    report = {
        "template": "fastapiadmin",
        "spec_digest": digest(plan.model_dump()),
        **dict.fromkeys(
            (
                "generated_runtime_verified",
                "native_codegen",
                "automatic_mount",
                "menu_and_permissions",
                "real_crud",
                "restart_persistence",
                "frontend_build",
                "frontend_typecheck",
                "real_browser",
                "source_unmodified",
            ),
            True,
        ),
        "portable_restored": {
            **dict.fromkeys(
                (
                    "passed",
                    "fresh_database",
                    "frontend_started",
                    "installed_from_lock",
                    "standalone_launcher",
                    "restart",
                ),
                True,
            ),
            **dict.fromkeys(
                ("source_database_reused", "original_platform_imported", "model_required"), False
            ),
        },
    }
    write_json(reports / "acceptance.json", report)
    write_json(reports / "approved-spec.json", plan.model_dump())
    calls = []

    def style(saved, receipt, files):
        assert saved == report
        assert receipt == {"template": "fastapiadmin", "spec_digest": digest(plan.model_dump())}
        assert files == manifest(product)
        calls.append("style")

    def business(saved, receipt, spec_path):
        assert saved == report
        assert spec_path == reports / "approved-spec.json"
        calls.append("business")

    def projection(saved, actual_plan, files, evidence_sha256):
        assert saved == report
        assert actual_plan == plan
        assert files == manifest(product)
        assert evidence_sha256 == sha(reports / "acceptance.json")
        calls.append("projection")
        return {"version": 2, "test_wiring_only": True}

    monkeypatch.setattr(gate, "require_native_style", style)
    monkeypatch.setattr(gate, "require_native_business", business)
    monkeypatch.setattr(gate, "native_review_evidence", projection)
    return plan, product, reports, report, calls


def invoke(execution):
    plan, product, reports, report, _ = execution
    return gate.verify_review_projection("fastapiadmin", plan, product, reports, report)


def status(execution):
    return json.loads((execution[2] / "review-projection-status.json").read_text(encoding="utf-8"))


def test_gate_calls_strict_production_checks_with_actual_saved_hash_and_sources(execution):
    result = invoke(execution)
    assert execution[4] == ["style", "business", "projection"]
    assert result == {"version": 2, "test_wiring_only": True}
    assert status(execution)["passed"] is True
    assert status(execution)["phase"] == "complete"
    assert status(execution)["model_calls"] == 0
    assert status(execution)["source_digest"] == digest(manifest(execution[1]))


@pytest.mark.parametrize("kind", ["missing", "oversize", "different", "foreign", "template"])
def test_gate_rejects_unbound_artifact_before_projector(execution, monkeypatch, kind):
    path = execution[2] / "acceptance.json"
    if kind == "missing":
        path.unlink()
    elif kind == "oversize":
        monkeypatch.setattr(gate, "MAX_ACCEPTANCE_BYTES", 1)
    elif kind == "different":
        write_json(path, {**execution[3], "forged": True})
    else:
        key, value = ("spec_digest", "0" * 64) if kind == "foreign" else ("template", "yudao-vben")
        execution[3][key] = value
        write_json(path, execution[3])
    with pytest.raises((ValueError, OSError)):
        invoke(execution)
    assert execution[4] == []
    assert status(execution)["passed"] is False
    assert status(execution)["phase"] == "saved-execution-evidence"


@pytest.mark.parametrize(
    "step", ["require_native_style", "require_native_business", "native_review_evidence"]
)
def test_failure_retains_actual_report_and_safe_phase_without_stale_pass(
    execution, monkeypatch, step
):
    path = execution[2] / "acceptance.json"
    before = path.read_bytes()
    write_json(execution[2] / "review-projection.json", {"stale": True})

    def fail(*args):
        raise ValueError("secret-test-canary")

    monkeypatch.setattr(gate, step, fail)
    with pytest.raises(ValueError):
        invoke(execution)
    assert path.read_bytes() == before
    assert not (execution[2] / "review-projection.json").exists()
    current = status(execution)
    assert current["passed"] is False
    assert current["phase"] == (
        "production-review-projection"
        if step == "native_review_evidence"
        else "native-style-and-business"
    )
    assert "secret-test-canary" not in json.dumps(current)


@pytest.mark.parametrize("kind", ["source", "acceptance"])
def test_gate_rejects_changes_during_projection(execution, monkeypatch, kind):
    def mutate(*args):
        if kind == "source":
            (execution[1] / "start.py").write_text("# tampered\n", encoding="utf-8")
        else:
            write_json(execution[2] / "acceptance.json", {"tampered": True})
        return {"version": 2}

    monkeypatch.setattr(gate, "native_review_evidence", mutate)
    with pytest.raises(ValueError, match="changed during projection"):
        invoke(execution)
    assert status(execution)["passed"] is False
    assert not (execution[2] / "review-projection.json").exists()


def test_main_never_stops_after_run_acceptance():
    import inspect

    source = inspect.getsource(gate.main)
    assert "report = run_acceptance(" in source
    assert "verify_review_projection(args.template, plan, output, reports, report)" in source


@pytest.mark.parametrize(
    "location,key,required",
    [
        *[
            ("original", key, True)
            for key in (
                "generated_runtime_verified",
                "native_codegen",
                "automatic_mount",
                "menu_and_permissions",
                "real_crud",
                "restart_persistence",
                "frontend_build",
                "frontend_typecheck",
                "real_browser",
                "source_unmodified",
            )
        ],
        *[
            ("restored", key, True)
            for key in (
                "passed",
                "fresh_database",
                "frontend_started",
                "installed_from_lock",
                "standalone_launcher",
                "restart",
            )
        ],
        *[
            ("restored", key, False)
            for key in ("source_database_reused", "original_platform_imported", "model_required")
        ],
    ],
)
@pytest.mark.parametrize("mutation", ["opposite", "missing", "number"])
def test_shared_production_runtime_gates_cannot_be_bypassed(
    execution, location, key, required, mutation
):
    report = execution[3]
    target = report if location == "original" else report["portable_restored"]
    if mutation == "missing":
        target.pop(key)
    else:
        target[key] = not required if mutation == "opposite" else int(required)
    write_json(execution[2] / "acceptance.json", report)
    with pytest.raises(PrerequisiteError):
        invoke(execution)
    assert execution[4] == []
    assert status(execution)["phase"] == "native-runtime-deployment"
    assert status(execution)["passed"] is False


def test_parse_and_hash_are_bound_to_the_same_read_bytes(execution, monkeypatch):
    path = execution[2] / "acceptance.json"
    original_sha = sha(path)
    loads = gate.json.loads
    observed = []

    def swap_after_read(raw):
        value = loads(raw)
        write_json(path, {"changed_between_read_and_hash": True})
        return value

    def projection(saved, plan, files, evidence_sha256):
        observed.append(evidence_sha256)
        assert evidence_sha256 == original_sha
        return {"version": 2}

    monkeypatch.setattr(gate.json, "loads", swap_after_read)
    monkeypatch.setattr(gate, "native_review_evidence", projection)
    with pytest.raises(ValueError, match="changed during projection"):
        invoke(execution)
    assert observed == [original_sha]
    monkeypatch.setattr(gate.json, "loads", loads)
    assert status(execution)["passed"] is False
````
