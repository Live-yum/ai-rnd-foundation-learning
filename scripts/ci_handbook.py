"""Verify construction from the handbook alone, without original source/archive access."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.build_handbook import OUTPUT, ROOT
from scripts.rebuild_from_handbook import restore


def run(argv, directory, env, timeout=900):
    result = subprocess.run(argv, cwd=directory, env=env, timeout=timeout, check=True)
    return result.returncode


def main():
    text = OUTPUT.read_bytes()
    expected = json.loads((ROOT / "templates/vendor/manifest.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="rnd-book-only-") as folder:
        base = Path(folder)
        book = base / OUTPUT.name
        book.write_bytes(text)
        destination = base / "student-project"
        count = restore(book, destination)
        assert not list((destination / "templates/vendor").glob("*.zip"))
        env = dict(os.environ, PYTHONPATH=str(destination), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        # Installation packages may be reused; project imports MUST come from the restored tree.
        run([sys.executable, "-c", "from pathlib import Path; import workbench.store; "
             "assert Path(workbench.store.__file__).resolve().is_relative_to(Path.cwd())"], destination, env)
        run([sys.executable, "-m", "scripts.build_handbook"], destination, env)
        assert (destination / OUTPUT.name).read_bytes() == text
        run([sys.executable, "-m", "scripts.vendor_templates", "--fetch"], destination, env)
        actual = json.loads((destination / "templates/vendor/manifest.json").read_text(encoding="utf-8"))
        for want, got in zip(expected["sources"], actual["sources"], strict=True):
            # ZIP deflate bytes can differ across zlib versions. Source digests verify content.
            for field in ("name", "sha", "source_digest", "files"):
                assert want[field] == got[field], (field, want["name"])
        run([sys.executable, "-m", "pytest", "tests/test_contracts.py", "tests/test_store.py",
             "tests/test_vendor.py", "tests/test_local_only.py", "-q"], destination, env)
        report = {"passed": True, "text_files_restored": count,
                  "original_project_imported": False, "original_archives_copied": False,
                  "third_party_fixed_revisions_rebuilt": len(actual["sources"]),
                  "handbook_sha256": hashlib.sha256(text).hexdigest()}
        (ROOT / "reports").mkdir(exist_ok=True)
        (ROOT / "reports/handbook-clean-room.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
