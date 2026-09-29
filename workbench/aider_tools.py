"""Optional genuine Aider RepoMap and offline SEARCH/REPLACE, with platform-owned gates."""

import difflib
import hashlib
import json
import os
import tempfile
from pathlib import Path

from filelock import FileLock
from pydantic import BaseModel, ConfigDict, Field

from workbench.filesystem import atomic_text, files, sha, write_json
from workbench.retrieval import allowed
from workbench.rules import Rules
from workbench.settings import ROOT
from workbench.tools import run_command

TOOL = ROOT / "tools/aider"


class Edit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search: str = Field(min_length=1, max_length=20000)
    replace: str = Field(max_length=20000)


class Edits(BaseModel):
    model_config = ConfigDict(extra="forbid")
    before_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    edits: list[Edit] = Field(min_length=1, max_length=8)
    explanation: str = Field(max_length=2000)


def tool_python():
    path = TOOL / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not path.is_file():
        raise ValueError(
            "Aider工具未安装：执行 uv run rnd tools install-aider；平台仍使用Python3.14"
        )
    return path


def environment(home):
    home = Path(home)
    home.mkdir(parents=True, exist_ok=True)
    return {
        "HOME": str(home),
        "USERPROFILE": str(home),
        "APPDATA": str(home),
        "LOCALAPPDATA": str(home),
        "XDG_CONFIG_HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "AIDER_ANALYTICS": "false",
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        "NO_COLOR": "1",
    }


def worker(operation, source, argument, output, timeout):
    # clean_env in run_command excludes all provider and native database credentials.
    return run_command(
        [
            str(tool_python()),
            str(TOOL / "worker.py"),
            operation,
            str(source),
            str(argument),
            str(output),
        ],
        source,
        timeout,
        environment(Path(output).parent / "home"),
    )


def repo_map(source, settings, max_chars=8000):
    from workbench.domain import digest
    from workbench.filesystem import manifest

    if not 500 <= max_chars <= 30000:
        raise ValueError("RepoMap预算需要500到30000字符")
    original = manifest(source)
    with tempfile.TemporaryDirectory(prefix="rnd-repomap-") as temp:
        temp = Path(temp)
        stage = temp / "source"
        stage.mkdir()
        names, size = [], 0
        for name, path in files(source):
            if not allowed(name) or path.suffix not in {
                ".py",
                ".java",
                ".ts",
                ".tsx",
                ".vue",
                ".js",
                ".jsx",
            }:
                continue
            size += path.stat().st_size
            if size > 100_000_000 or len(names) >= 25000:
                raise ValueError("Aider代码快照超过上限，请选择更小的源码目录")
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
            names.append(name)
        request, output = temp / "request.json", temp / "result.json"
        write_json(request, {"files": names, "budget": max_chars})
        worker("map", stage, request, output, settings.tool_timeout)
        if not output.is_file() or output.stat().st_size > 2_000_000:
            raise ValueError("Aider地图结果缺失或超限")
        result = json.loads(output.read_text(encoding="utf-8"))
        text = result["text"]
        kept, used = [], 0
        for line in text.splitlines(keepends=True):
            if used + len(line) > max_chars:
                break
            kept.append(line)
            used += len(line)
        result.update(
            text="".join(kept), truncated=used < len(text), source_digest=digest(original)
        )
        if manifest(source) != original:
            raise ValueError("生成地图时源码发生变化，拒绝返回过期地图")
        return result


def proposed_content(before, proposal):
    content = before
    for edit in proposal.edits:
        if any(
            marker in edit.search or marker in edit.replace
            for marker in ("<<<<<<<", "=======", ">>>>>>>")
        ):
            raise ValueError("编辑内容不得嵌入SEARCH/REPLACE控制标记")
        if content.count(edit.search) != 1:
            raise ValueError("SEARCH必须在当前文件中精确且唯一匹配；不启用模糊替换")
        content = content.replace(edit.search, edit.replace, 1)
    if content == before or len(content.encode("utf-8")) > 60000:
        raise ValueError("编辑为空或超过规则文件上限")
    Rules(content)
    return content


