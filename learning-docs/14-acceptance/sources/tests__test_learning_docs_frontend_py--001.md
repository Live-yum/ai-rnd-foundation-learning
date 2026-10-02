# tests/test_learning_docs_frontend.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.rebuild_from_handbook`、`scripts.rebuild_learning_docs`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `write_files`（L16–L20）：接收`root`、`files`。 控制顺序：L17遍历`files.items()`。 调用`files.items`、`target.parent.mkdir`、`target.write_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_vue_authored_source_and_generated_assets_are_both_losslessly_collected`（L23–L46）：接收`tmp_path`、`monkeypatch`。 控制顺序：L39断言`rows.keys() == files.keys()`；L40遍历`files.items()`；L41断言`rows[name] == (data if name.startswith("workbench/web/") else data.decode())`；L43断言`{ name: value.encode() if isinstance(value, str) else value for name, value in restor…`。 调用`"<template>中文</template>\n".encode`、`"(()=>{const s='中文';})();".encode`、`write_files`、`monkeypatch.setattr`、`dict`、`next`、`legacy.sources`、`rows.keys`、`files.keys`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_assets_use_labeled_folded_base64_without_losing_bytes`（L52–L64）：接收`name`。 控制顺序：L55断言`len(pages) == 1`；L57断言`"/sources/assets/" in row["parts"][0]`；L58断言`"<details>" in document and "无需手写" in document`；L59断言`"构建快照" in document and "真实操作截图" not in document`；L60断言`row["sha256"] == hashlib.sha256(data).hexdigest()`；L61断言`check_fences(document) == 1`；L63断言`(language, path) == ("base64", name)`；L64断言`base64.b64decode(payload.replace("\n", ""), validate=True) == data`。 调用`builder.source_pages`、`len`、`next`、`iter`、`pages.values`、`hashlib.sha256(data).hexdigest`、`hashlib.sha256`、`check_fences`、`fences`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_vue_and_streaming_stage_allocation_preserves_import_order`（L82–L83）：接收`name`、`stage`。 控制顺序：L83断言`builder.stage_for(name) == stage`。 调用`builder.stage_for`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_frontend_installs_tests_builds_and_compares_without_git`（L86–L100）：接收`tmp_path`。 控制顺序：L94断言`acceptance.rebuild_frontend(tmp_path, expected, "npm", run) == 1`；L95断言`commands == [ ["npm", "ci", "--prefix", "ui", "--no-audit", "--no-fund"], ["npm", "te…`；L100断言`not (tmp_path / ".git").exists()`。 调用`write_files`、`acceptance.rebuild_frontend`、`(tmp_path / ".git").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_frontend_installs_tests_builds_and_compares_without_git.run`（L91–L92）：接收`argv`。 调用`commands.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_frontend_rejects_incomplete_or_different_builds`（L104–L116）：接收`tmp_path`、`damage`。 控制顺序：L107按`damage == "missing"`分支；L109按`damage == "extra"`分支；L111按`damage == "bytes"`分支。 调用`write_files`、`(tmp_path / "workbench/web/app.js").unlink`、`pytest.raises`、`acceptance.verify_frontend_bundle`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_test_failure_stops_before_build_and_byte_comparison`（L119–L130）：接收`tmp_path`。 控制顺序：L129断言`len(commands) == 2`；L130断言`all("build" not in command for command in commands)`。 调用`pytest.raises`、`acceptance.rebuild_frontend`、`len`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_test_failure_stops_before_build_and_byte_comparison.run`（L122–L125）：接收`argv`。 控制顺序：L124按`"test" in argv`分支；L125抛异常，停止当前正常路径。 调用`commands.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_lessons_distinguish_browser_evidence_and_current_startup_delivery_boundaries`（L133–L144）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L138断言`"`start` 还会要求真实模型配置" not in startup`；L139断言`"没有供应商Key时启动操作台" in control`；L140断言`"SOURCE_READY" in control`；L141断言`"uv run python -m scripts.ci_guided_browser" in final`；L142断言`"reports/learning-docs-guided-browser" in final`；L143断言`"不能把纯函数测试当作整条页面链已通过" in final`；L144断言`all(check_fences(stage["body"]) >= 0 for stage in stages.values())`。 调用`builder.read_content`、`all`、`check_fences`、`stages.values`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_calls_real_browser_driver_and_copies_its_distinct_evidence`（L147–L170）：接收`tmp_path`。 控制顺序：L166断言`acceptance.verify_frontend_browser(destination, "student-python", run, reports) == su…`；L169断言`commands == [["student-python", "-m", "scripts.ci_guided_browser"]]`；L170断言`json.loads((reports / "summary.json").read_text()) == summary`。 调用`acceptance.verify_frontend_browser`、`json.loads`、`(reports / "summary.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_calls_real_browser_driver_and_copies_its_distinct_evidence.run`（L159–L164）：接收`argv`。 调用`commands.append`、`write_files`、`json.dumps(summary).encode`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_preserves_browser_failure_without_accepting_an_old_success`（L173–L189）：接收`tmp_path`。 控制顺序：L184断言`(reports / "workbench.log").read_bytes() == b"fixture failure"`；L185断言`not (reports / "summary.json").exists()`；L187断言`not (reports / "old.png").exists()`；L188断言`(previous / "summary.json").read_bytes() == b'{"passed":true}'`；L189断言`(previous / "old.png").read_bytes() == b"old image"`。 调用`write_files`、`pytest.raises`、`acceptance.verify_frontend_browser`、`(reports / "workbench.log").read_bytes`、`(reports / "summary.json").exists`、`(reports / "old.png").exists`、`(previous / "summary.json").read_bytes`、`(previous / "old.png").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_preserves_browser_failure_without_accepting_an_old_success.run`（L178–L180）：接收`argv`。 控制顺序：L180抛异常，停止当前正常路径。 调用`write_files`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanroom_browser_refuses_reusing_an_existing_evidence_directory`（L192–L199）：接收`tmp_path`。 控制顺序：L198断言`commands == []`；L199断言`(reports / "summary.json").read_bytes() == b'{"passed":true}'`。 调用`write_files`、`pytest.raises`、`acceptance.verify_frontend_browser`、`(reports / "summary.json").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_learning_docs_frontend.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L199。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7944`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_learning_docs_frontend.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2167d7bfa82b3633fc4c43f9a84b547dde4d2c0e981352de40d77f49e1d31b41"} -->
````python
# tests/test_learning_docs_frontend.py
"""Lossless Vue source/asset teaching and genuinely rebuilt clean-room assets."""

