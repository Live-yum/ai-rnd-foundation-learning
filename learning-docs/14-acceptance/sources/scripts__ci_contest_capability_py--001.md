# scripts/ci_contest_capability.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_contest_capability；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_security_probe`、`scripts.daytona_capability_profile`、`scripts.daytona_native_capability_profile`、`scripts.extension_oracles`、`workbench.capability_execution`、`workbench.capability_sandbox`、`workbench.filesystem`、`workbench.local_only`、`workbench.sandbox`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `install_authored_fixture`（L31–L39）：接收`product`。 控制顺序：L33按`destination.exists() or destination.is_symlink()`分支；L34抛异常，停止当前正常路径；L37按`not marker.exists()`分支。 调用`destination.exists`、`destination.is_symlink`、`ValueError`、`destination.parent.mkdir`、`marker.exists`、`marker.write_text`、`shutil.copytree`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_business_proof`（L42–L55）：接收`proof`。 控制顺序：L44按`proof.get("passed") is not True or proof.get("cleanup") != "deleted" or business.get(…`分支；L55抛异常，停止当前正常路径。 调用`proof.get`、`business.get`、`list`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L58–L124）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L122按`client is not None`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`install_loopback_guard`、`Settings`、`write_json`、`capability_execution_prerequisites`、`selection`、`require_native_profile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_contest_capability.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L128。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4896`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_contest_capability.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "dbc786083e1035904177554582dba928581ac7b7862929ccf3557efd77df6fba"} -->
````python
# scripts/ci_contest_capability.py
"""Authored native contest slice against trusted independent business assertions.

This is deliberately not model-generation evidence. The full original request
retains its unimplemented obligations regardless of this bounded slice result.
"""

import argparse
import shutil
import tempfile
from pathlib import Path

from scripts.capability_security_probe import security_probe_for_profile
from scripts.daytona_capability_profile import inspect_created_sandbox
from scripts.daytona_native_capability_profile import (
    ENVIRONMENT,
    HOME,
    require_native_profile,
    selection,
)
from scripts.extension_oracles import contest
from workbench.capability_execution import capability_execution_prerequisites
from workbench.capability_sandbox import _verify
from workbench.filesystem import write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings

FIXTURE = ROOT / "tests/fixtures/contest_native/module_contest"


def install_authored_fixture(product):
    destination = product / "backend/app/plugin/module_rnd/contest"
    if destination.exists() or destination.is_symlink():
        raise ValueError("Authored fixture must not overwrite another candidate module")
    destination.parent.mkdir(parents=True, exist_ok=True)
    marker = destination.parent / "__init__.py"
    if not marker.exists():
        marker.write_text("", encoding="utf-8")
    shutil.copytree(FIXTURE, destination)


def require_business_proof(proof):
    business = proof.get("business_oracle", {})
    if (
        proof.get("passed") is not True
        or proof.get("cleanup") != "deleted"
        or business.get("protocol") != contest.CONTRACT_VERSION
        or business.get("full_request_complete") is not False
        or business.get("remaining_obligations") != list(contest.REMAINING)
        or business.get("fresh_replay") is not True
        or business.get("same_cluster") is not True
        or business.get("distinct_database_oid") is not True
        or business.get("witnesses") != {name: True for name in contest.SEMANTICS}
    ):
        raise ValueError("Independent native contest assertions did not all pass")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=HOME)
    parser.add_argument("--product", type=Path, default=ROOT / ".native/tool-product")
    args = parser.parse_args()
    install_loopback_guard()
    settings = Settings(
        _env_file=args.directory / ENVIRONMENT,
        tool_timeout=900,
        capability_execution_enabled=True,
        capability_profile_directory=args.directory,
    )
    summary = {
        "passed": False,
        "model_transport": "authored-reference-fixture",
        "paid_model_calls": 0,
        "full_request_complete": False,
    }
    report = ROOT / "reports/contest-capability.json"
    write_json(report, summary)
    client = None
    try:
        directory, record = capability_execution_prerequisites(settings, selection())
        require_native_profile(directory)
        client = client_for(settings)
        with tempfile.TemporaryDirectory(prefix="rnd-authored-contest-") as temporary:
            product = Path(temporary) / "product"
            shutil.copytree(
                args.product,
                product,
                ignore=shutil.ignore_patterns(
                    ".venv", "node_modules", ".git", "__pycache__", ".env", ".env.*", "*.pyc"
                ),
            )
            install_authored_fixture(product)
            from scripts.ci_native_capability_security import fixed_plan

            plan = fixed_plan(product)
            plan.runtime.database_tables.extend(
                ["rnd_contest_team", "rnd_contest_membership", "rnd_contest_invitation"]
            )
            proof = _verify(
                product,
                plan,
                plan.scenarios,
                settings,
                selection(),
                ROOT / "reports/contest-capability-detail.json",
                client=client,
                aggregate=True,
                control_observer=lambda sandbox_id: inspect_created_sandbox(
                    directory, sandbox_id, require_resources=True, selection=selection()
                ),
                security_probe=security_probe_for_profile(directory, record),
                trusted_oracle=contest.CONTRACT_VERSION,
            )
            require_business_proof(proof)
            summary.update(
                passed=True,
                business_oracle=proof["business_oracle"],
                cleanup=proof["cleanup"],
                source_digest=proof["source_digest"],
            )
    finally:
        if client is not None:
            close_client(client)
        write_json(report, summary)


if __name__ == "__main__":
    main()
````
