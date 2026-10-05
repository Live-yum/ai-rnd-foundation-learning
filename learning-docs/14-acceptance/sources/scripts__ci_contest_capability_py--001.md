# scripts/ci_contest_capability.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_contest_capability；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_security_probe`、`scripts.ci_native_capability_source`、`scripts.daytona_capability_profile`、`scripts.daytona_native_capability_profile`、`scripts.extension_oracles`、`workbench.capability_execution`、`workbench.capability_sandbox`、`workbench.domain`、`workbench.filesystem`、`workbench.local_only`、`workbench.sandbox`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `install_authored_fixture`（L38–L53）：接收`product`。 控制顺序：L41按`destination.exists() or destination.is_symlink()`分支；L42抛异常，停止当前正常路径；L45按`not marker.exists()`分支。 调用`dict`、`require_exact_source`、`manifest`、`destination.exists`、`destination.is_symlink`、`ValueError`、`destination.parent.mkdir`、`marker.exists`、`marker.write_text`等。 返回路径：L53的`expected`。
- `require_business_proof`（L56–L69）：接收`proof`。 控制顺序：L58按`proof.get("passed") is not True or proof.get("cleanup") != "deleted" or business.get(…`分支；L69抛异常，停止当前正常路径。 调用`proof.get`、`business.get`、`list`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L72–L146）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L98按`record["inputs"]["product"] != handoff["product"] or record["inputs"]["source_identit…`分支；L104抛异常，停止当前正常路径；L134按`proof["source_digest"] != digest(inventory)`分支；L135抛异常，停止当前正常路径；L144按`client is not None`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`install_loopback_guard`、`Settings`、`write_json`、`capability_execution_prerequisites`、`selection`、`require_native_profile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_contest_capability.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L150。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6155`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_contest_capability.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6ad95db456f0f62f2f505ccaac2625f4cb5d62c9329d4cf481c605ecf0791dcf"} -->
````python
# scripts/ci_contest_capability.py
"""Authored native contest slice against trusted independent business assertions.

This is deliberately not model-generation evidence. The full original request
retains its unimplemented obligations regardless of this bounded slice result.
"""

import argparse
import tempfile
from pathlib import Path

from scripts.capability_security_probe import security_probe_for_profile
from scripts.ci_native_capability_source import (
    PRODUCT,
    RECEIPT,
    copy_exact_source,
    require_exact_source,
    require_handoff,
)
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
from workbench.domain import digest
from workbench.filesystem import manifest, sha, write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings

FIXTURE = ROOT / "tests/fixtures/contest_native/module_contest"


def install_authored_fixture(product):
    expected = dict(require_exact_source(product, manifest(product)))
    destination = product / "backend/app/plugin/module_rnd/contest"
    if destination.exists() or destination.is_symlink():
        raise ValueError("Authored fixture must not overwrite another candidate module")
    destination.parent.mkdir(parents=True, exist_ok=True)
    marker = destination.parent / "__init__.py"
    if not marker.exists():
        marker.write_text("", encoding="utf-8")
        expected[marker.relative_to(product).as_posix()] = sha(marker)
    fixture = manifest(FIXTURE)
    copy_exact_source(FIXTURE, destination, fixture)
    prefix = destination.relative_to(product).as_posix() + "/"
    expected.update({prefix + name: value for name, value in fixture.items()})
    require_exact_source(product, expected)
    return expected


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
    parser.add_argument("--product", type=Path, default=PRODUCT)
    parser.add_argument("--source-receipt", type=Path, default=RECEIPT)
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
        handoff = require_handoff(args.product, args.source_receipt)
        if (
            record["inputs"]["product"] != handoff["product"]
            or record["inputs"]["source_identity"] != handoff["source_identity"]
            or record["inputs"]["descriptors"] != handoff["descriptors"]
            or record["inputs"]["descriptor_roles"] != handoff["descriptor_roles"]
        ):
            raise ValueError("Authored contest must use the exact registered CI source baseline")
        client = client_for(settings)
        with tempfile.TemporaryDirectory(prefix="rnd-authored-contest-") as temporary:
            product = Path(temporary) / "product"
            copy_exact_source(args.product, product, handoff["inventory"])
            inventory = install_authored_fixture(product)
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
                profile_record=record,
                control_observer=lambda sandbox_id: inspect_created_sandbox(
                    directory, sandbox_id, require_resources=True, selection=selection()
                ),
                security_probe=security_probe_for_profile(directory, record),
                trusted_oracle=contest.CONTRACT_VERSION,
            )
            require_business_proof(proof)
            require_exact_source(product, inventory)
            if proof["source_digest"] != digest(inventory):
                raise ValueError("Authored contest proof does not bind the exact augmented source")
            require_handoff(args.product, args.source_receipt)
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
