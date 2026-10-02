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
