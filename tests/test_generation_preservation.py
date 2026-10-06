"""Generator retries must not remove product databases, credentials or user files."""

import json

import pytest

from workbench.domain import digest
from workbench.generator import PrerequisiteError, generate_basic


def snapshot(root):
    return {
        str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }


def existing(tmp_path, plan):
    product = tmp_path / "product"
    receipt = generate_basic(plan, product)
    (product / ".data").mkdir()
    (product / ".data/product.db").write_bytes(b"user-owned-database-sentinel\x00\xff")
    (product / ".data/deployment.env").write_bytes(b"test-only-local-data")
    (product / "user-notes.txt").write_text("用户保存的内容", encoding="utf-8")
    (product / ".env").write_bytes(b"USER_SETTING=test-only-sentinel\n")
    (product / "user_module.py").write_bytes(b"# user-maintained code\nvalue = 42\n")
    return product, receipt


@pytest.mark.parametrize(
    "failure",
    [
        "missing",
        "malformed",
        "invalid_utf8",
        "null",
        "list",
        "partial",
        "spec",
        "selection",
        "missing_files",
        "empty_files",
        "receipt_directory",
    ],
)
def test_existing_generation_without_matching_receipt_preserves_every_byte(tmp_path, plan, failure):
    product, receipt = existing(tmp_path, plan)
    path = tmp_path / "generation.json"
    if failure in {"missing", "receipt_directory"}:
        path.unlink()
        if failure == "receipt_directory":
            path.mkdir()
    elif failure == "malformed":
        path.write_text("{broken", encoding="utf-8")
    elif failure == "invalid_utf8":
        path.write_bytes(b"\xff\xfeinvalid")
    else:
        value = receipt
        if failure == "null":
            value = None
        elif failure == "list":
            value = []
        elif failure == "partial":
            value = {}
        elif failure == "spec":
            value["spec_digest"] = digest({"other": "design"})
        elif failure == "selection":
            value["selection"]["database"] = "postgresql"
        elif failure == "missing_files":
            value.pop("files")
        elif failure == "empty_files":
            value["files"] = {}
        path.write_text(json.dumps(value), encoding="utf-8")
    before = snapshot(tmp_path)
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(plan, product)
    assert snapshot(tmp_path) == before


def test_changed_design_cannot_reset_existing_product(tmp_path, plan):
    product, _ = existing(tmp_path, plan)
    before = snapshot(tmp_path)
    changed = plan.model_copy(update={"title": plan.title + " changed"})
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(changed, product)
    assert snapshot(tmp_path) == before


def test_matching_generation_is_idempotent_and_preserves_user_data(tmp_path, plan):
    product, receipt = existing(tmp_path, plan)
    before = snapshot(tmp_path)
    assert generate_basic(plan, product) == receipt
    assert snapshot(tmp_path) == before


def test_unknown_existing_empty_directory_is_not_adopted(tmp_path, plan):
    product = tmp_path / "product"
    product.mkdir()
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(plan, product)
    assert product.is_dir() and list(product.iterdir()) == []


def test_existing_non_directory_is_not_removed(tmp_path, plan):
    product = tmp_path / "product"
    product.write_bytes(b"user-file")
    with pytest.raises(PrerequisiteError, match="已保留"):
        generate_basic(plan, product)
    assert product.read_bytes() == b"user-file"


@pytest.mark.parametrize("failure", ["copy", "publish", "receipt"])
def test_interrupted_generation_retries_without_partial_product(
    tmp_path, plan, monkeypatch, failure
):
    import workbench.generator as generator

    product = tmp_path / "product"

    def fail(*args):
        raise OSError(f"{failure} interrupted")

    with monkeypatch.context() as patch:
        if failure == "copy":
            patch.setattr(generator.shutil, "copyfile", fail)
        elif failure == "publish":
            patch.setattr(generator.Path, "rename", fail)
        else:
            write = generator.write_json

            def interrupted(path, value):
                if path == tmp_path / "generation.json":
                    raise OSError("receipt interrupted")
                return write(path, value)

            patch.setattr(generator, "write_json", interrupted)
        with pytest.raises(OSError, match="interrupted"):
            generate_basic(plan, product)
    assert product.exists() == (failure == "receipt")
    assert not list(tmp_path.glob(".generating-*"))
    if product.exists():
        (product / ".data").mkdir()
        (product / ".data/product.db").write_bytes(b"preserve after publication")
        before = snapshot(product)
    receipt = generate_basic(plan, product)
    assert receipt == json.loads((tmp_path / "generation.json").read_text())
    assert not list(tmp_path.glob(".generation-*.pending.json"))
    if failure == "receipt":
        assert snapshot(product) == before
