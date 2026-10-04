"""Locked dependency build contracts; never execute source hooks in these tests."""

import io
import json
import tarfile
import tomllib
import zipfile

import pytest

from scripts import daytona_dependency_build as build
from scripts.daytona_native_capability_profile import ROOT


def test_reviewed_bundled_native_graph_includes_required_sdists_and_exact_default_groups():
    with zipfile.ZipFile(ROOT / "templates/vendor/fastapiadmin.zip") as archive:
        project = build.normalize(archive.read("backend/pyproject.toml"))
        lock = build.normalize(archive.read("backend/uv.lock"))
        parsed = build.validate_python(project, lock)
        build.validate_node(
            archive.read("frontend/web/package.json"),
            archive.read("frontend/web/pnpm-lock.yaml"),
        )
    assert "sqlglot[rs]==27.8.0" in tomllib.loads(project.decode())["project"]["dependencies"]
    assert tomllib.loads(project.decode())["tool"]["uv"]["default-groups"] == ["dev"]
    spec = json.loads((ROOT / "scripts/daytona_dependency_build.lock.json").read_bytes())
    packages = {row["name"]: row for row in parsed["package"]}
    for record in spec["sdists"]:
        assert packages[record["name"]]["version"] == record["version"]
        assert packages[record["name"]]["sdist"]["hash"] == "sha256:" + record["sha256"]
        assert packages[record["name"]]["sdist"]["url"] == record["url"]
    assert {row["name"] for row in spec["sdists"]} == {
        "crcmod",
        "esdk-obs-python",
        "sqlglotrs",
    }


@pytest.mark.parametrize(
    "extra",
    [
        '[build-system]\nrequires=["untrusted"]\nbuild-backend="payload"\n',
        '[tool.uv.sources]\nfoo={path="../workspace"}\n',
        '[tool.uv]\nconfig-settings={hook="payload"}\n',
    ],
)
def test_candidate_build_backends_and_local_configuration_rejected(extra):
    with pytest.raises(ValueError, match="backend|configuration"):
        build.validate_python(
            ('[project]\nname="fixture"\nversion="1"\n' + extra).encode(),
            b"version=1\n",
        )


@pytest.mark.parametrize(
    "source",
    ['{path="../local"}', '{git="https://example.test/repo"}', '{virtual="../other"}'],
)
def test_local_and_workspace_lock_packages_rejected(source):
    with pytest.raises(ValueError, match="hashed registry"):
        build.validate_python(
            b'[project]\nname="fixture"\nversion="1"\n',
            ('[[package]]\nname="evil"\nsource=' + source + "\n").encode(),
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://pypi.org/simple",
        "https://name:secret@pypi.org/simple",
        "https://pypi.org/simple?token=x",
        "https://evil.test/simple",
    ],
)
def test_registry_authentication_and_unreviewed_hosts_rejected(url):
    with pytest.raises(ValueError, match="official registry"):
        build.public_url(url, {"pypi.org"})


@pytest.mark.parametrize(
    "package,lock",
    [
        ({"dependencies": {"evil": "file:../payload"}}, "lockfileVersion: '9.0'"),
        (
            {"dependencies": {"evil": "https://evil.test/a.tgz"}},
            "lockfileVersion: '9.0'",
        ),
        (
            {"pnpm": {"patchedDependencies": {"a": "evil.patch"}}},
            "lockfileVersion: '9.0'",
        ),
        (
            {},
            "packages:\n  evil:\n    resolution:\n      tarball: https://evil.test/a.tgz\n",
        ),
        ({}, "importers:\n  ../workspace: {}\n"),
    ],
)
def test_node_hooks_local_sources_and_unhashed_artifacts_rejected(package, lock):
    with pytest.raises(ValueError):
        build.validate_node(json.dumps(package).encode(), lock.encode())


