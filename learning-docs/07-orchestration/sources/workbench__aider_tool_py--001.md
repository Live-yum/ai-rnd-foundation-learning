# workbench/aider_tool.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：隔离的Aider命令行适配。** Repo Map与SEARCH/REPLACE调用真实Aider CLI，但CLI不持有大模型Key。先用原文唯一匹配算出期望结果，再在临时Git工作区应用，检查实际结果和变更文件集合；只把批准的规则文件放回产品。

**对应关系：** coding_engine=aider → code_rules_with_aider → gateway/preview_blocks/apply_blocks；ci_aider_workflow。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.coding`、`workbench.domain`、`workbench.filesystem`、`workbench.knowledge`、`workbench.rules`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `EditBlocks`（L27–L31）：继承`BaseModel`。声明的数据项为`before_sha256`、`blocks`、`explanation`；类型约束/数据库列参数以完整定义为准。
- `executable`（L34–L49）：接收`settings`。 控制顺序：L42按`not candidate.is_absolute() or not candidate.is_file()`分支；L43抛异常，停止当前正常路径；L47按`not interpreter.is_file()`分支；L48抛异常，停止当前正常路径。 调用`Path`、`candidate.is_absolute`、`candidate.is_file`、`ValueError`、`interpreter.is_file`、`str`。 返回路径：L49的`str(interpreter)`。
- `isolated_environment`（L52–L66）：接收`home`。 调用`str`。 返回路径：L53的`{ "HOME": str(home), "USERPROFILE": str(home), "XDG_CONFIG_HOME": str(home), "XDG_CACHE_HO…`。
- `git`（L69–L83）：接收`work`、`home`、`*args`。 调用`run_command`、`str`、`isolated_environment`。 返回路径：L70的`run_command( [ "git", "-c", "core.hooksPath=" + str(home / "hooks"), "-c", "user.name=RND …`。
- `command`（L86–L134）：接收`settings`、`work`、`home`、`*args`。 控制顺序：L97按`not re.search(r"\b" + re.escape(AIDER_VERSION) + r"\b", version)`分支；L98抛异常，停止当前正常路径。 调用`atomic_text`、`isolated_environment`、`run_command`、`executable`、`str`、`re.search`、`re.escape`、`ValueError`。 返回路径：L99的`run_command( [ executable(settings), str(ROOT / "tools/aider/offline_runner.py"), "--model…`。
- `preview_blocks`（L137–L152）：接收`before`、`blocks`。每段SEARCH必须与原文唯一匹配；预先算出的完整新文本是检查Aider实际执行结果的依据。 控制顺序：L143按`not 1 <= len(matches) <= 8 or pattern.sub("", blocks).strip()`分支；L144抛异常，停止当前正常路径；L146遍历`matches`；L148按`not old or current.count(old) != 1`分支；L149抛异常，停止当前正常路径。 调用`re.compile`、`list`、`pattern.finditer`、`len`、`pattern.sub("", blocks).strip`、`pattern.sub`、`ValueError`、`match.groups`、`current.count`等。 返回路径：L152的`current`。
- `apply_blocks`（L155–L204）：接收`product`、`value`、`settings`、`attempt`。保护对象是原产品目录：先在隔离副本验证全部变更，只把批准且校验通过的结果复制回去。 控制顺序：L159按`sha(path) != value.before_sha256`分支；L160抛异常，停止当前正常路径；L177按`actual != expected`分支；L178抛异常，停止当前正常路径；L183按`manifest(product) != original`分支；L184抛异常，停止当前正常路径；L185按`evidence.exists()`分支。 调用`Path`、`manifest`、`sha`、`ValueError`、`preview_blocks`、`path.read_text`、`digest`、`value.model_dump`、`evidence.parent.mkdir`等。 返回路径：L204的`receipt`。
- `code_rules_with_aider`（L207–L226）：接收`run_id`、`plan`、`product`、`gateway`、`settings`、`attempt`、`error`。 控制顺序：L224抛异常，停止当前正常路径。 调用`INSTRUCTION.replace`、`gateway.complete`、`rule_context`、`apply_blocks`、`ValueError`、`build_index`、`Path`。 返回路径：L226的`receipt`。
- `repo_map`（L229–L272）：接收`source`、`index_dir`、`settings`。 控制顺序：L238按`len(selected) > 20000 or sum(p.stat().st_size for _, p in selected) > 80_000_000`分支；L239抛异常，停止当前正常路径；L245遍历`selected`。 调用`current_index`、`files`、`len`、`sum`、`p.stat`、`ValueError`、`tempfile.TemporaryDirectory`、`Path`、`work.mkdir`等。 返回路径：L272的`report`。

</details>

**创建路径：** `workbench/aider_tool.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L272。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10120`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/aider_tool.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2dbb259cec7368bbe53e2a604c6f28667596fb7c751171be109a580a34bb9911"} -->
````python
# workbench/aider_tool.py
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

from workbench.coding import INSTRUCTION, apply_patch, rule_context
from workbench.domain import Patch, digest
from workbench.filesystem import atomic_text, files, manifest, sha, write_json
from workbench.knowledge import build_index
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
    interpreter = candidate.parent / ("python.exe" if os.name == "nt" else "python")
    if not interpreter.is_file():
        raise ValueError("Aider路径旁没有对应Python解释器；请使用tools/aider的独立uv环境")
    return str(interpreter)


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
    # YAML config must be a mapping; Git and dotenv still use a separate empty file.
    atomic_text(home / "aider.yml", "{}\n")
    env = isolated_environment(home)
    version = run_command(
        [executable(settings), str(ROOT / "tools/aider/offline_runner.py"), "--version"],
        work,
        timeout=30,
        extra_env=env,
    )["log"]
    if not re.search(r"\b" + re.escape(AIDER_VERSION) + r"\b", version):
        raise ValueError("Aider 版本与受测版本不一致，请使用仓库的 tools/aider/uv.lock")
    return run_command(
        [
            executable(settings),
            str(ROOT / "tools/aider/offline_runner.py"),
            "--model",
            "gpt-4o-mini",
            "--edit-format",
            "diff",
            "--config",
            str(home / "aider.yml"),
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
            network="disabled",
            explanation=value.explanation,
        )
        write_json(product.parent / f"coding-{attempt}.json", receipt)
    return receipt


def code_rules_with_aider(run_id, plan, product, gateway, settings, attempt, error=""):
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
        rule_context(plan, product, error),
        EditBlocks,
    )
    try:
        receipt = apply_blocks(product, value, settings, attempt)
    except ToolFailure as exc:
        raise ValueError("Aider 编辑失败，未写入产品；检查工具安装和当前补丁") from exc
    build_index(product, Path(product).parent / "knowledge", "generated-product")
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
        "network": "disabled",
    }
    write_json(Path(index_dir) / "repo-map.json", report)
    return report
````
