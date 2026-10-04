# scripts/ci_capability_security.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_capability_security；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_security_probe`、`scripts.ci_capability_profile`、`scripts.daytona_capability_profile`、`workbench.capability_execution`、`workbench.capability_sandbox`、`workbench.domain`、`workbench.filesystem`、`workbench.local_only`、`workbench.sandbox`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L30–L103）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L44按`settings.sandbox_provider != "daytona"`分支；L45抛异常，停止当前正常路径；L80按`proof.get("restart_security_checks") != proof.get("security_checks")`分支；L81抛异常，停止当前正常路径；L101按`client is not None`分支。 调用`install_loopback_guard`、`Settings`、`write_json`、`ValueError`、`require_profile`、`require_browser_acceptance`、`client_for`、`tempfile.TemporaryDirectory`、`Path`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_capability_security.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L107。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4403`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_capability_security.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6620dc993c1eedac14e17a2fb682b6dece4a88d88a9b22b8ae7bc0a3bc232e5a"} -->
````python
# scripts/ci_capability_security.py
"""Real local-service safety acceptance; never accepts candidate/source inputs.

The fixed positive app establishes liveness after independent adversarial
identity/resource checks. A successful result permits only this exact profile,
verifier revision and SQLite selection, never general native stack execution.
No receipt is published until cleanup is confirmed. Missing quotas fail closed.
"""

import tempfile
from pathlib import Path

from scripts.capability_security_probe import run_security_probe
from scripts.ci_capability_profile import fixed_application, require_profile_evidence
from scripts.daytona_capability_profile import HOME, inspect_created_sandbox, require_profile
from workbench.capability_execution import (
    PROTOCOL,
    RECEIPT,
    profile_binding,
    require_security_receipt,
    verifier_identity,
)
from workbench.capability_sandbox import _verify
from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client, validate_configuration
from workbench.settings import ROOT, Settings


def main():
    install_loopback_guard()
    settings = Settings(_env_file=HOME / "workbench.env", tool_timeout=300)
    destination = HOME / RECEIPT
    summary_path = ROOT / "reports/capability-security.json"
    summary = {
        "passed": False,
        "paid_model_calls": 0,
        "scope": "real-local-security-and-fixed-positive",
    }
    # Invalidate an older acceptance before testing; failure never leaves a
    # stale successful entry under the current installation's admission path.
    write_json(destination, summary)
    write_json(summary_path, summary)
    if settings.sandbox_provider != "daytona":
        raise ValueError("Security acceptance requires real local Daytona")
    record = require_profile(HOME, settings.daytona_snapshot)
    from workbench.capability_browser_isolation import require_browser_acceptance

    browser_image = require_browser_acceptance(settings.capability_browser_image)
    client = client_for(settings)
    try:
        with tempfile.TemporaryDirectory(prefix="rnd-security-positive-") as directory:
            product = Path(directory) / "product"
            plan = fixed_application(product)
            selected = plan.selection.model_dump()
            validate_configuration(settings, selected["template"], selected)
            proof = _verify(
                product,
                plan,
                plan.scenarios,
                settings,
                selected,
                ROOT / "reports/capability-security-detail.json",
                client=client,
                aggregate=True,
                control_observer=lambda sandbox_id: inspect_created_sandbox(
                    HOME, sandbox_id, require_resources=True
                ),
                security_probe=run_security_probe,
            )
            require_profile_evidence(
                proof,
                aggregate=True,
                source_digest=digest(manifest(product)),
                plan_digest=digest(plan.model_dump()),
                scenarios=plan.scenarios,
                selection=selected,
                database_tables=plan.runtime.database_tables,
            )
            if proof.get("restart_security_checks") != proof.get("security_checks"):
                raise ValueError("Restart did not preserve the complete security boundary")
            acceptance = {
                "protocol": PROTOCOL,
                "passed": True,
                "verifier_identity": verifier_identity(),
                "profile": profile_binding(record),
                "selection": selected,
                "checks": proof["security_checks"],
                "positive_product": True,
                "cleanup": proof["cleanup"],
                "paid_model_calls": 0,
                "restart_kind": proof.get("restart_kind"),
                "browser_image": browser_image,
            }
            require_security_receipt(acceptance, record, browser_image=browser_image)
        close_client(client)
        client = None
        write_json(destination, acceptance)
        summary.update(acceptance)
    finally:
        if client is not None:
            close_client(client)
        write_json(summary_path, summary)


if __name__ == "__main__":
    main()
````
