"""Locked dependency build contracts; never execute source hooks in these tests."""

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path

import pytest

from scripts import daytona_dependency_build as build
from scripts.daytona_native_capability_profile import ROOT


@pytest.fixture
def uv_cli(tmp_path):
    """Exercise the installed uv, with no user config, credentials or network."""
    executable = shutil.which("uv")
    assert executable, "Install the official uv CLI required by the repository test workflow"
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR") if key in os.environ}
    env.update(
        HOME=str(tmp_path),
        USERPROFILE=str(tmp_path),
        TMP=str(tmp_path),
        TEMP=str(tmp_path),
        UV_CACHE_DIR=str(tmp_path / "uv-cache"),
        UV_PYTHON=sys.executable,
        UV_PYTHON_DOWNLOADS="never",
        UV_OFFLINE="1",
        UV_NO_CONFIG="1",
        UV_NO_PROGRESS="1",
        UV_LINK_MODE="copy",
    )

    def invoke(command, cwd, *, extra=()):
        result = subprocess.run(
            [executable, *command[1:], *extra, "--offline", "--no-config"],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result

    return invoke


def metadata_wheel(directory, name):
    """A data-only wheel: no source, backend, importable code or install hooks."""
    path = directory / (name.replace("-", "_") + "-1.0-py3-none-any.whl")
    dist_info = name.replace("-", "_") + "-1.0.dist-info/"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            dist_info + "METADATA", f"Metadata-Version: 2.3\nName: {name}\nVersion: 1.0\n"
        )
        archive.writestr(
            dist_info + "WHEEL", "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        )
        archive.writestr(dist_info + "RECORD", "")
    return path


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


@pytest.mark.parametrize("mode", ["basic", "native", "harness"])
def test_install_uses_locked_export_runtime_groups_no_project_hooks_or_sdists(
    tmp_path, monkeypatch, uv_cli, mode
):
    project = tmp_path / "runtime"
    project.mkdir()
    (project / "pyproject.toml").write_text('[project]\nname="test"\nversion="1"\n')
    (project / "uv.lock").write_text("version=1\n")
    calls = []
    monkeypatch.setattr(build, "BUILD", tmp_path)
    (tmp_path / "source-builds.json").write_text("[]")

    def run(command, cwd, **kwargs):
        calls.append(command)
        # Let the actual parser reject invalid argument names and mappings.
        uv_cli(command, cwd, extra=("--help",))
        if command[1] == "export":
            (tmp_path / (project.name + "-requirements.lock.txt")).write_text(
                "package==1 --hash=sha256:" + "a" * 64 + "\n"
            )

    monkeypatch.setattr(build, "run", run)
    build.install(project, basic=mode == "basic", harness=mode == "harness")
    assert "--locked" in calls[0] and "--no-emit-project" in calls[0]
    assert ("--no-dev" in calls[0]) is (mode == "basic")
    assert ("--all-extras" in calls[0]) is (mode == "harness")
    assert str(project / ".venv") in calls[1]
    assert "--require-hashes" in calls[2] and "--no-build" in calls[2]
    assert calls[2][-1] == str(tmp_path / "runtime-requirements.lock.txt")


@pytest.mark.skipif(os.name == "nt", reason="Image builder uses Linux venv interpreter paths")
@pytest.mark.parametrize(
    "mode,expected",
    [
        ("basic", {"runtime"}),
        ("native", {"runtime", "dev"}),
        ("harness", {"runtime", "dev", "extra"}),
    ],
)
def test_install_real_uv_offline_hashed_wheel_dry_run(
    tmp_path, monkeypatch, uv_cli, mode, expected
):
    project = tmp_path / "project"
    project.mkdir()
    wheelhouse = tmp_path / "wheels"
    wheelhouse.mkdir()
    wheels = {
        group: metadata_wheel(wheelhouse, "fixture-" + group)
        for group in ("runtime", "dev", "extra")
    }
    (project / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\nrequires-python=">=3.14"\n'
        'dependencies=["fixture-runtime==1.0"]\n'
        '[project.optional-dependencies]\nextra=["fixture-extra==1.0"]\n'
        '[dependency-groups]\ndev=["fixture-dev==1.0"]\n'
        "[tool.uv]\npackage=false\n"
    )
    lock = (
        'version=1\nrevision=3\nrequires-python=">=3.14"\n'
        '[[package]]\nname="fixture"\nversion="1"\nsource={virtual="."}\n'
        'dependencies=[{name="fixture-runtime"}]\n'
        '[package.optional-dependencies]\nextra=[{name="fixture-extra"}]\n'
        '[package.dev-dependencies]\ndev=[{name="fixture-dev"}]\n'
        "[package.metadata]\nrequires-dist=["
        '{name="fixture-runtime",specifier="==1.0"},'
        '{name="fixture-extra",specifier="==1.0",marker="extra == \'extra\'"}]\n'
        'provides-extras=["extra"]\n'
        '[package.metadata.requires-dev]\ndev=[{name="fixture-dev",specifier="==1.0"}]\n'
    )
    for group, wheel in wheels.items():
        lock += (
            f'[[package]]\nname="fixture-{group}"\nversion="1.0"\n'
            'source={registry="https://pypi.org/simple"}\n'
            f'wheels=[{{url="https://files.pythonhosted.org/packages/{wheel.name}",'
            f'hash="sha256:{build.sha(wheel)}",size={wheel.stat().st_size}}}]\n'
        )
    (project / "uv.lock").write_text(lock)
    original = {name: build.sha(project / name) for name in ("pyproject.toml", "uv.lock")}
    wheel = wheels["runtime"]
    (tmp_path / "source-builds.json").write_text(
        json.dumps(
            [
                {
                    "name": "fixture-runtime",
                    "version": "1.0",
                    "wheel": str(wheel),
                    "wheel_sha256": build.sha(wheel),
                }
            ]
        )
    )
    monkeypatch.setattr(build, "BUILD", tmp_path)
    monkeypatch.setattr(build, "PYTHON", sys.executable)
    results = []

    def run(command, cwd, **kwargs):
        # Only metadata-only local wheels can be resolved; nothing is installed.
        extra = (
            ("--dry-run", "--no-index", "--find-links", str(wheelhouse))
            if command[1:3] == ["pip", "sync"]
            else ()
        )
        results.append(uv_cli(command, cwd, extra=extra))

    monkeypatch.setattr(build, "run", run)
    build.install(project, basic=mode == "basic", harness=mode == "harness")
    requirements = (tmp_path / "project-requirements.lock.txt").read_text()
    for group, wheel in wheels.items():
        assert ("fixture-" + group in requirements) is (group in expected)
        assert (build.sha(wheel) in requirements) is (group in expected)
    assert ("fixture-runtime @ " in requirements) is (mode == "native")
    assert f"Would install {len(expected)} package" in results[-1].stderr
    assert original == {name: build.sha(project / name) for name in original}
    assert not list((project / ".venv").rglob("fixture*.dist-info"))


def test_fetch_real_uv_parser_keeps_install_requirements_flag(tmp_path, monkeypatch, uv_cli):
    project = tmp_path / "project"
    project.mkdir()
    (project / "uv.lock").write_text("package=[]\n")
    wheel = metadata_wheel(tmp_path, "fixture-tool")
    lock = tmp_path / "tools.json"
    lock.write_text(
        json.dumps(
            {
                "tools": [
                    {
                        "url": "https://files.pythonhosted.org/" + wheel.name,
                        "sha256": build.sha(wheel),
                    }
                ],
                "sdists": [],
            }
        )
    )
    calls = []
    monkeypatch.setattr(build, "BUILD", tmp_path)
    monkeypatch.setattr(build.os, "geteuid", lambda: 1000, raising=False)
    monkeypatch.setattr(build, "download", lambda *args: wheel)

    def run(command, cwd, **kwargs):
        calls.append((command, kwargs))
        uv_cli(command, cwd, extra=("--help",))

    monkeypatch.setattr(build, "run", run)
    build.fetch(lock, project)
    command, kwargs = calls[-1]
    assert command[1:3] == ["pip", "install"]
    assert command[-2:] == ["-r", str(tmp_path / "build-tools.txt")]
    assert {"--no-deps", "--no-build", "--require-hashes", "--no-index"} <= set(command)
    assert kwargs == {"offline": True}


@pytest.mark.parametrize("package", ["crcmod", "esdk-obs-python", "sqlglotrs"])
def test_source_build_real_uv_parser_without_executing_backend(
    tmp_path, monkeypatch, uv_cli, package
):
    (tmp_path / "sources.json").write_text(
        json.dumps([{"name": package, "source": str(tmp_path / "never-execute")}])
    )
    monkeypatch.setattr(build, "BUILD", tmp_path)

    class ParserChecked(Exception):
        pass

    def run(command, cwd, **kwargs):
        uv_cli(command, cwd, extra=("--help",))
        assert command[1:4] == ["build", "--wheel", "--no-build-isolation"]
        assert "--offline" in command and kwargs == {"offline": True}
        if package == "sqlglotrs":
            assert command[-3:-1] == ["--config-setting", "build-args=--locked --offline"]
        assert Path(command[-1]).name == "never-execute"
        raise ParserChecked

    monkeypatch.setattr(build, "run", run)
    with pytest.raises(ParserChecked):
        build.build_sources()


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


def test_profile_workflows_execute_real_dependency_cli_checks_before_image_builds():
    import yaml

    for name in ("capability-profile.yml", "native-capability-profile.yml"):
        document = yaml.safe_load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8"))
        steps = document["jobs"]["local-service"]["steps"]
        preflight = next(
            step
            for step in steps
            if step.get("name") == "Check ordinary launcher behavior and strict receipt contracts"
        )
        build_images = next(
            step
            for step in steps
            if step.get("name") == "Build pinned release locally and lock immutable images"
        )
        assert "tests/test_daytona_dependency_build.py" in preflight["run"]
        assert "tests/test_daytona_dependency_image.py" in preflight["run"]
        assert preflight["env"]["RND_REQUIRE_LANDLOCK"] == "1"
        assert preflight["env"]["RND_REQUIRE_SECCOMP_BPF"] == "1"
        assert steps.index(preflight) < steps.index(build_images)
