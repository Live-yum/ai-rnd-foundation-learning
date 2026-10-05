"""Real pinned source/layout regression; all database/runtime execution is stubbed.

This proves source preservation and descriptor admission, not native/live CI success.
"""

import ast
import base64
import builtins
import copy
import hashlib
import importlib.util
import inspect
import json
import os
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from capability_dependency_fixtures import profile_record
from test_ci_native_capability_security import product as baseline_product  # noqa: F401

from scripts import ci_native_capability_source as handoff
from scripts import daytona_capability_profile as base
from scripts import daytona_dependency_build as build
from scripts import daytona_dependency_image as image
from scripts import daytona_native_capability_profile as native
from scripts.ci_native_capability_security import fixed_plan
from scripts.ci_native_generated import acceptance_spec
from workbench import capability_dependencies as admission
from workbench import portable
from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest, pack_source, sha, unpack
from workbench.native_environment import copy_source, prepare_fastapi_registry
from workbench.vendor import VENDOR, unpack_source
from workbench.vendor import inventory as vendor_inventory

EXTRA_DESCRIPTORS = {
    "frontend/app/package.json",
    "frontend/app/pnpm-lock.yaml",
    "frontend/app/src/uni_modules/mp-html/package.json",
    "frontend/docs/package.json",
    "frontend/docs/pnpm-lock.yaml",
}
NAMES = {"pyproject.toml", "uv.lock", "package.json", "pnpm-lock.yaml", "pom.xml"}
POSIX = pytest.mark.skipif(
    not hasattr(os, "O_NOFOLLOW"), reason="Actual POSIX no-follow source copy"
)


def native_record():
    return next(item for item in vendor_inventory() if item["name"] == "fastapiadmin")


def test_real_pinned_archive_contains_all_nine_original_descriptors_and_complete_source():
    record = native_record()
    archive = VENDOR / record["archive"]
    assert record["sha"] == "1cd12c726ad9032c17ef85ce805ce991be60fbdf"
    assert (
        sha(archive)
        == record["archive_sha256"]
        == "015ad88bbfaf2d8a6c861d381150d7c4c77d98a4d3c4874e409126fc943bc505"
    )
    with zipfile.ZipFile(archive) as bundle:
        original = {
            item.filename: hashlib.sha256(bundle.read(item)).hexdigest()
            for item in bundle.infolist()
        }
    assert len(original) == record["files"] == 1136
    assert digest(original) == record["source_digest"]
    roles = build.native_descriptor_roles()
    assert image.native_descriptor_roles() == roles
    assert admission.native_descriptor_roles() == roles
    assert set(roles["auxiliary_source"]) == EXTRA_DESCRIPTORS
    assert {name for name in original if Path(name).name in NAMES} == set(
        roles["runtime"]
    ) | EXTRA_DESCRIPTORS
    assert {key: len(paths) for key, paths in roles.items()} == {
        "runtime": 4,
        "portable_launcher": 2,
        "auxiliary_source": 5,
    }
    assert set(native.DESCRIPTORS) == {name for paths in roles.values() for name in paths}


@pytest.fixture
def real_product(settings, tmp_path, monkeypatch):
    record = native_record()
    source = unpack_source(settings, record)
    original = manifest(source)
    product = tmp_path / "product"
    copy_source(source, product)
    assert manifest(product) == original
    reports = tmp_path / "reports"
    prepare_fastapi_registry(product / "backend", reports)
    # Deterministic generated-source placeholders only. No candidate code executes.
    atomic_text(
        product / "backend/app/plugin/module_rnd/device/controller.py",
        "# generated module fixture\n",
    )
    atomic_text(
        product / "frontend/web/src/views/module_rnd/device/index.vue",
        "<template>fixture</template>\n",
    )
    atomic_text(reports / "business-schema.sql", "-- schema contract fixture only\n")
    atomic_text(reports / "menu-seed.sql", "-- menu contract fixture only\n")
    target = {
        "entity": "device",
        "table": "wb_01234567_device",
        "api": "/rnd/device",
        "list": "/rnd/device/list",
        "route": "/module_rnd/device",
        "permission": "module_rnd:device",
    }

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(
        portable,
        "create_engine",
        lambda *a: SimpleNamespace(connect=Connection, dispose=lambda: None),
    )
    monkeypatch.setattr(
        portable,
        "inspect",
        lambda *a: SimpleNamespace(
            get_columns=lambda table: [
                {"name": name} for name in ("id", "name", "quantity", "active")
            ]
        ),
    )
    portable.build_native_delivery(
        "fastapiadmin", product, reports, acceptance_spec(), [target], "unused-schema-stub"
    )
    assert manifest(source) == original
    return product, source, original