@pytest.mark.parametrize(
    "kind,name",
    [
        ("symlink", "package/link"),
        ("hardlink", "package/link"),
        ("file", "../escape"),
        ("file", "/absolute"),
        ("file", "package/.cargo/config.toml"),
    ],
)
def test_source_archive_does_not_extract_links_traversal_or_cargo_hooks(tmp_path, kind, name):
    path = tmp_path / "source.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        item = tarfile.TarInfo(name)
        item.type = {
            "file": tarfile.REGTYPE,
            "symlink": tarfile.SYMTYPE,
            "hardlink": tarfile.LNKTYPE,
        }[kind]
        item.linkname = "/outside"
        archive.addfile(item, io.BytesIO())
    with pytest.raises(ValueError, match="Unsafe"):
        build.extract_source(path, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_built_wheel_replacement_preserves_other_hashes_and_markers(tmp_path):
    wheel = (tmp_path / "crcmod-1.7-cp314-cp314-linux_x86_64.whl").absolute()
    raw = (
        'crcmod==1.7 ; python_version >= "3.14" \\\n    --hash=sha256:'
        + "a" * 64
        + "\nother==1 \\\n    --hash=sha256:"
        + "b" * 64
        + "\n"
    )
    item = {
        "name": "crcmod",
        "version": "1.7",
        "wheel": str(wheel),
        "wheel_sha256": "c" * 64,
    }
    replaced = build.replace_source_requirements(raw, [item])
    assert "crcmod @ " + wheel.as_uri() + ' ; python_version >= "3.14"' in replaced
    assert "c" * 64 in replaced and "a" * 64 not in replaced and "b" * 64 in replaced
    with pytest.raises(ValueError, match="selected exactly once"):
        build.replace_source_requirements("other==1\n", [item])


def test_install_uses_locked_export_runtime_groups_no_project_hooks_or_sdists(
    tmp_path, monkeypatch
):
    project = tmp_path / "runtime"
    project.mkdir()
    (project / "pyproject.toml").write_text('[project]\nname="test"\nversion="1"\n')
    (project / "uv.lock").write_text("version=1\n")
    calls = []
    monkeypatch.setattr(build, "BUILD", tmp_path)

    def run(command, cwd, **kwargs):
        calls.append(command)
        if command[1] == "export":
            (tmp_path / (project.name + "-requirements.lock.txt")).write_text(
                "package==1 --hash=sha256:" + "a" * 64 + "\n"
            )

    monkeypatch.setattr(build, "run", run)
    build.install(project, basic=True)
    assert "--locked" in calls[0] and "--no-emit-project" in calls[0] and "--no-dev" in calls[0]
    assert str(project / ".venv") in calls[1]
    assert "--require-hashes" in calls[2] and "--no-build" in calls[2]
    assert "--all-extras" not in repr(calls)


def test_recipes_separate_nonroot_offline_build_and_never_relocate_environments():
    base = (ROOT / "tools/daytona/capability-snapshot.Dockerfile").read_text()
    native = (ROOT / "tools/daytona/capability-native-snapshot.Dockerfile").read_text()
    assert "AS dependency-builder" in base and "AS dependency-builder" in native
    assert "RUN --network=none /opt/rnd/bin/python-build" in native
    assert "USER daytona" in native.split("RUN --network=none")[0]
    assert "PYO3_USE_ABI3_FORWARD_COMPATIBILITY" not in native
    assert "rm -rf .venv" not in base and "rm -rf /opt/rnd/prewarm" not in native
    assert "--mount=" not in native and "--mount=" not in base
    assert "chown -R" not in native and "chmod -R" not in native
    assert "--ignore-scripts" in native and "--package-import-method=copy" in native


def test_native_source_build_does_not_silently_accept_pure_python_fallback(tmp_path):
    path = tmp_path / "crcmod.whl"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("crcmod-1.7.dist-info/WHEEL", "Wheel-Version: 1.0\nTag: py3-none-any\n")
        archive.writestr("crcmod/__init__.py", "# pure fallback")
    with pytest.raises(ValueError, match="no native extension"):
        build.wheel_outputs(path, "crcmod")
    with zipfile.ZipFile(path, "a") as archive:
        archive.writestr("crcmod/_crcfunext.cpython-314-x86_64-linux-gnu.so", b"fixture ELF")
    outputs = build.wheel_outputs(path, "crcmod")
    assert len(outputs["native_extensions"]) == 1
    assert outputs["wheel_tags"] == ["py3-none-any"]