import base64
import hashlib
import json

import pytest

from scripts import build_handbook as legacy
from scripts import build_learning_docs as builder
from scripts import ci_learning_docs as acceptance
from scripts.rebuild_from_handbook import extract
from scripts.rebuild_learning_docs import check_fences, fences


def write_files(root, files):
    for name, data in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def test_vue_authored_source_and_generated_assets_are_both_losslessly_collected(
    tmp_path, monkeypatch
):
    files = {
        "ui/src/App.vue": "<template>中文</template>\n".encode(),
        "ui/package-lock.json": b'{"lockfileVersion":3}\n',
        "workbench/web/index.html": b'<script src="/ui/app.js"></script>',
        "workbench/web/app.js": "(()=>{const s='中文';})();".encode(),
        "workbench/web/style.css": b"body{margin:0}\n",
    }
    write_files(tmp_path, files)
    write_files(tmp_path, {"ui/node_modules/not-owned/index.js": b"not source"})
    monkeypatch.setattr(legacy, "ROOT", tmp_path)
    monkeypatch.setattr(legacy, "GROUPS", [("control plane", ["ui", "workbench"])])
    monkeypatch.setattr(legacy, "GUIDES", [])
    rows = dict(next(legacy.sources())[1])
    assert rows.keys() == files.keys()
    for name, data in files.items():
        assert rows[name] == (data if name.startswith("workbench/web/") else data.decode())
    restored = extract(legacy.render())
    assert {
        name: value.encode() if isinstance(value, str) else value
        for name, value in restored.items()
    } == files


@pytest.mark.parametrize(
    "name", ["workbench/web/app.js", "workbench/web/style.css", "workbench/web/index.html"]
)
def test_generated_assets_use_labeled_folded_base64_without_losing_bytes(name):
    data = b"generated runtime snapshot\x00\xff\n"
    pages, row = builder.source_pages(name, data, 8)
    assert len(pages) == 1
    document = next(iter(pages.values()))
    assert "/sources/assets/" in row["parts"][0]
    assert "<details>" in document and "无需手写" in document
    assert "构建快照" in document and "真实操作截图" not in document
    assert row["sha256"] == hashlib.sha256(data).hexdigest()
    assert check_fences(document) == 1
    _, language, path, payload = next(fences(document))
    assert (language, path) == ("base64", name)
    assert base64.b64decode(payload.replace("\n", ""), validate=True) == data


@pytest.mark.parametrize(
    "name,stage",
    [
        ("ui/src/App.vue", 8),
        ("ui/src/api.ts", 8),
        ("ui/tests/stream.test.ts", 8),
        ("ui/package-lock.json", 8),
        ("workbench/model_settings.py", 1),
        ("workbench/clarification.py", 2),
        ("workbench/streaming.py", 3),
        ("tests/test_streaming_backend.py", 8),
        ("tests/test_model_settings.py", 8),
        ("tests/test_clarification_choices.py", 8),
    ],
)
def test_vue_and_streaming_stage_allocation_preserves_import_order(name, stage):
    assert builder.stage_for(name) == stage


