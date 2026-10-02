# tests/test_native_archive_limits.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `archive`（L15–L23）：接收`rows`、`compressed`。 控制顺序：L20遍历`rows`。 调用`io.BytesIO`、`zipfile.ZipFile`、`z.writestr`、`output.seek`。 返回路径：L23的`output`。
- `test_registered_template_limits_are_bounded_and_generic_is_unchanged`（L30–L34）：接收`template`、`limit`。 控制顺序：L31断言`filesystem.archive_entry_limit(template) == limit`；L32断言`filesystem.ARCHIVE_MAX_BYTES == 200_000_000`；L33断言`filesystem.ARCHIVE_MAX_FILE_BYTES == 32_000_000`；L34断言`filesystem.ARCHIVE_MAX_RATIO == 200`。 调用`filesystem.archive_entry_limit`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_archive_template_cannot_select_a_larger_budget`（L37–L43）：接收`tmp_path`。 调用`pytest.raises`、`unpack`、`archive`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entry_limit_rejects_before_any_write`（L49–L56）：接收`tmp_path`、`template`、`count`。 控制顺序：L56断言`not (tmp_path / "out").exists()`。 调用`pytest.raises`、`unpack`、`archive`、`range`、`(tmp_path / "out").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_preserves_expanded_byte_budget_without_allocating_a_bomb`（L59–L65）：接收`tmp_path`。 控制顺序：L65断言`not (tmp_path / "out").exists()`。 调用`bytearray`、`archive([("source.py", "x")]).getvalue`、`archive`、`data.index`、`struct.pack_into`、`pytest.raises`、`unpack`、`io.BytesIO`、`(tmp_path / "out").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compressed_archive_budget_includes_headers`（L68–L73）：接收`tmp_path`、`monkeypatch`。 控制顺序：L73断言`not (tmp_path / "out").exists()`。 调用`archive`、`monkeypatch.setattr`、`len`、`data.getvalue`、`pytest.raises`、`unpack`、`(tmp_path / "out").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_preserves_per_file_source_budget`（L76–L80）：接收`tmp_path`、`monkeypatch`。 控制顺序：L80断言`not (tmp_path / "out").exists()`。 调用`monkeypatch.setattr`、`pytest.raises`、`unpack`、`archive`、`(tmp_path / "out").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compression_ratio_is_rejected_before_extraction`（L84–L91）：接收`tmp_path`、`template`。 控制顺序：L91断言`not (tmp_path / "out").exists()`。 调用`pytest.raises`、`unpack`、`archive`、`(tmp_path / "out").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_paths_and_secrets_are_preflighted_before_first_write`（L98–L105）：接收`tmp_path`、`name`、`template`。 控制顺序：L105断言`not (tmp_path / "out").exists()`。 调用`pytest.raises`、`unpack`、`archive`、`(tmp_path / "out").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_symlinks_and_case_collisions_remain_rejected`（L109–L115）：接收`tmp_path`、`template`。 控制顺序：L112遍历`(archive([(link, "target")]), archive([("a.py", "a"), ("A.py", "b…`；L115断言`not (tmp_path / "out").exists()`。 调用`zipfile.ZipInfo`、`archive`、`pytest.raises`、`unpack`、`(tmp_path / "out").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_producer_and_consumer_share_policy_and_exclude_runtime_files`（L118–L133）：接收`tmp_path`。 控制顺序：L122遍历`[".git", "node_modules", "target", "dist", "logs", ".deployment"]`；L129断言`packed == restored`；L130断言`packed["entry_count"] == 1`；L131断言`filesystem.manifest(source) == filesystem.manifest(tmp_path / "restored")`；L132断言`inspect_archive(target, tmp_path / "unused", template="yudao-vben") == packed`；L133断言`not (tmp_path / "unused").exists()`。 调用`source.mkdir`、`(source / "app.py").write_text`、`(source / name).mkdir`、`(source / name / "excluded.txt").write_text`、`(source / ".env").write_text`、`pack_source`、`unpack`、`filesystem.manifest`、`inspect_archive`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_producer_leaves_no_downloadable_partial_package`（L136–L145）：接收`tmp_path`、`monkeypatch`。 控制顺序：L144断言`not target.exists()`；L145断言`not target.with_suffix(".zip.tmp").exists()`。 调用`source.mkdir`、`(source / "app.py").write_text`、`monkeypatch.setattr`、`pytest.raises`、`pack_source`、`target.exists`、`target.with_suffix(".zip.tmp").exists`、`target.with_suffix`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_native_sources_plus_generated_files_restore_at_13594_entries`（L148–L183）：接收`tmp_path`。 源码说明：Real pinned source bytes, plus 74 explicitly synthetic generated test files. The failed product's saved source manifest had exactly 13,594 entries. Its private ZIP was not retained, so this reproduces。 控制顺序：L159遍历`[ ("yudao-backend.zip", "backend"), ("yudao-frontend.zip", "front…`；L164遍历`source.infolist()`；L165断言`not item.is_dir()`；L168断言`count == 13520`；L169遍历`range(13594 - count)`；L177断言`report["entry_count"] == 13594`；L178断言`report["entry_limit"] == 25000`；L179断言`report["uncompressed_bytes"] < 200_000_000`。后续分支沿下方源码相同行号继续阅读。 调用`zipfile.ZipFile`、`source.infolist`、`item.is_dir`、`out.writestr`、`source.read`、`range`、`pytest.raises`、`unpack`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pack_source_refuses_output_inside_source_tree`（L186–L189）：接收`tmp_path`。 控制顺序：L189断言`not (tmp_path / "delivery.zip").exists()`。 调用`pytest.raises`、`pack_source`、`(tmp_path / "delivery.zip").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database`（L193–L273）：接收`tmp_path`、`monkeypatch`、`fault`。 源码说明：Real ZIP/file checks with explicit fake database/process, never runtime proof.。 控制顺序：L255按`fault`分支；L258断言`execution == ["pack", "unpack"]`；L259断言`not (tmp_path / "reports/portable-start.json").exists()`；L262断言`report["archive_round_trip"] is True`；L263断言`report["archive"]["entry_limit"] == 25000`；L264断言`report["archive"]["entry_count"] == 2`；L265断言`json.loads((tmp_path / "reports/portable-start.json").read_text(encoding="utf-8"))[ "…`；L271断言`execution == ["pack", "unpack", "start"]`。后续分支沿下方源码相同行号继续阅读。 调用`source.mkdir`、`(source / "start.py").write_text`、`(source / "app.py").write_text`、`filesystem.manifest`、`monkeypatch.setattr`、`Connection`、`pytest.raises`、`portable.verify_native_delivery`、`(tmp_path / "reports/portable-start.json").exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database.Connection`（L208–L216）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database.Connection.__enter__`（L209–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L210的`self`。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database.Connection.__exit__`（L212–L213）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database.Connection.execute`（L215–L216）：接收`statement`。 调用`database_operations.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database.pack`（L221–L228）：接收`*args`、`**kwargs`。 控制顺序：L222断言`kwargs == {"template": "yudao-vben"}`；L225按`fault == "archive_changed"`分支。 调用`original_pack`、`execution.append`、`args[1].open`、`stream.write`。 返回路径：L228的`result`。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database.restore`（L230–L236）：接收`*args`、`**kwargs`。先验证所有源码块与目标路径，再向空目录写入；这一步本身不执行任何写出的项目代码。 控制顺序：L231断言`kwargs == {"template": "yudao-vben"}`；L234按`fault == "restored_source_changed"`分支。 调用`original_unpack`、`execution.append`、`(args[1] / "app.py").write_text`。 返回路径：L236的`result`。
- `test_independent_native_verification_consumes_zip_before_start_and_cleans_database.run`（L238–L249）：接收`command`、`cwd`、`timeout`、`env`、`**kwargs`。 控制顺序：L239断言`execution == ["pack", "unpack"]`；L240断言`filesystem.manifest(cwd) == before`；L241断言`cwd != source`；L242断言`"restore_" in env["NATIVE_DELIVERY_DATABASE_URL"]`；L243断言`env["NATIVE_DELIVERY_DATABASE_URL"].endswith("_codegen")`。 调用`filesystem.manifest`、`env["NATIVE_DELIVERY_DATABASE_URL"].endswith`、`execution.append`、`filesystem.write_json`。 返回路径：L249的`{"log": "Explicit unit process fake"}`。

