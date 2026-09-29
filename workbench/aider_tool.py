"""Pinned Aider CLI, used only in a disposable local Git worktree with no keys.

ModelGateway owns model routing, quotas and structured outputs. Aider --apply is
an editing engine, not an autonomous shell agent. Platform validation/verification
remain the authority. The production product is written only after validation.
"""

import os
import re
import shutil
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from workbench.coding import INSTRUCTION, apply_patch
from workbench.domain import Patch, digest
from workbench.filesystem import atomic_text, files, manifest, sha, write_json
from workbench.knowledge import build_index, context_for
from workbench.rules import Rules
from workbench.settings import ROOT
from workbench.tools import ToolFailure, run_command

AIDER_VERSION = "0.86.2"


class EditBlocks(BaseModel):
    model_config = ConfigDict(extra="forbid")
    before_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    blocks: str = Field(min_length=1, max_length=50000)
    explanation: str = Field(max_length=2000)


def executable(settings):
    candidate = (
        Path(settings.aider_executable)
        if settings.aider_executable
        else (
            ROOT / "tools/aider/.venv" / ("Scripts/aider.exe" if os.name == "nt" else "bin/aider")
        )
    )
    if not candidate.is_absolute() or not candidate.is_file():
        raise ValueError(
            "Aider 未安装：执行 uv sync --locked --project tools/aider --python 3.12（独立工具环境）"
        )
    return str(candidate)


def isolated_environment(home):
    return {
        "HOME": str(home),
        "USERPROFILE": str(home),
        "XDG_CONFIG_HOME": str(home),
        "XDG_CACHE_HOME": str(home / "cache"),
        "APPDATA": str(home),
        "LOCALAPPDATA": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": str(home / "empty"),
        "GIT_TERMINAL_PROMPT": "0",
        "OPENAI_API_KEY": "unused-local-editing-only",
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        "AIDER_ANALYTICS": "false",
    }


def git(work, home, *args):
    return run_command(
        [
            "git",
            "-c",
            "core.hooksPath=" + str(home / "hooks"),
            "-c",
            "user.name=RND bounded editor",
            "-c",
            "user.email=rnd@localhost",
            *args,
        ],
        work,
        extra_env=isolated_environment(home),
    )


def command(settings, work, home, *args):
    atomic_text(home / "empty", "")
    env = isolated_environment(home)
    version = run_command([executable(settings), "--version"], work, timeout=30, extra_env=env)[
        "log"
    ]
    if not re.search(r"\b" + re.escape(AIDER_VERSION) + r"\b", version):
        raise ValueError("Aider 版本与受测版本不一致，请使用仓库的 tools/aider/uv.lock")
    return run_command(
        [
            executable(settings),
            "--model",
            "gpt-4o-mini",
            "--edit-format",
            "diff",
            "--config",
            str(home / "empty"),
            "--env-file",
            str(home / "empty"),
            "--input-history-file",
            str(home / "input"),
            "--chat-history-file",
            str(home / "chat"),
            "--no-auto-commits",
            "--no-dirty-commits",
            "--no-gitignore",
            "--no-add-gitignore-files",
            "--no-auto-lint",
            "--no-auto-test",
            "--no-suggest-shell-commands",
            "--no-detect-urls",
            "--no-check-update",
            "--no-show-release-notes",
            "--no-analytics",
            "--no-pretty",
            "--no-stream",
            "--yes-always",
            *args,
        ],
        work,
        timeout=settings.tool_timeout,
        extra_env=env,
    )


def preview_blocks(before, blocks):
    pattern = re.compile(
        r"custom_rules\.py\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE(?:\n|$)",
        re.DOTALL,
    )
    matches = list(pattern.finditer(blocks))
    if not 1 <= len(matches) <= 8 or pattern.sub("", blocks).strip():
        raise ValueError("只接受1至8个custom_rules.py的完整SEARCH/REPLACE块，不接受其他路径或命令")
    current = before
    for match in matches:
        old, new = match.groups()
        if not old or current.count(old) != 1:
            raise ValueError("SEARCH 必须在当前原文中唯一匹配；禁止模糊修改或整文件覆盖")
        current = current.replace(old, new, 1)
    Rules(current)
    return current


