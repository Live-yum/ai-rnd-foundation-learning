"""Recovery refuses changed source/plan/database and never resets retained state."""

import pytest

from scripts.ci_native_generated import acceptance_spec
from workbench.filesystem import atomic_text
from workbench.generator import PrerequisiteError
from workbench.native_recovery import identity, load, save


def checkpoint(tmp_path):
    source, product = tmp_path / "source", tmp_path / "product"
    atomic_text(source / "app.py", "upstream")
    atomic_text(product / "app.py", "generated")
    plan = acceptance_spec()
    url = "postgresql+psycopg://native:never-store-me@127.0.0.1:5432/test_codegen"
    expected = identity("fastapiadmin", plan, url, source, None)
    path = tmp_path / "recovery.json"
    save(path, expected, product, [{"entity": "device"}], resumable=True, stage="generated")
    return path, expected, product, source, plan, url


def test_recovery_retains_files_targets_and_excludes_credentials(tmp_path):
    path, expected, product, *_ = checkpoint(tmp_path)
    state = load(path, expected, product)
    assert state["targets"] == [{"entity": "device"}]
    assert (product / "app.py").read_text() == "generated"
    assert "never-store-me" not in path.read_text()


@pytest.mark.parametrize("change", ["files", "source", "database", "plan", "unsafe", "missing"])
def test_native_recovery_fail_closed(tmp_path, change):
    path, expected, product, source, plan, url = checkpoint(tmp_path)
    if change == "files":
        atomic_text(product / "app.py", "user edits")
    elif change == "source":
        atomic_text(source / "app.py", "other upstream")
        expected = identity("fastapiadmin", plan, url, source, None)
    elif change == "database":
        expected = identity(
            "fastapiadmin", plan, url.replace("test_codegen", "other_codegen"), source, None
        )
    elif change == "plan":
        expected = {**expected, "spec_digest": "changed"}
    elif change == "unsafe":
        save(path, expected, product, [], resumable=False, stage="native-generation")
    else:
        path.unlink()
    before = (product / "app.py").read_bytes()
    with pytest.raises(PrerequisiteError):
        load(path, expected, product)
    assert (product / "app.py").read_bytes() == before


def test_verified_customization_reuse_requires_unchanged_code(tmp_path):
    from workbench.domain import digest
    from workbench.filesystem import sha, write_json
    from workbench.native_coding import verified_native_customization
    from workbench.native_recovery import NativeIntegrityError

    plan = acceptance_spec()
    product, reports = tmp_path / "product", tmp_path / "reports"
    atomic_text(product / "rule.py", "safe rule")
    assert verified_native_customization(plan, product, reports) is False
    write_json(
        reports / "native-coding.json",
        {
            "passed": True,
            "plop": {"spec_digest": digest(plan.model_dump())},
            "edit": {
                "verified": True,
                "frontend_build": True,
                "frontend_typecheck": True,
                "real_browser": True,
                "after": {"rule.py": sha(product / "rule.py")},
            },
        },
    )
    assert verified_native_customization(plan, product, reports) is True
    atomic_text(product / "rule.py", "external edits")
    with pytest.raises(NativeIntegrityError):
        verified_native_customization(plan, product, reports)
