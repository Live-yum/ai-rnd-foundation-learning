# tests/test_native_capability_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `product`（L22–L44）：接收`tmp_path`。 控制顺序：L25遍历`("backend", "deployment")`。 调用`atomic_text`、`json.dumps`。 返回路径：L44的`root`。
- `foundation`（L48–L54）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L49的`{ "profile": native.base.PROFILE, "recipe_identity": "e" * 64, "runner": {"image_id": RUNN…`。
- `image_for`（L57–L79）：接收`record`。 返回路径：L58的`{ "Id": IMAGE, "Os": "linux", "Architecture": "amd64", "RepoDigests": ["127.0.0.1:6000/" +…`。
- `prepared`（L83–L116）：接收`tmp_path`、`product`、`foundation`、`monkeypatch`。 调用`directory.mkdir`、`native.product_inputs`、`native.recipe_identity`、`native.base_identity`、`native.native_stamp`、`native.selection`、`copy.deepcopy`、`dict`、`image_for`等。 返回路径：L116的`directory, record, image`。
- `test_filtered_dependency_context_never_copies_product_code_secrets_or_hooks`（L119–L135）：接收`product`、`tmp_path`。 控制顺序：L125断言`paths == {"product/" + name for name in native.DESCRIPTORS} \| { "Dockerfile", "harne…`；L130断言`"https://pypi.org/simple" in (context / "product/backend/uv.lock").read_text()`；L131断言`"tuna.tsinghua" in (product / "backend/uv.lock").read_text()`；L132断言`native.product_inputs(product) == expected`；L133断言`not any( "must-not-be-copied" in path.read_text() for path in context.rglob("*") if p…`。 调用`native.product_inputs`、`context.mkdir`、`native.prepare_context`、`path.relative_to(context).as_posix`、`path.relative_to`、`context.rglob`、`path.is_file`、`(context / "product/backend/uv.lock").read_text`、`(product / "backend/uv.lock").read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registry_credentials_are_rejected_before_build`（L146–L149）：接收`product`、`value`。 调用`atomic_text`、`pytest.raises`、`native.product_inputs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secret_files_are_filtered_but_dependency_and_source_drift_are_distinct`（L152–L161）：接收`product`。 控制顺序：L155断言`native.product_inputs(product) == original`；L158断言`changed["dependency_identity"] == original["dependency_identity"]`；L159断言`changed["source_identity"] != original["source_identity"]`；L161断言`native.product_inputs(product)["dependency_identity"] != original["dependency_identit…`。 调用`native.product_inputs`、`atomic_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_exact_native_manifest_selection_is_supported`（L172–L175）：接收`product`、`metadata`。 调用`atomic_text`、`json.dumps`、`pytest.raises`、`native.product_inputs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_locks_and_symlinks_are_rejected`（L178–L184）：接收`product`、`tmp_path`。 调用`(product / "backend/uv.lock").unlink`、`pytest.raises`、`native.product_inputs`、`(product / "backend/uv.lock").symlink_to`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_context_rejects_source_drift`（L187–L191）：接收`product`、`tmp_path`。 调用`native.product_inputs`、`atomic_text`、`pytest.raises`、`native.prepare_context`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_readonly_check_revalidates_base_snapshot_and_normalizes_native_record`（L194–L208）：接收`prepared`、`monkeypatch`、`foundation`。 控制顺序：L202断言`native.require_native_profile(directory, record["snapshot"]["snapshot"]) == record`；L203断言`checked == [directory]`；L204断言`record["runner"] == foundation["runner"]`；L205断言`record["selection"]["database"] == "postgresql"`；L206断言`record["resources"] == {"cpu": 2, "memory": 6, "disk": 30}`。 调用`monkeypatch.setattr`、`checked.append`、`native.require_native_profile`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_record_tampering_fails_closed`（L228–L233）：接收`prepared`、`mutation`。 调用`mutation`、`atomic_text`、`json.dumps`、`pytest.raises`、`native.require_native_profile`、`pytest.mark.parametrize`、`record.update`、`record["runner"].update`、`record["base"].update`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_image_drift_is_rejected`（L249–L253）：接收`prepared`、`mutation`。 调用`mutation`、`pytest.raises`、`native.require_native_profile`、`pytest.mark.parametrize`、`image.update`、`image["Config"].update`、`image["Config"]["Labels"].update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_product_lock_drift_prevents_reusing_native_profile`（L256–L260）：接收`prepared`、`product`。 调用`atomic_text`、`pytest.raises`、`native.require_native_profile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_uses_only_owned_base_and_separate_ready_record`（L264–L314）：接收`prepared`、`product`、`monkeypatch`、`failure`。 控制顺序：L276遍历`protected`；L302按`failure`分支；L305断言`not (directory / native.LOCK).exists()`；L308断言`result == expected`；L309断言`native.require_native_profile(directory) == result`；L310断言`not (directory / native.ENVIRONMENT).exists()`；L311按`os.name != "nt"`分支；L312断言`(directory / native.LOCK).stat().st_mode & 0o777 == 0o600`。后续分支沿下方源码相同行号继续阅读。 调用`(directory / native.LOCK).unlink`、`atomic_text`、`monkeypatch.setattr`、`calls.append`、`pytest.raises`、`native.prepare`、`(directory / native.LOCK).exists`、`native.require_native_profile`、`(directory / native.ENVIRONMENT).exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_uses_only_owned_base_and_separate_ready_record.docker`（L280–L295）：接收`*args`、`**kwargs`。 控制顺序：L282按`args[0] == "build"`分支；L284断言`not (context / "product/.env").exists()`；L285断言`not (context / "product/backend/main.py").exists()`；L286断言`"BASE_IMAGE=127.0.0.1:6000/rnd-python@" + DIGEST in args`；L287断言`"--pull=false" in args`；L288按`failure == "input"`分支；L290按`args[0] == "push"`分支；L291按`failure == "push"`分支。后续分支沿下方源码相同行号继续阅读。 调用`calls.append`、`Path`、`(context / "product/.env").exists`、`(context / "product/backend/main.py").exists`、`atomic_text`、`RuntimeError`。 返回路径：L295的`""`。
- `test_prepare_refuses_overwrite_before_docker`（L317–L323）：接收`prepared`、`product`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`native.prepare`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base`（L327–L396）：接收`prepared`、`monkeypatch`、`failure`。 控制顺序：L344按`failure == "source"`分支；L346按`failure == "state"`分支；L348按`failure == "resources"`分支；L379按`failure`分支；L382断言`not (directory / native.ENVIRONMENT).exists()`；L386断言`KEY in content and "fastapiadmin/postgresql" in content`；L387断言`"CAPABILITY_EXECUTION_ENABLED" not in content`；L388断言`"local" in content`。后续分支沿下方源码相同行号继续阅读。 调用`atomic_text`、`json.dumps`、`SimpleNamespace`、`Snapshots`、`monkeypatch.setattr`、`calls.append`、`pytest.raises`、`native.register_worker`、`(directory / native.ENVIRONMENT).exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.Snapshots`（L351–L359）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.Snapshots.create`（L352–L359）：接收`params`、`**kwargs`。 控制顺序：L354断言`params.image == snapshot["digest"]`；L355断言`{ name: getattr(params.resources, name) for name in native.RESOURCES } == native.RESO…`；L358断言`params.region_id == "local" and kwargs["timeout"] == 600`。 调用`calls.append`、`getattr`。 返回路径：L359的`existing`。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.factory`（L363–L367）：接收`settings`。 控制顺序：L364断言`settings.daytona_api_key.get_secret_value() == KEY`；L365断言`settings.daytona_api_url == "http://127.0.0.1:3000/api"`；L366断言`settings.daytona_target == "local"`。 调用`settings.daytona_api_key.get_secret_value`。 返回路径：L367的`client`。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.close`（L369–L373）：接收`value`。 控制顺序：L370断言`value is client`；L372按`failure == "close"`分支；L373抛异常，停止当前正常路径。 调用`calls.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_has_bounded_subprocess_and_no_key_in_argv`（L399–L407）：接收`prepared`、`monkeypatch`。 控制顺序：L405断言`args[0][1:4] == ["-m", "scripts.daytona_native_capability_profile", "register-worker"…`；L406断言`kwargs["timeout"] == 720`；L407断言`KEY not in repr(calls)`。 调用`monkeypatch.setattr`、`calls.append`、`native.register`、`repr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_does_not_overwrite_other_native_credentials`（L410–L418）：接收`prepared`、`monkeypatch`。 调用`atomic_text`、`json.dumps`、`native.write_private_new`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`native.register_worker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_recipe_keeps_control_identity_pinned_tools_and_no_product_execution`（L421–L443）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L423遍历`( "ARG BASE_IMAGE", "FROM ${BASE_IMAGE}", "libseccomp2 procps", "…`；L440断言`text in recipe`；L441断言`recipe.rstrip().endswith("USER 0:0")`；L442断言`"warm.py" not in recipe and "vite build" not in recipe`；L443断言`"CAPABILITY_EXECUTION_ENABLED" not in recipe`。 调用`(native.ROOT / native.DOCKERFILE).read_text`、`recipe.rstrip().endswith`、`recipe.rstrip`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_key_cannot_inject_environment_or_shell_syntax`（L449–L451）：接收`key`。 调用`pytest.raises`、`native.environment_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_native_environment_must_remain_private`（L454–L463）：接收`prepared`。 控制顺序：L455按`os.name == "nt"`分支。 调用`pytest.skip`、`atomic_text`、`json.dumps`、`native.environment_text`、`path.chmod`、`pytest.raises`、`native.register_worker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_metadata_cannot_be_adopted_through_a_symlink`（L466–L473）：接收`prepared`、`tmp_path`。 调用`atomic_text`、`json.dumps`、`(directory / native.LOCK).unlink`、`(directory / native.LOCK).symlink_to`、`pytest.raises`、`native.require_native_profile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_capability_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L473。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18938`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_capability_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f0996cb74171e7d7ef1863328ba00b04cac25521651d93c09d4af7354715806b"} -->
````python
# tests/test_native_capability_profile.py
"""Native preparation contracts use explicit fakes, never live Docker/runtime proof."""

import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import daytona_native_capability_profile as native
from workbench.filesystem import atomic_text

RUNNER = "sha256:" + "a" * 64
BASE_IMAGE = "sha256:" + "b" * 64
IMAGE = "sha256:" + "c" * 64
DIGEST = "sha256:" + "d" * 64
KEY = "existing-local-account-fixture"


@pytest.fixture
def product(tmp_path):
    root = tmp_path / "product"
    atomic_text(root / "deployment/manifest.json", json.dumps({"template": "fastapiadmin"}))
    for folder in ("backend", "deployment"):
        atomic_text(
            root / folder / "pyproject.toml", '[project]\nname = "fixture"\nversion = "1"\n'
        )
        atomic_text(
            root / folder / "uv.lock",
            'version = 1\nregistry = "https://pypi.tuna.tsinghua.edu.cn/simple"\n',
        )
    atomic_text(
        root / "frontend/web/package.json", '{"name":"fixture","scripts":{"prepare":"DO_NOT_RUN"}}'
    )
    atomic_text(root / "frontend/web/pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
    atomic_text(root / "backend/main.py", "raise RuntimeError('never execute candidate source')\n")
    atomic_text(
        root / "deployment/workbench/native_environment.py",
        "raise RuntimeError('untrusted control')\n",
    )
    atomic_text(root / "frontend/web/.pnpmfile.cjs", "throw Error('untrusted package hook')")
    atomic_text(root / ".env", "API_KEY=must-not-be-copied\n")
    return root


@pytest.fixture
def foundation():
    return {
        "profile": native.base.PROFILE,
        "recipe_identity": "e" * 64,
        "runner": {"image_id": RUNNER, "tag": "fixed-base-runner", "recipe_sha256": "f" * 64},
        "snapshot": {"image_id": BASE_IMAGE, "digest": "registry:6000/rnd-python@" + DIGEST},
    }


def image_for(record):
    return {
        "Id": IMAGE,
        "Os": "linux",
        "Architecture": "amd64",
        "RepoDigests": ["127.0.0.1:6000/" + native.FAMILY + "@" + DIGEST],
        "Config": {
            "User": "0:0",
            "WorkingDir": native.base.CONTROL_WORKDIR,
            "Entrypoint": [],
            "Cmd": [],
            "Labels": {
                "org.opencontainers.image.revision": native.base.DAYTONA_SOURCE,
                "rnd.capability.profile": native.PROFILE,
                "rnd.capability.recipe": record["recipe_identity"],
                "rnd.capability.base-recipe": record["base"]["recipe_identity"],
                "rnd.capability.base-image": record["base"]["snapshot_image_id"],
                "rnd.capability.base-digest": record["base"]["snapshot_digest"],
                "rnd.capability.dependencies": record["dependency_identity"],
                "rnd.capability.input": record["inputs"]["source_identity"],
            },
        },
    }


@pytest.fixture
def prepared(tmp_path, product, foundation, monkeypatch):
    directory = tmp_path / "profile"
    directory.mkdir()
    inputs = native.product_inputs(product)
    identity, recipes = native.recipe_identity()
    base = native.base_identity(foundation)
    stamp = native.native_stamp(identity, base, inputs)
    record = {
        "profile": native.PROFILE,
        "recipe_identity": identity,
        "recipes": recipes,
        "selection": native.selection(),
        "base": base,
        "runner": copy.deepcopy(foundation["runner"]),
        "inputs": inputs,
        "dependency_identity": inputs["dependency_identity"],
        "resources": dict(native.RESOURCES),
        "snapshot": {
            "image": "registry:6000/" + native.FAMILY + "@" + DIGEST,
            "digest": "registry:6000/" + native.FAMILY + "@" + DIGEST,
            "image_id": IMAGE,
            "local_tag": "127.0.0.1:6000/" + native.FAMILY + ":" + stamp,
            "source_hash": stamp,
            "snapshot": native.FAMILY + "-" + stamp,
            "user": "0:0",
            "working_dir": native.base.CONTROL_WORKDIR,
            "recipe_sha256": recipes[native.DOCKERFILE],
        },
    }
    image = image_for(record)
    atomic_text(directory / native.LOCK, json.dumps(record))
    monkeypatch.setattr(native.base, "require_profile", lambda path: copy.deepcopy(foundation))
    monkeypatch.setattr(native.base, "inspect_image", lambda reference: copy.deepcopy(image))
    return directory, record, image


def test_filtered_dependency_context_never_copies_product_code_secrets_or_hooks(product, tmp_path):
    expected = native.product_inputs(product)
    context = tmp_path / "context"
    context.mkdir()
    native.prepare_context(product, context, expected)
    paths = {path.relative_to(context).as_posix() for path in context.rglob("*") if path.is_file()}
    assert paths == {"product/" + name for name in native.DESCRIPTORS} | {
        "Dockerfile",
        "harness/pyproject.toml",
        "harness/uv.lock",
    }
    assert "https://pypi.org/simple" in (context / "product/backend/uv.lock").read_text()
    assert "tuna.tsinghua" in (product / "backend/uv.lock").read_text()
    assert native.product_inputs(product) == expected
    assert not any(
        "must-not-be-copied" in path.read_text() for path in context.rglob("*") if path.is_file()
    )


@pytest.mark.parametrize(
    "value",
    [
        "_authToken=secret",
        "registry=https://person:secret@registry.npmjs.org/",
        "password=${TOKEN}",
    ],
)
def test_registry_credentials_are_rejected_before_build(product, value):
    atomic_text(product / "frontend/web/.npmrc", value)
    with pytest.raises(ValueError, match="configuration|URLs"):
        native.product_inputs(product)


def test_secret_files_are_filtered_but_dependency_and_source_drift_are_distinct(product):
    original = native.product_inputs(product)
    atomic_text(product / ".env", "CHANGED_PRIVATE_SECRET=ignored\n")
    assert native.product_inputs(product) == original
    atomic_text(product / "backend/main.py", "changed source\n")
    changed = native.product_inputs(product)
    assert changed["dependency_identity"] == original["dependency_identity"]
    assert changed["source_identity"] != original["source_identity"]
    atomic_text(product / "backend/uv.lock", "version = 2\n")
    assert native.product_inputs(product)["dependency_identity"] != original["dependency_identity"]


@pytest.mark.parametrize(
    "metadata",
    [
        {"template": "python-basic"},
        {"template": "fastapiadmin", "database": "sqlite"},
        {"template": "fastapiadmin", "selection": {"template": "python-basic"}},
    ],
)
def test_only_exact_native_manifest_selection_is_supported(product, metadata):
    atomic_text(product / "deployment/manifest.json", json.dumps(metadata))
    with pytest.raises(ValueError):
        native.product_inputs(product)


def test_missing_locks_and_symlinks_are_rejected(product, tmp_path):
    (product / "backend/uv.lock").unlink()
    with pytest.raises(ValueError, match="missing a dependency descriptor"):
        native.product_inputs(product)
    (product / "backend/uv.lock").symlink_to(tmp_path / "not-a-lock")
    with pytest.raises(ValueError):
        native.product_inputs(product)


def test_context_rejects_source_drift(product, tmp_path):
    expected = native.product_inputs(product)
    atomic_text(product / "backend/main.py", "changed")
    with pytest.raises(ValueError, match="input changed"):
        native.prepare_context(product, tmp_path / "context", expected)


def test_readonly_check_revalidates_base_snapshot_and_normalizes_native_record(
    prepared, monkeypatch, foundation
):
    directory, record, _ = prepared
    checked = []
    monkeypatch.setattr(
        native.base, "require_profile", lambda path: checked.append(path) or foundation
    )
    assert native.require_native_profile(directory, record["snapshot"]["snapshot"]) == record
    assert checked == [directory]
    assert record["runner"] == foundation["runner"]
    assert record["selection"]["database"] == "postgresql"
    assert record["resources"] == {"cpu": 2, "memory": 6, "disk": 30}
    with pytest.raises(ValueError, match="derived identity"):
        native.require_native_profile(directory, "wrong-snapshot")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(profile="arbitrary-profile"),
        lambda record: record.update(recipe_identity="0" * 64),
        lambda record: record.update(resources={"cpu": 99, "memory": 6, "disk": 30}),
        lambda record: record["runner"].update(image_id="sha256:" + "0" * 64),
        lambda record: record["base"].update(recipe_identity="0" * 64),
        lambda record: record.update(dependency_identity="0" * 64),
        lambda record: record["snapshot"].update(user="daytona"),
        lambda record: record["snapshot"].update(working_dir="/tmp"),
        lambda record: record["snapshot"].update(local_tag="remote:latest"),
        lambda record: record["snapshot"].update(image_id="mutable"),
        lambda record: record["snapshot"].update(image="remote:latest"),
        lambda record: record["snapshot"].update(source_hash="0" * 16),
    ],
)
def test_native_record_tampering_fails_closed(prepared, mutation):
    directory, record, _ = prepared
    mutation(record)
    atomic_text(directory / native.LOCK, json.dumps(record))
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda image: image.update(Id="sha256:" + "0" * 64),
        lambda image: image.update(RepoDigests=[]),
        lambda image: image.update(Architecture="arm64"),
        lambda image: image["Config"].update(User="daytona"),
        lambda image: image["Config"].update(WorkingDir="/tmp"),
        lambda image: image["Config"].update(Entrypoint=["untrusted"]),
        lambda image: image["Config"].update(Cmd=["untrusted"]),
        lambda image: image["Config"]["Labels"].update({"rnd.capability.input": "0" * 64}),
    ],
)
def test_live_image_drift_is_rejected(prepared, mutation):
    directory, _, image = prepared
    mutation(image)
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


def test_product_lock_drift_prevents_reusing_native_profile(prepared, product):
    directory, _, _ = prepared
    atomic_text(product / "backend/uv.lock", "version = 2\n")
    with pytest.raises(ValueError, match="input or base identity changed"):
        native.require_native_profile(directory)


@pytest.mark.parametrize("failure", [None, "push", "image", "input"])
def test_prepare_uses_only_owned_base_and_separate_ready_record(
    prepared, product, monkeypatch, failure
):
    directory, expected, image = prepared
    (directory / native.LOCK).unlink()
    protected = (
        "snapshot-image.json",
        "workbench.env",
        "api-key.json",
        native.base.LOCK,
        native.base.COMPOSE,
    )
    for name in protected:
        atomic_text(directory / name, "base-must-stay-unchanged")
    calls = []

    def docker(*args, **kwargs):
        calls.append((args, kwargs))
        if args[0] == "build":
            context = Path(args[-1])
            assert not (context / "product/.env").exists()
            assert not (context / "product/backend/main.py").exists()
            assert "BASE_IMAGE=127.0.0.1:6000/rnd-python@" + DIGEST in args
            assert "--pull=false" in args
            if failure == "input":
                atomic_text(product / "backend/main.py", "changed during build")
        if args[0] == "push":
            if failure == "push":
                raise RuntimeError("explicit publication failure")
            if failure == "image":
                image["Id"] = "sha256:" + "0" * 64
        return ""

    monkeypatch.setattr(native.local, "docker", docker)
    monkeypatch.setattr(
        native.base, "compose", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    monkeypatch.setattr(native.local, "wait_for_registry", lambda: None)
    if failure:
        with pytest.raises((ValueError, RuntimeError)):
            native.prepare(product, directory)
        assert not (directory / native.LOCK).exists()
    else:
        result = native.prepare(product, directory)
        assert result == expected
        assert native.require_native_profile(directory) == result
        assert not (directory / native.ENVIRONMENT).exists()
        if os.name != "nt":
            assert (directory / native.LOCK).stat().st_mode & 0o777 == 0o600
    assert all((directory / name).read_text() == "base-must-stay-unchanged" for name in protected)
    assert any(args[0] == "build" for args, _ in calls)


def test_prepare_refuses_overwrite_before_docker(prepared, product, monkeypatch):
    directory, _, _ = prepared
    monkeypatch.setattr(
        native.local, "docker", lambda *args, **kwargs: pytest.fail("Docker must not run")
    )
    with pytest.raises(ValueError, match="refuses to overwrite"):
        native.prepare(product, directory)


@pytest.mark.parametrize("failure", [None, "source", "state", "resources", "close"])
def test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base(
    prepared, monkeypatch, failure
):
    directory, record, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    atomic_text(directory / "workbench.env", "base-environment-unchanged")
    calls = []
    snapshot = record["snapshot"]
    existing = SimpleNamespace(
        name=snapshot["snapshot"],
        image_name=snapshot["digest"],
        state="active",
        cpu=2,
        mem=6,
        disk=30,
        entrypoint=[],
    )
    if failure == "source":
        existing.image_name = "mutable:tag"
    if failure == "state":
        existing.state = "failed"
    if failure == "resources":
        existing.mem = 12

    class Snapshots:
        def create(self, params, **kwargs):
            calls.append("create")
            assert params.image == snapshot["digest"]
            assert {
                name: getattr(params.resources, name) for name in native.RESOURCES
            } == native.RESOURCES
            assert params.region_id == "local" and kwargs["timeout"] == 600
            return existing

    client = SimpleNamespace(snapshot=Snapshots())

    def factory(settings):
        assert settings.daytona_api_key.get_secret_value() == KEY
        assert settings.daytona_api_url == "http://127.0.0.1:3000/api"
        assert settings.daytona_target == "local"
        return client

    def close(value):
        assert value is client
        calls.append("close")
        if failure == "close":
            raise RuntimeError("explicit close failure")

    monkeypatch.setattr(native, "install_loopback_guard", lambda: calls.append("guard"))
    monkeypatch.setattr(native, "client_for", factory)
    monkeypatch.setattr(native, "close_client", close)
    monkeypatch.setattr(native, "snapshot_named", lambda service, name: None)
    if failure:
        with pytest.raises((ValueError, RuntimeError)):
            native.register_worker(directory)
        assert not (directory / native.ENVIRONMENT).exists()
    else:
        native.register_worker(directory)
        content = (directory / native.ENVIRONMENT).read_text()
        assert KEY in content and "fastapiadmin/postgresql" in content
        assert "CAPABILITY_EXECUTION_ENABLED" not in content
        assert "local" in content
        monkeypatch.setattr(native, "snapshot_named", lambda service, name: existing)
        native.register_worker(directory)
        assert calls.count("create") == 1
        if os.name != "nt":
            assert (directory / native.ENVIRONMENT).stat().st_mode & 0o777 == 0o600
    assert calls[-1] == "close"
    assert (directory / "workbench.env").read_text() == "base-environment-unchanged"
    assert json.loads((directory / "api-key.json").read_text()) == {"value": KEY}


def test_registration_has_bounded_subprocess_and_no_key_in_argv(prepared, monkeypatch):
    directory, _, _ = prepared
    calls = []
    monkeypatch.setattr(native, "run_command", lambda *args, **kwargs: calls.append((args, kwargs)))
    native.register(directory)
    args, kwargs = calls[0]
    assert args[0][1:4] == ["-m", "scripts.daytona_native_capability_profile", "register-worker"]
    assert kwargs["timeout"] == 720
    assert KEY not in repr(calls)


def test_registration_does_not_overwrite_other_native_credentials(prepared, monkeypatch):
    directory, _, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    native.write_private_new(directory / native.ENVIRONMENT, "different credentials")
    monkeypatch.setattr(
        native, "client_for", lambda settings: pytest.fail("No SDK request allowed")
    )
    with pytest.raises(ValueError, match="refusing overwrite"):
        native.register_worker(directory)


def test_native_recipe_keeps_control_identity_pinned_tools_and_no_product_execution():
    recipe = (native.ROOT / native.DOCKERFILE).read_text()
    for text in (
        "ARG BASE_IMAGE",
        "FROM ${BASE_IMAGE}",
        "libseccomp2 procps",
        "postgresql-17",
        "redis-server",
        "pnpm@9.15.3",
        "--no-install-project",
        "--ignore-scripts",
        "--frozen-lockfile",
        "--store-dir /opt/rnd/pnpm-store",
        "node_modules/vue/package.json",
        "UV_OFFLINE=1",
        "WORKDIR /opt/rnd/control",
        "ENTRYPOINT []",
        "CMD []",
    ):
        assert text in recipe
    assert recipe.rstrip().endswith("USER 0:0")
    assert "warm.py" not in recipe and "vite build" not in recipe
    assert "CAPABILITY_EXECUTION_ENABLED" not in recipe


@pytest.mark.parametrize(
    "key", ["key\nREMOTE=x", "key;touch-payload", "key$(payload)", "key'quoted", "", None]
)
def test_existing_key_cannot_inject_environment_or_shell_syntax(key):
    with pytest.raises(ValueError, match="safely written"):
        native.environment_text(key, "rnd-native-fastapiadmin-" + "a" * 16)


def test_existing_native_environment_must_remain_private(prepared):
    if os.name == "nt":
        pytest.skip("POSIX file-mode contract")
    directory, record, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    path = directory / native.ENVIRONMENT
    atomic_text(path, native.environment_text(KEY, record["snapshot"]["snapshot"]))
    path.chmod(0o644)
    with pytest.raises(ValueError, match="private permissions"):
        native.register_worker(directory)


def test_native_metadata_cannot_be_adopted_through_a_symlink(prepared, tmp_path):
    directory, record, _ = prepared
    outside = tmp_path / "other-record.json"
    atomic_text(outside, json.dumps(record))
    (directory / native.LOCK).unlink()
    (directory / native.LOCK).symlink_to(outside)
    with pytest.raises(ValueError):
        native.require_native_profile(directory)
````