def test_full_real_source_preparation_keeps_auxiliary_bytes_inert_and_bound(real_product, tmp_path):
    product, source, original = real_product
    value = native.product_inputs(product)
    assert set(value["descriptors"]) == set(native.DESCRIPTORS)
    assert len(value["descriptors"]) == 11
    assert {name: sha(product / name) for name in EXTRA_DESCRIPTORS} == {
        name: original[name] for name in EXTRA_DESCRIPTORS
    }
    context = tmp_path / "context"
    context.mkdir()
    native.prepare_context(product, context, value)
    inputs = json.loads((context / "dependency-inputs.json").read_text())
    roles = build.validate_native_descriptor_inputs(inputs)
    assert roles == value["descriptor_roles"]
    assert len(inputs["source_descriptor_bytes"]) == 7
    for name, encoded in inputs["source_descriptor_bytes"].items():
        assert base64.b64decode(encoded, validate=True) == (product / name).read_bytes()
        assert inputs["original_descriptors"][name] == inputs["normalized_descriptors"][name]
    assert all(
        not (context / "product" / name).exists()
        for name in ("backend/app", "frontend/app/src/main.ts", "frontend/docs/docs")
    )
    assert native.product_inputs(product) == value
    assert manifest(source) == original


@POSIX
def test_full_archive_normalization_portable_package_capture_and_strict_admission(
    real_product, tmp_path
):
    product, source, original = real_product
    current = manifest(product)
    artifact = tmp_path / "complete-delivery.zip"
    packaged = pack_source(product, artifact, template="fastapiadmin")
    restored = tmp_path / "clean-restore"
    assert unpack(artifact, restored, template="fastapiadmin") == packaged
    assert manifest(restored) == current
    state = handoff.SourceHandoff(tmp_path / "source-handoff", tmp_path / "source-ready.json")
    state.capture(restored, current, sha(artifact))
    state.complete(
        {
            "generated_runtime_verified": True,
            "portable_restored": {
                "passed": True,
                "fresh_database": True,
                "standalone_launcher": True,
                "archive_round_trip": True,
                "source_archive_sha256": sha(artifact),
            },
        },
        product,
    )
    receipt = handoff.require_handoff(state.product, state.receipt)
    assert receipt["descriptor_roles"] == build.native_descriptor_roles()
    assert receipt["inventory"] == current
    assert manifest(state.product) == current
    assert manifest(source) == original
    record = profile_record(state.product, "fastapiadmin")
    expected = admission.require_dependency_descriptors(
        state.product, fixed_plan(state.product), record
    )
    assert expected["original_descriptors"] == receipt["descriptors"]
    assert len(expected["original_descriptors"]) == 11
    for name in original:
        if name not in {"backend/pyproject.toml", "backend/uv.lock"}:
            assert (state.product / name).read_bytes() == (source / name).read_bytes()


@pytest.fixture
def descriptor_product(baseline_product):  # noqa: F811 - imported pytest fixture
    with zipfile.ZipFile(VENDOR / native_record()["archive"]) as archive:
        for name in native.DESCRIPTORS:
            path = baseline_product / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(
                (native.ROOT / "templates" / name).read_bytes()
                if name.startswith("deployment/")
                else archive.read(name)
            )
    return baseline_product


@pytest.mark.parametrize("name", sorted(EXTRA_DESCRIPTORS))
@pytest.mark.parametrize("mutation", ["missing", "changed", "extra", "replacement"])
def test_all_auxiliary_descriptors_are_enforced_by_unchanged_candidate_hash_gate(
    descriptor_product, name, mutation
):
    product = descriptor_product
    record = profile_record(product, "fastapiadmin")
    plan = fixed_plan(product)
    path = product / name
    if mutation == "missing":
        path.unlink()
    elif mutation == "changed":
        path.write_bytes(path.read_bytes() + b"\n# changed")
    elif mutation == "extra":
        atomic_text(product / "unregistered/package.json", "{}")
    else:
        path.rename(path.with_name("replaced-" + path.name))
    with pytest.raises(admission.CheckFailure):
        admission.require_dependency_descriptors(product, plan, record)