def apply_blocks(product, value, settings, attempt=0):
    product = Path(product)
    original = manifest(product)
    path = product / "custom_rules.py"
    if sha(path) != value.before_sha256:
        raise ValueError("过期 Aider 补丁，原文件 SHA 不匹配")
    expected = preview_blocks(path.read_text(encoding="utf-8"), value.blocks)
    evidence = product.parent / "edits" / f"aider-{attempt}-{digest(value.model_dump())[:12]}"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="aider-", dir=evidence.parent) as temporary:
        root = Path(temporary)
        work, home = root / "work", root / "home"
        work.mkdir()
        home.mkdir()
        shutil.copyfile(path, work / "custom_rules.py")
        atomic_text(home / "edits.txt", value.blocks)
        git(work, home, "init", "-q")
        git(work, home, "add", "--", "custom_rules.py")
        git(work, home, "commit", "-qm", "Before bounded rule edit")
        before_commit = git(work, home, "rev-parse", "HEAD")["log"].strip()
        command(settings, work, home, "--apply", str(home / "edits.txt"), "custom_rules.py")
        actual = (work / "custom_rules.py").read_text(encoding="utf-8")
        if actual != expected:
            raise ValueError("Aider 结果与预验证补丁不一致；未修改产品")
        Rules(actual)
        git(work, home, "add", "--", "custom_rules.py")
        git(work, home, "commit", "--allow-empty", "-qm", "Validated bounded Aider edit")
        after_commit = git(work, home, "rev-parse", "HEAD")["log"].strip()
        if manifest(product) != original:
            raise ValueError("编辑期间产品源码变化，拒绝提交")
        if evidence.exists():
            shutil.rmtree(evidence)
        shutil.copytree(work, evidence)
        receipt = apply_patch(
            product,
            Patch(path="custom_rules.py", before_sha256=value.before_sha256, content=actual),
        )
        receipt.update(
            provider="aider-cli-apply",
            version=AIDER_VERSION,
            attempt=attempt,
            before_commit=before_commit,
            after_commit=after_commit,
            journal=str(evidence.relative_to(product.parent)),
            model_called_by_aider=False,
            explanation=value.explanation,
        )
        write_json(product.parent / f"coding-{attempt}.json", receipt)
    return receipt


def code_rules_with_aider(run_id, plan, product, gateway, settings, attempt, error=""):
    knowledge = Path(product).parent / "knowledge"
    build_index(product, knowledge, "generated-product")
    context = context_for(product, knowledge, ["custom_rules.py", "approved-spec.json"])
    instruction = INSTRUCTION.replace("必须返回 patches JSON", "必须返回 EditBlocks JSON")
    instruction += (
        "\n只返回before_sha256、blocks、explanation。blocks不加Markdown围栏，格式："
        "custom_rules.py\\n<<<<<<< SEARCH\\n唯一匹配原文\\n=======\\n替换代码\\n>>>>>>> REPLACE\\n。"
        "不得使用空SEARCH，不得改变已批准的正反例。"
    )
    value = gateway.complete(
        run_id,
        f"coding:aider:{attempt}",
        instruction,
        {"plan": plan.model_dump(), "context": context, "previous_error": error},
        EditBlocks,
    )
    try:
        receipt = apply_blocks(product, value, settings, attempt)
    except ToolFailure as exc:
        raise ValueError("Aider 编辑失败，未写入产品；检查工具安装和当前补丁") from exc
    build_index(product, knowledge, "generated-product")
    return receipt


def repo_map(source, index_dir, settings):
    from workbench.retrieval import CODE_SUFFIXES, current_index

    index = current_index(source, index_dir)
    selected = [
        (name, path)
        for name, path in files(source)
        if path.suffix in CODE_SUFFIXES and path.suffix != ".md"
    ]
    if len(selected) > 20000 or sum(p.stat().st_size for _, p in selected) > 80_000_000:
        raise ValueError("Aider Repo Map 输入超出预算，请分模板slot索引")
    with tempfile.TemporaryDirectory(prefix="rnd-repomap-") as temporary:
        root = Path(temporary)
        work, home = root / "work", root / "home"
        work.mkdir()
        home.mkdir()
        for name, path in selected:
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        git(work, home, "init", "-q")
        git(work, home, "add", "--all")
        result = command(
            settings,
            work,
            home,
            "--show-repo-map",
            "--map-tokens",
            "2048",
            "--map-multiplier-no-files",
            "1",
        )
    raw = result["log"]
    report = {
        "provider": "aider-cli-repo-map",
        "version": AIDER_VERSION,
        "source_digest": index["source_digest"],
        "text": raw[: settings.repo_map_chars],
        "truncated": len(raw) > settings.repo_map_chars,
        "model_called": False,
    }
    write_json(Path(index_dir) / "repo-map.json", report)
    return report
