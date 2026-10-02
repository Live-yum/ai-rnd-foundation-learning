# tests/test_recorded_design_contracts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_capabilities`、`workbench.domain`、`workbench.requirement_coverage`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `recorded`（L21–L32）：接收`template`。 控制顺序：L25断言`hashlib.sha256(payload).hexdigest() == RECORDED[template]`；L27断言`data["approval_status"] == "unapproved"`；L28断言`data["execution_authorized"] is False`；L29断言`data["purpose"] == "offline_contract_validation_only"`。 调用`( ROOT / "tests/fixtures/customer_design_diagnostics" / (template…`、`hashlib.sha256(payload).hexdigest`、`hashlib.sha256`、`json.loads`、`Requirement.model_validate`、`Plan.model_validate`。 返回路径：L30的`Requirement.model_validate(data["requirement"]), Plan.model_validate( data["candidate_plan…`。
- `corrected_copy`（L35–L49）：接收`template`。 控制顺序：L38遍历`value["business"]["permissions"]`；L39按`policy["role"] in {"manager", "service"}`分支；L40按`policy["entity"] == "customers" and "read_metrics" not in policy["actions"]`分支；L42按`policy["entity"] in {"requests", "tasks"} and "read_history" not in policy["actions"]`分支；L47按`template == "yudao-vben" and policy["entity"] == "tasks"`分支。 调用`recorded`、`deepcopy`、`candidate.model_dump`、`policy["actions"].append`、`policy["actions"].remove`、`Plan.model_validate`。 返回路径：L49的`requirement, Plan.model_validate(value)`。
- `test_exact_recorded_candidates_remove_false_namespace_gaps_retain_real_omissions`（L53–L72）：接收`template`。 控制顺序：L55断言`coverage_gaps(requirement, plan) == []`；L58按`template == "fastapiadmin"`分支；L59断言`gaps == diagnostics == []`；L61断言`gaps`；L62断言`any(d["code"] == "business_scope_mismatch" for d in diagnostics)`；L63断言`any( d["source"]["path"] == "business.metrics.3.role_scope" for d in diagnostics if "…`；L68按`template == "yudao-vben"`分支；L70断言`{(d["expected"]["role"], d["expected"]["entity"]) for d in history} == { (r, e) for r…`。 调用`recorded`、`coverage_gaps`、`business_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_offline_copy_with_only_reported_obligations_repaired_passes`（L76–L83）：接收`template`。 控制顺序：L78断言`not coverage_gaps(requirement, plan)`；L79断言`not business_gaps(requirement, plan)`；L82按`template != "fastapiadmin"`分支；L83断言`business_gaps(original_requirement, original)`。 调用`corrected_copy`、`coverage_gaps`、`business_gaps`、`recorded`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recorded_semantic_contract_mutations_remain_blocked`（L91–L132）：接收`template`、`mutation`。 控制顺序：L93断言`not business_gaps(requirement, plan)`；L96按`mutation == "scope"`分支；L102按`mutation == "write"`分支；L108按`mutation == "new_role"`分支；L113按`mutation == "relation"`分支；L117按`mutation == "metric"`分支；L119按`mutation == "workflow"`分支；L132断言`business_gaps(requirement, mutated)`。 调用`corrected_copy`、`business_gaps`、`plan.model_dump`、`next`、`next( p for p in business["permissions"] if p["role"] == "employe…`、`business["roles"].append`、`business["permissions"].append`、`Plan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_second_recorded_contracts_preserve_all_typed_and_business_obligations`（L143–L173）：接收`template`。 控制顺序：L146断言`hashlib.sha256(raw).hexdigest() == CURRENT_HASHES[template]`；L148断言`data["approval_status"] == "unapproved" and data["execution_authorized"] is False`；L151断言`not coverage_gaps(requirement, candidate)`；L152断言`not business_gaps(requirement, candidate)`；L154遍历`("requests", "tasks")`；L158断言`coverage_gaps(requirement, changed)`；L159按`template == "fastapiadmin"`分支；L160遍历`("requests", "tasks")`。后续分支沿下方源码相同行号继续阅读。 调用`file.read_bytes`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`json.loads`、`Requirement.model_validate`、`Plan.model_validate`、`coverage_gaps`、`business_gaps`、`candidate.model_copy`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_recorded_design_contracts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L173。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7325`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_recorded_design_contracts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "127c618ca3255ec8d11a7f49e0cad6ebbfe667ebc60bcd6b83d873bb291d3b6b"} -->
````python
# tests/test_recorded_design_contracts.py
"""Pure contract replay of recorded *unapproved* model diagnostics; never generation."""

import hashlib
import json
from copy import deepcopy

import pytest

from workbench.business_capabilities import business_gaps
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.settings import ROOT

RECORDED = {
    "python-basic": "c168b09cfb9ad7a06c55f2e3fcd78ecba260dd78bc82793e2c8dff35b75ea9c8",
    "fastapiadmin": "09fead7bdd076d1f50dacab5574072c78ac15900aa6141f58e4d90e1d9a702c6",
    "yudao-vben": "387597908c075b12193585499482402359ba99afcc8c99cd173e17d93f806afe",
}


def recorded(template):
    payload = (
        ROOT / "tests/fixtures/customer_design_diagnostics" / (template + ".json")
    ).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == RECORDED[template]
    data = json.loads(payload)
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    assert data["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(data["requirement"]), Plan.model_validate(
        data["candidate_plan"]
    )


def corrected_copy(template):
    requirement, candidate = recorded(template)
    value = deepcopy(candidate.model_dump())
    for policy in value["business"]["permissions"]:
        if policy["role"] in {"manager", "service"}:
            if policy["entity"] == "customers" and "read_metrics" not in policy["actions"]:
                policy["actions"].append("read_metrics")
            if (
                policy["entity"] in {"requests", "tasks"}
                and "read_history" not in policy["actions"]
            ):
                policy["actions"].append("read_history")
            if template == "yudao-vben" and policy["entity"] == "tasks":
                policy["actions"].remove("read_metrics")
    return requirement, Plan.model_validate(value)


@pytest.mark.parametrize("template", RECORDED)
def test_exact_recorded_candidates_remove_false_namespace_gaps_retain_real_omissions(template):
    requirement, plan = recorded(template)
    assert coverage_gaps(requirement, plan) == []
    diagnostics = []
    gaps = business_gaps(requirement, plan, diagnostics=diagnostics)
    if template == "fastapiadmin":
        assert gaps == diagnostics == []
    else:
        assert gaps
        assert any(d["code"] == "business_scope_mismatch" for d in diagnostics)
        assert any(
            d["source"]["path"] == "business.metrics.3.role_scope"
            for d in diagnostics
            if "path" in d["source"]
        )
    if template == "yudao-vben":
        history = [d for d in diagnostics if d["code"] == "business_missing_history_grant"]
        assert {(d["expected"]["role"], d["expected"]["entity"]) for d in history} == {
            (r, e) for r in ("manager", "service") for e in ("requests", "tasks")
        }


@pytest.mark.parametrize("template", RECORDED)
def test_exact_offline_copy_with_only_reported_obligations_repaired_passes(template):
    requirement, plan = corrected_copy(template)
    assert not coverage_gaps(requirement, plan)
    assert not business_gaps(requirement, plan)
    # Re-read the original: a local validation mutation is not an approved design.
    original_requirement, original = recorded(template)
    if template != "fastapiadmin":
        assert business_gaps(original_requirement, original)


@pytest.mark.parametrize("template", RECORDED)
@pytest.mark.parametrize(
    "mutation",
    ["scope", "write", "new_role", "relation", "metric", "workflow", "resolution_notice"],
)
def test_recorded_semantic_contract_mutations_remain_blocked(template, mutation):
    requirement, plan = corrected_copy(template)
    assert not business_gaps(requirement, plan)
    value = plan.model_dump()
    business = value["business"]
    if mutation == "scope":
        next(
            p
            for p in business["permissions"]
            if p["role"] == "service" and p["entity"] == "requests"
        )["scope"] = "all"
    elif mutation == "write":
        next(
            p
            for p in business["permissions"]
            if p["role"] == "employee" and p["entity"] == "customers"
        )["actions"].append("update")
    elif mutation == "new_role":
        business["roles"].append({"name": "observer", "label": "Unexpected observer"})
        business["permissions"].append(
            {"role": "observer", "entity": "customers", "actions": ["read"], "scope": "all"}
        )
    elif mutation == "relation":
        next(r for r in business["relations"] if r["field"] == "customer_id")["target_entity"] = (
            "tasks"
        )
    elif mutation == "metric":
        next(m for m in business["metrics"] if m["kind"] == "group_count")["group_by"] = "name"
    elif mutation == "workflow":
        business["workflows"][0]["transitions"][1]["set_timestamp"] = None
    else:
        business["notifications"] = [
            n
            for n in business["notifications"]
            if not (
                n["recipient"] == "creator"
                and n["event"] == "transitioned"
                and n["transition"] == "resolve"
            )
        ]
    mutated = Plan.model_validate(value)
    assert business_gaps(requirement, mutated)


CURRENT_HASHES = {
    "python-basic": "0ad2c86625dd7454bab688edf402c59b4a3d28ba3e4f5eb07f8c3b9747dfd8a5",
    "fastapiadmin": "3b03ca2f5b8b488bf958f4e685c398428b17e640d697bdcf284ddabfddc13099",
    "yudao-vben": "561b5bcabca92dff7d845c31ca33f2c3c221004bd195384cbca471e8db0fa72c",
}


@pytest.mark.parametrize("template", CURRENT_HASHES)
def test_second_recorded_contracts_preserve_all_typed_and_business_obligations(template):
    file = ROOT / "tests/fixtures/customer_design_diagnostics/2a4106f" / (template + ".json")
    raw = file.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CURRENT_HASHES[template]
    data = json.loads(raw)
    assert data["approval_status"] == "unapproved" and data["execution_authorized"] is False
    requirement = Requirement.model_validate(data["requirement"])
    candidate = Plan.model_validate(data["candidate_plan"])
    assert not coverage_gaps(requirement, candidate)
    assert not business_gaps(requirement, candidate)
    # These are pure validator regressions, not approval or generated runtime proof.
    for entity_name in ("requests", "tasks"):
        changed = candidate.model_copy(deep=True)
        entity = next(e for e in changed.entities if e.name == entity_name)
        next(f for f in entity.fields if f.name == "detail").max_length = 200
        assert coverage_gaps(requirement, changed)
    if template == "fastapiadmin":
        for entity in ("requests", "tasks"):
            for transition in ("start", "resolve"):
                changed = candidate.model_copy(deep=True)
                changed.business.notifications = [
                    n
                    for n in changed.business.notifications
                    if not (
                        n.entity == entity
                        and n.event == "transitioned"
                        and n.transition == transition
                        and n.recipient == "assignee"
                    )
                ]
                assert business_gaps(requirement, changed)
````