def test_cleanroom_frontend_installs_tests_builds_and_compares_without_git(tmp_path):
    expected = {"workbench/web/app.js": b"built from restored source", "ui/src/main.ts": b"source"}
    write_files(tmp_path, expected)
    commands = []

    def run(argv):
        commands.append(argv)

    assert acceptance.rebuild_frontend(tmp_path, expected, "npm", run) == 1
    assert commands == [
        ["npm", "ci", "--prefix", "ui", "--no-audit", "--no-fund"],
        ["npm", "test", "--prefix", "ui"],
        ["npm", "run", "build", "--prefix", "ui"],
    ]
    assert not (tmp_path / ".git").exists()


@pytest.mark.parametrize("damage", ["missing", "extra", "bytes", "no_snapshot"])
def test_cleanroom_frontend_rejects_incomplete_or_different_builds(tmp_path, damage):
    expected = {"workbench/web/app.js": b"snapshot"}
    write_files(tmp_path, expected)
    if damage == "missing":
        (tmp_path / "workbench/web/app.js").unlink()
    elif damage == "extra":
        write_files(tmp_path, {"workbench/web/unexpected.js": b"extra"})
    elif damage == "bytes":
        write_files(tmp_path, {"workbench/web/app.js": b"different"})
    else:
        expected = {}
    with pytest.raises(AssertionError):
        acceptance.verify_frontend_bundle(tmp_path, expected)


def test_frontend_test_failure_stops_before_build_and_byte_comparison(tmp_path):
    commands = []

    def run(argv):
        commands.append(argv)
        if "test" in argv:
            raise RuntimeError("frontend tests failed")

    with pytest.raises(RuntimeError, match="frontend tests failed"):
        acceptance.rebuild_frontend(tmp_path, {}, "npm", run)
    assert len(commands) == 2
    assert all("build" not in command for command in commands)


def test_lessons_distinguish_browser_evidence_and_current_startup_delivery_boundaries():
    stages = {stage["id"]: stage for stage in builder.read_content()}
    startup = stages["00-environment"]["body"]
    control = stages["08-control-plane"]["body"]
    final = stages["14-acceptance"]["body"]
    assert "`start` 还会要求真实模型配置" not in startup
    assert "没有供应商Key时启动操作台" in control
    assert "SOURCE_READY" in control
    assert "uv run python -m scripts.ci_guided_browser" in final
    assert "reports/learning-docs-guided-browser" in final
    assert "不能把纯函数测试当作整条页面链已通过" in final
    assert all(check_fences(stage["body"]) >= 0 for stage in stages.values())


def test_cleanroom_calls_real_browser_driver_and_copies_its_distinct_evidence(tmp_path):
    destination, reports = tmp_path / "restored", tmp_path / "evidence"
    summary = {
        "passed": True,
        "real_browser": True,
        "actual_incremental_sse": True,
        "first_delta_before_provider_complete": True,
        "unicode_split_replay_dedupe": True,
        "model_mode": "explicit-local-http-fixtures",
    }
    commands = []

    def run(argv):
        commands.append(argv)
        write_files(
            destination,
            {"reports/guided-browser/summary.json": json.dumps(summary).encode()},
        )

    assert (
        acceptance.verify_frontend_browser(destination, "student-python", run, reports) == summary
    )
    assert commands == [["student-python", "-m", "scripts.ci_guided_browser"]]
    assert json.loads((reports / "summary.json").read_text()) == summary


def test_cleanroom_preserves_browser_failure_without_accepting_an_old_success(tmp_path):
    destination = tmp_path / "restored"
    previous, reports = tmp_path / "evidence/previous", tmp_path / "evidence/current"
    write_files(previous, {"summary.json": b'{"passed":true}', "old.png": b"old image"})

    def run(argv):
        write_files(destination, {"reports/guided-browser/workbench.log": b"fixture failure"})
        raise RuntimeError("browser failed")

    with pytest.raises(RuntimeError, match="browser failed"):
        acceptance.verify_frontend_browser(destination, "student-python", run, reports)
    assert (reports / "workbench.log").read_bytes() == b"fixture failure"
    assert not (reports / "summary.json").exists()

    assert not (reports / "old.png").exists()
    assert (previous / "summary.json").read_bytes() == b'{"passed":true}'
    assert (previous / "old.png").read_bytes() == b"old image"


def test_cleanroom_browser_refuses_reusing_an_existing_evidence_directory(tmp_path):
    reports = tmp_path / "evidence"
    write_files(reports, {"summary.json": b'{"passed":true}'})
    commands = []
    with pytest.raises(FileExistsError):
        acceptance.verify_frontend_browser(tmp_path / "student", "python", commands.append, reports)
    assert commands == []
    assert (reports / "summary.json").read_bytes() == b'{"passed":true}'
````
