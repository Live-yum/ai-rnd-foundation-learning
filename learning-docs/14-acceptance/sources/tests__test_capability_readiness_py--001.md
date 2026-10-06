# tests/test_capability_readiness.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`workbench.capability_contracts`、`workbench.capability_readiness`、`workbench.domain`、`workbench.orchestration`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_matching_pinned_dependency_proof_closes_only_exact_supported_profile`（L12–L31）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L17断言`before["items"][0]["status"] == "awaiting-matching-isolation-profile"`；L26断言`after["items"][0]["status"] == "verified"`；L28断言`migration["status"] == "unverified"`；L29断言`migration["bootstrap_and_restart_observed"] is True`；L31断言`stale["items"][0]["status"] != "verified"`。 调用`proposed`、`ExtensionDesign`、`fixture_baseline`、`readiness_report`、`digest`、`plan.model_dump`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_external_fixture_or_model_claim_never_closes_external_prerequisite`（L34–L74）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L66断言`service["status"] == "awaiting-approved-independent-probe"`；L67断言`service["adapter_fixture_scenarios"] == ["fixture"]`；L68断言`service["evidence_digest"] is None`；L69断言`next( item for item in result["items"] if item.get("description") == "new unreviewed …`。 调用`proposed`、`ExternalPrerequisite`、`ExtensionDesign`、`fixture_baseline`、`digest`、`plan.model_dump`、`readiness_report`、`next`、`item.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_readiness.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L74。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2879`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_readiness.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f89a19913d47112ee4c56feaf66722876c21bd4038491dd86c562de43a35d3e1"} -->
````python
# tests/test_capability_readiness.py
"""Status accounting cannot turn fixture/manual claims into live service proof."""

from test_capability_obligations import proposed

from scripts.capability_fixture import fixture_baseline
from workbench.capability_contracts import ExternalPrerequisite
from workbench.capability_readiness import readiness_report
from workbench.domain import digest
from workbench.orchestration import ExtensionDesign


def test_matching_pinned_dependency_proof_closes_only_exact_supported_profile():
    plan, _, _ = proposed()
    design = ExtensionDesign(baseline=fixture_baseline(), implementation=plan)
    listing = {"app.py": "a" * 64}
    before = readiness_report(design, listing)
    assert before["items"][0]["status"] == "awaiting-matching-isolation-profile"
    proof = {
        "passed": True,
        "plan_digest": digest(plan.model_dump()),
        "source_digest": digest(listing),
        "dependency_profile": {"pinned": "image"},
        "consumer": {"cold_start": True, "restart": True},
    }
    after = readiness_report(design, listing, proof)
    assert after["items"][0]["status"] == "verified"
    migration = next(item for item in after["items"] if item["kind"] == "migration")
    assert migration["status"] == "unverified"
    assert migration["bootstrap_and_restart_observed"] is True
    stale = readiness_report(design, {"app.py": "b" * 64}, proof)
    assert stale["items"][0]["status"] != "verified"


def test_external_fixture_or_model_claim_never_closes_external_prerequisite():
    plan, scope, _ = proposed()
    plan.prerequisites = [
        ExternalPrerequisite(
            id="email",
            kind="service",
            description="real email service",
            requirements=[scope["sources"][0]["id"]],
            provider="manual",
        )
    ]
    design = ExtensionDesign(
        baseline=fixture_baseline(),
        implementation=plan,
        dependency_requests=["new unreviewed package"],
    )
    proof = {
        "passed": True,
        "plan_digest": digest(plan.model_dump()),
        "source_digest": digest({}),
        "checks": [
            {
                "id": "fixture",
                "external_service": "email",
                "passed": True,
                "evidence": "external_fixture",
            }
        ],
        "external_receipts": {"email": {"approved": True, "verified": True}},
    }
    result = readiness_report(design, {}, proof)
    service = next(item for item in result["items"] if item["id"] == "email")
    assert service["status"] == "awaiting-approved-independent-probe"
    assert service["adapter_fixture_scenarios"] == ["fixture"]
    assert service["evidence_digest"] is None
    assert (
        next(
            item for item in result["items"] if item.get("description") == "new unreviewed package"
        )["status"]
        == "awaiting-reviewed-locked-profile"
    )
````
