# tests/test_native_offline.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generation.native.offline`、`workbench.templates`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `plan`（L15–L41）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L16的`{ "title": "Offline tickets", "data_scope": "per_user", "acceptance": ["Create tickets"], …`。
- `sources`（L44–L50）：接收`template`。 调用`vendor.inventory`。 返回路径：L46的`[ {k: row[k] for k in ("slot", "sha", "source_digest")} for row in vendor.inventory() if r…`。
- `forbidden`（L53–L54）：接收`*args`、`**kwargs`。 控制顺序：L54抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fastapi_real_business_sources_without_runtime`（L57–L96）：接收`tmp_path`、`monkeypatch`。 控制顺序：L64断言`receipt["generation_status"] == "partial"`；L65断言`receipt["pending_steps"]`；L66断言`"backend/main.py" not in receipt["generated_files"]`；L67断言`len(receipt["generated_files"]) == 12`；L68遍历`receipt["generated_files"]`；L70断言`path.is_file()`；L71按`path.suffix == ".py"`分支；L74断言`"class TicketsModel" in (root / "model.py").read_text()`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`baseline.parent.mkdir`、`baseline.write_text`、`generate_offline`、`plan`、`sources`、`len`、`path.is_file`、`ast.parse`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_output_is_deterministic_and_never_clobbers`（L100–L110）：接收`tmp_path`、`template`。 控制顺序：L103断言`generate_offline(template, plan(), second, sources(template)) == receipt`；L104遍历`receipt["generated_files"]`；L105断言`(first / name).read_bytes() == (second / name).read_bytes()`；L110断言`marker.read_text() == "USER EDIT"`。 调用`generate_offline`、`plan`、`sources`、`(first / name).read_bytes`、`(second / name).read_bytes`、`marker.write_text`、`pytest.raises`、`marker.read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_is_honest_sql_only_partial`（L113–L125）：接收`tmp_path`、`monkeypatch`。 控制顺序：L117断言`receipt["generation_status"] == "partial"`；L118断言`any("not Java/Vue" in s for s in receipt["pending_steps"])`；L120断言`'CREATE TABLE "wb_tickets"' in sql`；L121断言`'"title" VARCHAR(80) NOT NULL' in sql`；L122断言`'"due" DATE NOT NULL' in sql`；L123断言`not any(p.endswith((".java", ".vue")) for p in receipt["generated_files"])`；L125断言`"java/dal/do.vm" in template_inputs`。 调用`monkeypatch.setattr`、`generate_offline`、`plan`、`sources`、`any`、`(tmp_path / "backend/sql/workbench-business.sql").read_text`、`p.endswith`、`json.loads`、`(tmp_path / "generated/offline-template-inputs.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rejects_unpinned_source_and_tampered_archive`（L128–L141）：接收`tmp_path`、`monkeypatch`。 控制顺序：L141断言`not (tmp_path / "out").exists()`。 调用`sources`、`pytest.raises`、`generate_offline`、`plan`、`vendor.inventory`、`fake.mkdir`、`(fake / "fastapiadmin.zip").write_bytes`、`monkeypatch.setattr`、`(tmp_path / "out").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_symlink_and_colliding_paths_leave_no_outputs`（L144–L153）：接收`tmp_path`。 控制顺序：L152断言`not list(outside.iterdir())`；L153断言`not (out / "generated").exists()`。 调用`outside.mkdir`、`out.mkdir`、`(out / "backend").symlink_to`、`pytest.raises`、`generate_offline`、`plan`、`sources`、`list`、`outside.iterdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reserved_native_fields_are_not_silently_discarded`（L156–L161）：接收`tmp_path`。 控制顺序：L161断言`not list(tmp_path.iterdir())`。 调用`plan`、`pytest.raises`、`generate_offline`、`sources`、`list`、`tmp_path.iterdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_and_traversal_targets_rejected`（L167–L170）：接收`tmp_path`、`name`。 控制顺序：L170断言`not list(tmp_path.iterdir())`。 调用`pytest.raises`、`_write_new`、`list`、`tmp_path.iterdir`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_casefold_existing_path_conflict_is_preflighted`（L173–L178）：接收`tmp_path`。 控制顺序：L177断言`not (tmp_path / "generated").exists()`；L178断言`not list((tmp_path / "BACKEND").iterdir())`。 调用`(tmp_path / "BACKEND").mkdir`、`pytest.raises`、`generate_offline`、`plan`、`sources`、`(tmp_path / "generated").exists`、`list`、`(tmp_path / "BACKEND").iterdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_junction_is_rejected`（L181–L187）：接收`tmp_path`、`monkeypatch`。 控制顺序：L187断言`not (tmp_path / "generated").exists()`。 调用`(tmp_path / "backend").mkdir`、`monkeypatch.setattr`、`original`、`pytest.raises`、`generate_offline`、`plan`、`sources`、`(tmp_path / "generated").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_offline.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L187。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8225`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_offline.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "17cae9101d8c9263abc1b0057e51f5a68100d3bf8d9864bb837135f5ef280fd3"} -->
````python
# tests/test_native_offline.py
"""Source-only native generation must be useful without executing upstream code."""

import ast
import json
import socket
import subprocess
from pathlib import Path

import pytest

from workbench.generation.native.offline import _write_new, generate_offline
from workbench.templates import vendor


def plan():
    return {
        "title": "Offline tickets",
        "data_scope": "per_user",
        "acceptance": ["Create tickets"],
        "entities": [
            {
                "name": "tickets",
                "description": "Ticket ' \" {danger()} </script>",
                "fields": [
                    {
                        "name": "title",
                        "kind": "text",
                        "label": "Title ' \" {danger()} </script>",
                        "min_length": 2,
                        "max_length": 80,
                        "searchable": True,
                    },
                    {"name": "priority", "kind": "integer", "minimum": 1, "maximum": 10},
                    {"name": "done", "kind": "boolean"},
                    {"name": "due", "kind": "date", "date_range": True},
                    {"name": "updated", "kind": "datetime", "required": False},
                    {"name": "stage", "kind": "enum", "choices": ["open", "closed"]},
                ],
            }
        ],
    }


def sources(template):
    # Exact immutable metadata supplied by prepare_sources, no mutable templates.
    return [
        {k: row[k] for k in ("slot", "sha", "source_digest")}
        for row in vendor.inventory()
        if row["template"] == template
    ]


def forbidden(*args, **kwargs):
    raise AssertionError("Offline generation attempted a process/network operation")


def test_fastapi_real_business_sources_without_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    baseline = tmp_path / "backend" / "main.py"
    baseline.parent.mkdir()
    baseline.write_text("raise RuntimeError('upstream must not execute')\n")
    receipt = generate_offline("fastapiadmin", plan(), tmp_path, sources("fastapiadmin"))
    assert receipt["generation_status"] == "partial"
    assert receipt["pending_steps"]
    assert "backend/main.py" not in receipt["generated_files"]
    assert len(receipt["generated_files"]) == 12
    for name in receipt["generated_files"]:
        path = tmp_path / name
        assert path.is_file()
        if path.suffix == ".py":
            ast.parse(path.read_text())
    root = tmp_path / "backend/app/plugin/module_rnd/tickets"
    assert "class TicketsModel" in (root / "model.py").read_text()
    assert "String(80)" in (root / "model.py").read_text()
    assert "TicketsRouter" in (root / "controller.py").read_text()
    schema = ast.parse((root / "schema.py").read_text())
    create = next(
        node
        for node in schema.body
        if isinstance(node, ast.ClassDef) and node.name == "TicketsCreateSchema"
    )
    fields = {node.target.id: node for node in create.body if isinstance(node, ast.AnnAssign)}
    for name in ("title", "priority", "done", "due", "stage"):
        default = next(k.value for k in fields[name].value.keywords if k.arg == "default")
        assert isinstance(default, ast.Constant) and default.value is Ellipsis
    assert ast.unparse(fields["stage"].annotation) == "Literal['open', 'closed']"
    title_args = {k.arg: ast.literal_eval(k.value) for k in fields["title"].value.keywords}
    assert title_args["max_length"] == 80
    assert title_args["description"] == plan()["entities"][0]["fields"][0]["label"]
    api_source = (tmp_path / "frontend/web/src/api/module_rnd/tickets.ts").read_text()
    assert "/rnd/tickets" in api_source
    assert "//rnd" not in api_source
    assert (tmp_path / "frontend/web/src/views/module_rnd/tickets/index.vue").is_file()
    stored = json.loads((tmp_path / "generated/business-schema.json").read_text())
    assert stored["entities"][0]["description"] == plan()["entities"][0]["description"]


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_output_is_deterministic_and_never_clobbers(tmp_path, template):
    first, second = tmp_path / "first", tmp_path / "second"
    receipt = generate_offline(template, plan(), first, sources(template))
    assert generate_offline(template, plan(), second, sources(template)) == receipt
    for name in receipt["generated_files"]:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    marker = first / receipt["generated_files"][0]
    marker.write_text("USER EDIT")
    with pytest.raises(FileExistsError):
        generate_offline(template, plan(), first, sources(template))
    assert marker.read_text() == "USER EDIT"


def test_yudao_is_honest_sql_only_partial(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    receipt = generate_offline("yudao-vben", plan(), tmp_path, sources("yudao-vben"))
    assert receipt["generation_status"] == "partial"
    assert any("not Java/Vue" in s for s in receipt["pending_steps"])
    sql = (tmp_path / "backend/sql/workbench-business.sql").read_text()
    assert 'CREATE TABLE "wb_tickets"' in sql
    assert '"title" VARCHAR(80) NOT NULL' in sql
    assert '"due" DATE NOT NULL' in sql
    assert not any(p.endswith((".java", ".vue")) for p in receipt["generated_files"])
    template_inputs = json.loads((tmp_path / "generated/offline-template-inputs.json").read_text())
    assert "java/dal/do.vm" in template_inputs


def test_rejects_unpinned_source_and_tampered_archive(tmp_path, monkeypatch):
    bad = sources("fastapiadmin")
    bad[0]["sha"] = "bad"
    with pytest.raises(ValueError, match="pinned"):
        generate_offline("fastapiadmin", plan(), tmp_path / "out", bad)
    rows = vendor.inventory()
    fake = tmp_path / "vendor"
    fake.mkdir()
    (fake / "fastapiadmin.zip").write_bytes(b"not the pinned archive")
    monkeypatch.setattr(vendor, "inventory", lambda: rows)
    monkeypatch.setattr(vendor, "VENDOR", fake)
    with pytest.raises(ValueError, match="checksum"):
        generate_offline("fastapiadmin", plan(), tmp_path / "out", sources("fastapiadmin"))
    assert not (tmp_path / "out").exists()


def test_symlink_and_colliding_paths_leave_no_outputs(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    out = tmp_path / "out"
    out.mkdir()
    (out / "backend").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="符号链接|Symlink"):
        generate_offline("fastapiadmin", plan(), out, sources("fastapiadmin"))
    assert not list(outside.iterdir())
    assert not (out / "generated").exists()


def test_reserved_native_fields_are_not_silently_discarded(tmp_path):
    value = plan()
    value["entities"][0]["fields"][0]["name"] = "created_id"
    with pytest.raises(ValueError, match="collision"):
        generate_offline("fastapiadmin", value, tmp_path, sources("fastapiadmin"))
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "name", ["C:/escape.py", "../escape.py", "folder:stream/file.py", "a/../../escape.py"]
)
def test_windows_and_traversal_targets_rejected(tmp_path, name):
    with pytest.raises(ValueError):
        _write_new(tmp_path, {name: "unsafe"})
    assert not list(tmp_path.iterdir())


def test_casefold_existing_path_conflict_is_preflighted(tmp_path):
    (tmp_path / "BACKEND").mkdir()
    with pytest.raises(FileExistsError, match="Case-insensitive"):
        generate_offline("fastapiadmin", plan(), tmp_path, sources("fastapiadmin"))
    assert not (tmp_path / "generated").exists()
    assert not list((tmp_path / "BACKEND").iterdir())


def test_windows_junction_is_rejected(tmp_path, monkeypatch):
    (tmp_path / "backend").mkdir()
    original = Path.is_junction
    monkeypatch.setattr(Path, "is_junction", lambda self: self.name == "backend" or original(self))
    with pytest.raises(ValueError, match="junction"):
        generate_offline("fastapiadmin", plan(), tmp_path, sources("fastapiadmin"))
    assert not (tmp_path / "generated").exists()
````