</details>

**创建路径：** `tests/test_native_archive_limits.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L273。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11395`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_archive_limits.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2fc82afb6210dbdebe8c707e00d64d7d37be82efb8747570aaf7934362719b36"} -->
````python
# tests/test_native_archive_limits.py
"""Source-only ZIP boundaries; no model, native runtime or approval substitutes."""

import io
import stat
import struct
import zipfile

import pytest

from workbench import filesystem
from workbench.filesystem import inspect_archive, pack_source, unpack
from workbench.settings import ROOT


def archive(rows, *, compressed=False):
    output = io.BytesIO()
    with zipfile.ZipFile(
        output, "w", zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
    ) as z:
        for name, data in rows:
            z.writestr(name, data)
    output.seek(0)
    return output


@pytest.mark.parametrize(
    "template,limit",
    [(None, 10000), ("python-basic", 10000), ("fastapiadmin", 10000), ("yudao-vben", 25000)],
)
def test_registered_template_limits_are_bounded_and_generic_is_unchanged(template, limit):
    assert filesystem.archive_entry_limit(template) == limit
    assert filesystem.ARCHIVE_MAX_BYTES == 200_000_000
    assert filesystem.ARCHIVE_MAX_FILE_BYTES == 32_000_000
    assert filesystem.ARCHIVE_MAX_RATIO == 200


