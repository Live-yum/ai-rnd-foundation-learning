"""Canonical package downloads preserve the pinned upstream lock exactly."""

import re
from zipfile import ZipFile

from workbench.native_environment import prepare_fastapi_registry
from workbench.settings import ROOT


def test_pinned_registry_rewrite_preserves_versions_hashes_and_is_idempotent(tmp_path):
    backend = tmp_path / "backend"
    backend.mkdir()
    with ZipFile(ROOT / "templates/vendor/fastapiadmin.zip") as z:
        for name in ["pyproject.toml", "uv.lock"]:
            source = next(n for n in z.namelist() if n.endswith("backend/" + name))
            (backend / name).write_bytes(z.read(source))
    before = (backend / "uv.lock").read_text(encoding="utf-8")
    prepare_fastapi_registry(backend, tmp_path / "reports")
    after = (backend / "uv.lock").read_text(encoding="utf-8")
    assert "pypi.tuna.tsinghua.edu.cn" not in after
    assert "https://files.pythonhosted.org/packages/" in after
    assert re.findall(r'(?:version|hash) = "[^"]+"', before) == re.findall(
        r'(?:version|hash) = "[^"]+"', after
    )
    receipt = prepare_fastapi_registry(backend, tmp_path / "reports")
    assert all(v["before_sha256"] == v["after_sha256"] for v in receipt.values())
