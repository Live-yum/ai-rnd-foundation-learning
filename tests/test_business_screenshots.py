"""Bounded synthetic-product PNG evidence; no credentials or arbitrary file exports."""

import importlib.util
import struct
import zlib
from pathlib import Path

import pytest


def png():
    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00\xff"))
        + chunk(b"IEND", b"")
    )


def verifier():
    path = Path(__file__).parents[1] / "templates/product/verify_business.py"
    spec = importlib.util.spec_from_file_location("business_screenshot_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entry(**changes):
    return {
        "file": "manager--customers--list.png",
        "role": "manager",
        "entity": "customers",
        "view": "list",
        **changes,
    }


def test_only_listed_bounded_pngs_can_be_exported(tmp_path):
    module = verifier()
    value = png()
    (tmp_path / entry()["file"]).write_bytes(value)
    records = module.validate_screenshots(tmp_path, [entry()])
    assert records[0]["bytes"] == len(value)
    assert len(records[0]["sha256"]) == 64
    assert not any(str(tmp_path) in str(v) for v in records[0].values())


@pytest.mark.parametrize(
    "change",
    [
        {"file": "../secret.png"},
        {"file": "credentials.json"},
        {"role": "../manager"},
        {"entity": "../../private"},
        {"view": "login"},
        {"view": "platform"},
        {"view": ["list"]},
        {"token": "not-allowed"},
    ],
)
def test_manifest_rejects_unknown_views_paths_and_secret_fields(tmp_path, change):
    with pytest.raises(ValueError):
        verifier().validate_screenshots(tmp_path, [entry(**change)])


def test_manifest_rejects_symlink_and_unlisted_sidecar(tmp_path):
    module = verifier()
    target = tmp_path / "real.png"
    target.write_bytes(png())
    try:
        (tmp_path / entry()["file"]).symlink_to(target)
    except OSError:
        pytest.skip("Symlinks not available on this runner")
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])


def test_manifest_rejects_non_png_duplicate_and_unrequested_files(tmp_path):
    module = verifier()
    path = tmp_path / entry()["file"]
    path.write_text("synthetic credential sidecar", encoding="utf-8")
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])
    path.write_bytes(png())
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry(), entry()])
    with pytest.raises(ValueError):
        module.validate_screenshots(None, [entry()])
    (tmp_path / "private.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])


def test_manifest_rejects_limits(tmp_path, monkeypatch):
    module = verifier()
    path = tmp_path / entry()["file"]
    path.write_bytes(png())
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()] * 49)
    monkeypatch.setattr(module, "SCREENSHOT_FILE_BYTES", 7)
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])
    monkeypatch.setattr(module, "SCREENSHOT_FILE_BYTES", 99)
    monkeypatch.setattr(module, "SCREENSHOT_TOTAL_BYTES", 7)
    with pytest.raises(ValueError):
        module.validate_screenshots(tmp_path, [entry()])


def test_png_header_cannot_disguise_text_or_trailing_credentials(tmp_path):
    path = tmp_path / entry()["file"]
    for payload in [b"\x89PNG\r\n\x1a\nnot-an-image", png() + b"private-sidecar"]:
        path.write_bytes(payload)
        with pytest.raises(ValueError):
            verifier().validate_screenshots(tmp_path, [entry()])


def test_requested_screenshot_output_cannot_silently_be_empty(tmp_path):
    assert verifier().validate_screenshots(None, []) == []
    with pytest.raises(ValueError):
        verifier().validate_screenshots(tmp_path, [])
