# tests/test_capability_native_freeze.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `captured_script`（L11–L21）：接收`monkeypatch`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`runtime.verify_and_freeze_native_sources`。 返回路径：L21的`scripts[0]`。
- `captured_script.capture`（L15–L17）：接收`sandbox`、`argv`、`timeout`。 调用`scripts.append`、`SimpleNamespace`。 返回路径：L17的`SimpleNamespace(exit_code=0)`。
- `test_ancestor_symlink_rejected_before_privileged_mkdir_or_chown`（L25–L48）：接收`tmp_path`、`monkeypatch`、`relative`。 控制顺序：L47断言`mutations == []`；L48断言`list(outside.iterdir()) == []`。 调用`captured_script`、`root.mkdir`、`(root / "frontend/web/dist").mkdir`、`(root / "frontend/web/dist/index.html").write_text`、`outside.mkdir`、`target.parent.mkdir`、`target.symlink_to`、`control.write_text`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_writable_hardlink_cannot_restore_protected_source_write_access`（L51–L73）：接收`tmp_path`、`monkeypatch`。 控制顺序：L72断言`mutations == []`；L73断言`source.read_text() == "protected = True"`。 调用`captured_script`、`(root / "frontend/web/dist").mkdir`、`(root / "frontend/web/dist/index.html").write_text`、`(root / "backend/app").mkdir`、`source.write_text`、`(root / "backend/logs").mkdir`、`os.link`、`control.write_text`、`script.replace("/tmp/rnd-capability/product", str(root)).replace`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_freeze.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L73。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2761`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_freeze.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b22a7b5de07b56df701186101deab0456aaa6455076536e4cd56ced87a92b871"} -->
````python
# tests/test_capability_native_freeze.py
"""Exercise trusted freeze script against owned hostile symlink fixtures only."""

import json
from types import SimpleNamespace

import pytest

from workbench import capability_native_runtime as runtime


def captured_script(monkeypatch):
    scripts = []
    sandbox = SimpleNamespace(fs=SimpleNamespace(upload_file=lambda *a, **kw: None))

    def capture(sandbox, argv, timeout):
        scripts.append(argv[-1])
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(runtime, "control_exec", capture)
    runtime.verify_and_freeze_native_sources(sandbox, {}, 10)
    return scripts[0]


@pytest.mark.parametrize("relative", ["backend/static", "backend", "frontend/web/node_modules"])
def test_ancestor_symlink_rejected_before_privileged_mkdir_or_chown(
    tmp_path, monkeypatch, relative
):
    script = captured_script(monkeypatch)
    root = tmp_path / "product"
    root.mkdir()
    (root / "frontend/web/dist").mkdir(parents=True)
    (root / "frontend/web/dist/index.html").write_text("owned test")
    outside = tmp_path / "outside"
    outside.mkdir()
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(outside, target_is_directory=True)
    control = tmp_path / "manifest.json"
    control.write_text(json.dumps({}))
    script = script.replace("/tmp/rnd-capability/product", str(root)).replace(
        "/tmp/rnd-module-control/private/source-manifest.json", str(control)
    )
    mutations = []
    monkeypatch.setattr("os.chown", lambda *a: mutations.append(a))
    with pytest.raises(AssertionError):
        exec(compile(script, "<owned-freeze-test>", "exec"), {})
    assert mutations == []
    assert list(outside.iterdir()) == []


def test_writable_hardlink_cannot_restore_protected_source_write_access(tmp_path, monkeypatch):
    import os

    script = captured_script(monkeypatch)
    root = tmp_path / "product"
    (root / "frontend/web/dist").mkdir(parents=True)
    (root / "frontend/web/dist/index.html").write_text("owned test")
    (root / "backend/app").mkdir(parents=True)
    source = root / "backend/app/protected.py"
    source.write_text("protected = True")
    (root / "backend/logs").mkdir()
    os.link(source, root / "backend/logs/source-link")
    control = tmp_path / "manifest.json"
    control.write_text("{}")
    script = script.replace("/tmp/rnd-capability/product", str(root)).replace(
        "/tmp/rnd-module-control/private/source-manifest.json", str(control)
    )
    mutations = []
    monkeypatch.setattr("os.chown", lambda *a: mutations.append(a))
    with pytest.raises(AssertionError):
        exec(compile(script, "<owned-hardlink-test>", "exec"), {})
    assert mutations == []
    assert source.read_text() == "protected = True"
````
