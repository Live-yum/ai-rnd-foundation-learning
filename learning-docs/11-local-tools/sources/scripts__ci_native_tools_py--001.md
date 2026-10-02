# scripts/ci_native_tools.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生Plop/Aider修复与可恢复中断验收。** 真实生成后故意中断再恢复，权限验证后再中断再恢复；规则夹具先给错误候选，真实正反例拒绝并回滚，随后修复，最终完成浏览器/独立新库验收。

**对应关系：** native-toolchain-daytona矩阵 → 原生工具验收 → 已验证产品供快照准备。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_native_generated`、`scripts.native_coding_fixture`、`workbench.domain`、`workbench.filesystem`、`workbench.native`、`workbench.native_coding`、`workbench.native_lab`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L18–L146）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L68按`str(exc) != "explicit-test-interruption-after-native-generation"`分支；L69抛异常，停止当前正常路径；L71抛异常，停止当前正常路径；L73断言`checkpoint["resumable"] and checkpoint["targets"]`；L97按`str(exc) != "explicit-test-interruption-after-native-permissions"`分支；L98抛异常，停止当前正常路径；L100抛异常，停止当前正常路径；L116断言`final_permissions["attempt_id"] not in permission_attempts`。后续分支沿下方源码相同行号继续阅读。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`Settings`、`Path`、`prepare_sources`、`acceptance_spec`、`CustomRule`、`NativeCodingFixture`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.interrupted`（L53–L54）：接收`*args`。 控制顺序：L54抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main.interrupt_after_permissions`（L79–L82）：接收`*values`。 控制顺序：L82抛异常，停止当前正常路径。 调用`real_permissions`、`permission_attempts.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_native_tools.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L150。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5865`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_native_tools.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3ccd22a4b12522a9ae4f25cf5b11fe7596133785323f46f44095240ba3f0c1d3"} -->
````python
# scripts/ci_native_tools.py
"""Real native Plop + Aider repair + backend/frontend/browser/fresh DB acceptance."""

import argparse
import json
import os
from pathlib import Path

from scripts.ci_native_generated import acceptance_spec
from scripts.native_coding_fixture import NativeCodingFixture
from workbench.domain import CustomRule
from workbench.filesystem import write_json
from workbench.native import prepare_sources
from workbench.native_coding import native_rule_customizer
from workbench.native_lab import run_acceptance
from workbench.settings import ROOT, Settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    parser.add_argument("--output", type=Path, default=ROOT / ".native/tool-product")
    args = parser.parse_args()
    settings = Settings(
        data_dir=ROOT / ".data/native-tools",
        coding_engine="aider",
        tool_timeout=900,
        _env_file=None,
    )
    sources = {row["slot"]: Path(row["path"]) for row in prepare_sources(settings, args.template)}
    plan = acceptance_spec()
    plan.custom_rules = [
        CustomRule(
            description="quantity不能为负；新增和修改都校验，前端也要提示。",
            entity="device",
            accept_examples=[
                {"name": "device-rule", "quantity": 0, "active": False},
                {"name": "device-rule-second", "quantity": 7, "active": True},
            ],
            reject_examples=[{"name": "device-rule", "quantity": -1, "active": False}],
        )
    ]
    fixture = NativeCodingFixture(fail_first=True)
    reports = ROOT / "reports/native-tools"
    outcome = {
        "passed": False,
        "template": args.template,
        "model_transport": "explicit-fixture",
        "model_calls": 0,
    }
    try:
        actual_customization = native_rule_customizer(settings, fixture, "ci-native")

        def interrupted(*args):
            raise RuntimeError("explicit-test-interruption-after-native-generation")

        try:
            run_acceptance(
                args.template,
                sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
                args.output if args.template == "fastapiadmin" else args.output / "backend",
                sources.get("frontend"),
                os.environ["NATIVE_TEST_DATABASE_URL"],
                reports,
                plan,
                customization=interrupted,
            )
        except RuntimeError as exc:
            if str(exc) != "explicit-test-interruption-after-native-generation":
                raise
        else:
            raise AssertionError("Native interruption fixture did not run")
        checkpoint = json.loads((reports / "recovery.json").read_text(encoding="utf-8"))
        assert checkpoint["resumable"] and checkpoint["targets"]
        import workbench.native_lab as native_lab

        real_permissions = native_lab.generated_permissions
        permission_attempts = []

        def interrupt_after_permissions(*values):
            result = real_permissions(*values)
            permission_attempts.append(result["attempt_id"])
            raise RuntimeError("explicit-test-interruption-after-native-permissions")

        native_lab.generated_permissions = interrupt_after_permissions
        try:
            run_acceptance(
                args.template,
                sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
                args.output if args.template == "fastapiadmin" else args.output / "backend",
                sources.get("frontend"),
                os.environ["NATIVE_TEST_DATABASE_URL"],
                reports,
                plan,
                customization=actual_customization,
            )
        except RuntimeError as exc:
            if str(exc) != "explicit-test-interruption-after-native-permissions":
                raise
        else:
            raise AssertionError("Native permission interruption fixture did not run")
        finally:
            native_lab.generated_permissions = real_permissions
        report = run_acceptance(
            args.template,
            sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
            args.output if args.template == "fastapiadmin" else args.output / "backend",
            sources.get("frontend"),
            os.environ["NATIVE_TEST_DATABASE_URL"],
            reports,
            plan,
            customization=actual_customization,
        )
        final_permissions = json.loads(
            (reports / "generated/permissions.json").read_text(encoding="utf-8")
        )
        assert final_permissions["attempt_id"] not in permission_attempts
        edits = json.loads((reports / "native-coding.json").read_text())
        first = json.loads((reports / "coding-0.json").read_text())
        assert edits["passed"] and edits["repaired"] and edits["attempts"] == 2
        assert first["rolled_back"] and not first["verified"]
        assert report["portable_restored"]["business_rules"]["passed"]
        outcome.update(
            passed=True,
            actual_aider=True,
            actual_plop=True,
            actual_browser=True,
            automatic_repair=True,
            rollback_verified=True,
            same_run_resume=True,
            source_database_preserved=True,
            fresh_database=True,
            native_report=report,
        )
    finally:
        write_json(reports / "toolchain-acceptance.json", outcome)
    print(
        json.dumps(
            {
                "passed": True,
                "template": args.template,
                "actual_aider": True,
                "actual_plop": True,
                "repair": True,
            }
        )
    )


if __name__ == "__main__":
    main()
````
