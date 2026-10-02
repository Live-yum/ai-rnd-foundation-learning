# scripts/ci_native_bundled.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：从随附原生源码生成并独立新库恢复。** 从vendor清单取得固定源码，把真实Plan交给native_lab，启用完整原生运行和portable新库复验。没有前端或独立恢复证据不能通过。

**对应关系：** native-runtime工作流 → 本脚本 → reports/native中的运行与恢复证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_native_generated`、`workbench.domain`、`workbench.filesystem`、`workbench.native`、`workbench.native_delivery`、`workbench.native_evidence`、`workbench.native_lab`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `approved_customer_replay`（L36–L52）：接收`name`、`template`。 源码说明：Only the recorded approved synthetic Plan, never a diagnostic candidate.。 控制顺序：L42按`template != record["template"] or path.is_symlink()`分支；L43抛异常，停止当前正常路径；L44按`path.stat().st_size > MAX_REPLAY_PLAN_BYTES`分支；L45抛异常，停止当前正常路径；L47按`hashlib.sha256(raw).hexdigest() != record["sha256"]`分支；L48抛异常，停止当前正常路径；L50按`DiagnosticTextBudget().scrub(text) != text`分支；L51抛异常，停止当前正常路径。 调用`path.is_symlink`、`ValueError`、`path.stat`、`path.read_bytes`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`raw.decode`、`DiagnosticTextBudget().scrub`、`DiagnosticTextBudget`等。 返回路径：L52的`Plan.model_validate_json(text)`。
- `verify_review_projection`（L55–L104）：接收`template`、`plan`、`product`、`reports`、`report`。 源码说明：Exercise production review projection using only this execution's saved proof.。 控制顺序：L71按`path.is_symlink() or path.stat().st_size > MAX_ACCEPTANCE_BYTES`分支；L72抛异常，停止当前正常路径；L75按`len(raw) > MAX_ACCEPTANCE_BYTES`分支；L76抛异常，停止当前正常路径；L78按`saved != report or saved.get("template") != template or saved.get("spec_digest") != s…`分支；L83抛异常，停止当前正常路径；L95按`sha(path) != status["acceptance_sha256"] or manifest(product) != files`分支；L96抛异常，停止当前正常路径。 调用`digest`、`plan.model_dump`、`projection_path.unlink`、`write_json`、`path.is_symlink`、`path.stat`、`ValueError`、`path.open`、`handle.read`等。 返回路径：L100的`projection`。
- `main`（L107–L136）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.add_mutually_exclusive_group`、`inputs.add_argument`、`sorted`、`parser.parse_args`、`approved_customer_replay`、`Plan.model_validate_json`、`args.spec.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_native_bundled.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L140。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5912`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_native_bundled.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d2b05558be20c3181c511c06407e21f3d9c72c3d9091b4955f3e8776ac1e6af2"} -->
````python
# scripts/ci_native_bundled.py
"""Run original native acceptance AND standalone empty-database deployment from vendored code."""

import argparse
import hashlib
import json
import os
from pathlib import Path

from scripts.ci_native_generated import acceptance_spec
from workbench.domain import Plan, digest
from workbench.filesystem import manifest, sha, write_json
from workbench.native import prepare_sources
from workbench.native_delivery import (
    require_native_business,
    require_native_runtime,
    require_native_style,
)
from workbench.native_evidence import MAX_ACCEPTANCE_BYTES, native_review_evidence
from workbench.native_lab import run_acceptance
from workbench.settings import ROOT, Settings

APPROVED_CUSTOMER_REPLAYS = {
    "yudao-1d7": {
        "template": "yudao-vben",
        "path": "tests/fixtures/customer_approved_replays/yudao-1d7.json",
        "sha256": "16731f7c60a15916058d64c503525aafe93e1c53e0da62bae1eb8d0c227730f5",
    },
    "fastapi-0e8": {
        "template": "fastapiadmin",
        "path": "tests/fixtures/customer_approved_replays/fastapi-0e8.json",
        "sha256": "023ed6b43f20de90ef3b68033263212204314c2df0be08095fd6f9ec9e56dcb4",
    },
}


