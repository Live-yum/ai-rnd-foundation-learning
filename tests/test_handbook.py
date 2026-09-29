import subprocess
import sys

from scripts.build_handbook import OUTPUT, render, sources
from scripts.rebuild_from_handbook import extract, restore


def test_document_matches_every_source():
    assert OUTPUT.read_text(encoding="utf-8") == render()
    rows = extract(OUTPUT.read_text(encoding="utf-8"))
    for _, files in sources():
        for name, content in files:
            assert rows[name] == content


def test_reconstruction_is_complete(tmp_path):
    destination = tmp_path / "restored"
    restore(OUTPUT, destination)
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", str(destination / "workbench")], check=True
    )
    result = subprocess.run(
        [sys.executable, "-m", "scripts.build_handbook"],
        cwd=destination,
        text=True,
        capture_output=True,
        check=True,
    )
    assert (destination / OUTPUT.name).read_bytes() == OUTPUT.read_bytes(), result.stdout