def apply_edits(product, proposal, settings, attempt):
    from workbench.domain import digest

    product = Path(product)
    path = product / "custom_rules.py"
    receipt_path = product.parent / f"aider-{attempt}.json"
    with FileLock(str(product.parent / "aider-edit.lock"), timeout=30):
        if path.is_symlink():
            raise ValueError("拒绝通过符号链接修改规则")
        fingerprint = digest(proposal.model_dump())
        if receipt_path.exists():
            old = json.loads(receipt_path.read_text(encoding="utf-8"))
            if old.get("proposal_digest") == fingerprint and old["after"] == sha(path):
                return {**old, "replayed": True}
        if sha(path) != proposal.before_sha256:
            raise ValueError("文件已变化，拒绝过期Aider编辑")
        before = path.read_text(encoding="utf-8")
        expected = proposed_content(before, proposal)
        with tempfile.TemporaryDirectory(prefix="rnd-aider-edit-") as temp:
            temp = Path(temp)
            stage = temp / "source"
            stage.mkdir()
            atomic_text(stage / "custom_rules.py", before)
            env = environment(temp / "home")

            def git(*args):
                return run_command(
                    [
                        "git",
                        "-c",
                        "core.hooksPath=" + str(temp / "no-hooks"),
                        "-c",
                        "user.name=RND bounded editor",
                        "-c",
                        "user.email=rnd@localhost",
                        *args,
                    ],
                    stage,
                    settings.tool_timeout,
                    env,
                )["log"].strip()

            git("init", "-q")
            git("add", "--", "custom_rules.py")
            git("commit", "-qm", "Before bounded Aider edit")
            before_commit = git("rev-parse", "HEAD")
            blocks = []
            for edit in proposal.edits:
                # Aider's block format is line-oriented. Require whole-line boundaries.
                if not edit.search.endswith("\n") or (
                    edit.replace and not edit.replace.endswith("\n")
                ):
                    raise ValueError("Aider SEARCH/REPLACE块必须包含完整行并以换行结束")
                blocks.append(
                    "custom_rules.py\n```python\n<<<<<<< SEARCH\n"
                    + edit.search
                    + "=======\n"
                    + edit.replace
                    + ">>>>>>> REPLACE\n```\n"
                )
            response, output = temp / "response.txt", temp / "result.json"
            atomic_text(response, "\n".join(blocks))
            worker("apply", stage, response, output, settings.tool_timeout)
            if {n for n, _ in files(stage)} != {"custom_rules.py"}:
                raise ValueError("Aider产生了白名单外文件；原项目未修改")
            if (stage / "custom_rules.py").read_text(encoding="utf-8") != expected:
                raise ValueError("Aider实际结果不等于已批准的精确替换；原项目未修改")
            git("add", "--", "custom_rules.py")
            git("commit", "-qm", "Apply bounded Aider SEARCH REPLACE")
            after_commit = git("rev-parse", "HEAD")
            bundle = product.parent / f"aider-{attempt}.bundle"
            if bundle.exists():
                bundle.unlink()
            git("bundle", "create", str(bundle.resolve()), "--all")
            receipt = {
                "engine": "aider-0.86.2-apply",
                "model_calls_by_aider": 0,
                "proposal_digest": fingerprint,
                "path": "custom_rules.py",
                "before": proposal.before_sha256,
                "after": hashlib.sha256(expected.encode()).hexdigest(),
                "before_commit": before_commit,
                "after_commit": after_commit,
                "bundle": bundle.name,
                "bundle_sha256": sha(bundle),
                "replayed": False,
                "diff": "".join(
                    difflib.unified_diff(
                        before.splitlines(True),
                        expected.splitlines(True),
                        fromfile="a/custom_rules.py",
                        tofile="b/custom_rules.py",
                    )
                ),
            }
            # Write recovery receipt first: a crash after atomic replacement can replay safely.
            write_json(receipt_path, receipt)
            if sha(path) != proposal.before_sha256:
                raise ValueError("提交前检测到文件变化，拒绝覆盖")
            atomic_text(path, expected)
            return receipt