def test_unknown_archive_template_cannot_select_a_larger_budget(tmp_path):
    with pytest.raises(ValueError, match="未知"):
        unpack(
            archive([("template.json", '{"template":"yudao-vben"}')]),
            tmp_path / "out",
            template="untrusted",
        )


@pytest.mark.parametrize(
    "template,count", [(None, 10001), ("fastapiadmin", 10001), ("yudao-vben", 25001)]
)
def test_entry_limit_rejects_before_any_write(tmp_path, template, count):
    with pytest.raises(ValueError, match=rf"条目数量.*{count}"):
        unpack(
            archive((f"source/{i}.py", "") for i in range(count)),
            tmp_path / "out",
            template=template,
        )
    assert not (tmp_path / "out").exists()


def test_native_preserves_expanded_byte_budget_without_allocating_a_bomb(tmp_path):
    data = bytearray(archive([("source.py", "x")]).getvalue())
    central = data.index(b"PK\x01\x02")
    struct.pack_into("<I", data, central + 24, 200_000_001)
    with pytest.raises(ValueError, match="解压字节数.*200000001"):
        unpack(io.BytesIO(data), tmp_path / "out", template="yudao-vben")
    assert not (tmp_path / "out").exists()


def test_compressed_archive_budget_includes_headers(tmp_path, monkeypatch):
    data = archive([("source.py", "x")])
    monkeypatch.setattr(filesystem, "ARCHIVE_MAX_BYTES", len(data.getvalue()) - 1)
    with pytest.raises(ValueError, match="压缩包文件字节数"):
        unpack(data, tmp_path / "out", template="yudao-vben")
    assert not (tmp_path / "out").exists()


