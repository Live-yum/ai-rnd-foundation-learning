# workbench/capability_readiness.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `readiness_report`（L11–L84）：接收`design`、`source_inventory`、`proof`。 控制顺序：L34遍历`design.dependency_requests`；L57遍历`plan.prerequisites`。 调用`digest`、`plan.model_dump`、`proof.get`、`items.append`、`bool`、`consumer.get`、`check.get`、`prerequisite.model_dump`。 返回路径：L79的`{ "protocol": "capability-readiness-v1", **binding, "items": items, "resume": "Retry the s…`。

</details>

**创建路径：** `workbench/capability_readiness.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L84。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3381`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_readiness.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0c2d5bea7202012a325e7e6ba2ba7879ae8939fda41693411f9682b3701c2aa1"} -->
````python
# workbench/capability_readiness.py
"""Durable prerequisite accounting from existing trusted controller evidence.

This report is not an authorization, probe, installation or service credential.
It records what can be rechecked on the same retained candidate. Unsupported
external probes and old-schema upgrades cannot become green through approval.
"""

from workbench.domain import digest


def readiness_report(design, source_inventory, proof=None):
    proof = proof or {}
    plan = design.implementation
    binding = {
        "plan_digest": digest(plan.model_dump()),
        "source_digest": plan.source_digest,
        "source_inventory_digest": digest(source_inventory),
    }
    current = (
        proof.get("passed") is True
        and proof.get("source_digest") == binding["source_inventory_digest"]
        and proof.get("plan_digest") == binding["plan_digest"]
    )
    profile = proof.get("dependency_profile") if current else None
    items = [
        {
            "id": "locked-dependencies",
            "kind": "dependency",
            "status": "verified" if profile else "awaiting-matching-isolation-profile",
            "evidence_digest": digest(profile) if profile else None,
            "scope": "exact current readonly image and descriptors; no new dependency authorization",
        }
    ]
    for request in design.dependency_requests:
        items.append(
            {
                "id": "dependency-" + digest(request)[:24],
                "kind": "dependency",
                "description": request,
                "status": "awaiting-reviewed-locked-profile",
                "evidence_digest": None,
            }
        )
    consumer = proof.get("consumer", {}) if current else {}
    items.append(
        {
            "id": "existing-schema-migration",
            "kind": "migration",
            "status": "unverified",
            "evidence_digest": None,
            "bootstrap_and_restart_observed": bool(
                consumer.get("cold_start") is True and consumer.get("restart") is True
            ),
            "scope": "Cold bootstrap or unchanged-schema restart is not an old-version data migration.",
        }
    )
    for prerequisite in plan.prerequisites:
        fixtures = [
            check["id"]
            for check in proof.get("checks", [])
            if current
            and check.get("external_service") == prerequisite.id
            and check.get("evidence") == "external_fixture"
            and check.get("passed") is True
        ]
        items.append(
            {
                "id": prerequisite.id,
                "kind": prerequisite.kind,
                "description": prerequisite.description,
                "requirements": prerequisite.requirements,
                "contract_digest": digest(prerequisite.model_dump()),
                "status": "awaiting-approved-independent-probe",
                "adapter_fixture_scenarios": fixtures,
                "evidence_digest": None,
                "scope": "No supported live probe receipt exists; neither model claims nor manual acknowledgement verifies a service.",
            }
        )
    return {
        "protocol": "capability-readiness-v1",
        **binding,
        "items": items,
        "resume": "Retry the same run after the exact supported profile is verified; retain candidates and never silently regenerate or reduce scope.",
    }
````
