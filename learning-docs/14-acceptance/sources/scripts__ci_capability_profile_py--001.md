# scripts/ci_capability_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_capability_profile；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`scripts.daytona_capability_profile`、`workbench.capability_contracts`、`workbench.capability_sandbox`、`workbench.capability_verification`、`workbench.domain`、`workbench.filesystem`、`workbench.local_only`、`workbench.sandbox`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fixed_application`（L29–L79）：接收`product`、`atomic_consumer`。 控制顺序：L31遍历`("pyproject.toml", "uv.lock")`；L52按`atomic_consumer`分支。 调用`product.mkdir`、`shutil.copyfile`、`(product / "app.py").write_text`、`APP.replace( " # CUSTOM_ACCESS", " from access import readable\n …`、`APP.replace`、`(product / "access.py").write_text`、`scope_sources`、`make_plan`、`digest`等。 返回路径：L79的`plan`。
- `require_atomic_consumer_evidence`（L82–L89）：接收`product`、`plan`、`proof`。 控制顺序：L86按`not plan.obligations`分支；L87抛异常，停止当前正常路径。 调用`CheckFailure`、`require_obligation_evidence`、`require_consumer_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_profile_evidence`（L92–L110）：接收`proof`、`**bindings`。 源码说明：Keep strict validation; explain only an allowlisted browser failure.。 控制顺序：L99按`proof.get("passed") is False and isinstance(phase, str) and phase in BROWSER_PHASES a…`分支；L106抛异常，停止当前正常路径；L110抛异常，停止当前正常路径。 调用`require_evidence`、`proof.get`、`diagnostic.get`、`isinstance`、`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L113–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L124按`settings.sandbox_provider != "daytona"`分支；L125抛异常，停止当前正常路径；L163抛异常，停止当前正常路径。 调用`install_loopback_guard`、`Settings`、`write_json`、`ValueError`、`require_profile`、`tempfile.TemporaryDirectory`、`Path`、`fixed_application`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_capability_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L169。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6618`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_capability_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "da4256749d396004ad8db659cde89ae70b2d7463410217557e88bb0c9ebce850"} -->
````python
# scripts/ci_capability_profile.py
"""Positive isolation acceptance with only the repository's fixed authored app.

No model, arbitrary source directory, or task argument is accepted. Unsupported
kernel/profile prerequisites fail this command; exit 78 is never a passing proof.
Production source execution remains separately disabled pending review.
"""

import shutil
import tempfile
from pathlib import Path

from scripts.capability_fixture import APP, GOAL, SHARED_ROUTES, make_plan
from scripts.daytona_capability_profile import HOME, inspect_created_sandbox, require_profile
from workbench.capability_contracts import CapabilityPlan, scope_sources
from workbench.capability_sandbox import _verify
from workbench.capability_verification import (
    BROWSER_ERROR_CODES,
    BROWSER_PHASES,
    CheckFailure,
    require_evidence,
)
from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client, validate_configuration
from workbench.settings import ROOT, Settings


def fixed_application(product, *, atomic_consumer=False):
    product.mkdir(parents=True)
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / "templates/product" / name, product / name)
    (product / "app.py").write_text(
        APP.replace(
            "    # CUSTOM_ACCESS",
            "    from access import readable\n    allowed = readable(row['owner'],name,member)",
        ).replace("# CUSTOM_ROUTES", SHARED_ROUTES),
        encoding="utf-8",
    )
    (product / "access.py").write_text(
        "def readable(owner, actor, member):\n    return owner == actor or member\n",
        encoding="utf-8",
    )
    sources = scope_sources([GOAL])
    plan = make_plan(
        {
            "source_units": sources,
            "source_digest": digest([GOAL]),
            "selection": {"template": "python-basic"},
        }
    )
    if atomic_consumer:
        from workbench.capability_consumer import prepare_consumer

        plan = CapabilityPlan.model_validate(
            {
                **plan.model_dump(),
                "obligations": [
                    {
                        "id": "authored-retained-profile",
                        "source_id": sources[0]["id"],
                        "source_sha256": sources[0]["sha256"],
                        "assertion": "Authored fixture profile title is physically retained before restart replay",
                        "scenario_id": "private_records",
                        "physical": {
                            "table": "entries",
                            "key": {"id": "${entry}"},
                            "values": {"title": "持久化资料-${nonce}"},
                        },
                    }
                ],
            }
        )
        # This is an authored verifier fixture, never a model-produced product
        # or a declaration that all clauses of GOAL have been completed.
        shutil.copyfile(ROOT / "templates/product/start.py", product / "start.py")
        write_json(product / "selection.json", plan.selection.model_dump())
        prepare_consumer(product, plan)
    return plan


def require_atomic_consumer_evidence(product, plan, proof):
    from workbench.capability_consumer import require_consumer_evidence
    from workbench.capability_obligations import require_obligation_evidence

    if not plan.obligations:
        raise CheckFailure("Live authored acceptance must exercise pre-replay physical retention")
    require_obligation_evidence(plan, proof, aggregate=True)
    require_consumer_evidence(product, plan, proof)


def require_profile_evidence(proof, **bindings):
    """Keep strict validation; explain only an allowlisted browser failure."""
    try:
        require_evidence(proof, **bindings)
    except CheckFailure:
        diagnostic = proof.get("browser_diagnostic", {})
        phase, code = diagnostic.get("phase"), diagnostic.get("error_code")
        if (
            proof.get("passed") is False
            and isinstance(phase, str)
            and phase in BROWSER_PHASES
            and isinstance(code, str)
            and code in BROWSER_ERROR_CODES
        ):
            raise CheckFailure(
                f"Browser acceptance failed: {phase}/{code}; "
                "see capability-profile-detail.json; strict evidence rejected"
            ) from None
        raise


def main():
    install_loopback_guard()
    settings = Settings(_env_file=HOME / "workbench.env", tool_timeout=300)
    report_path = ROOT / "reports/capability-profile.json"
    summary = {
        "passed": False,
        "authored_fixture": True,
        "paid_model_calls": 0,
        "production_execution_enabled": False,
    }
    write_json(report_path, summary)
    if settings.sandbox_provider != "daytona":
        raise ValueError("Positive profile acceptance requires the real local Daytona service")
    record = require_profile(HOME, settings.daytona_snapshot)
    with tempfile.TemporaryDirectory(prefix="rnd-fixed-profile-") as directory:
        product = Path(directory) / "product"
        plan = fixed_application(product, atomic_consumer=True)
        selected = plan.selection.model_dump()
        validate_configuration(settings, selected["template"], selected)
        client = client_for(settings)
        try:
            proof = _verify(
                product,
                plan,
                plan.scenarios,
                settings,
                selected,
                ROOT / "reports/capability-profile-detail.json",
                client=client,
                aggregate=True,
                profile_record=record,
                control_observer=lambda sandbox_id: inspect_created_sandbox(HOME, sandbox_id),
            )
            summary["proof"] = settings.redact_data(proof)
            require_profile_evidence(
                proof,
                source_digest=digest(manifest(product)),
                plan_digest=digest(plan.model_dump()),
                scenarios=plan.scenarios,
                selection=selected,
                database_tables=plan.runtime.database_tables,
                aggregate=True,
            )
            require_atomic_consumer_evidence(product, plan, proof)
            summary["passed"] = True
        finally:
            try:
                close_client(client)
            except Exception:
                summary["passed"] = False
                raise
            finally:
                write_json(report_path, summary)


if __name__ == "__main__":
    main()
````