def approved_customer_replay(name, template):
    """Only the recorded approved synthetic Plan, never a diagnostic candidate."""
    from scripts.ci_real_model import MAX_REPLAY_PLAN_BYTES, DiagnosticTextBudget

    record = APPROVED_CUSTOMER_REPLAYS[name]
    path = ROOT / record["path"]
    if template != record["template"] or path.is_symlink():
        raise ValueError("Approved replay template/path mismatch")
    if path.stat().st_size > MAX_REPLAY_PLAN_BYTES:
        raise ValueError("Approved replay exceeds size limit")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError("Approved replay digest mismatch")
    text = raw.decode("utf-8")
    if DiagnosticTextBudget().scrub(text) != text:
        raise ValueError("Approved replay contains credential-like content")
    return Plan.model_validate_json(text)


def verify_review_projection(template, plan, product, reports, report):
    """Exercise production review projection using only this execution's saved proof."""
    status = {
        "version": 1,
        "template": template,
        "model_calls": 0,
        "spec_digest": digest(plan.model_dump()),
        "phase": "saved-execution-evidence",
        "passed": False,
    }
    status_path = reports / "review-projection-status.json"
    projection_path = reports / "review-projection.json"
    projection_path.unlink(missing_ok=True)
    write_json(status_path, status)
    try:
        path = reports / "acceptance.json"
        if path.is_symlink() or path.stat().st_size > MAX_ACCEPTANCE_BYTES:
            raise ValueError("Unsafe native acceptance artifact")
        with path.open("rb") as handle:
            raw = handle.read(MAX_ACCEPTANCE_BYTES + 1)
        if len(raw) > MAX_ACCEPTANCE_BYTES:
            raise ValueError("Native acceptance exceeds size limit")
        saved = json.loads(raw)
        if (
            saved != report
            or saved.get("template") != template
            or saved.get("spec_digest") != status["spec_digest"]
        ):
            raise ValueError("Native acceptance is not bound to this execution")
        status["acceptance_sha256"] = hashlib.sha256(raw).hexdigest()
        files = manifest(product)
        status["source_digest"] = digest(files)
        receipt = {"template": template, "spec_digest": status["spec_digest"]}
        status["phase"] = "native-runtime-deployment"
        require_native_runtime(saved)
        status["phase"] = "native-style-and-business"
        require_native_style(saved, receipt, files)
        require_native_business(saved, receipt, reports / "approved-spec.json")
        status["phase"] = "production-review-projection"
        projection = native_review_evidence(saved, plan, files, status["acceptance_sha256"])
        if sha(path) != status["acceptance_sha256"] or manifest(product) != files:
            raise ValueError("Native evidence or source changed during projection")
        write_json(projection_path, projection)
        status.update(phase="complete", passed=True)
        print("Native production review projection PASS (zero model calls)", flush=True)
        return projection
    finally:
        # Preserve a bounded allowlisted phase and hashes, never exception text,
        # environment variables, copied runtime folders or fabricated proof rows.
        write_json(status_path, status)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--spec", type=Path)
    inputs.add_argument("--approved-replay", choices=sorted(APPROVED_CUSTOMER_REPLAYS))
    args = parser.parse_args()
    plan = (
        approved_customer_replay(args.approved_replay, args.template)
        if args.approved_replay
        else Plan.model_validate_json(args.spec.read_text(encoding="utf-8"))
        if args.spec
        else acceptance_spec()
    )
    s = Settings(data_dir=ROOT / ".data/native-ci", _env_file=None)
    rows = prepare_sources(s, args.template)
    sources = {r["slot"]: Path(r["path"]) for r in rows}
    reports = ROOT / "reports/native"
    write_json(reports / "bundled-sources.json", rows)
    output = ROOT / ".native/product"
    report = run_acceptance(
        args.template,
        sources["fastapiadmin"] if args.template == "fastapiadmin" else sources["backend"],
        output if args.template == "fastapiadmin" else output / "backend",
        sources.get("frontend"),
        os.environ["NATIVE_TEST_DATABASE_URL"],
        reports,
        plan,
    )
    verify_review_projection(args.template, plan, output, reports, report)


if __name__ == "__main__":
    main()
````
