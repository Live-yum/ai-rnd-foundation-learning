# scripts/ci_acceptance.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_acceptance；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_evidence`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `file_hashes`（L55–L63）：接收`folder`。 控制顺序：L57遍历`sorted(folder.rglob("*"))`；L58按`path.is_symlink()`分支；L59抛异常，停止当前正常路径；L60按`path.is_file() and path != folder / "stage.json"`分支。 调用`sorted`、`folder.rglob`、`path.is_symlink`、`ValueError`、`path.is_file`、`safe_name`、`path.relative_to(folder).as_posix`、`path.relative_to`、`hashlib.sha256(path.read_bytes()).hexdigest`等。 返回路径：L63的`result`。
- `stage_binding`（L66–L71）：接收`binding`、`name`。 调用`name.endswith`。 返回路径：L67的`{ **binding, "stage": name, "platform": "win32" if name.endswith("windows-latest") else "l…`。
- `receipt`（L74–L88）：接收`name`、`folder`。 控制顺序：L75按`name not in STAGES`分支；L76抛异常，停止当前正常路径；L78按`(folder / "stage.json").exists()`分支；L79抛异常，停止当前正常路径；L80遍历`STAGES[name]`；L81按`not (folder / relative).is_file() or not (folder / relative).stat().st_size`分支；L82抛异常，停止当前正常路径；L84按`binding["platform"] != sys.platform`分支。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`folder.mkdir`、`(folder / "stage.json").exists`、`(folder / relative).is_file`、`(folder / relative).stat`、`stage_binding`、`run_binding`、`write_json`、`file_hashes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_jobs`（L91–L100）：接收`needs`。 控制顺序：L92按`not isinstance(needs, dict) or set(needs) != REQUIRED_JOBS`分支；L93抛异常，停止当前正常路径；L99按`failed`分支；L100抛异常，停止当前正常路径。 调用`isinstance`、`set`、`ValueError`、`needs.items`、`value.get`、`", ".join`、`sorted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `aggregate`（L103–L202）：接收`folder`、`needs`、`binding`、`count`。 控制顺序：L107按`type(count) is not int or not 1 <= count <= 64`分支；L108抛异常，停止当前正常路径；L121按`not folder.is_dir() or {path.name for path in folder.iterdir()} != expected`分支；L122抛异常，停止当前正常路径；L123遍历`STAGES`；L126按`digest(stage) != digest( {"version": 1, "binding": stage_binding(binding, name), "fil…`分支；L129抛异常，停止当前正常路径；L130按`any( not (path / item).is_file() or not (path / item).stat().st_size for item in STAG…`分支。后续分支沿下方源码相同行号继续阅读。 调用`require_jobs`、`type`、`ValueError`、`expected.update`、`range`、`folder.is_dir`、`folder.iterdir`、`read_json`、`digest`等。 返回路径：L197的`{ "passed": True, "binding": binding, "groups": summaries, "required_jobs": sorted(REQUIRE…`。
- `main`（L205–L221）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L214按`args.command == "receipt"`分支。 调用`argparse.ArgumentParser`、`parser.add_subparsers`、`commands.add_parser`、`stage.add_argument`、`sorted`、`Path`、`gate.add_argument`、`parser.parse_args`、`receipt`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_acceptance.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L225。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8595`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_acceptance.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "53557fade9cb1a7d9e6a9ea2710da44fe828892c6e9b8ce3ba6a3238988c072a"} -->
````python
# scripts/ci_acceptance.py
"""Always-run acceptance gate: failed dependencies or incomplete evidence are never green."""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path

from scripts.ci_evidence import (
    digest,
    read_json,
    restore_source_artifact,
    run_binding,
    safe_name,
    write_json,
)

REQUIRED_JOBS = {
    "frontend",
    "source-validation",
    "tests",
    "postgres",
    "clean-install",
    "native-sources",
    "handbook-only",
    "restored-tests",
    "restored-browser",
    "restored-install",
    "browser",
}
STAGES = {
    "frontend": [],
    "source-validation-ubuntu-latest": ["protocol.xml"],
    "source-validation-windows-latest": ["protocol.xml"],
    "postgres": ["postgres.xml"],
    "clean-install-ubuntu-latest": ["clean-install.json"],
    "clean-install-windows-latest": ["clean-install.json"],
    "native-sources": ["native-sources.json"],
    "handbook-only": [
        "learning-docs-clean-room.json",
        "restored-source/manifest.json",
        "restored-source/source.zip",
    ],
    "restored-browser": [
        "restored/restored.json",
        "restored/guided-browser/summary.json",
        "restored/signup-scope-browser/browser.json",
    ],
    "restored-install": ["restored/restored.json", "restored/clean-install.json"],
    "browser": ["guided-browser/summary.json", "signup-scope-browser/browser.json"],
}


def file_hashes(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlink evidence")
        if path.is_file() and path != folder / "stage.json":
            name = safe_name(path.relative_to(folder).as_posix())
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def stage_binding(binding, name):
    return {
        **binding,
        "stage": name,
        "platform": "win32" if name.endswith("windows-latest") else "linux",
    }


def receipt(name, folder):
    if name not in STAGES:
        raise ValueError("Unknown CI stage")
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / "stage.json").exists():
        raise ValueError("Refuse stale stage receipt")
    for relative in STAGES[name]:
        if not (folder / relative).is_file() or not (folder / relative).stat().st_size:
            raise ValueError("Missing required stage evidence: " + relative)
    binding = stage_binding(run_binding(), name)
    if binding["platform"] != sys.platform:
        raise ValueError("Wrong stage platform")
    write_json(
        folder / "stage.json", {"version": 1, "binding": binding, "files": file_hashes(folder)}
    )


def require_jobs(needs):
    if not isinstance(needs, dict) or set(needs) != REQUIRED_JOBS:
        raise ValueError("Missing or unexpected required jobs")
    failed = [
        name
        for name, value in needs.items()
        if not isinstance(value, dict) or value.get("result") != "success"
    ]
    if failed:
        raise ValueError("Required jobs failed, cancelled or skipped: " + ", ".join(sorted(failed)))


def aggregate(folder, needs, binding, *, count=4):
    from scripts.ci_pytest import validate_shard

    require_jobs(needs)
    if type(count) is not int or not 1 <= count <= 64:
        raise ValueError("Invalid aggregate shard count")
    prefix = "acceptance-" + binding["attempt"] + "-"
    expected = {prefix + name for name in STAGES}
    groups = [
        ("source", "linux", "ubuntu-latest"),
        ("source", "win32", "windows-latest"),
        ("restored", "linux", "ubuntu-latest"),
    ]
    expected.update(
        prefix + f"{origin}-{os_name}-{index}"
        for origin, _, os_name in groups
        for index in range(count)
    )
    if not folder.is_dir() or {path.name for path in folder.iterdir()} != expected:
        raise ValueError("Missing, duplicate or unexpected acceptance artifacts")
    for name in STAGES:
        path = folder / (prefix + name)
        stage = read_json(path / "stage.json")
        if digest(stage) != digest(
            {"version": 1, "binding": stage_binding(binding, name), "files": file_hashes(path)}
        ):
            raise ValueError("Stale or changed stage evidence: " + name)
        if any(
            not (path / item).is_file() or not (path / item).stat().st_size for item in STAGES[name]
        ):
            raise ValueError("Missing required stage evidence: " + name)
    prepared = folder / (prefix + "handbook-only")
    with tempfile.TemporaryDirectory(prefix="verify-restored-source-") as temporary:
        manifest = restore_source_artifact(
            prepared / "restored-source", Path(temporary) / "verified", binding
        )
    preparation = read_json(prepared / "learning-docs-clean-room.json")
    source_digest = manifest.get("source_digest")
    if (
        manifest.get("binding") != binding
        or not isinstance(source_digest, str)
        or preparation.get("source_digest") != source_digest
        or preparation.get("original_project_imported") is not False
        or preparation.get("original_archives_copied") is not False
        or preparation.get("python_environment") != "independent locked student-project venv"
        or preparation.get("passed") is not False
        or preparation.get("prepared") is not True
        or preparation.get("tests_executed") is not False
        or preparation.get("phase") != "prepared_for_independent_acceptance"
    ):
        raise ValueError("Missing genuine reconstruction evidence")
    for phase in ("browser", "install"):
        restored = read_json(folder / (prefix + "restored-" + phase) / "restored/restored.json")
        if (
            restored.get("binding") != {**binding, "source_digest": source_digest}
            or restored.get("phase") != phase
            or restored.get("passed") is not True
            or restored.get("original_project_imported") is not False
            or restored.get("python_environment") != "independent locked student-project venv"
        ):
            raise ValueError("Restored acceptance did not pass independently")
    inventories, summaries = {}, []
    for origin, platform, os_name in groups:
        reference, union, skipped = None, [], 0
        current = {
            **binding,
            "origin": origin,
            "platform": platform,
            "source_digest": binding["head"] if origin == "source" else source_digest,
        }
        for index in range(count):
            path = folder / (prefix + f"{origin}-{os_name}-{index}")
            inventory, omitted = validate_shard(path, current, index, count)
            if reference is not None and inventory["nodeids"] != reference:
                raise ValueError("Shards disagree on complete platform collection")
            reference = inventory["nodeids"]
            union.extend(inventory["selected"])
            skipped += omitted
        if sorted(union) != reference or len(union) != len(set(union)):
            raise ValueError("Shards do not cover the exact full suite once")
        inventories[(origin, platform)] = reference
        summaries.append(
            {
                "origin": origin,
                "platform": platform,
                "collected": len(reference),
                "passed": len(reference) - skipped,
                "skipped": skipped,
                "inventory_digest": inventory["inventory_digest"],
                "shards": count,
            }
        )
    if inventories[("source", "linux")] != inventories[("restored", "linux")]:
        raise ValueError("Restored suite lost or added source tests")
    return {
        "passed": True,
        "binding": binding,
        "groups": summaries,
        "required_jobs": sorted(REQUIRED_JOBS),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    stage = commands.add_parser("receipt")
    stage.add_argument("name", choices=sorted(STAGES))
    stage.add_argument("--reports", type=Path, default=Path("reports"))
    gate = commands.add_parser("aggregate")
    gate.add_argument("--artifacts", type=Path, default=Path("acceptance-artifacts"))
    args = parser.parse_args()
    if args.command == "receipt":
        receipt(args.name, args.reports)
    else:
        import json

        result = aggregate(args.artifacts, json.loads(os.environ["CI_NEEDS"]), run_binding())
        write_json(Path("reports/acceptance.json"), result)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
````
