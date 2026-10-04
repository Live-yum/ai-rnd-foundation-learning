# tests/test_daytona_dependency_build.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_native_capability_profile`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_reviewed_bundled_native_graph_includes_required_sdists_and_exact_default_groups`（L15–L36）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L24断言`"sqlglot[rs]==27.8.0" in tomllib.loads(project.decode())["project"]["dependencies"]`；L25断言`tomllib.loads(project.decode())["tool"]["uv"]["default-groups"] == ["dev"]`；L28遍历`spec["sdists"]`；L29断言`packages[record["name"]]["version"] == record["version"]`；L30断言`packages[record["name"]]["sdist"]["hash"] == "sha256:" + record["sha256"]`；L31断言`packages[record["name"]]["sdist"]["url"] == record["url"]`；L32断言`{row["name"] for row in spec["sdists"]} == { "crcmod", "esdk-obs-python", "sqlglotrs"…`。 调用`zipfile.ZipFile`、`build.normalize`、`archive.read`、`build.validate_python`、`build.validate_node`、`tomllib.loads`、`project.decode`、`json.loads`、`(ROOT / "scripts/daytona_dependency_build.lock.json").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_build_backends_and_local_configuration_rejected`（L47–L52）：接收`extra`。 调用`pytest.raises`、`build.validate_python`、`('[project]\nname="fixture"\nversion="1"\n' + extra).encode`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_and_workspace_lock_packages_rejected`（L59–L64）：接收`source`。 调用`pytest.raises`、`build.validate_python`、`('[[package]]\nname="evil"\nsource=' + source + "\n").encode`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registry_authentication_and_unreviewed_hosts_rejected`（L76–L78）：接收`url`。 调用`pytest.raises`、`build.public_url`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_hooks_local_sources_and_unhashed_artifacts_rejected`（L100–L102）：接收`package`、`lock`。 调用`pytest.raises`、`build.validate_node`、`json.dumps(package).encode`、`json.dumps`、`lock.encode`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_archive_does_not_extract_links_traversal_or_cargo_hooks`（L115–L128）：接收`tmp_path`、`kind`、`name`。 控制顺序：L128断言`not (tmp_path / "output").exists()`。 调用`tarfile.open`、`tarfile.TarInfo`、`archive.addfile`、`io.BytesIO`、`pytest.raises`、`build.extract_source`、`(tmp_path / "output").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_built_wheel_replacement_preserves_other_hashes_and_markers`（L131–L150）：接收`tmp_path`。 控制顺序：L147断言`"crcmod @ " + wheel.as_uri() + ' ; python_version >= "3.14"' in replaced`；L148断言`"c" * 64 in replaced and "a" * 64 not in replaced and "b" * 64 in replaced`。 调用`(tmp_path / "crcmod-1.7-cp314-cp314-linux_x86_64.whl").absolute`、`str`、`build.replace_source_requirements`、`wheel.as_uri`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_install_uses_locked_export_runtime_groups_no_project_hooks_or_sdists`（L153–L175）：接收`tmp_path`、`monkeypatch`。 控制顺序：L172断言`"--locked" in calls[0] and "--no-emit-project" in calls[0] and "--no-dev" in calls[0]`；L173断言`str(project / ".venv") in calls[1]`；L174断言`"--require-hashes" in calls[2] and "--no-build" in calls[2]`；L175断言`"--all-extras" not in repr(calls)`。 调用`project.mkdir`、`(project / "pyproject.toml").write_text`、`(project / "uv.lock").write_text`、`monkeypatch.setattr`、`build.install`、`str`、`repr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_install_uses_locked_export_runtime_groups_no_project_hooks_or_sdists.run`（L163–L168）：接收`command`、`cwd`、`**kwargs`。 控制顺序：L165按`command[1] == "export"`分支。 调用`calls.append`、`(tmp_path / (project.name + "-requirements.lock.txt")).write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recipes_separate_nonroot_offline_build_and_never_relocate_environments`（L178–L188）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L181断言`"AS dependency-builder" in base and "AS dependency-builder" in native`；L182断言`"RUN --network=none /opt/rnd/bin/python-build" in native`；L183断言`"USER daytona" in native.split("RUN --network=none")[0]`；L184断言`"PYO3_USE_ABI3_FORWARD_COMPATIBILITY" not in native`；L185断言`"rm -rf .venv" not in base and "rm -rf /opt/rnd/prewarm" not in native`；L186断言`"--mount=" not in native and "--mount=" not in base`；L187断言`"chown -R" not in native and "chmod -R" not in native`；L188断言`"--ignore-scripts" in native and "--package-import-method=copy" in native`。 调用`(ROOT / "tools/daytona/capability-snapshot.Dockerfile").read_text`、`(ROOT / "tools/daytona/capability-native-snapshot.Dockerfile").re…`、`native.split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_source_build_does_not_silently_accept_pure_python_fallback`（L191–L202）：接收`tmp_path`。 控制顺序：L201断言`len(outputs["native_extensions"]) == 1`；L202断言`outputs["wheel_tags"] == ["py3-none-any"]`。 调用`zipfile.ZipFile`、`archive.writestr`、`pytest.raises`、`build.wheel_outputs`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_dependency_build.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L202。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7880`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_dependency_build.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a158d37a97ff32f4e99dd561c892f0075bc5bb152a0aceee052cab18a94de30a"} -->
````python
# tests/test_daytona_dependency_build.py
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
````
