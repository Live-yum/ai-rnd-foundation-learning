# tests/test_capability_readonly_dependencies.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_contracts`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `plan`（L18–L60）：接收`profile`。 调用`SimpleNamespace`、`TaskCommand`。 返回路径：L20的`SimpleNamespace( selection=SimpleNamespace( template=profile, database="postgresql" if nat…`。
- `expected`（L63–L83）：接收`profile`。 调用`hashlib.sha256(b"descriptor").hexdigest`、`hashlib.sha256`。 返回路径：L76的`{ "schema": 1, "profile": profile, "image_id": "sha256:" + "a" * 64, "manifest_sha256": "b…`。
- `test_exact_installs_translate_to_immutable_tools_only`（L86–L118）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L88断言`dependencies.readonly_prepare_commands(base) == []`；L89断言`dependencies.readonly_start_command(base).argv[0] == dependencies.PYTHON_ROOT + "/bin…`；L95断言`len(commands) == 2`；L96断言`commands[0].argv == [ dependencies.NODE, dependencies.NATIVE_NODE_ROOT + "/vite/bin/v…`；L103断言`commands[1].argv == [ dependencies.NODE, dependencies.NATIVE_NODE_ROOT + "/vue-tsc/bi…`；L109断言`dependencies.readonly_start_command(value).argv[0] == dependencies.NATIVE_PYTHON_ROOT…`；L113断言`dependencies.readonly_start_command(value, native.frontend_start_command()).argv[0] =…`；L118断言`dependencies.readonly_prepare_commands(value) == commands`。 调用`plan`、`dependencies.readonly_prepare_commands`、`dependencies.readonly_start_command`、`len`、`native.frontend_start_command`、`native.native_prepare_commands`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_alternate_prepare_and_launch_contracts_fail_closed`（L125–L143）：接收`profile`、`mutation`。 控制顺序：L127按`profile == "fastapiadmin"`分支；L129按`mutation == "extra"`分支；L131按`mutation == "install-cwd"`分支；L133按`mutation == "alternate-flag"`分支；L135按`mutation == "shell"`分支；L137按`mutation == "launch-env"`分支。 调用`plan`、`native.native_prepare_commands`、`value.runtime.prepare.append`、`TaskCommand`、`value.runtime.prepare[0].argv.append`、`pytest.raises`、`dependencies.readonly_prepare_commands`、`dependencies.readonly_start_command`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_requires_strict_known_profile`（L159–L178）：接收`mutation`。 控制顺序：L161按`mutation == "extra-field"`分支；L163按`mutation == "missing-descriptor"`分支；L165按`mutation == "extra-descriptor"`分支；L167按`mutation == "wrong-profile"`分支；L169按`mutation == "boolean-schema"`分支；L171按`mutation == "bad-hash"`分支；L173按`mutation == "bad-image"`分支。 调用`expected`、`value["original_descriptors"].pop`、`pytest.raises`、`dependencies.require_dependency_manifest`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_descriptors_are_checked_without_importing_candidate`（L181–L192）：接收`tmp_path`。 控制顺序：L182遍历`("pyproject.toml", "uv.lock")`；L189断言`dependencies.require_dependency_descriptors(tmp_path, plan(), record) == value`。 调用`(tmp_path / name).write_text`、`(tmp_path / "sitecustomize.py").write_text`、`expected`、`dependencies.require_dependency_descriptors`、`plan`、`(tmp_path / "uv.lock").write_text`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_binding_rejects_image_drift_and_hidden_dependency_tree`（L196–L208）：接收`tmp_path`、`mutation`。 控制顺序：L197遍历`("pyproject.toml", "uv.lock")`；L201按`mutation == "image"`分支；L203按`mutation == "venv"`分支。 调用`(tmp_path / name).write_text`、`expected`、`(tmp_path / ".venv").mkdir`、`(tmp_path / "package.json").write_text`、`pytest.raises`、`dependencies.require_dependency_descriptors`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_admission_requires_whole_trusted_verifier_receipt`（L214–L268）：接收`monkeypatch`、`mutation`。 控制顺序：L220按`mutation == "manifest"`分支；L222按`mutation == "tree"`分支；L224按`mutation == "false-flag"`分支；L226按`mutation == "extra"`分支；L228按`mutation == "schema"`分支；L242按`mutation`分支；L248断言`dependencies.prepare_readonly_dependencies( None, plan(), 10, expected=value, source_…`；L256断言`calls == [ [ "/usr/bin/python3", "-I", "-S", dependencies.IMAGE_VERIFIER, "verify-run…`。 调用`expected`、`proof.update`、`monkeypatch.setattr`、`pytest.raises`、`dependencies.prepare_readonly_dependencies`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_admission_requires_whole_trusted_verifier_receipt.execute`（L232–L234）：接收`sandbox`、`argv`、`timeout`。 调用`calls.append`、`SimpleNamespace`、`json.dumps`。 返回路径：L234的`SimpleNamespace(exit_code=1 if mutation == "exit" else 0, result=json.dumps(proof))`。
- `linked_graph`（L272–L323）：接收`tmp_path`、`monkeypatch`。 源码说明：Real links/inodes; model root ownership only because pytest is unprivileged.。 控制顺序：L274按`os.name != "posix"`分支。 调用`pytest.skip`、`(product / "frontend/web").mkdir`、`(image / ".pnpm/vite/node_modules/vite").mkdir`、`(image / ".pnpm/vue-tsc/node_modules/vue-tsc").mkdir`、`(image / ".pnpm/esbuild/node_modules/@esbuild/linux-x64").mkdir`、`(image / ".pnpm/esbuild/node_modules/@esbuild/linux-x64/esbuild")…`、`(image / "vite").symlink_to`、`(image / "vue-tsc").symlink_to`、`(image / "@esbuild").mkdir`等。 返回路径：L316的`SimpleNamespace( product=product, image=image, control=control, namespace=namespace, reloc…`。
- `linked_graph.ownership`（L293–L298）：接收`path`、`*args`、`**kwargs`。 调用`original_lstat`、`list`、`os.stat_result`。 返回路径：L298的`os.stat_result(row)`。
- `linked_graph.relocate`（L304–L309）：接收`script`。 调用`script.replace(dependencies.PRODUCT, product.as_posix()) .replace…`、`script.replace(dependencies.PRODUCT, product.as_posix()) .replace`、`script.replace`、`product.as_posix`、`str`。 返回路径：L305的`script.replace(dependencies.PRODUCT, product.as_posix()) .replace(dependencies.NATIVE_NODE…`。
- `test_product_dependency_root_is_real_with_exact_complete_image_graph`（L326–L339）：接收`linked_graph`。 控制顺序：L329断言`modules.is_dir() and not modules.is_symlink()`；L330断言`(modules / ".pnpm").resolve() == value.image / ".pnpm"`；L331断言`(modules / "@esbuild").is_dir() and not (modules / "@esbuild").is_symlink()`；L332断言`(modules / "@esbuild/linux-x64/esbuild").read_bytes() == b"native"`；L333断言`not (modules / ".bin").exists()`；L334断言`(modules / ".vite-temp").is_dir() and not (modules / ".vite-temp").is_symlink()`；L335断言`all(path.is_relative_to(value.product) for path in value.mutations)`。 调用`modules.is_dir`、`modules.is_symlink`、`(modules / ".pnpm").resolve`、`(modules / "@esbuild").is_dir`、`(modules / "@esbuild").is_symlink`、`(modules / "@esbuild/linux-x64/esbuild").read_bytes`、`(modules / ".bin").exists`、`(modules / ".vite-temp").is_dir`、`(modules / ".vite-temp").is_symlink`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_postbuild_link_map_rejects_tampering`（L359–L395）：接收`linked_graph`、`mutation`。 控制顺序：L362按`mutation == "replace"`分支；L367按`mutation == "add-link"`分支；L369按`mutation == "add-file"`分支；L371按`mutation == "add-directory"`分支；L373按`mutation == "add-bin"`分支；L375按`mutation == "cache-link"`分支；L377按`mutation == "cache-hardlink"`分支；L379按`mutation == "ancestor-link"`分支。后续分支沿下方源码相同行号继续阅读。 调用`os.readlink`、`link.rename`、`link.symlink_to`、`(modules / "unexpected").symlink_to`、`(modules / "evil.js").write_text`、`(modules / "evil").mkdir`、`(modules / ".bin").symlink_to`、`(modules / ".vite-temp/config.mjs").symlink_to`、`os.link`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `freeze_script`（L398–L409）：接收`monkeypatch`、`inventory`。 调用`monkeypatch.setattr`、`native.verify_and_freeze_native_sources`、`SimpleNamespace`。 返回路径：L409的`scripts[0]`。
- `freeze_script.execute`（L401–L403）：接收`sandbox`、`argv`、`timeout`。 调用`scripts.append`、`SimpleNamespace`。 返回路径：L403的`SimpleNamespace(exit_code=0)`。
- `test_freeze_full_inventory_precedes_any_privileged_mutation`（L424–L467）：接收`linked_graph`、`monkeypatch`、`mutation`。 控制顺序：L437按`mutation == "python"`分支；L439按`mutation == "javascript"`分支；L441按`mutation == "unlisted-link"`分支；L443按`mutation == "hardlink"`分支；L445按`mutation == "cache-hardlink"`分支；L447按`mutation == "unknown-directory"`分支；L453按`mutation`分支；L456断言`value.mutations == []`。后续分支沿下方源码相同行号继续阅读。 调用`(value.product / "backend/app").mkdir`、`source.write_text`、`(value.product / "frontend/web/dist").mkdir`、`(value.product / "frontend/web/dist/index.html").write_text`、`(value.product / "frontend/web/dist/app.js").write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`source_manifest.write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run_source_script`（L470–L481）：接收`product`、`control`、`value`、`inventory`、`initial`、`relocate`。 调用`dependencies._source_contract`、`control.write_text`、`json.dumps`、`repr`、`relocate(script) .replace(dependencies.PRODUCT, product.as_posix(…`、`relocate(script) .replace`、`relocate`、`product.as_posix`、`control.as_posix`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_base_source_inventory_freezes_only_after_exact_preflight`（L498–L537）：接收`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L505按`mutation == "unexpected-python"`分支；L507按`mutation == "unexpected-pyc"`分支；L509按`mutation == "symlink"`分支；L511按`mutation == "hardlink"`分支；L513按`mutation == "source-change"`分支；L515按`mutation == "root-database"`分支；L517按`mutation == "database-source-overlap"`分支；L523按`mutation`分支。后续分支沿下方源码相同行号继续阅读。 调用`product.mkdir`、`source.write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`plan`、`(product / "injected.py").write_text`、`(product / "injected.pyc").write_bytes`、`(product / "data").symlink_to`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_base_final_inventory_allows_only_exact_database_files`（L543–L568）：接收`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L553按`mutation == "added-source"`分支；L555按`mutation == "data-python"`分支；L557按`mutation == "data-link"`分支；L559按`mutation == "db-hardlink"`分支；L562按`mutation == "modified-source"`分支；L564按`mutation`分支。 调用`product.mkdir`、`source.write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`monkeypatch.setattr`、`run_source_script`、`plan`、`(product / "data/app.db").write_bytes`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_final_inventory_allows_narrow_runtime_data_only`（L574–L618）：接收`linked_graph`、`mutation`。 控制顺序：L580遍历`("backend/data", "backend/logs", "backend/static/upload", "fronte…`；L582遍历`( "backend/data/jobs.sqlite", "backend/logs/server.log", "backend…`；L590按`mutation == "data-source"`分支；L592按`mutation == "log-source"`分支；L594按`mutation == "upload-source"`分支；L596按`mutation == "dist-link"`分支；L598按`mutation == "outside-module"`分支；L600按`mutation`分支。 调用`(value.product / "backend/app").mkdir`、`source.write_text`、`hashlib.sha256(source.read_bytes()).hexdigest`、`hashlib.sha256`、`source.read_bytes`、`(value.product / directory).mkdir`、`(value.product / name).write_text`、`(value.product / "backend/data/extra.py").write_text`、`(value.product / "backend/logs/extra.log.py").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_broken_dependency_link_rejected_explicitly`（L621–L628）：接收`tmp_path`。 控制顺序：L622遍历`("pyproject.toml", "uv.lock")`。 调用`(tmp_path / name).write_text`、`(tmp_path / ".venv").symlink_to`、`expected`、`pytest.raises`、`dependencies.require_dependency_descriptors`、`plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_initial_ownership_preflights_whole_tree_before_any_chown`（L632–L674）：接收`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L650断言`len(scripts) == 1`；L651断言`not any("/usr/bin/chown" in argv or "/usr/bin/cp" in argv for argv in calls)`；L652遍历`("product", "home", "tmp", "cache")`；L658按`mutation == "symlink"`分支；L673断言`mutations == []`；L674断言`list(outside.iterdir()) == []`。 调用`monkeypatch.setattr`、`pytest.raises`、`isolation.prepare_identity`、`plan`、`len`、`any`、`(tmp_path / name).mkdir`、`source.write_text`、`outside.mkdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_initial_ownership_preflights_whole_tree_before_any_chown.control`（L638–L645）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L640按`argv == ["/usr/bin/id", "-u"]`分支；L642按`argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]`分支。 调用`calls.append`、`SimpleNamespace`、`scripts.append`。 返回路径：L641的`SimpleNamespace(exit_code=0, result="0\n")`；L644的`SimpleNamespace(exit_code=1, result="")`；L645的`SimpleNamespace(exit_code=0, result="")`。
- `test_database_code_or_unsafe_location_rejected_before_creation`（L697–L705）：接收`tmp_path`、`database_path`。 控制顺序：L698遍历`("pyproject.toml", "uv.lock")`。 调用`(tmp_path / name).write_text`、`plan`、`expected`、`pytest.raises`、`dependencies.require_dependency_descriptors`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_database_only_suffixes_admitted_before_creation`（L709–L716）：接收`tmp_path`、`database_path`。 控制顺序：L710遍历`("pyproject.toml", "uv.lock")`；L716断言`dependencies.require_dependency_descriptors(tmp_path, value, record) == binding`。 调用`(tmp_path / name).write_text`、`plan`、`expected`、`dependencies.require_dependency_descriptors`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dependency_profile_database_pair_must_match`（L722–L726）：接收`profile`、`database`。 调用`plan`、`pytest.raises`、`dependencies._profile`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_trusted_source_script_rejects_forged_database_contract_before_mutation`（L733–L757）：接收`tmp_path`、`monkeypatch`、`mode`、`database_path`。 控制顺序：L756断言`mutations == []`；L757断言`sorted(path.name for path in product.iterdir()) == ["app.py"]`。 调用`product.mkdir`、`(product / "app.py").write_text`、`hashlib.sha256(b"source").hexdigest`、`hashlib.sha256`、`control.write_text`、`json.dumps`、`("MODE=" + repr(mode) + "\n" + dependencies.SOURCE_CODE) .replace…`、`("MODE=" + repr(mode) + "\n" + dependencies.SOURCE_CODE) .replace`、`repr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_readonly_dependencies.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L757。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`28688`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_readonly_dependencies.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c557545e7318d033c3107daef8614fc9b9e010334676ce8edc513962318a87b4"} -->
````python
# tests/test_capability_readonly_dependencies.py
"""Pinned commands, data-only admission, and hostile dependency-link fixtures."""

import hashlib
import json
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

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
        else [
            "backend/pyproject.toml",
            "backend/uv.lock",
            "deployment/pyproject.toml",
            "deployment/uv.lock",
            "frontend/web/package.json",
            "frontend/web/pnpm-lock.yaml",
        ]
    )
    return {
        "schema": 1,
        "profile": profile,
        "image_id": "sha256:" + "a" * 64,
        "manifest_sha256": "b" * 64,
        "installed_tree_sha256": "c" * 64,
        "original_descriptors": {name: hashlib.sha256(b"descriptor").hexdigest() for name in names},
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
    assert commands[0].argv == [
        dependencies.NODE,
        dependencies.NATIVE_NODE_ROOT + "/vite/bin/vite.js",
        "build",
        "--mode",
        "production",
    ]
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
