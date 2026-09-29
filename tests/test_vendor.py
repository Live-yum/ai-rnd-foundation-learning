import hashlib
import zipfile

import pytest

from workbench.domain import digest
from workbench.filesystem import manifest
from workbench.vendor import VENDOR, inventory, unpack_source


def test_an_ordinary_checkout_contains_actual_native_code_archives():
    rows = inventory()
    assert {r["name"] for r in rows} == {"fastapiadmin", "yudao-backend", "yudao-frontend"}
    for item in rows:
        archive = VENDOR / item["archive"]
        assert (
            archive.is_file()
            and hashlib.sha256(archive.read_bytes()).hexdigest() == item["archive_sha256"]
        )
        with zipfile.ZipFile(archive) as z:
            assert "LICENSE" in z.namelist()
            assert len(z.namelist()) == item["files"]
            assert not any(
                n.endswith((".ttf", ".otf", ".woff", ".woff2", ".pem", ".key"))
                for n in z.namelist()
            )
            assert any(n.endswith((".py", ".java", ".vue")) for n in z.namelist())


def test_offline_unpack_is_reusable_and_detects_source_changes(settings):
    item = next(r for r in inventory() if r["name"] == "fastapiadmin")
    dest = unpack_source(settings, item)
    assert digest(manifest(dest)) == item["source_digest"]
    assert unpack_source(settings, item) == dest
    (dest / "LICENSE").write_text("changed")
    with pytest.raises(ValueError, match="修改"):
        unpack_source(settings, item)