def descriptor_input():
    roles = build.native_descriptor_roles()
    raw = {name: ("inert data for " + name).encode() for paths in roles.values() for name in paths}
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
    return {
        "descriptor_roles": roles,
        "original_descriptors": hashes,
        "normalized_descriptors": dict(hashes),
        "source_descriptor_bytes": {
            name: base64.b64encode(raw[name]).decode("ascii")
            for name in [*roles["portable_launcher"], *roles["auxiliary_source"]]
        },
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-name",
        "extra-name",
        "wrong-role",
        "missing-role",
        "duplicate-role",
        "bytes",
        "missing-bytes",
        "extra-bytes",
        "normalization",
        "noncanonical",
        "invalid-base64",
        "nonascii-base64",
        "noncanonical-padding",
        "byte-budget",
        "total-budget",
    ],
)
def test_collector_rejects_incomplete_or_modified_metadata_before_any_process(
    tmp_path, monkeypatch, mutation
):
    value = descriptor_input()
    name = next(iter(value["source_descriptor_bytes"]))
    if mutation == "missing-name":
        value["original_descriptors"].pop(name)
    elif mutation == "extra-name":
        value["original_descriptors"]["frontend/other/package.json"] = "a" * 64
    elif mutation == "wrong-role":
        value["descriptor_roles"]["runtime"].append(
            value["descriptor_roles"]["auxiliary_source"].pop()
        )
    elif mutation == "missing-role":
        value.pop("descriptor_roles")
    elif mutation == "duplicate-role":
        value["descriptor_roles"]["runtime"].append(name)
    elif mutation == "bytes":
        value["source_descriptor_bytes"][name] = base64.b64encode(b"different valid data").decode()
    elif mutation == "missing-bytes":
        value["source_descriptor_bytes"].pop(name)
    elif mutation == "extra-bytes":
        value["source_descriptor_bytes"]["unknown/uv.lock"] = "YQ=="
    elif mutation == "normalization":
        value["normalized_descriptors"][name] = "b" * 64
    elif mutation == "noncanonical":
        value["source_descriptor_bytes"][name] += "\n"
    elif mutation == "invalid-base64":
        value["source_descriptor_bytes"][name] = "not base64!"
    elif mutation == "nonascii-base64":
        value["source_descriptor_bytes"][name] = "无效编码"
    elif mutation == "noncanonical-padding":
        value["source_descriptor_bytes"][name] = "YR=="
        for key in ("original_descriptors", "normalized_descriptors"):
            value[key][name] = hashlib.sha256(b"a").hexdigest()
    elif mutation == "total-budget":
        monkeypatch.setattr(
            build,
            "SOURCE_DESCRIPTOR_BYTES",
            max(len(base64.b64decode(raw)) for raw in value["source_descriptor_bytes"].values())
            + 1,
        )
    else:
        monkeypatch.setattr(build, "SOURCE_DESCRIPTOR_BYTES", 1)
    inputs, output = tmp_path / "inputs.json", tmp_path / "output.json"
    inputs.write_text(json.dumps(value))
    monkeypatch.setattr(
        build, "run", lambda *a, **kw: pytest.fail("Executed before descriptor data validation")
    )
    with pytest.raises(ValueError):
        build.collect(inputs, output, native=True)
    assert not output.exists()


@pytest.mark.parametrize(
    "mutation",
    [
        None,
        "wrong-role",
        "missing-role",
        "extra-role",
        "missing-descriptor",
        "extra-descriptor",
        "normalized-auxiliary",
        "raw-transport-retained",
    ],
)
def test_sealed_image_manifest_requires_exact_roles_and_all_source_hashes(mutation):
    value = descriptor_input()
    value.pop("source_descriptor_bytes")
    record = {
        **value,
        "roots": image.ROOTS["fastapiadmin"],
        "groups": image.GROUPS["fastapiadmin"],
        "recipe_identity": "a" * 64,
        "platform": {"os": "linux", "architecture": "amd64", "python": "3.14.7"},
        "entries": {},
        "installed_tree_sha256": image.digest({}),
    }
    if mutation == "wrong-role":
        record["descriptor_roles"]["runtime"] = record["descriptor_roles"]["auxiliary_source"]
    elif mutation == "missing-role":
        record.pop("descriptor_roles")
    elif mutation == "extra-role":
        record["descriptor_roles"]["other"] = []
    elif mutation == "missing-descriptor":
        record["original_descriptors"].pop("frontend/docs/package.json")
    elif mutation == "extra-descriptor":
        record["original_descriptors"]["extra/package.json"] = "a" * 64
        record["normalized_descriptors"]["extra/package.json"] = "a" * 64
    elif mutation == "normalized-auxiliary":
        record["normalized_descriptors"]["frontend/docs/package.json"] = "a" * 64
    elif mutation == "raw-transport-retained":
        record["source_descriptor_bytes"] = {}
    document = {"schema": 1, "profiles": {"fastapiadmin": record}}
    if mutation is None:
        assert image.validate_manifest(document, "fastapiadmin") == record
    else:
        with pytest.raises(ValueError):
            image.validate_manifest(document, "fastapiadmin")


