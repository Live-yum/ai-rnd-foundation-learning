# tests/test_permission_analysis_contract.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_capabilities`、`workbench.business_contracts`、`workbench.domain`、`workbench.errors`、`workbench.flow`、`workbench.llm`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `permission`（L36–L39）：接收`plan`、`role`。 调用`next`。 返回路径：L37的`next( row for row in plan.business.permissions if row.role == role and row.entity == "requ…`。
- `synthetic`（L42–L57）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Requirement`、`plan.business.model_dump`。 返回路径：L57的`requirement, plan`。
- `offline_gateway`（L60–L79）：接收`store`、`provider`、`result`、`seen`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L79的`ModelGateway(store.settings, store, httpx.MockTransport(handle))`。
- `offline_gateway.handle`（L65–L77）：接收`request`。 调用`seen.append`、`json.loads`、`httpx.Response`、`result.model_dump_json`。 返回路径：L67的`httpx.Response( 200, json={ "choices": [ { "finish_reason": "stop", "message": {"role": "a…`。
- `test_recorded_permission_failure_is_exact_read_only_evidence`（L83–L102）：接收`filename`。 控制顺序：L86断言`len(raw) == size`；L87断言`hashlib.sha256(raw).hexdigest() == digest`；L89断言`data["approval_status"] == "unapproved"`；L90断言`data["execution_authorized"] is False`；L91断言`data["purpose"] == "offline_contract_validation_only"`；L95断言`BusinessSpec.model_validate(requirement.facts["business"]) == plan.business`；L96断言`"manager/service 可创建服务请求" in requirement.acceptance[4]`；L97断言`"create" in permission(plan, "manager").actions`。后续分支沿下方源码相同行号继续阅读。 调用`(FIXTURES / filename).read_bytes`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`json.loads`、`(FIXTURES / "yudao-unapproved-design.json").read_bytes`、`Requirement.model_validate`、`Plan.model_validate`、`requirement.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_analysis_uses_existing_pydantic_schema_through_official_wrapper`（L106–L149）：接收`settings`、`store`、`monkeypatch`、`provider`。 控制顺序：L128断言`len(seen) == 1`；L130断言`request["response_format"] == {"type": "json_object"}`；L131断言`wrapped == [(Requirement, {"method": "json_mode", "include_raw": True})]`；L133断言`payload["business_contract_schema"] == BusinessSpec.model_json_schema()`；L137断言`"grant-only" in description and "absent actions stay denied" in description`；L138断言`"intersection" in description and "never their union" in description`；L140断言`"features/acceptance 的权限叙述必须从同一权限表展开" in instruction`；L141断言`"取共同动作而非权限并集" in instruction`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`synthetic`、`plan.model_dump`、`Workflow`、`offline_gateway`、`new_run`、`store.set_automation`、`workflow.analyse`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_analysis_uses_existing_pydantic_schema_through_official_wrapper.record`（L116–L118）：接收`schema`、`**kwargs`。 调用`wrapped.append`、`original`。 返回路径：L118的`original(self, schema, **kwargs)`。
- `test_invented_multi_role_claim_cannot_expand_typed_grants`（L152–L158）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L157断言`business_gaps(requirement, plan)`；L158断言`requirement.model_dump() == before`。 调用`synthetic`、`requirement.model_dump`、`permission(plan, "service").actions.append`、`permission`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_semantic_review_still_blocks_delivery_and_cannot_be_disabled`（L161–L199）：接收`settings`、`store`。 控制顺序：L184断言`payload["requirement"] == state["requirement"]`；L185断言`payload["plan"] == state["plan"]`；L186断言`payload["independent_evidence"] == state["verification"]`；L189断言`report["delivery_clearance"] is False`；L190断言`report["uncovered_requirements"] == [finding]`；L196断言`len(seen) == 1`；L197断言`state == before`；L198断言`not (root / "delivery.zip").exists()`。后续分支沿下方源码相同行号继续阅读。 调用`synthetic`、`ModelReview`、`Workflow`、`offline_gateway`、`new_run`、`requirement.model_dump`、`plan.model_dump`、`json.loads`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_permission_analysis_contract.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L199。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8410`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_permission_analysis_contract.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "991f31db64089cb1a86207872eec8d061b5757e0826afd6893d9fbf6e4078221"} -->
````python
# tests/test_permission_analysis_contract.py
"""Offline schema/prompt plumbing; prose alignment remains a model review gate.

Recorded unapproved designs are immutable pure-validator inputs, never executable
fixtures. The workflow tests below build a separate synthetic contract.
"""

import hashlib
import json

import httpx
import pytest
from conftest import new_run
from pydantic import SecretStr

from workbench.business_capabilities import business_gaps
from workbench.business_contracts import BusinessSpec
from workbench.domain import ModelReview, Plan, Requirement
from workbench.errors import UnsupportedScope
from workbench.flow import Workflow
from workbench.llm import ModelGateway
from workbench.settings import ROOT

FIXTURES = ROOT / "tests/fixtures/customer_design_diagnostics/d3ea684"
RECORDED = {
    "yudao-unapproved-design.json": (
        49388,
        "1a42c492a59cfd70c162cdb5c33999e77684cfa0342e1de59280988eb48100a1",
    ),
    "yudao-summary.json": (
        16693,
        "b4197e6d957341b5e8e770a37f0f3cd9b2b1bf67ba2483ac1565c5c2c9d9654b",
    ),
}


def permission(plan, role):
    return next(
        row for row in plan.business.permissions if row.role == role and row.entity == "requests"
    )


def synthetic():
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    requirement = Requirement(
        summary="Customer service permission analysis",
        users=["manager", "service", "employee"],
        data_scope="shared",
        features=["客户、服务请求与协作任务"],
        acceptance=[
            "manager 可创建服务请求；service 仅处理分配给自己的服务请求。",
            "manager/service 均可查询自己权限范围内的服务请求。",
        ],
        facts={"business": plan.business.model_dump(mode="json")},
    )
    return requirement, plan


def offline_gateway(store, provider, result, seen):
    store.settings.base_url = f"https://api.{provider}.com/v1"
    store.settings.model = "deepseek-flash" if provider == "deepseek" else "gpt-4o-mini"
    store.settings.api_key = SecretStr("offline-test-key")

    def handle(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": result.model_dump_json()},
                    }
                ]
            },
        )

    return ModelGateway(store.settings, store, httpx.MockTransport(handle))


@pytest.mark.parametrize("filename", RECORDED)
def test_recorded_permission_failure_is_exact_read_only_evidence(filename):
    size, digest = RECORDED[filename]
    raw = (FIXTURES / filename).read_bytes()
    assert len(raw) == size
    assert hashlib.sha256(raw).hexdigest() == digest
    data = json.loads((FIXTURES / "yudao-unapproved-design.json").read_bytes())
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    assert data["purpose"] == "offline_contract_validation_only"
    requirement = Requirement.model_validate(data["requirement"])
    plan = Plan.model_validate(data["candidate_plan"])
    before = requirement.model_dump(), plan.model_dump()
    assert BusinessSpec.model_validate(requirement.facts["business"]) == plan.business
    assert "manager/service 可创建服务请求" in requirement.acceptance[4]
    assert "create" in permission(plan, "manager").actions
    assert "create" not in permission(plan, "service").actions
    # Schema validity is not a deterministic proof of arbitrary prose coherence.
    assert business_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == before
    assert (FIXTURES / filename).read_bytes() == raw


@pytest.mark.parametrize("provider", ["deepseek", "openai"])
def test_analysis_uses_existing_pydantic_schema_through_official_wrapper(
    settings, store, monkeypatch, provider
):
    from langchain_deepseek import ChatDeepSeek
    from langchain_openai import ChatOpenAI

    cls = ChatDeepSeek if provider == "deepseek" else ChatOpenAI
    original = cls.with_structured_output
    wrapped = []

    def record(self, schema, **kwargs):
        wrapped.append((schema, kwargs))
        return original(self, schema, **kwargs)

    monkeypatch.setattr(cls, "with_structured_output", record)
    requirement, plan = synthetic()
    before = plan.model_dump()
    seen = []
    workflow = Workflow(settings, store, offline_gateway(store, provider, requirement, seen))
    run = new_run(store)
    store.set_automation(run, True, "synthetic-fixture-consent")
    result = workflow.analyse({"run_id": run, "template": "python-basic", "round": 1})
    assert len(seen) == 1
    request = seen[0]
    assert request["response_format"] == {"type": "json_object"}
    assert wrapped == [(Requirement, {"method": "json_mode", "include_raw": True})]
    payload = json.loads(request["messages"][1]["content"])
    assert payload["business_contract_schema"] == BusinessSpec.model_json_schema()
    description = payload["business_contract_schema"]["$defs"]["PermissionSpec"]["properties"][
        "actions"
    ]["description"]
    assert "grant-only" in description and "absent actions stay denied" in description
    assert "intersection" in description and "never their union" in description
    instruction = request["messages"][0]["content"]
    assert "features/acceptance 的权限叙述必须从同一权限表展开" in instruction
    assert "取共同动作而非权限并集" in instruction
    assert "不得为凑齐叙述而扩大权限" in instruction
    assert "用户明确要求但尚未覆盖的动作仍须保留原文并解决，不能静默删除" in instruction
    parsed = Requirement.model_validate(result["requirement"])
    assert parsed.facts == requirement.facts
    assert parsed.acceptance == requirement.acceptance
    assert plan.model_dump() == before
    assert "create" not in permission(plan, "service").actions
    assert store.model_records(run)[0]["structured_output"] == "langchain.with_structured_output"


def test_invented_multi_role_claim_cannot_expand_typed_grants():
    requirement, plan = synthetic()
    requirement.acceptance = ["manager/service 可创建服务请求"]
    before = requirement.model_dump()
    permission(plan, "service").actions.append("create")
    assert business_gaps(requirement, plan)
    assert requirement.model_dump() == before


def test_semantic_review_still_blocks_delivery_and_cannot_be_disabled(settings, store):
    requirement, plan = synthetic()
    requirement.acceptance = ["manager/service 可创建服务请求"]
    finding = "service 创建服务请求与 grant-only 权限及拒绝证据不一致"
    review = ModelReview(summary="权限叙述冲突", uncovered_requirements=[finding])
    seen = []
    settings.model_review = True
    workflow = Workflow(settings, store, offline_gateway(store, "deepseek", review, seen))
    state = {
        "run_id": new_run(store),
        "template": "python-basic",
        "attempt": 0,
        "requirement": requirement.model_dump(),
        "plan": plan.model_dump(),
        "verification": {
            "passed": True,
            "fixture_evidence": {"role": "service", "action": "create", "denied": True},
        },
    }
    before = json.loads(json.dumps(state))
    with pytest.raises(UnsupportedScope, match="grant-only"):
        workflow.model_review(state)
    payload = json.loads(seen[0]["messages"][1]["content"])
    assert payload["requirement"] == state["requirement"]
    assert payload["plan"] == state["plan"]
    assert payload["independent_evidence"] == state["verification"]
    root = workflow.product(state).parent
    report = json.loads((root / "model-review.json").read_text(encoding="utf-8"))
    assert report["delivery_clearance"] is False
    assert report["uncovered_requirements"] == [finding]
    settings.model_review = False
    with pytest.raises(UnsupportedScope, match="grant-only"):
        workflow.model_review(state)
    with pytest.raises(UnsupportedScope, match="grant-only"):
        workflow.package(state)
    assert len(seen) == 1
    assert state == before
    assert not (root / "delivery.zip").exists()
    assert not (root / "delivery.json").exists()
````
