"""Small regression contracts; full Vben verification uses the real pinned application."""

import json
from pathlib import Path

import pytest

from workbench.filesystem import manifest
from workbench.native_environment import copy_source
from workbench.native_vben import (
    adapt_generated_form,
    checked_replacement,
    initialize_vben_boundary,
)
from workbench.tools import run_command


def test_checked_replacement_is_exact_and_preserves_unrelated_source():
    source = "before; old; after;"
    assert checked_replacement(source, "old", "new", 1, "fixture") == "before; new; after;"
    assert source == "before; old; after;"


@pytest.mark.parametrize("source", ["missing", "old old"])
def test_changed_or_ambiguous_upstream_context_fails_closed(source):
    with pytest.raises(ValueError, match="compatibility contract changed"):
        checked_replacement(source, "old", "new", 1, "fixture")


def test_vben_boundary_is_local_and_excluded_from_delivery(tmp_path):
    source = tmp_path / "upstream"
    (source / ".git").mkdir(parents=True)
    (source / ".git/config").write_text("never-copy-upstream-credentials")
    (source / ".env").write_text("API_KEY=never-copy-me")
    (source / "package.json").write_text(json.dumps({"name": "boundary-fixture"}))
    destination = tmp_path / "product"
    copy_source(source, destination)
    before = manifest(destination)
    initialize_vben_boundary(destination)
    assert manifest(destination) == before
    assert not (destination / ".env").exists()
    config = (destination / ".git/config").read_text()
    assert "remote" not in config and "never-copy" not in config
    assert not (destination / ".git/hooks").exists()
    result = run_command(["git", "rev-parse", "--show-toplevel"], destination, 30)
    assert Path(result["log"].strip()).resolve() == destination.resolve()
    with pytest.raises(ValueError, match="fresh source copy"):
        initialize_vben_boundary(destination)


@pytest.mark.parametrize("class_name", ["WbDevice", "WbCategory", "WbAssetItem"])
def test_generated_modal_keeps_precise_dto_and_optional_create_payload(class_name):
    dto = f"Infra{class_name}Api.{class_name}"
    source = (
        "const [Modal, modalApi] = useVbenModal({\n"
        f"const data = modalApi.getData<{dto}>();\n"
        "if (!data || !data.id) return;\n});"
    )
    result = adapt_generated_form(source, class_name)
    assert f"useVbenModal<Partial<{dto}>>(" in result
    assert "modalApi.getData()" in result
    assert "if (!data || !data.id) return;" in result
    assert "getData<" in source
    assert "@ts-ignore" not in result and "any" not in result


def test_generated_modal_contract_drift_is_not_silently_accepted():
    with pytest.raises(ValueError, match="compatibility contract changed"):
        adapt_generated_form("const [Modal, modalApi] = useVbenModal({});", "WbDevice")
