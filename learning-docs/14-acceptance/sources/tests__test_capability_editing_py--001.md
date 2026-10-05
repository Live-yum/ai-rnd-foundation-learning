# tests/test_capability_editing.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_editing`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `task`（L10–L18）：接收`files`。 调用`CapabilityTask`。 返回路径：L11的`CapabilityTask( id="team", title="Team rules", requirements=["source-0-0"], files=files, c…`。
- `edits`（L21–L25）：接收`path`、`before`、`content`。 调用`CapabilityEdits`。 返回路径：L22的`CapabilityEdits( explanation="test fixture", files=[{"path": path, "before_sha256": before…`。
- `test_candidate_is_separate_and_replay_is_hash_bound`（L28–L47）：接收`tmp_path`。 控制顺序：L38断言`receipt["host_execution"] is False`；L39断言`(product / "app.py").read_text() == "original\n"`；L40断言`"never import" in (candidate / "app.py").read_text()`；L41断言`apply_candidate(product, value, task(["app.py"]), {"template": "python-basic"}, candi…`。 调用`product.mkdir`、`(product / "app.py").write_text`、`sha`、`edits`、`apply_candidate`、`task`、`(product / "app.py").read_text`、`(candidate / "app.py").read_text`、`(candidate / "app.py").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_protected_paths_cannot_be_approved_by_model`（L61–L68）：接收`tmp_path`、`path`。 控制顺序：L68断言`not (tmp_path / "candidate").exists()`。 调用`product.mkdir`、`pytest.raises`、`apply_candidate`、`edits`、`task`、`(tmp_path / "candidate").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_and_extra_edits_fail_before_copy`（L71–L90）：接收`tmp_path`。 调用`product.mkdir`、`(product / "app.py").write_text`、`pytest.raises`、`apply_candidate`、`edits`、`task`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_editing.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L90。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2866`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_editing.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "af027f0d03d6a53b1a238b9ca52838ef55ddab045455128ff235d5dd186bc583"} -->
````python
# tests/test_capability_editing.py
"""Candidate editing must not mutate baselines or execute product code."""

import pytest

from workbench.capability_contracts import CapabilityEdits, CapabilityTask
from workbench.capability_editing import apply_candidate
from workbench.filesystem import sha


def task(files):
    return CapabilityTask(
        id="team",
        title="Team rules",
        requirements=["source-0-0"],
        files=files,
        contract="Cross-record bounded team module",
        scenarios=["teams"],
    )


def edits(path, before=None, content="raise RuntimeError('never import generated code')\n"):
    return CapabilityEdits(
        explanation="test fixture",
        files=[{"path": path, "before_sha256": before, "content": content}],
    )


def test_candidate_is_separate_and_replay_is_hash_bound(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("original\n")
    before = sha(product / "app.py")
    value = edits("app.py", before)
    candidate = tmp_path / "candidate"
    receipt = apply_candidate(
        product, value, task(["app.py"]), {"template": "python-basic"}, candidate
    )
    assert receipt["host_execution"] is False
    assert (product / "app.py").read_text() == "original\n"
    assert "never import" in (candidate / "app.py").read_text()
    assert (
        apply_candidate(product, value, task(["app.py"]), {"template": "python-basic"}, candidate)
        == receipt
    )
    (candidate / "app.py").write_text("tampered")
    with pytest.raises(ValueError, match="身份"):
        apply_candidate(product, value, task(["app.py"]), {"template": "python-basic"}, candidate)


@pytest.mark.parametrize(
    "path",
    [
        "pyproject.toml",
        "verify.py",
        "workbench/flow.py",
        "deployment/run.py",
        "start.py",
        "package.json",
    ],
)
def test_protected_paths_cannot_be_approved_by_model(tmp_path, path):
    product = tmp_path / "product"
    product.mkdir()
    with pytest.raises(ValueError):
        apply_candidate(
            product, edits(path), task([path]), {"template": "python-basic"}, tmp_path / "candidate"
        )
    assert not (tmp_path / "candidate").exists()


def test_stale_and_extra_edits_fail_before_copy(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("original")
    with pytest.raises(ValueError, match="前像"):
        apply_candidate(
            product,
            edits("app.py"),
            task(["app.py"]),
            {"template": "python-basic"},
            tmp_path / "candidate",
        )
    with pytest.raises(ValueError, match="全部文件"):
        apply_candidate(
            product,
            edits("extra.py"),
            task(["app.py"]),
            {"template": "python-basic"},
            tmp_path / "candidate",
        )
````