def test_native_preserves_per_file_source_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(filesystem, "ARCHIVE_MAX_FILE_BYTES", 64)
    with pytest.raises(ValueError, match="单文件"):
        unpack(archive([("source.py", "x" * 65)]), tmp_path / "out", template="yudao-vben")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("template", [None, "yudao-vben"])
def test_compression_ratio_is_rejected_before_extraction(tmp_path, template):
    with pytest.raises(ValueError, match="压缩比"):
        unpack(
            archive([("source.py", b"0" * 1_000_000)], compressed=True),
            tmp_path / "out",
            template=template,
        )
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    "name", ["../escape", "/absolute", "C:/escape", "..\\escape", ".env", "config/secret.key"]
)
@pytest.mark.parametrize("template", [None, "yudao-vben"])
def test_all_paths_and_secrets_are_preflighted_before_first_write(tmp_path, name, template):
    with pytest.raises(ValueError):
        unpack(
            archive([("first-good.py", "safe"), (name, "synthetic")]),
            tmp_path / "out",
            template=template,
        )
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("template", [None, "yudao-vben"])
def test_symlinks_and_case_collisions_remain_rejected(tmp_path, template):
    link = zipfile.ZipInfo("linked")
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    for data in (archive([(link, "target")]), archive([("a.py", "a"), ("A.py", "b")])):
        with pytest.raises(ValueError, match="重复路径或符号链接"):
            unpack(data, tmp_path / "out", template=template)
        assert not (tmp_path / "out").exists()


def test_producer_and_consumer_share_policy_and_exclude_runtime_files(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "app.py").write_text("print('source')\n", encoding="utf-8")
    for name in [".git", "node_modules", "target", "dist", "logs", ".deployment"]:
        (source / name).mkdir()
        (source / name / "excluded.txt").write_text("synthetic excluded bytes", encoding="utf-8")
    (source / ".env").write_text("synthetic credential", encoding="utf-8")
    target = tmp_path / "delivery.zip"
    packed = pack_source(source, target, template="yudao-vben")
    restored = unpack(target, tmp_path / "restored", template="yudao-vben")
    assert packed == restored
    assert packed["entry_count"] == 1
    assert filesystem.manifest(source) == filesystem.manifest(tmp_path / "restored")
    assert inspect_archive(target, tmp_path / "unused", template="yudao-vben") == packed
    assert not (tmp_path / "unused").exists()


def test_failed_producer_leaves_no_downloadable_partial_package(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "app.py").write_text("x=1\n", encoding="utf-8")
    target = tmp_path / "delivery.zip"
    monkeypatch.setattr(filesystem, "archive_entry_limit", lambda template: 0)
    with pytest.raises(ValueError, match="条目数量"):
        pack_source(source, target, template="yudao-vben")
    assert not target.exists()
    assert not target.with_suffix(".zip.tmp").exists()


def test_pinned_native_sources_plus_generated_files_restore_at_13594_entries(tmp_path):
    """Real pinned source bytes, plus 74 explicitly synthetic generated test files.

    The failed product's saved source manifest had exactly 13,594 entries. Its
    private ZIP was not retained, so this reproduces that boundary honestly
    without pretending to possess the original generated bytes or runtime proof.
    Native Actions separately round-trip and execute the exact approved Plan.
    """
    target = tmp_path / "native-source.zip"
    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for filename, prefix in [
            ("yudao-backend.zip", "backend"),
            ("yudao-frontend.zip", "frontend-product"),
        ]:
            with zipfile.ZipFile(ROOT / "templates/vendor" / filename) as source:
                for item in source.infolist():
                    assert not item.is_dir()
                    out.writestr(prefix + "/" + item.filename, source.read(item))
                    count += 1
        assert count == 13520
        for index in range(13594 - count):
            out.writestr(
                f"synthetic-generated/source_{index}.py",
                f"# Explicit test-only generated source {index}\n",
            )
    with pytest.raises(ValueError, match="条目数量.*13594.*10000"):
        unpack(target, tmp_path / "generic")
    report = unpack(target, tmp_path / "native", template="yudao-vben")
    assert report["entry_count"] == 13594
    assert report["entry_limit"] == 25000
    assert report["uncompressed_bytes"] < 200_000_000
    assert len(list((tmp_path / "native").rglob("*.*"))) > 10000
    with zipfile.ZipFile(target) as source:
        for item in source.infolist():
            assert (tmp_path / "native" / item.filename).read_bytes() == source.read(item)


