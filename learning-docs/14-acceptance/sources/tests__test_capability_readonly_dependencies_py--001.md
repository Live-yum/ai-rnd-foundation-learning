# tests/test_capability_readonly_dependencies.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_contracts`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `plan`（L20–L62）：接收`profile`。 调用`SimpleNamespace`、`TaskCommand`。 返回路径：L22的`SimpleNamespace( selection=SimpleNamespace( template=profile, database="postgresql" if nat…`。
- `expected`（L65–L86）：接收`profile`。 调用`dependencies.native_descriptor_roles().values`、`dependencies.native_descriptor_roles`、`hashlib.sha256(b"descriptor").hexdigest`、`hashlib.sha256`、`runtime_patches`。 返回路径：L71的`{ "schema": 1, "profile": profile, "image_id": "sha256:" + "a" * 64, "manifest_sha256": "b…`。
- `test_exact_installs_translate_to_immutable_tools_only`（L89–L117）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L91断言`dependencies.readonly_prepare_commands(base) == []`；L92断言`dependencies.readonly_start_command(base).argv[0] == dependencies.PYTHON_ROOT + "/bin…`；L98断言`len(commands) == 2`；L99断言`commands[0] == native.native_frontend_build_command()`；L100断言`commands[0].argv[:3] == [dependencies.NODE, "--input-type=module", "--eval"]`；L101断言`dependencies.NATIVE_NODE_ROOT + "/vite/dist/node/index.js" in commands[0].argv[3]`；L102断言`commands[1].argv == [ dependencies.NODE, dependencies.NATIVE_NODE_ROOT + "/vue-tsc/bi…`；L108断言`dependencies.readonly_start_command(value).argv[0] == dependencies.NATIVE_PYTHON_ROOT…`。后续分支沿下方源码相同行号继续阅读。 调用`plan`、`dependencies.readonly_prepare_commands`、`dependencies.readonly_start_command`、`len`、`native.native_frontend_build_command`、`native.frontend_start_command`、`native.native_prepare_commands`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_alternate_prepare_and_launch_contracts_fail_closed`（L124–L142）：接收`profile`、`mutation`。 控制顺序：L126按`profile == "fastapiadmin"`分支；L128按`mutation == "extra"`分支；L130按`mutation == "install-cwd"`分支；L132按`mutation == "alternate-flag"`分支；L134按`mutation == "shell"`分支；L136按`mutation == "launch-env"`分支。 调用`plan`、`native.native_prepare_commands`、`value.runtime.prepare.append`、`TaskCommand`、`value.runtime.prepare[0].argv.append`、`pytest.raises`、`dependencies.readonly_prepare_commands`、`dependencies.readonly_start_command`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_requires_strict_known_profile`（L158–L177）：接收`mutation`。 控制顺序：L160按`mutation == "extra-field"`分支；L162按`mutation == "missing-descriptor"`分支；L164按`mutation == "extra-descriptor"`分支；L166按`mutation == "wrong-profile"`分支；L168按`mutation == "boolean-schema"`分支；L170按`mutation == "bad-hash"`分支；L172按`mutation == "bad-image"`分支。 调用`expected`、`value["original_descriptors"].pop`、`pytest.raises`、`dependencies.require_dependency_manifest`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_descriptors_are_checked_without_importing_candidate`（L180–L191）：接收`tmp_path`。 控制顺序：L181遍历`("pyproject.toml", "uv.lock")`；L188断言`dependencies.require_dependency_descriptors(tmp_path, plan(), record) == value`。 调用`(tmp_path / name).write_text`、`(tmp_path / "sitecustomize.py").write_text`、`expected`、`dependencies.require_dependency_descriptors`、`plan`、`(tmp_path / "uv.lock").write_text`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_binding_rejects_image_drift_and_hidden_dependency_tree`（L195–L207）：接收`tmp_path`、`mutation`。 控制顺序：L196遍历`("pyproject.toml", "uv.lock")`；L200按`mutation == "image"`分支；L202按`mutation == "venv"`分支。 调用`(tmp_path / name).write_text`、`expected`、`(tmp_path / ".venv").mkdir`、`(tmp_path / "package.json").write_text`、`pytest.raises`、`dependencies.require_dependency_descriptors`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_admission_requires_whole_trusted_verifier_receipt`（L213–L267）：接收`monkeypatch`、`mutation`。 控制顺序：L219按`mutation == "manifest"`分支；L221按`mutation == "tree"`分支；L223按`mutation == "false-flag"`分支；L225按`mutation == "extra"`分支；L227按`mutation == "schema"`分支；L241按`mutation`分支；L247断言`dependencies.prepare_readonly_dependencies( None, plan(), 10, expected=value, source_…`；L255断言`calls == [ [ "/usr/bin/python3", "-I", "-S", dependencies.IMAGE_VERIFIER, "verify-run…`。 调用`expected`、`proof.update`、`monkeypatch.setattr`、`pytest.raises`、`dependencies.prepare_readonly_dependencies`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_admission_requires_whole_trusted_verifier_receipt.execute`（L231–L233）：接收`sandbox`、`argv`、`timeout`。 调用`calls.append`、`SimpleNamespace`、`json.dumps`。 返回路径：L233的`SimpleNamespace(exit_code=1 if mutation == "exit" else 0, result=json.dumps(proof))`。
- `test_native_initial_and_restart_require_exact_runtime_patch_receipt`（L274–L324）：接收`monkeypatch`、`phase`、`mutation`。 控制顺序：L289按`mutation == "missing"`分支；L291按`mutation == "stale"`分支；L293按`mutation == "different-path"`分支；L298按`mutation == "extra"`分支；L300按`mutation == "old-profile"`分支；L316按`mutation`分支；L319断言`len(calls) == (0 if mutation == "old-profile" else 1)`；L321断言`verify(None, plan("fastapiadmin"), 10, expected=value, source_inventory={}) == { **pr…`。 调用`expected`、`copy.deepcopy`、`proof.update`、`proof.pop`、`proof["runtime_patches"][0][ "relative_path" ].replace`、`value.pop`、`monkeypatch.setattr`、`pytest.raises`、`verify`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_initial_and_restart_require_exact_runtime_patch_receipt.execute`（L305–L307）：接收`sandbox`、`argv`、`timeout`。 调用`calls.append`、`SimpleNamespace`、`json.dumps`。 返回路径：L307的`SimpleNamespace(exit_code=0, result=json.dumps(proof))`。
- `linked_graph`（L328–L379）：接收`tmp_path`、`monkeypatch`。 源码说明：Real links/inodes; model root ownership only because pytest is unprivileged.。 控制顺序：L330按`os.name != "posix"`分支。 调用`pytest.skip`、`(product / "frontend/web").mkdir`、`(image / ".pnpm/vite/node_modules/vite").mkdir`、`(image / ".pnpm/vue-tsc/node_modules/vue-tsc").mkdir`、`(image / ".pnpm/esbuild/node_modules/@esbuild/linux-x64").mkdir`、`(image / ".pnpm/esbuild/node_modules/@esbuild/linux-x64/esbuild")…`、`(image / "vite").symlink_to`、`(image / "vue-tsc").symlink_to`、`(image / "@esbuild").mkdir`等。 返回路径：L372的`SimpleNamespace( product=product, image=image, control=control, namespace=namespace, reloc…`。
- `linked_graph.ownership`（L349–L354）：接收`path`、`*args`、`**kwargs`。 调用`original_lstat`、`list`、`os.stat_result`。 返回路径：L354的`os.stat_result(row)`。
- `linked_graph.relocate`（L360–L365）：接收`script`。 调用`script.replace(dependencies.PRODUCT, product.as_posix()) .replace…`、`script.replace(dependencies.PRODUCT, product.as_posix()) .replace`、`script.replace`、`product.as_posix`、`str`。 返回路径：L361的`script.replace(dependencies.PRODUCT, product.as_posix()) .replace(dependencies.NATIVE_NODE…`。
- `test_product_dependency_root_is_real_with_exact_complete_image_graph`（L382–L395）：接收`linked_graph`。 控制顺序：L385断言`modules.is_dir() and not modules.is_symlink()`；L386断言`(modules / ".pnpm").resolve() == value.image / ".pnpm"`；L387断言`(modules / "@esbuild").is_dir() and not (modules / "@esbuild").is_symlink()`；L388断言`(modules / "@esbuild/linux-x64/esbuild").read_bytes() == b"native"`；L389断言`not (modules / ".bin").exists()`；L390断言`(modules / ".vite-temp").is_dir() and not (modules / ".vite-temp").is_symlink()`；L391断言`all(path.is_relative_to(value.product) for path in value.mutations)`。 调用`modules.is_dir`、`modules.is_symlink`、`(modules / ".pnpm").resolve`、`(modules / "@esbuild").is_dir`、`(modules / "@esbuild").is_symlink`、`(modules / "@esbuild/linux-x64/esbuild").read_bytes`、`(modules / ".bin").exists`、`(modules / ".vite-temp").is_dir`、`(modules / ".vite-temp").is_symlink`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_postbuild_link_map_rejects_tampering`（L415–L451）：接收`linked_graph`、`mutation`。 控制顺序：L418按`mutation == "replace"`分支；L423按`mutation == "add-link"`分支；L425按`mutation == "add-file"`分支；L427按`mutation == "add-directory"`分支；L429按`mutation == "add-bin"`分支；L431按`mutation == "cache-link"`分支；L433按`mutation == "cache-hardlink"`分支；L435按`mutation == "ancestor-link"`分支。后续分支沿下方源码相同行号继续阅读。 调用`os.readlink`、`link.rename`、`link.symlink_to`、`(modules / "unexpected").symlink_to`、`(modules / "evil.js").write_text`、`(modules / "evil").mkdir`、`(modules / ".bin").symlink_to`、`(modules / ".vite-temp/config.mjs").symlink_to`、`os.link`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `freeze_script`（L454–L465）：接收`monkeypatch`、`inventory`。 调用`monkeypatch.setattr`、`native.verify_and_freeze_native_sources`、`SimpleNamespace`。 返回路径：L465的`scripts[0]`。
- `freeze_script.execute`（L457–L459）：接收`sandbox`、`argv`、`timeout`。 调用`scripts.append`、`SimpleNamespace`。 返回路径：L459的`SimpleNamespace(exit_code=0)`。
- `test_freeze_full_inventory_precedes_any_privileged_mutation`（L480–L523）：接收`linked_graph`、`monkeypatch`、`mutation`。 控制顺序：L493按`mutation == "python"`分支；L495按`mutation == "javascript"`分支；L497按`mutation == "unlisted-link"`分支；L499按`mutation == "hardlink"`分支；L501按`mutation == "cache-hardlink"`分支；L503按`mutation == "unknown-directory"`分支；L509按`mutation`分支；L512断言`value.mutations == []`。后续分支沿下方源码相同行号继续阅读。 调用`(value.product / "backend/app").mkdir`、`source.write_text`、`(value.product / "frontend/web/dist").mkdir`、`(value.product / "frontend/web/dist/index.html").write_text`、`(value.product / "frontend/web/dist/app.js").write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`source_manifest.write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run_source_script`（L526–L537）：接收`product`、`control`、`value`、`inventory`、`initial`、`relocate`。 调用`dependencies._source_contract`、`control.write_text`、`json.dumps`、`repr`、`relocate(script) .replace(dependencies.PRODUCT, product.as_posix(…`、`relocate(script) .replace`、`relocate`、`product.as_posix`、`control.as_posix`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_base_source_inventory_freezes_only_after_exact_preflight`（L554–L593）：接收`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L561按`mutation == "unexpected-python"`分支；L563按`mutation == "unexpected-pyc"`分支；L565按`mutation == "symlink"`分支；L567按`mutation == "hardlink"`分支；L569按`mutation == "source-change"`分支；L571按`mutation == "root-database"`分支；L573按`mutation == "database-source-overlap"`分支；L579按`mutation`分支。后续分支沿下方源码相同行号继续阅读。 调用`product.mkdir`、`source.write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`plan`、`(product / "injected.py").write_text`、`(product / "injected.pyc").write_bytes`、`(product / "data").symlink_to`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_base_final_inventory_allows_only_exact_database_files`（L599–L624）：接收`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L609按`mutation == "added-source"`分支；L611按`mutation == "data-python"`分支；L613按`mutation == "data-link"`分支；L615按`mutation == "db-hardlink"`分支；L618按`mutation == "modified-source"`分支；L620按`mutation`分支。 调用`product.mkdir`、`source.write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`monkeypatch.setattr`、`run_source_script`、`plan`、`(product / "data/app.db").write_bytes`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_final_inventory_allows_narrow_runtime_data_only`（L630–L674）：接收`linked_graph`、`mutation`。 控制顺序：L636遍历`("backend/data", "backend/logs", "backend/static/upload", "fronte…`；L638遍历`( "backend/data/jobs.sqlite", "backend/logs/server.log", "backend…`；L646按`mutation == "data-source"`分支；L648按`mutation == "log-source"`分支；L650按`mutation == "upload-source"`分支；L652按`mutation == "dist-link"`分支；L654按`mutation == "outside-module"`分支；L656按`mutation`分支。 调用`(value.product / "backend/app").mkdir`、`source.write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`(value.product / directory).mkdir`、`(value.product / name).write_text`、`(value.product / "backend/data/extra.py").write_text`、`(value.product / "backend/logs/extra.log.py").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_broken_dependency_link_rejected_explicitly`（L677–L684）：接收`tmp_path`。 控制顺序：L678遍历`("pyproject.toml", "uv.lock")`。 调用`(tmp_path / name).write_text`、`(tmp_path / ".venv").symlink_to`、`expected`、`pytest.raises`、`dependencies.require_dependency_descriptors`、`plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_initial_ownership_preflights_whole_tree_before_any_chown`（L688–L730）：接收`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L706断言`len(scripts) == 1`；L707断言`not any("/usr/bin/chown" in argv or "/usr/bin/cp" in argv for argv in calls)`；L708遍历`("product", "home", "tmp", "cache")`；L714按`mutation == "symlink"`分支；L729断言`mutations == []`；L730断言`list(outside.iterdir()) == []`。 调用`monkeypatch.setattr`、`pytest.raises`、`isolation.prepare_identity`、`plan`、`len`、`any`、`(tmp_path / name).mkdir`、`source.write_text`、`outside.mkdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_initial_ownership_preflights_whole_tree_before_any_chown.control`（L694–L701）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L696按`argv == ["/usr/bin/id", "-u"]`分支；L698按`argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]`分支。 调用`calls.append`、`SimpleNamespace`、`scripts.append`。 返回路径：L697的`SimpleNamespace(exit_code=0, result="0\n")`；L700的`SimpleNamespace(exit_code=1, result="")`；L701的`SimpleNamespace(exit_code=0, result="")`。
- `test_database_code_or_unsafe_location_rejected_before_creation`（L753–L761）：接收`tmp_path`、`database_path`。 控制顺序：L754遍历`("pyproject.toml", "uv.lock")`。 调用`(tmp_path / name).write_text`、`plan`、`expected`、`pytest.raises`、`dependencies.require_dependency_descriptors`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_database_only_suffixes_admitted_before_creation`（L765–L772）：接收`tmp_path`、`database_path`。 控制顺序：L766遍历`("pyproject.toml", "uv.lock")`；L772断言`dependencies.require_dependency_descriptors(tmp_path, value, record) == binding`。 调用`(tmp_path / name).write_text`、`plan`、`expected`、`dependencies.require_dependency_descriptors`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dependency_profile_database_pair_must_match`（L778–L782）：接收`profile`、`database`。 调用`plan`、`pytest.raises`、`dependencies._profile`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_trusted_source_script_rejects_forged_database_contract_before_mutation`（L789–L813）：接收`tmp_path`、`monkeypatch`、`mode`、`database_path`。 控制顺序：L812断言`mutations == []`；L813断言`sorted(path.name for path in product.iterdir()) == ["app.py"]`。 调用`product.mkdir`、`(product / "app.py").write_text`、`hashlib.sha256(b"source").hexdigest`、`hashlib.sha256`、`control.write_text`、`json.dumps`、`("MODE=" + repr(mode) + "\n" + dependencies.SOURCE_CODE) .replace…`、`("MODE=" + repr(mode) + "\n" + dependencies.SOURCE_CODE) .replace`、`repr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_readonly_dependencies.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L813。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`31018`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_readonly_dependencies.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0fd7baa246bbaff57217f36dc83fb3b51d84ff133110d73fe9bd4afa5f2bd7ab"} -->
````python
# tests/test_capability_readonly_dependencies.py
"""Pinned commands, data-only admission, and hostile dependency-link fixtures."""

import copy
import hashlib
import json
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest
from capability_dependency_fixtures import runtime_patches

from workbench import capability_dependencies as dependencies
from workbench import capability_native_runtime as native
from workbench.capability_contracts import TaskCommand
from workbench.capability_verification import CheckFailure


def plan(profile="python-basic"):
    native_profile = profile == "fastapiadmin"
    return SimpleNamespace(
        selection=SimpleNamespace(
            template=profile, database="postgresql" if native_profile else "sqlite"
        ),
        runtime=SimpleNamespace(
            port=8123,
            database_path="data/app.db",
            prepare=[]
            if native_profile
            else [
                TaskCommand(
                    argv=["uv", "sync", "--locked", "--offline", "--no-dev", "--python", "3.14"]
                )
            ],
            start=TaskCommand(
                cwd="backend" if native_profile else ".",
                argv=[
                    ".venv/bin/python",
                    "-m",
                    "uvicorn",
                    "app:create_app",
                    "--factory",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8123",
                ]
                if native_profile
                else [
                    "./.venv/bin/python",
                    "-m",
                    "uvicorn",
                    "app:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8123",
                ],
            ),
        ),
    )


def expected(profile="python-basic"):
    names = (
        ["pyproject.toml", "uv.lock"]
        if profile == "python-basic"
        else [name for paths in dependencies.native_descriptor_roles().values() for name in paths]
    )
    return {
        "schema": 1,
        "profile": profile,
        "image_id": "sha256:" + "a" * 64,
        "manifest_sha256": "b" * 64,
        "installed_tree_sha256": "c" * 64,
        "original_descriptors": {name: hashlib.sha256(b"descriptor").hexdigest() for name in names},
        **(
            {
                "descriptor_roles": dependencies.native_descriptor_roles(),
                "runtime_patches": runtime_patches(),
            }
            if profile == "fastapiadmin"
            else {}
        ),
    }


def test_exact_installs_translate_to_immutable_tools_only():
    base = plan()
    assert dependencies.readonly_prepare_commands(base) == []
    assert (
        dependencies.readonly_start_command(base).argv[0]
        == dependencies.PYTHON_ROOT + "/bin/python"
    )
    value = plan("fastapiadmin")
    commands = dependencies.readonly_prepare_commands(value)
    assert len(commands) == 2
    assert commands[0] == native.native_frontend_build_command()
    assert commands[0].argv[:3] == [dependencies.NODE, "--input-type=module", "--eval"]
    assert dependencies.NATIVE_NODE_ROOT + "/vite/dist/node/index.js" in commands[0].argv[3]
    assert commands[1].argv == [
        dependencies.NODE,
        dependencies.NATIVE_NODE_ROOT + "/vue-tsc/bin/vue-tsc.js",
        "--noEmit",
        "--skipLibCheck",
    ]
    assert (
        dependencies.readonly_start_command(value).argv[0]
        == dependencies.NATIVE_PYTHON_ROOT + "/bin/python"
    )
    assert (
        dependencies.readonly_start_command(value, native.frontend_start_command()).argv[0]
        == dependencies.NODE
    )
    value.runtime.prepare = native.native_prepare_commands()
    assert dependencies.readonly_prepare_commands(value) == commands


@pytest.mark.parametrize("profile", ["python-basic", "fastapiadmin"])
@pytest.mark.parametrize(
    "mutation", ["extra", "install-cwd", "alternate-flag", "shell", "launch-env", "launch-cwd"]
)
def test_alternate_prepare_and_launch_contracts_fail_closed(profile, mutation):
    value = plan(profile)
    if profile == "fastapiadmin":
        value.runtime.prepare = native.native_prepare_commands()
    if mutation == "extra":
        value.runtime.prepare.append(TaskCommand(argv=["true"]))
    elif mutation == "install-cwd":
        value.runtime.prepare[0].cwd = "different"
    elif mutation == "alternate-flag":
        value.runtime.prepare[0].argv.append("--no-build")
    elif mutation == "shell":
        value.runtime.prepare[0].argv = ["/bin/sh", "-c", "true"]
    elif mutation == "launch-env":
        value.runtime.start.argv = ["env", *value.runtime.start.argv]
    else:
        value.runtime.start.cwd = "different"
    with pytest.raises(CheckFailure):
        dependencies.readonly_prepare_commands(value)
        dependencies.readonly_start_command(value)


@pytest.mark.parametrize(
    "mutation",
    [
        "extra-field",
        "missing-descriptor",
        "extra-descriptor",
        "wrong-profile",
        "boolean-schema",
        "bad-hash",
        "bad-image",
        "escaped-descriptor",
    ],
)
def test_manifest_requires_strict_known_profile(mutation):
    value = expected()
    if mutation == "extra-field":
        value["trusted"] = True
    elif mutation == "missing-descriptor":
        del value["original_descriptors"]["uv.lock"]
    elif mutation == "extra-descriptor":
        value["original_descriptors"]["other/uv.lock"] = "d" * 64
    elif mutation == "wrong-profile":
        value["profile"] = "fastapiadmin"
    elif mutation == "boolean-schema":
        value["schema"] = True
    elif mutation == "bad-hash":
        value["manifest_sha256"] = "b" * 63
    elif mutation == "bad-image":
        value["image_id"] = "latest"
    else:
        value["original_descriptors"]["../uv.lock"] = value["original_descriptors"].pop("uv.lock")
    with pytest.raises(CheckFailure):
        dependencies.require_dependency_manifest(value, "python-basic")


def test_local_descriptors_are_checked_without_importing_candidate(tmp_path):
    for name in ("pyproject.toml", "uv.lock"):
        (tmp_path / name).write_text("descriptor")
    (tmp_path / "sitecustomize.py").write_text(
        "raise AssertionError('candidate code must never run')"
    )
    value = expected()
    record = {"snapshot": {"image_id": value["image_id"], "dependency_manifest": value}}
    assert dependencies.require_dependency_descriptors(tmp_path, plan(), record) == value
    (tmp_path / "uv.lock").write_text("changed")
    with pytest.raises(CheckFailure, match="描述符"):
        dependencies.require_dependency_descriptors(tmp_path, plan(), record)


@pytest.mark.parametrize("mutation", ["image", "venv", "extra-descriptor"])
def test_local_binding_rejects_image_drift_and_hidden_dependency_tree(tmp_path, mutation):
    for name in ("pyproject.toml", "uv.lock"):
        (tmp_path / name).write_text("descriptor")
    value = expected()
    record = {"snapshot": {"image_id": value["image_id"], "dependency_manifest": value}}
    if mutation == "image":
        record["snapshot"]["image_id"] = "sha256:" + "f" * 64
    elif mutation == "venv":
        (tmp_path / ".venv").mkdir()
    else:
        (tmp_path / "package.json").write_text("{}")
    with pytest.raises(CheckFailure):
        dependencies.require_dependency_descriptors(tmp_path, plan(), record)


@pytest.mark.parametrize(
    "mutation", [None, "manifest", "tree", "false-flag", "extra", "schema", "exit"]
)
def test_runtime_admission_requires_whole_trusted_verifier_receipt(monkeypatch, mutation):
    value = expected()
    proof = {
        key: value[key] for key in ("schema", "profile", "manifest_sha256", "installed_tree_sha256")
    }
    proof.update({key: True for key in dependencies.RECEIPT_FLAGS})
    if mutation == "manifest":
        proof["manifest_sha256"] = "e" * 64
    elif mutation == "tree":
        proof["installed_tree_sha256"] = "e" * 64
    elif mutation == "false-flag":
        proof["readonly_verified"] = 1
    elif mutation == "extra":
        proof["claim"] = True
    elif mutation == "schema":
        proof["schema"] = True
    calls = []

    def execute(sandbox, argv, timeout):
        calls.append(argv)
        return SimpleNamespace(exit_code=1 if mutation == "exit" else 0, result=json.dumps(proof))

    monkeypatch.setattr(dependencies, "control_exec", execute)
    monkeypatch.setattr(
        dependencies,
        "_verify_sources",
        lambda *a, **kw: {"source_inventory_verified": True, "source_inventory_sha256": "f" * 64},
    )
    if mutation:
        with pytest.raises(CheckFailure):
            dependencies.prepare_readonly_dependencies(
                None, plan(), 10, expected=value, source_inventory={"app.py": "f" * 64}
            )
    else:
        assert dependencies.prepare_readonly_dependencies(
            None, plan(), 10, expected=value, source_inventory={"app.py": "f" * 64}
        ) == {
            **proof,
            "product_links_verified": True,
            "source_inventory_verified": True,
            "source_inventory_sha256": "f" * 64,
        }
    assert calls == [
        [
            "/usr/bin/python3",
            "-I",
            "-S",
            dependencies.IMAGE_VERIFIER,
            "verify-runtime",
            "--profile",
            "python-basic",
            "--product",
            dependencies.PRODUCT,
        ]
    ]


@pytest.mark.parametrize("phase", ["initial", "restart"])
@pytest.mark.parametrize(
    "mutation", [None, "missing", "stale", "different-path", "extra", "old-profile"]
)
def test_native_initial_and_restart_require_exact_runtime_patch_receipt(
    monkeypatch, phase, mutation
):
    value = expected("fastapiadmin")
    proof = {
        key: copy.deepcopy(value[key])
        for key in (
            "schema",
            "profile",
            "manifest_sha256",
            "installed_tree_sha256",
            "runtime_patches",
        )
    }
    proof.update({key: True for key in dependencies.RECEIPT_FLAGS})
    if mutation == "missing":
        proof.pop("runtime_patches")
    elif mutation == "stale":
        proof["runtime_patches"][0]["id"] = "old"
    elif mutation == "different-path":
        # Both paths are permitted, but restart must bind the original physical instance.
        proof["runtime_patches"][0]["relative_path"] = proof["runtime_patches"][0][
            "relative_path"
        ].replace("vite@7.3.3/", "vite@7.3.3_jiti@2.6.1/")
    elif mutation == "extra":
        proof["runtime_patches"][0]["hook"] = True
    elif mutation == "old-profile":
        value.pop("runtime_patches")
        proof.pop("runtime_patches")
    calls = []

    def execute(sandbox, argv, timeout):
        calls.append(argv)
        return SimpleNamespace(exit_code=0, result=json.dumps(proof))

    monkeypatch.setattr(dependencies, "control_exec", execute)
    monkeypatch.setattr(dependencies, "_verify_sources", lambda *a, **kw: {})
    verify = (
        dependencies.prepare_readonly_dependencies
        if phase == "initial"
        else dependencies.verify_readonly_dependencies
    )
    if mutation:
        with pytest.raises(CheckFailure):
            verify(None, plan("fastapiadmin"), 10, expected=value, source_inventory={})
        assert len(calls) == (0 if mutation == "old-profile" else 1)
    else:
        assert verify(None, plan("fastapiadmin"), 10, expected=value, source_inventory={}) == {
            **proof,
            "product_links_verified": True,
        }


@pytest.fixture
def linked_graph(tmp_path, monkeypatch):
    """Real links/inodes; model root ownership only because pytest is unprivileged."""
    if os.name != "posix":
        pytest.skip("Actual POSIX ownership/modes; portable admission tests remain enabled")
    product = tmp_path / "product"
    (product / "frontend/web").mkdir(parents=True)
    image = tmp_path / "image/node_modules"
    (image / ".pnpm/vite/node_modules/vite").mkdir(parents=True)
    (image / ".pnpm/vue-tsc/node_modules/vue-tsc").mkdir(parents=True)
    (image / ".pnpm/esbuild/node_modules/@esbuild/linux-x64").mkdir(parents=True)
    (image / ".pnpm/esbuild/node_modules/@esbuild/linux-x64/esbuild").write_bytes(b"native")
    (image / "vite").symlink_to(".pnpm/vite/node_modules/vite")
    (image / "vue-tsc").symlink_to(".pnpm/vue-tsc/node_modules/vue-tsc")
    (image / "@esbuild").mkdir()
    (image / "@esbuild/linux-x64").symlink_to("../.pnpm/esbuild/node_modules/@esbuild/linux-x64")
    (image / ".bin").mkdir()
    (image / ".bin/vite").write_text("image only")
    control = tmp_path / "links.json"
    mutations = []
    original_lstat = Path.lstat

    def ownership(path, *args, **kwargs):
        result = original_lstat(path, *args, **kwargs)
        row = list(result)
        row[0] &= ~0o022
        row[4] = 20000 if path == product / "frontend/web/node_modules/.vite-temp" else 0
        return os.stat_result(row)

    monkeypatch.setattr(Path, "lstat", ownership)
    monkeypatch.setattr(os, "chown", lambda path, *a, **kw: mutations.append(Path(path)))
    monkeypatch.setattr(os, "lchown", lambda path, *a, **kw: mutations.append(Path(path)))

    def relocate(script):
        return (
            script.replace(dependencies.PRODUCT, product.as_posix())
            .replace(dependencies.NATIVE_NODE_ROOT, str(image))
            .replace(dependencies.LINK_MANIFEST, str(control))
        )

    namespace = {}
    exec(
        compile(relocate(dependencies.CREATE_NATIVE_LINKS), "<owned-image-link-fixture>", "exec"),
        namespace,
    )
    return SimpleNamespace(
        product=product,
        image=image,
        control=control,
        namespace=namespace,
        relocate=relocate,
        mutations=mutations,
    )


def test_product_dependency_root_is_real_with_exact_complete_image_graph(linked_graph):
    value = linked_graph
    modules = value.product / "frontend/web/node_modules"
    assert modules.is_dir() and not modules.is_symlink()
    assert (modules / ".pnpm").resolve() == value.image / ".pnpm"
    assert (modules / "@esbuild").is_dir() and not (modules / "@esbuild").is_symlink()
    assert (modules / "@esbuild/linux-x64/esbuild").read_bytes() == b"native"
    assert not (modules / ".bin").exists()
    assert (modules / ".vite-temp").is_dir() and not (modules / ".vite-temp").is_symlink()
    assert all(path.is_relative_to(value.product) for path in value.mutations)
    (modules / ".vite-temp/vite.config.ts.timestamp-1234567890-a4b0.mjs").write_text(
        "generated config"
    )
    value.namespace["validate_links"]()


@pytest.mark.parametrize(
    "mutation",
    [
        "replace",
        "add-link",
        "add-file",
        "add-directory",
        "add-bin",
        "cache-link",
        "cache-hardlink",
        "ancestor-link",
        "escape",
        "scope-replace",
        "cache-source",
        "cache-directory",
    ],
)
def test_postbuild_link_map_rejects_tampering(linked_graph, mutation):
    value = linked_graph
    modules = value.product / "frontend/web/node_modules"
    if mutation == "replace":
        link = modules / "vite"
        target = os.readlink(link)
        link.rename(value.product / "old-vite-link")
        link.symlink_to(target)
    elif mutation == "add-link":
        (modules / "unexpected").symlink_to(value.image / "vite")
    elif mutation == "add-file":
        (modules / "evil.js").write_text("evil")
    elif mutation == "add-directory":
        (modules / "evil").mkdir()
    elif mutation == "add-bin":
        (modules / ".bin").symlink_to(value.image / ".bin")
    elif mutation == "cache-link":
        (modules / ".vite-temp/config.mjs").symlink_to(value.image / "vite")
    elif mutation == "cache-hardlink":
        os.link(value.image / ".bin/vite", modules / ".vite-temp/config.mjs")
    elif mutation == "ancestor-link":
        modules.rename(value.product / "old-modules")
        modules.symlink_to(value.product / "old-modules")
    elif mutation == "escape":
        (modules / "vite").unlink()
        (modules / "vite").symlink_to(value.product)
    elif mutation == "cache-source":
        (modules / ".vite-temp/unexpected.mjs").write_text("bad")
    elif mutation == "cache-directory":
        (modules / ".vite-temp/added").mkdir()
    else:
        scope = modules / "@esbuild"
        scope.rename(value.product / "old-scope")
        scope.mkdir()
        (scope / "linux-x64").symlink_to(value.image / "@esbuild/linux-x64")
    with pytest.raises(AssertionError):
        value.namespace["validate_links"]()


def freeze_script(monkeypatch, inventory):
    scripts = []

    def execute(sandbox, argv, timeout):
        scripts.append(argv[-1])
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(native, "control_exec", execute)
    native.verify_and_freeze_native_sources(
        SimpleNamespace(fs=SimpleNamespace(upload_file=lambda *a, **kw: None)), inventory, 10
    )
    return scripts[0]


@pytest.mark.parametrize(
    "mutation",
    [
        None,
        "python",
        "javascript",
        "unlisted-link",
        "hardlink",
        "cache-hardlink",
        "unknown-directory",
    ],
)
def test_freeze_full_inventory_precedes_any_privileged_mutation(
    linked_graph, monkeypatch, mutation
):
    value = linked_graph
    (value.product / "backend/app").mkdir(parents=True)
    source = value.product / "backend/app/main.py"
    source.write_text("protected=True")
    (value.product / "frontend/web/dist").mkdir()
    (value.product / "frontend/web/dist/index.html").write_text("build output")
    (value.product / "frontend/web/dist/app.js").write_text("legitimate build output")
    inventory = {"backend/app/main.py": hashlib.sha256(source.read_bytes()).hexdigest()}
    source_manifest = value.control.parent / "source.json"
    source_manifest.write_text(json.dumps(inventory))
    if mutation == "python":
        (value.product / "backend/app/added.py").write_text("unexpected")
    elif mutation == "javascript":
        (value.product / "frontend/web/added.mjs").write_text("unexpected")
    elif mutation == "unlisted-link":
        (value.product / "backend/app/alias.py").symlink_to(source)
    elif mutation == "hardlink":
        os.link(source, value.product / "backend/app/alias.py")
    elif mutation == "cache-hardlink":
        os.link(source, value.product / "frontend/web/node_modules/.vite-temp/config.mjs")
    elif mutation == "unknown-directory":
        (value.product / "backend/app/unknown").mkdir()
    value.mutations.clear()
    script = value.relocate(freeze_script(monkeypatch, inventory)).replace(
        native.CONTROL + "/private/source-manifest.json", str(source_manifest)
    )
    if mutation:
        with pytest.raises(AssertionError):
            exec(compile(script, "<owned-native-freeze>", "exec"), {})
        assert value.mutations == []
    else:
        exec(compile(script, "<owned-native-freeze>", "exec"), {})
        assert value.mutations
        assert all(
            path.is_relative_to(value.product) and not path.is_symlink() for path in value.mutations
        )
        assert (
            stat.S_IMODE((value.product / "frontend/web/node_modules/.vite-temp").stat().st_mode)
            == 0o700
        )
        value.namespace["validate_links"]()


def run_source_script(
    product, control, value, inventory, *, initial, relocate=lambda script: script
):
    contract = dependencies._source_contract(value, inventory)
    control.write_text(json.dumps(contract))
    script = "MODE=" + repr("initial" if initial else "verify") + "\n" + dependencies.SOURCE_CODE
    script = (
        relocate(script)
        .replace(dependencies.PRODUCT, product.as_posix())
        .replace(dependencies.SOURCE_INVENTORY, control.as_posix())
    )
    exec(compile(script, "<owned-source-inventory>", "exec"), {})


@pytest.mark.parametrize(
    "mutation",
    [
        None,
        "unexpected-python",
        "unexpected-pyc",
        "symlink",
        "hardlink",
        "source-change",
        "root-database",
        "database-source-overlap",
    ],
)
@pytest.mark.skipif(os.name != "posix", reason="Actual POSIX frozen permission modes")
def test_base_source_inventory_freezes_only_after_exact_preflight(tmp_path, monkeypatch, mutation):
    product = tmp_path / "product"
    product.mkdir()
    source = product / "app.py"
    source.write_text("source = True")
    inventory = {"app.py": hashlib.sha256(source.read_bytes()).hexdigest()}
    value = plan()
    if mutation == "unexpected-python":
        (product / "injected.py").write_text("bad")
    elif mutation == "unexpected-pyc":
        (product / "injected.pyc").write_bytes(b"bad")
    elif mutation == "symlink":
        (product / "data").symlink_to(tmp_path)
    elif mutation == "hardlink":
        os.link(source, product / "alias.py")
    elif mutation == "source-change":
        source.write_text("changed")
    elif mutation == "root-database":
        value.runtime.database_path = "app.db"
    elif mutation == "database-source-overlap":
        (product / "data").mkdir()
        (product / "data/module.py").write_text("source")
        inventory["data/module.py"] = hashlib.sha256(b"source").hexdigest()
    mutations = []
    monkeypatch.setattr(os, "chown", lambda path, *a, **kw: mutations.append(Path(path)))
    if mutation:
        error = (
            CheckFailure
            if mutation in {"root-database", "database-source-overlap"}
            else AssertionError
        )
        with pytest.raises(error):
            run_source_script(product, tmp_path / "source.json", value, inventory, initial=True)
        assert mutations == []
    else:
        run_source_script(product, tmp_path / "source.json", value, inventory, initial=True)
        assert mutations == [product, source, product / "data"]
        assert stat.S_IMODE(product.stat().st_mode) == 0o755
        assert stat.S_IMODE(source.stat().st_mode) == 0o644
        assert stat.S_IMODE((product / "data").stat().st_mode) == 0o700


@pytest.mark.parametrize(
    "mutation", [None, "added-source", "data-python", "data-link", "db-hardlink", "modified-source"]
)
def test_base_final_inventory_allows_only_exact_database_files(tmp_path, monkeypatch, mutation):
    product = tmp_path / "product"
    product.mkdir()
    source = product / "app.py"
    source.write_text("source = True")
    inventory = {"app.py": hashlib.sha256(source.read_bytes()).hexdigest()}
    monkeypatch.setattr(os, "chown", lambda *a, **kw: None, raising=False)
    run_source_script(product, tmp_path / "source.json", plan(), inventory, initial=True)
    (product / "data/app.db").write_bytes(b"database")
    (product / "data/app.db-wal").write_bytes(b"wal")
    if mutation == "added-source":
        (product / "added.py").write_text("bad")
    elif mutation == "data-python":
        (product / "data/added.py").write_text("bad")
    elif mutation == "data-link":
        (product / "data/app.db-shm").symlink_to(source)
    elif mutation == "db-hardlink":
        (product / "data/app.db").unlink()
        os.link(source, product / "data/app.db")
    elif mutation == "modified-source":
        source.write_text("changed")
    if mutation:
        with pytest.raises(AssertionError):
            run_source_script(product, tmp_path / "source.json", plan(), inventory, initial=False)
    else:
        run_source_script(product, tmp_path / "source.json", plan(), inventory, initial=False)


@pytest.mark.parametrize(
    "mutation", [None, "data-source", "log-source", "upload-source", "dist-link", "outside-module"]
)
def test_native_final_inventory_allows_narrow_runtime_data_only(linked_graph, mutation):
    value = linked_graph
    (value.product / "backend/app").mkdir(parents=True)
    source = value.product / "backend/app/main.py"
    source.write_text("source = True")
    inventory = {"backend/app/main.py": hashlib.sha256(source.read_bytes()).hexdigest()}
    for directory in ("backend/data", "backend/logs", "backend/static/upload", "frontend/web/dist"):
        (value.product / directory).mkdir(parents=True, exist_ok=True)
    for name in (
        "backend/data/jobs.sqlite",
        "backend/logs/server.log",
        "backend/static/upload/document.pdf",
        "frontend/web/dist/index.html",
        "frontend/web/dist/app.js",
    ):
        (value.product / name).write_text("runtime output")
    if mutation == "data-source":
        (value.product / "backend/data/extra.py").write_text("bad")
    elif mutation == "log-source":
        (value.product / "backend/logs/extra.log.py").write_text("bad")
    elif mutation == "upload-source":
        (value.product / "backend/static/upload/extra.py").write_text("bad")
    elif mutation == "dist-link":
        (value.product / "frontend/web/dist/injected.js").symlink_to(source)
    elif mutation == "outside-module":
        (value.product / "backend/app/extra.py").write_text("bad")
    if mutation:
        with pytest.raises(AssertionError):
            run_source_script(
                value.product,
                value.control.parent / "source.json",
                plan("fastapiadmin"),
                inventory,
                initial=False,
                relocate=value.relocate,
            )
    else:
        run_source_script(
            value.product,
            value.control.parent / "source.json",
            plan("fastapiadmin"),
            inventory,
            initial=False,
            relocate=value.relocate,
        )


def test_local_broken_dependency_link_rejected_explicitly(tmp_path):
    for name in ("pyproject.toml", "uv.lock"):
        (tmp_path / name).write_text("descriptor")
    (tmp_path / ".venv").symlink_to(tmp_path / "missing")
    value = expected()
    record = {"snapshot": {"image_id": value["image_id"], "dependency_manifest": value}}
    with pytest.raises(CheckFailure, match="符号链接"):
        dependencies.require_dependency_descriptors(tmp_path, plan(), record)


@pytest.mark.parametrize("mutation", ["symlink", "hardlink"])
def test_initial_ownership_preflights_whole_tree_before_any_chown(tmp_path, monkeypatch, mutation):
    from workbench import capability_isolation as isolation

    calls = []
    scripts = []

    def control(sandbox, argv, timeout):
        calls.append(argv)
        if argv == ["/usr/bin/id", "-u"]:
            return SimpleNamespace(exit_code=0, result="0\n")
        if argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]:
            scripts.append(argv[-1])
            return SimpleNamespace(exit_code=1, result="")
        return SimpleNamespace(exit_code=0, result="")

    monkeypatch.setattr(isolation, "control_exec", control)
    with pytest.raises(isolation.IsolationUnavailable, match="链接"):
        isolation.prepare_identity(None, plan(), 10)
    assert len(scripts) == 1
    assert not any("/usr/bin/chown" in argv or "/usr/bin/cp" in argv for argv in calls)
    for name in ("product", "home", "tmp", "cache"):
        (tmp_path / name).mkdir()
    source = tmp_path / "product/app.py"
    source.write_text("source")
    outside = tmp_path / "outside"
    outside.mkdir()
    if mutation == "symlink":
        (tmp_path / "product/link").symlink_to(outside, target_is_directory=True)
    else:
        os.link(source, tmp_path / "product/alias.py")
    mutations = []
    monkeypatch.setattr(os, "chown", lambda *a, **kw: mutations.append(a), raising=False)
    with pytest.raises(AssertionError):
        exec(
            compile(
                scripts[0].replace("/tmp/rnd-capability", tmp_path.as_posix()),
                "<owned-initial-ownership>",
                "exec",
            ),
            {},
        )
    assert mutations == []
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize(
    "database_path",
    [
        "data/added.py",
        "data/added.pyc",
        "data/native.so",
        "data/executable",
        "app.db",
        ".venv/state.db",
        "data/__pycache__/state.db",
        "data/.git/state.db",
        "data/node_modules/state.db",
        "data/../state.db",
        "data//state.db",
        "./data/state.db",
        "data:alternate/state.db",
        "data\\state.db",
        "pyproject.toml/state.db",
    ],
)
def test_database_code_or_unsafe_location_rejected_before_creation(tmp_path, database_path):
    for name in ("pyproject.toml", "uv.lock"):
        (tmp_path / name).write_text("descriptor")
    value = plan()
    value.runtime.database_path = database_path
    binding = expected()
    record = {"snapshot": {"image_id": binding["image_id"], "dependency_manifest": binding}}
    with pytest.raises(CheckFailure, match="SQLite"):
        dependencies.require_dependency_descriptors(tmp_path, value, record)


@pytest.mark.parametrize("database_path", ["data/app.db", "state/app.sqlite", "store/app.sqlite3"])
def test_database_only_suffixes_admitted_before_creation(tmp_path, database_path):
    for name in ("pyproject.toml", "uv.lock"):
        (tmp_path / name).write_text("descriptor")
    value = plan()
    value.runtime.database_path = database_path
    binding = expected()
    record = {"snapshot": {"image_id": binding["image_id"], "dependency_manifest": binding}}
    assert dependencies.require_dependency_descriptors(tmp_path, value, record) == binding


@pytest.mark.parametrize(
    "profile,database", [("python-basic", "postgresql"), ("fastapiadmin", "sqlite")]
)
def test_dependency_profile_database_pair_must_match(profile, database):
    value = plan(profile)
    value.selection.database = database
    with pytest.raises(CheckFailure):
        dependencies._profile(value)


@pytest.mark.parametrize("mode", ["initial", "verify"])
@pytest.mark.parametrize(
    "database_path", ["data/added.py", "data/native.so", "app.db", "data/../state.db"]
)
def test_trusted_source_script_rejects_forged_database_contract_before_mutation(
    tmp_path, monkeypatch, mode, database_path
):
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("source")
    contract = {
        "profile": "python-basic",
        "database": "sqlite",
        "database_path": database_path,
        "inventory": {"app.py": hashlib.sha256(b"source").hexdigest()},
    }
    control = tmp_path / "contract.json"
    control.write_text(json.dumps(contract))
    script = (
        ("MODE=" + repr(mode) + "\n" + dependencies.SOURCE_CODE)
        .replace(dependencies.PRODUCT, product.as_posix())
        .replace(dependencies.SOURCE_INVENTORY, control.as_posix())
    )
    mutations = []
    monkeypatch.setattr(os, "chown", lambda *a, **kw: mutations.append(a), raising=False)
    with pytest.raises(AssertionError):
        exec(compile(script, "<forged-database-contract>", "exec"), {})
    assert mutations == []
    assert sorted(path.name for path in product.iterdir()) == ["app.py"]
````
