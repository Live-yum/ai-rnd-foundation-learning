"""Small regression contracts; full Vben verification uses the real pinned application."""

import json
from pathlib import Path

import pytest

from workbench.domain import FieldSpec
from workbench.filesystem import manifest
from workbench.native_environment import copy_source
from workbench.native_vben import (
    adapt_generated_form,
    adapt_generated_schema,
    checked_replacement,
    initialize_vben_boundary,
    prune_generated_import,
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


@pytest.mark.parametrize(
    "identifier,line",
    [
        ("Dayjs", "import type { Dayjs } from 'dayjs';\n"),
        ("getDictOptions", "import { getDictOptions } from '@vben/hooks';\n"),
    ],
)
def test_pruning_never_removes_an_import_still_used(identifier, line):
    assert (
        prune_generated_import(line + "const unrelated = 1;", identifier, line)
        == "const unrelated = 1;"
    )
    used = line + f"const value = {identifier};"
    assert prune_generated_import(used, identifier, line) == used
    with pytest.raises(ValueError, match="Duplicate"):
        prune_generated_import(line + line, identifier, line)


def schema_field(name, component, options=False):
    return (
        "    {\n"
        + f"      fieldName: '{name}',\n      label: '{name}',\n"
        + f"      component: '{component}',\n      componentProps: {{\n"
        + ("        options: [],\n" if options else "        placeholder: 'value',\n")
        + "      },\n    },"
    )


def test_generated_schema_preserves_zero_false_and_all_fields():
    source = (
        schema_field("itemCount", "Input")
        + "\n"
        + schema_field("enabled", "RadioGroup", True)
        + "\n"
        + schema_field("itemCount", "Input")
        + "\n"
        + schema_field("enabled", "Select", True)
    )
    result = adapt_generated_schema(
        source,
        [
            FieldSpec(name="item_count", kind="integer"),
            FieldSpec(name="enabled", kind="boolean"),
        ],
    )
    assert result.count("fieldName:") == source.count("fieldName:") == 4
    assert result.count("component: 'InputNumber'") == 2
    assert result.count("precision: 0") == 2
    assert result.count("component: 'RadioGroup'") == 2
    assert result.count("value: false") == result.count("value: true") == 2
    assert "value: 'false'" not in result
    assert "options: []" in source and "options: []" not in result


@pytest.mark.parametrize("source", ["", schema_field("enabled", "Switch", True)])
def test_unknown_generated_boolean_shape_fails_closed(source):
    with pytest.raises(ValueError, match="Unsupported generated"):
        adapt_generated_schema(source, [FieldSpec(name="enabled", kind="boolean")])


@pytest.mark.parametrize(
    "kind,component",
    [("enum", "Input"), ("enum", "Select"), ("date", "DatePicker"), ("datetime", "DatePicker")],
)
def test_business_scalar_controls_are_not_misclassified_as_boolean(kind, component):
    field = FieldSpec(
        name="category" if kind == "enum" else "due_at",
        kind=kind,
        choices=["a", "b"] if kind == "enum" else [],
    )
    name = "category" if kind == "enum" else "dueAt"
    original = schema_field(name, component, component == "Select")
    assert adapt_generated_schema(original, [field]) == original


def test_business_fields_preserved_while_classic_boolean_guard_still_runs():
    source = schema_field("category", "Input") + "\n" + schema_field("enabled", "Select", True)
    result = adapt_generated_schema(
        source,
        [
            FieldSpec(name="category", kind="enum", choices=["a", "b"]),
            FieldSpec(name="enabled", kind="boolean"),
        ],
    )
    assert schema_field("category", "Input") in result
    assert result.count("component: 'RadioGroup'") == 1
    with pytest.raises(ValueError, match="Unsupported generated boolean control"):
        adapt_generated_schema(
            schema_field("enabled", "Input"), [FieldSpec(name="enabled", kind="boolean")]
        )