def test_pack_source_refuses_output_inside_source_tree(tmp_path):
    with pytest.raises(ValueError, match="源码目录"):
        pack_source(tmp_path, tmp_path / "delivery.zip", template="yudao-vben")
    assert not (tmp_path / "delivery.zip").exists()


@pytest.mark.parametrize("fault", [None, "archive_changed", "restored_source_changed"])
def test_independent_native_verification_consumes_zip_before_start_and_cleans_database(
    tmp_path, monkeypatch, fault
):
    """Real ZIP/file checks with explicit fake database/process, never runtime proof."""
    import json

    from workbench import portable, tools

    source = tmp_path / "source"
    source.mkdir()
    (source / "start.py").write_text("# test-only launcher\n", encoding="utf-8")
    (source / "app.py").write_text("# immutable test source\n", encoding="utf-8")
    before = filesystem.manifest(source)
    database_operations, execution = [], []

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, statement):
            database_operations.append(statement)

    monkeypatch.setattr(portable.psycopg, "connect", lambda *a, **kw: Connection())
    original_pack, original_unpack = filesystem.pack_source, filesystem.unpack

    def pack(*args, **kwargs):
        assert kwargs == {"template": "yudao-vben"}
        result = original_pack(*args, **kwargs)
        execution.append("pack")
        if fault == "archive_changed":
            with args[1].open("ab") as stream:
                stream.write(b"changed archive bytes")
        return result

    def restore(*args, **kwargs):
        assert kwargs == {"template": "yudao-vben"}
        result = original_unpack(*args, **kwargs)
        execution.append("unpack")
        if fault == "restored_source_changed":
            (args[1] / "app.py").write_text("# changed test bytes\n", encoding="utf-8")
        return result

    def run(command, cwd, timeout, env, **kwargs):
        assert execution == ["pack", "unpack"]
        assert filesystem.manifest(cwd) == before
        assert cwd != source
        assert "restore_" in env["NATIVE_DELIVERY_DATABASE_URL"]
        assert env["NATIVE_DELIVERY_DATABASE_URL"].endswith("_codegen")
        execution.append("start")
        filesystem.write_json(
            cwd / ".deployment/reports/portable-start.json",
            {"passed": True, "frontend_started": True, "restart": True},
        )
        return {"log": "Explicit unit process fake"}

    monkeypatch.setattr(filesystem, "pack_source", pack)
    monkeypatch.setattr(filesystem, "unpack", restore)
    monkeypatch.setattr(tools, "run_command", run)
    args = (source, "postgresql+psycopg://test:test@127.0.0.1/native_codegen", tmp_path / "reports")
    if fault:
        with pytest.raises(ValueError, match="ZIP"):
            portable.verify_native_delivery(*args, template="yudao-vben")
        assert execution == ["pack", "unpack"]
        assert not (tmp_path / "reports/portable-start.json").exists()
    else:
        report = portable.verify_native_delivery(*args, template="yudao-vben")
        assert report["archive_round_trip"] is True
        assert report["archive"]["entry_limit"] == 25000
        assert report["archive"]["entry_count"] == 2
        assert (
            json.loads((tmp_path / "reports/portable-start.json").read_text(encoding="utf-8"))[
                "archive"
            ]
            == report["archive"]
        )
        assert execution == ["pack", "unpack", "start"]
    assert len(database_operations) == 2  # create only the owned new DB, then drop it
    assert filesystem.manifest(source) == before
````
