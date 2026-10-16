# tests/test_source_candidate_derivation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.delivery`、`workbench.filesystem`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `prepared`（L15–L60）：接收`tmp_path`、`monkeypatch`、`retained`。 控制顺序：L16按`retained`分支。 调用`source.mkdir`、`(source / "example.py").write_text`、`write_json`、`manifest`、`monkeypatch.setattr`、`candidates.retain_failed_candidate`、`native_plan`、`minimal_candidate`、`shutil.copytree`等。 返回路径：L60的`args, kwargs`。
- `test_derivation_atomic_recovery_and_replay`（L65–L106）：接收`tmp_path`、`monkeypatch`、`retained`、`crash`。 控制顺序：L75按`crash == "status"`分支；L82按`crash == "receipt"`分支；L89按`crash`分支；L92断言`not destination.parent.exists()`；L96断言`candidates.derive_candidate(*args, **kwargs) == result`；L98断言`result.get("preserve_runtime_files") is None`；L99断言`result["verification_status"] == base["verification_status"]`；L100断言`result["generation_status"] == base["generation_status"]`。后续分支沿下方源码相同行号继续阅读。 调用`prepared`、`manifest`、`checkpoint.exists`、`checkpoint.read_bytes`、`monkeypatch.setattr`、`pytest.raises`、`candidates.derive_candidate`、`destination.parent.exists`、`candidates.verify_candidate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_derivation_atomic_recovery_and_replay.interrupted`（L77–L79）：接收`*values`。 控制顺序：L79抛异常，停止当前正常路径。 调用`original_status`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_derivation_atomic_recovery_and_replay.interrupted`（L84–L86）：接收`*values`、`**options`。 控制顺序：L86抛异常，停止当前正常路径。 调用`original_refresh`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_derivation_never_adopts_unapproved_tampering`（L111–L125）：接收`tmp_path`、`monkeypatch`、`retained`、`attack`。 控制顺序：L114按`attack in {"derived", "receipt"}`分支；L116按`attack == "receipt"`分支。 调用`prepared`、`candidates.derive_candidate`、`json.loads`、`path.read_text`、`write_json`、`(target / "unapproved.py").write_text`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_published_derivation_git_journal_remains_valid_after_atomic_move`（L128–L161）：接收`tmp_path`、`monkeypatch`。 控制顺序：L129按`not shutil.which("git")`分支；L158抛异常，停止当前正常路径；L159断言`result["source_commit"]["status"] == "committed"`；L160断言`candidates.verify_candidate(args[2], result)["source_commit"] == result["source_commi…`；L161断言`candidates.derive_candidate(*args, **kwargs) == result`。 调用`shutil.which`、`pytest.skip`、`prepared`、`monkeypatch.undo`、`monkeypatch.setattr`、`candidates.derive_candidate`、`exc.add_note`、`json.dumps`、`candidates.verify_candidate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_published_derivation_git_journal_remains_valid_after_atomic_move.observed_git`（L138–L149）：接收`work`、`home`、`*arguments`。 控制顺序：L140按`arguments[-2:] in { ("rev-parse", "--show-toplevel"), ("rev-parse", "--absolute-git-d…`分支。 调用`original_git`、`paths.append`、`str`。 返回路径：L149的`result`。
- `test_derivation_rejects_redirected_publish_directory`（L164–L174）：接收`tmp_path`、`monkeypatch`。 控制顺序：L174断言`list(outside.iterdir()) == []`。 调用`prepared`、`outside.mkdir`、`args[2].parent.symlink_to`、`pytest.skip`、`pytest.raises`、`candidates.derive_candidate`、`list`、`outside.iterdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_source_candidate_derivation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L174。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7049`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_candidate_derivation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "83ec110444964e7e58d985c449086bcd043a5a19a53deccdb8ca789de0b321e5"} -->
````python
# tests/test_source_candidate_derivation.py
"""Derived source drafts publish complete evidence without touching recovery sources."""

import json
import shutil

import pytest

from tests.test_source_candidate_delivery import minimal_candidate, native_plan
from workbench.core.contracts import digest
from workbench.delivery import source_candidate as candidates
from workbench.filesystem import manifest, write_json
from workbench.generation.python_basic import PrerequisiteError


def prepared(tmp_path, monkeypatch, retained):
    if retained:
        source = tmp_path / "product"
        source.mkdir()
        (source / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
        write_json(
            tmp_path / "native-evidence/recovery.json",
            {
                "files": manifest(source),
                "targets": [1],
                "stage": "validation-interrupted",
            },
        )
        monkeypatch.setattr(candidates.shutil, "which", lambda name: None)
        base = candidates.retain_failed_candidate(
            "fastapiadmin",
            native_plan(),
            source,
            [],
            "ToolFailure",
        )
    else:
        source, base = minimal_candidate(tmp_path, monkeypatch)
    edited = tmp_path / "attempt/product"
    shutil.copytree(source, edited)
    (edited / "example.py").write_text("VALUE = 2\n", encoding="utf-8")
    edit = {
        "before": manifest(source),
        "files": manifest(edited),
        "identity": "e" * 64,
        "task": "edit",
    }
    derivation = {
        "parent_receipt_digest": digest(base),
        "edit_identity": edit["identity"],
        "task": "edit",
        "approved_files": ["example.py"],
        "candidate_edit_files_digest": digest(edit["files"]),
    }
    args = (source, edited, tmp_path / "attempt/source/product", base, edit)
    kwargs = {
        "derivation": derivation,
        "pending_steps": ["运行验收"],
        "generated_files": ["example.py"],
    }
    return args, kwargs


@pytest.mark.parametrize("retained", [False, True])
@pytest.mark.parametrize("crash", [None, "status", "receipt"])
def test_derivation_atomic_recovery_and_replay(tmp_path, monkeypatch, retained, crash):
    args, kwargs = prepared(tmp_path, monkeypatch, retained)
    source, edited, destination, base, edit = args
    original = manifest(source)
    checkpoint = tmp_path / "native-evidence/recovery.json"
    before_checkpoint = checkpoint.read_bytes() if checkpoint.exists() else None
    raw_edit = manifest(edited)
    original_refresh = candidates.refresh_candidate
    original_status = candidates.write_status

    if crash == "status":

        def interrupted(*values):
            original_status(*values)
            raise RuntimeError("injected crash after status write")

        monkeypatch.setattr(candidates, "write_status", interrupted)
    elif crash == "receipt":

        def interrupted(*values, **options):
            original_refresh(*values, **options)
            raise RuntimeError("injected crash after native receipt write")

        monkeypatch.setattr(candidates, "refresh_candidate", interrupted)
    if crash:
        with pytest.raises(RuntimeError, match="injected crash"):
            candidates.derive_candidate(*args, **kwargs)
        assert not destination.parent.exists()
        monkeypatch.setattr(candidates, "refresh_candidate", original_refresh)
        monkeypatch.setattr(candidates, "write_status", original_status)
    result = candidates.derive_candidate(*args, **kwargs)
    assert candidates.derive_candidate(*args, **kwargs) == result
    candidates.verify_candidate(destination, result)
    assert result.get("preserve_runtime_files") is None
    assert result["verification_status"] == base["verification_status"]
    assert result["generation_status"] == base["generation_status"]
    assert result["source_derivation"]["parent_receipt_digest"] == digest(base)
    assert manifest(source) == original
    assert manifest(edited) == raw_edit
    if before_checkpoint is not None:
        assert checkpoint.read_bytes() == before_checkpoint
    assert not (destination.parent / "native-evidence/recovery.json").exists()


@pytest.mark.parametrize("retained", [False, True])
@pytest.mark.parametrize("attack", ["source", "raw-edit", "derived", "receipt"])
def test_derivation_never_adopts_unapproved_tampering(tmp_path, monkeypatch, retained, attack):
    args, kwargs = prepared(tmp_path, monkeypatch, retained)
    source, edited, destination, _, _ = args
    if attack in {"derived", "receipt"}:
        candidates.derive_candidate(*args, **kwargs)
    if attack == "receipt":
        path = destination.parent / "native-generation.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["source_derivation"]["task"] = "forged"
        write_json(path, value)
    else:
        target = {"source": source, "raw-edit": edited, "derived": destination}[attack]
        (target / "unapproved.py").write_text("UNAPPROVED = True\n", encoding="utf-8")
    with pytest.raises(PrerequisiteError):
        candidates.derive_candidate(*args, **kwargs)


def test_published_derivation_git_journal_remains_valid_after_atomic_move(tmp_path, monkeypatch):
    if not shutil.which("git"):
        pytest.skip("Git not installed")
    args, kwargs = prepared(tmp_path, monkeypatch, False)
    monkeypatch.undo()
    from workbench.coding import aider

    original_git = aider.git
    paths = []

    def observed_git(work, home, *arguments):
        result = original_git(work, home, *arguments)
        if arguments[-2:] in {
            ("rev-parse", "--show-toplevel"),
            ("rev-parse", "--absolute-git-dir"),
        }:
            # Owned temporary paths only: diagnose real-platform spelling without
            # dumping config, command environments, product content or credentials.
            paths.append(
                {"query": arguments[-1], "reported": result["log"][:1200], "work": str(work)}
            )
        return result

    monkeypatch.setattr(aider, "git", observed_git)
    try:
        result = candidates.derive_candidate(*args, **kwargs)
    except PrerequisiteError as exc:
        exc.add_note(
            "Owned Git directory diagnostics: " + json.dumps(paths[-4:], ensure_ascii=True)
        )
        raise
    assert result["source_commit"]["status"] == "committed"
    assert candidates.verify_candidate(args[2], result)["source_commit"] == result["source_commit"]
    assert candidates.derive_candidate(*args, **kwargs) == result


def test_derivation_rejects_redirected_publish_directory(tmp_path, monkeypatch):
    args, kwargs = prepared(tmp_path, monkeypatch, False)
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        args[2].parent.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks are unavailable")
    with pytest.raises(ValueError, match="符号链接|junction"):
        candidates.derive_candidate(*args, **kwargs)
    assert list(outside.iterdir()) == []
````