@pytest.mark.parametrize("mutation", [None, "missing", "swapped", "added", "hash", "descriptor"])
def test_compact_image_binding_and_candidate_admission_bind_native_roles(monkeypatch, mutation):
    value = descriptor_input()
    compact = {
        "schema": 1,
        "profile": "fastapiadmin",
        "manifest_sha256": "a" * 64,
        "installed_tree_sha256": "b" * 64,
        "original_descriptors": value["original_descriptors"],
        "descriptor_roles": value["descriptor_roles"],
    }
    original = copy.deepcopy(compact)
    if mutation == "missing":
        compact.pop("descriptor_roles")
    elif mutation == "swapped":
        compact["descriptor_roles"]["runtime"], compact["descriptor_roles"]["auxiliary_source"] = (
            compact["descriptor_roles"]["auxiliary_source"],
            compact["descriptor_roles"]["runtime"],
        )
    elif mutation == "added":
        compact["descriptor_roles"]["extra"] = []
    elif mutation == "hash":
        compact["original_descriptors"]["frontend/docs/package.json"] = "changed-not-a-hash"
    elif mutation == "descriptor":
        compact["original_descriptors"]["extra/package.json"] = "a" * 64
    monkeypatch.setattr(base.local, "docker", lambda *a, **k: json.dumps(compact))
    image_id = "sha256:" + "c" * 64
    if mutation is None:
        binding = base.inspect_dependency_manifest(
            image_id, "fastapiadmin", original["original_descriptors"]
        )
        base.validate_dependency_binding(
            binding, image_id, "fastapiadmin", original["original_descriptors"]
        )
        admission.require_dependency_manifest(binding, "fastapiadmin")
    else:
        with pytest.raises(ValueError):
            base.inspect_dependency_manifest(
                image_id, "fastapiadmin", original["original_descriptors"]
            )
        with pytest.raises(ValueError):
            base.validate_dependency_binding(
                {**compact, "image_id": image_id},
                image_id,
                "fastapiadmin",
                original["original_descriptors"],
            )
        with pytest.raises(admission.CheckFailure):
            admission.require_dependency_manifest({**compact, "image_id": image_id}, "fastapiadmin")


def test_no_image_install_execution_or_privilege_surface_expands():
    # Exact reviewed recipe hash proves no added COPY/RUN/network/user/permission operation.
    assert (
        sha(native.ROOT / native.DOCKERFILE)
        == native.REVIEWED_DOCKERFILE_SHA256
        == "1e9aa22679e06236a0c5f5cfbafe5fc2ff7f128f3f8e96aa38e398364e2bf5db"
    )
    assert image.ROOTS["fastapiadmin"] == [
        "/opt/rnd/runtime/fastapiadmin/backend/.venv",
        "/opt/rnd/runtime/fastapiadmin/frontend/node_modules",
        "/opt/rnd/python",
        "/usr/local/bin/node",
        "/opt/rnd/harness/.venv",
        "/opt/rnd/browser",
        "/opt/rnd/browsers",
    ]
    assert image.GROUPS["fastapiadmin"] == {
        "python": ["default-groups"],
        "extras": [],
        "node": ["dependencies", "devDependencies", "optionalDependencies"],
        "harness": {
            "python": ["default-groups"],
            "extras": ["postgres", "daytona"],
            "install_project": False,
        },
    }
    # The metadata collector still has only its two original bounded probe sites;
    # inert source bytes and descriptor roles cannot supply command arguments.
    tree = ast.parse(inspect.getsource(build.collect))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "run"
    ]
    assert len(calls) == 2
    assert all(
        "source_descriptor_bytes" not in ast.unparse(call)
        and "descriptor_roles" not in ast.unparse(call)
        for call in calls
    )


def test_packaged_controller_imports_with_scripts_unavailable(monkeypatch):
    original_import = builtins.__import__

    def without_scripts(name, *args, **kwargs):
        if name == "scripts" or name.startswith("scripts."):
            raise ModuleNotFoundError("scripts is intentionally absent from the workbench wheel")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_scripts)
    spec = importlib.util.spec_from_file_location(
        "packaged_capability_dependencies", admission.__file__
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.native_descriptor_roles() == admission.native_descriptor_roles()
