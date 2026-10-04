# scripts/daytona_native_capability_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_native_capability_profile；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_bootstrap`、`workbench.catalog`、`workbench.daytona_profiles`、`workbench.domain`、`workbench.filesystem`、`workbench.local_only`、`workbench.sandbox`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `recipe_identity`（L69–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sha`、`digest`。 返回路径：L71的`digest(recipes), recipes`。
- `selection`（L74–L75）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Selection(template="fastapiadmin").model_dump`、`Selection`。 返回路径：L75的`Selection(template="fastapiadmin").model_dump()`。
- `reject_credentials`（L78–L85）：接收`text`。 源码说明：Never send authenticated registry configuration into Docker build layers.。 控制顺序：L80按`re.search(r"(?:_auth\|authToken\|password\|username)\s*[=:]\|\$\{", text, re.IGNORECA…`分支；L81抛异常，停止当前正常路径；L82遍历`re.findall(r"https?://[^\s\"'<>]+", text)`；L84按`parsed.username is not None or parsed.password is not None or parsed.query`分支；L85抛异常，停止当前正常路径。 调用`re.search`、`ValueError`、`re.findall`、`urlsplit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `product_inputs`（L88–L118）：接收`product`。 控制顺序：L93按`not isinstance(metadata, dict) or metadata.get("template") != "fastapiadmin"`分支；L94抛异常，停止当前正常路径；L95按`"selection" in metadata and Selection.model_validate(metadata["selection"]).model_dum…`分支；L99抛异常，停止当前正常路径；L100按`"database" in metadata and metadata["database"] != "postgresql"`分支；L101抛异常，停止当前正常路径；L102遍历`files(product)`；L103按`path.name == ".npmrc"`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path(product).resolve`、`Path`、`manifest`、`inside`、`json.loads`、`metadata_path.read_text`、`isinstance`、`metadata.get`、`ValueError`等。 返回路径：L112的`{ "product": str(product), "source_identity": digest(before), "manifest_sha256": before["d…`。
- `prepare_context`（L121–L191）：接收`product`、`context`、`expected`。先确定模板源码位置与摘要，再生成检索上下文；返回的内容在规划节点使用，不是只写报告后丢弃。 源码说明：Copy allowlisted lock inputs only, never executable product sources/hooks.。 控制顺序：L124按`product_inputs(product) != expected`分支；L125抛异常，停止当前正常路径；L126遍历`DESCRIPTORS`；L130按`base.sha256(raw) != expected["descriptors"][name]`分支；L131抛异常，停止当前正常路径；L132按`name.startswith("backend/")`分支；L157遍历`("pyproject.toml", "uv.lock")`；L164遍历`("image", "build")`。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`product_inputs`、`ValueError`、`inside`、`target.parent.mkdir`、`inside(product, name).read_bytes`、`base.sha256`、`name.startswith`、`raw.decode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `base_identity`（L194–L202）：接收`record`。 调用`copy.deepcopy`。 返回路径：L195的`{ "profile": record["profile"], "recipe_identity": record["recipe_identity"], "snapshot_im…`。
- `native_stamp`（L205–L214）：接收`identity`、`foundation`、`inputs`。 调用`digest`、`selection`。 返回路径：L206的`digest( { "recipe_identity": identity, "base": foundation, "inputs": inputs, "selection": …`。
- `validate_image`（L217–L236）：接收`image`、`record`。 控制顺序：L220按`image.get("Os") != "linux" or image.get("Architecture") != "amd64" or labels.get("org…`分支；L236抛异常，停止当前正常路径。 调用`image.get`、`config.get`、`labels.get`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `write_private_new`（L239–L245）：接收`path`、`text`。 源码说明：Exclusive creation prevents replacing base metadata or an existing credential.。 调用`os.open`、`os.fdopen`、`output.write`、`output.flush`、`os.fsync`、`output.fileno`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prepare`（L248–L335）：接收`product`、`directory`。 控制顺序：L252按`any((directory / name).exists() for name in (LOCK, ENVIRONMENT))`分支；L253抛异常，停止当前正常路径；L293遍历`labels.items()`；L310按`len(digests) != 1 or published["Id"] != image["Id"]`分支；L311抛异常，停止当前正常路径；L327按`base_identity(base.require_profile(directory)) != foundation or product_inputs(produc…`分支；L332抛异常，停止当前正常路径。 调用`base.profile_directory`、`base_identity`、`base.require_profile`、`any`、`(directory / name).exists`、`ValueError`、`product_inputs`、`recipe_identity`、`native_stamp`等。 返回路径：L335的`record`。
- `require_native_profile`（L338–L380）：接收`directory`、`snapshot`。 源码说明：Read-only identity proof; runtime isolation/resource evidence is separate.。 控制顺序：L345按`record.get("profile") != PROFILE or record.get("selection") != selection() or record.…`分支；L357抛异常，停止当前正常路径；L361按`image.get("source_hash") != stamp or image.get("local_tag") != "127.0.0.1:6000/" + FA…`分支；L373抛异常，停止当前正常路径；L377按`inspected["Id"] != image["image_id"] or local_digest not in inspected.get("RepoDigest…`分支；L378抛异常，停止当前正常路径。 调用`base.profile_directory`、`base_identity`、`base.require_profile`、`json.loads`、`inside(directory, LOCK).read_text`、`inside`、`recipe_identity`、`record.get`、`selection`等。 返回路径：L380的`record`。
- `environment_text`（L383–L394）：接收`key`、`snapshot`。 控制顺序：L384按`not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,4096}", key)`分支；L385抛异常，停止当前正常路径。 调用`isinstance`、`re.fullmatch`、`ValueError`、`json.dumps`。 返回路径：L386的`"SANDBOX_PROVIDER=daytona\nDAYTONA_ALLOW_LOCAL_EXECUTION=true\n" "DAYTONA_API_URL=http://1…`。
- `register`（L397–L412）：接收`directory`。 调用`base.profile_directory`、`require_native_profile`、`run_command`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `register_worker`（L415–L464）：接收`directory`。 控制顺序：L422按`path.exists() and os.name != "nt" and path.stat().st_mode & 0o777 != 0o600`分支；L423抛异常，停止当前正常路径；L424按`path.exists() and path.read_text(encoding="utf-8") != content`分支；L425抛异常，停止当前正常路径；L440按`existing is None`分支；L450按`existing.name != metadata["snapshot"] or existing.image_name != metadata["digest"] or…`分支；L459抛异常，停止当前正常路径；L463按`not path.exists()`分支。 调用`base.profile_directory`、`require_native_profile`、`json.loads`、`(directory / "api-key.json").read_text`、`environment_text`、`inside`、`path.exists`、`path.stat`、`ValueError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L467–L483）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L473按`args.action == "prepare"`分支；L474按`args.product is None`分支；L477按`args.action == "check"`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`parser.error`、`prepare`、`require_native_profile`、`{"register": register, "register-worker": register_worker}[args.a…`、`print`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_native_capability_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L493。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`20452`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_native_capability_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "372bb7bc199011914d675d55c8c0189826a5c5fe83686fc5b27db7757d8264b7"} -->
````python
# scripts/daytona_native_capability_profile.py
"""Prepare/register the opt-in native profile without changing the base installation.

Only dependency descriptors reach the build context. Candidate source, frontend lifecycle hooks,
credentials and deployment control modules are never executed during preparation.
The warmed image is not runtime, browser, database or isolation acceptance evidence.
"""

import argparse
import copy
import json
import os
import re
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import SecretStr

from scripts import daytona_capability_profile as base
from scripts import daytona_dependency_build as dependencies
from scripts import daytona_local as local
from scripts.daytona_bootstrap import snapshot_named
from workbench.catalog import Selection
from workbench.daytona_profiles import dependency_identity
from workbench.domain import digest
from workbench.filesystem import files, inside, manifest, sha
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client
from workbench.settings import ROOT, Settings
from workbench.tools import run_command

HOME = base.HOME
PROFILE = "native-fastapiadmin-postgresql-v1"
LOCK = "native-fastapiadmin-profile.json"
ENVIRONMENT = "fastapiadmin.env"
FAMILY = "rnd-native-fastapiadmin"
RESOURCES = {"cpu": 2, "memory": 6, "disk": 30}
DOCKERFILE = "tools/daytona/capability-native-snapshot.Dockerfile"
RECIPE_PATHS = (
    "scripts/daytona_native_capability_profile.py",
    "scripts/daytona_dependency_image.py",
    "scripts/daytona_dependency_build.py",
    "scripts/daytona_dependency_build.lock.json",
    DOCKERFILE,
    # Record the matrix recipe lineage as well as the distinct safe warming recipe.
    "scripts/daytona_matrix_image.py",
    "tools/daytona/matrix.Dockerfile",
    "tools/daytona/warm.py",
    "workbench/daytona_profiles.py",
    "workbench/filesystem.py",
    "workbench/catalog.py",
    "workbench/template_adapters.py",
    "pyproject.toml",
    "uv.lock",
)
DESCRIPTORS = (
    "backend/pyproject.toml",
    "backend/uv.lock",
    "deployment/pyproject.toml",
    "deployment/uv.lock",
    "frontend/web/package.json",
    "frontend/web/pnpm-lock.yaml",
)


def recipe_identity():
    recipes = {name: sha(ROOT / name) for name in RECIPE_PATHS}
    return digest(recipes), recipes


def selection():
    return Selection(template="fastapiadmin").model_dump()


def reject_credentials(text):
    """Never send authenticated registry configuration into Docker build layers."""
    if re.search(r"(?:_auth|authToken|password|username)\s*[=:]|\$\{", text, re.IGNORECASE):
        raise ValueError("Authenticated dependency configuration is not a native build input")
    for url in re.findall(r"https?://[^\s\"'<>]+", text):
        parsed = urlsplit(url)
        if parsed.username is not None or parsed.password is not None or parsed.query:
            raise ValueError("Credential-bearing dependency URLs are not native build inputs")


def product_inputs(product):
    product = Path(product).resolve()
    before = manifest(product)
    metadata_path = inside(product, "deployment/manifest.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or metadata.get("template") != "fastapiadmin":
        raise ValueError("Native snapshot requires an exact fastapiadmin deployment manifest")
    if (
        "selection" in metadata
        and Selection.model_validate(metadata["selection"]).model_dump() != selection()
    ):
        raise ValueError("Native snapshot requires the registered PostgreSQL selection")
    if "database" in metadata and metadata["database"] != "postgresql":
        raise ValueError("Native snapshot requires PostgreSQL")
    for name, path in files(product):
        if path.name == ".npmrc":
            reject_credentials(path.read_text(encoding="utf-8"))
    for name in DESCRIPTORS:
        if name not in before:
            raise ValueError("Native snapshot is missing a dependency descriptor: " + name)
        reject_credentials(inside(product, name).read_text(encoding="utf-8"))
    identity = dependency_identity(product)
    if manifest(product) != before:
        raise ValueError("Native input changed while computing its identity")
    return {
        "product": str(product),
        "source_identity": digest(before),
        "manifest_sha256": before["deployment/manifest.json"],
        "descriptors": {name: before[name] for name in DESCRIPTORS},
        "dependency_identity": identity,
    }


def prepare_context(product, context, expected):
    """Copy allowlisted lock inputs only, never executable product sources/hooks."""
    product, context = Path(product), Path(context)
    if product_inputs(product) != expected:
        raise ValueError("Native input changed before preparing the build context")
    for name in DESCRIPTORS:
        target = inside(context / "product", name)
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = inside(product, name).read_bytes()
        if base.sha256(raw) != expected["descriptors"][name]:
            raise ValueError("Native dependency input changed during copy")
        if name.startswith("backend/"):
            # Same exact public-mirror substitutions as prepare_fastapi_registry.
            # Do not import or copy product/deployment/workbench to perform them.
            text = raw.decode("utf-8")
            tomllib.loads(text)
            text = text.replace(
                "https://pypi.tuna.tsinghua.edu.cn/simple", "https://pypi.org/simple"
            )
            text = text.replace(
                "https://pypi.tuna.tsinghua.edu.cn/packages/",
                "https://files.pythonhosted.org/packages/",
            )
            tomllib.loads(text)
            raw = text.encode("utf-8")
        target.write_bytes(raw)
    dependencies.validate_python(
        (context / "product/backend/pyproject.toml").read_bytes(),
        (context / "product/backend/uv.lock").read_bytes(),
    )
    dependencies.validate_node(
        (context / "product/frontend/web/package.json").read_bytes(),
        (context / "product/frontend/web/pnpm-lock.yaml").read_bytes(),
    )
    harness = context / "harness"
    harness.mkdir()
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / name, harness / name)
    dependencies.validate_python(
        (harness / "pyproject.toml").read_bytes(),
        (harness / "uv.lock").read_bytes(),
        trusted_project=True,
    )
    for name in ("image", "build"):
        shutil.copyfile(
            ROOT / f"scripts/daytona_dependency_{name}.py",
            context / f"dependency-{name}.py",
        )
    shutil.copyfile(
        ROOT / "scripts/daytona_dependency_build.lock.json",
        context / "dependency-build.lock.json",
    )
    (context / "dependency-inputs.json").write_text(
        json.dumps(
            {
                "recipe_identity": recipe_identity()[0],
                "original_descriptors": expected["descriptors"],
                "harness_descriptors": {
                    name: sha(harness / name) for name in ("pyproject.toml", "uv.lock")
                },
                "normalized_descriptors": {
                    name: sha(context / "product" / name) for name in DESCRIPTORS
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    shutil.copyfile(ROOT / DOCKERFILE, context / "Dockerfile")
    if product_inputs(product) != expected:
        raise ValueError("Native input changed while preparing the build context")


def base_identity(record):
    return {
        "profile": record["profile"],
        "recipe_identity": record["recipe_identity"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "runner": copy.deepcopy(record["runner"]),
        "rust_image": copy.deepcopy(record["bases"]["RUST_IMAGE"]),
    }


def native_stamp(identity, foundation, inputs):
    return digest(
        {
            "recipe_identity": identity,
            "base": foundation,
            "inputs": inputs,
            "selection": selection(),
            "resources": RESOURCES,
        }
    )[:16]


def validate_image(image, record):
    config = image.get("Config") or {}
    labels = config.get("Labels") or {}
    if (
        image.get("Os") != "linux"
        or image.get("Architecture") != "amd64"
        or labels.get("org.opencontainers.image.revision") != base.DAYTONA_SOURCE
        or labels.get("rnd.capability.profile") != PROFILE
        or labels.get("rnd.capability.recipe") != record["recipe_identity"]
        or labels.get("rnd.capability.base-recipe") != record["base"]["recipe_identity"]
        or labels.get("rnd.capability.base-image") != record["base"]["snapshot_image_id"]
        or labels.get("rnd.capability.base-digest") != record["base"]["snapshot_digest"]
        or labels.get("rnd.capability.dependencies") != record["dependency_identity"]
        or labels.get("rnd.capability.input") != record["inputs"]["source_identity"]
        or config.get("User") != "0:0"
        or config.get("WorkingDir") != base.CONTROL_WORKDIR
        or config.get("Entrypoint")
        or config.get("Cmd")
    ):
        raise ValueError("Native image does not match its reviewed root-control recipe")


def write_private_new(path, text):
    """Exclusive creation prevents replacing base metadata or an existing credential."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
        output.write(text)
        output.flush()
        os.fsync(output.fileno())


def prepare(product, directory=HOME):
    directory = base.profile_directory(directory)
    # The verified root-control Runner is reused unchanged, never rebuilt here.
    foundation = base_identity(base.require_profile(directory))
    if any((directory / name).exists() for name in (LOCK, ENVIRONMENT)):
        raise ValueError("Native setup refuses to overwrite an existing profile or environment")
    inputs = product_inputs(product)
    identity, recipes = recipe_identity()
    stamp = native_stamp(identity, foundation, inputs)
    tag = "127.0.0.1:6000/" + FAMILY + ":" + stamp
    record = {
        "profile": PROFILE,
        "selection": selection(),
        "recipe_identity": identity,
        "recipes": recipes,
        "base": foundation,
        "runner": copy.deepcopy(foundation["runner"]),
        "inputs": inputs,
        "dependency_identity": inputs["dependency_identity"],
        "resources": dict(RESOURCES),
    }
    with tempfile.TemporaryDirectory(prefix="native-capability-build-", dir=directory) as temporary:
        context = Path(temporary)
        prepare_context(product, context, inputs)
        argv = [
            "build",
            "--progress=plain",
            "--platform=linux/amd64",
            "--pull=false",
            "--build-arg",
            "BASE_IMAGE="
            + foundation["snapshot_digest"].replace("registry:6000/", "127.0.0.1:6000/", 1),
            "--build-arg",
            "RUST_IMAGE=" + foundation["rust_image"]["digest"],
        ]
        labels = {
            "org.opencontainers.image.revision": base.DAYTONA_SOURCE,
            "rnd.capability.profile": PROFILE,
            "rnd.capability.recipe": identity,
            "rnd.capability.base-recipe": foundation["recipe_identity"],
            "rnd.capability.base-image": foundation["snapshot_image_id"],
            "rnd.capability.base-digest": foundation["snapshot_digest"],
            "rnd.capability.dependencies": inputs["dependency_identity"],
            "rnd.capability.input": inputs["source_identity"],
        }
        for name, value in labels.items():
            argv += ["--label", name + "=" + value]
        argv += ["--tag", tag, str(context)]
        local.docker(*argv, timeout=3600)
    image = base.inspect_image(tag)
    validate_image(image, record)
    base.compose(directory, "up", "-d", "--pull", "never", "registry", "gateway")
    local.wait_for_registry()
    local.docker("push", tag, timeout=1200)
    published = base.inspect_image(tag)
    validate_image(published, record)
    prefix = "127.0.0.1:6000/" + FAMILY + "@sha256:"
    digests = [
        value
        for value in published.get("RepoDigests", [])
        if re.fullmatch(re.escape(prefix) + r"[a-f0-9]{64}", value)
    ]
    if len(digests) != 1 or published["Id"] != image["Id"]:
        raise ValueError("Native publication changed image identity or has no unique digest")
    immutable = digests[0].replace("127.0.0.1:6000/", "registry:6000/", 1)
    record["snapshot"] = {
        "image": immutable,
        "digest": immutable,
        "image_id": image["Id"],
        "local_tag": tag,
        "source_hash": stamp,
        "snapshot": FAMILY + "-" + stamp,
        "user": "0:0",
        "working_dir": base.CONTROL_WORKDIR,
        "recipe_sha256": recipes[DOCKERFILE],
    }
    record["snapshot"]["dependency_manifest"] = base.inspect_dependency_manifest(
        image["Id"], "fastapiadmin", inputs["descriptors"]
    )
    if (
        base_identity(base.require_profile(directory)) != foundation
        or product_inputs(product) != inputs
        or recipe_identity() != (identity, recipes)
    ):
        raise ValueError("Native build inputs or base profile changed during preparation")
    # Publish readiness last. Base snapshot-image.json/workbench.env are untouched.
    write_private_new(directory / LOCK, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return record


def require_native_profile(directory=HOME, snapshot=None):
    """Read-only identity proof; runtime isolation/resource evidence is separate."""
    directory = base.profile_directory(directory)
    foundation = base_identity(base.require_profile(directory))
    record = json.loads(inside(directory, LOCK).read_text(encoding="utf-8"))
    identity, recipes = recipe_identity()
    inputs = record.get("inputs", {})
    if (
        record.get("profile") != PROFILE
        or record.get("selection") != selection()
        or record.get("recipe_identity") != identity
        or record.get("recipes") != recipes
        or record.get("base") != foundation
        or record.get("runner") != foundation["runner"]
        or record.get("resources") != RESOURCES
        or not inputs.get("product")
        or inputs != product_inputs(inputs["product"])
        or record.get("dependency_identity") != inputs.get("dependency_identity")
    ):
        raise ValueError("Native profile recipe, dependency input or base identity changed")
    stamp = native_stamp(identity, foundation, inputs)
    image = record.get("snapshot", {})
    expected_digest = image.get("digest", "")
    if (
        image.get("source_hash") != stamp
        or image.get("local_tag") != "127.0.0.1:6000/" + FAMILY + ":" + stamp
        or image.get("snapshot") != FAMILY + "-" + stamp
        or image.get("image") != expected_digest
        or not re.fullmatch(r"registry:6000/" + FAMILY + r"@sha256:[a-f0-9]{64}", expected_digest)
        or not re.fullmatch(r"sha256:[a-f0-9]{64}", image.get("image_id", ""))
        or image.get("user") != "0:0"
        or image.get("working_dir") != base.CONTROL_WORKDIR
        or image.get("recipe_sha256") != recipes[DOCKERFILE]
        or (snapshot is not None and snapshot != image.get("snapshot"))
    ):
        raise ValueError("Native snapshot lock differs from its exact derived identity")
    inspected = base.inspect_image(image["local_tag"])
    validate_image(inspected, record)
    local_digest = expected_digest.replace("registry:6000/", "127.0.0.1:6000/", 1)
    if inspected["Id"] != image["image_id"] or local_digest not in inspected.get("RepoDigests", []):
        raise ValueError("Native snapshot tag no longer matches its immutable ID and digest")
    base.require_dependency_manifest(record, "fastapiadmin", inputs["descriptors"])
    return record


def environment_text(key, snapshot):
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,4096}", key):
        raise ValueError("Existing local account key cannot be safely written as environment data")
    return (
        "SANDBOX_PROVIDER=daytona\nDAYTONA_ALLOW_LOCAL_EXECUTION=true\n"
        "DAYTONA_API_URL=http://127.0.0.1:3000/api\nDAYTONA_TARGET=local\n"
        f"DAYTONA_API_KEY={key}\nDAYTONA_SNAPSHOT={snapshot}\n"
        + "DAYTONA_SNAPSHOTS='"
        + json.dumps({"fastapiadmin/postgresql": snapshot}, separators=(",", ":"))
        + "'\n"
        + "TOOL_TIMEOUT=300\n"
    )


def register(directory=HOME):
    directory = base.profile_directory(directory)
    require_native_profile(directory)
    run_command(
        [
            sys.executable,
            "-m",
            "scripts.daytona_native_capability_profile",
            "register-worker",
            "--directory",
            str(directory),
        ],
        ROOT,
        timeout=720,
        heartbeat="Local native snapshot registration",
    )


def register_worker(directory=HOME):
    directory = base.profile_directory(directory)
    record = require_native_profile(directory)
    metadata = record["snapshot"]
    key = json.loads((directory / "api-key.json").read_text(encoding="utf-8"))["value"]
    content = environment_text(key, metadata["snapshot"])
    path = inside(directory, ENVIRONMENT)
    if path.exists() and os.name != "nt" and path.stat().st_mode & 0o777 != 0o600:
        raise ValueError("Existing native environment does not have private permissions")
    if path.exists() and path.read_text(encoding="utf-8") != content:
        raise ValueError(
            "Native environment already exists with different values; refusing overwrite"
        )
    install_loopback_guard()
    from daytona import CreateSnapshotParams, Resources

    settings = Settings(
        _env_file=None,
        daytona_api_key=SecretStr(key),
        daytona_api_url="http://127.0.0.1:3000/api",
        daytona_target="local",
    )
    client = client_for(settings)
    try:
        existing = snapshot_named(client.snapshot, metadata["snapshot"])
        if existing is None:
            existing = client.snapshot.create(
                CreateSnapshotParams(
                    name=metadata["snapshot"],
                    image=metadata["digest"],
                    region_id="local",
                    resources=Resources(**RESOURCES),
                ),
                timeout=600,
            )
        if (
            existing.name != metadata["snapshot"]
            or existing.image_name != metadata["digest"]
            or str(getattr(existing.state, "value", existing.state)).lower() != "active"
            or existing.cpu != RESOURCES["cpu"]
            or existing.mem != RESOURCES["memory"]
            or existing.disk != RESOURCES["disk"]
            or existing.entrypoint
        ):
            raise ValueError("Existing native snapshot differs in identity, state or resources")
    finally:
        close_client(client)
    require_native_profile(directory, metadata["snapshot"])
    if not path.exists():
        write_private_new(path, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "register", "register-worker", "check"])
    parser.add_argument("--directory", type=Path, default=HOME)
    parser.add_argument("--product", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        if args.product is None:
            parser.error("prepare requires --product pointing to an already-generated product")
        prepare(args.product, args.directory)
    elif args.action == "check":
        require_native_profile(args.directory)
    else:
        {"register": register, "register-worker": register_worker}[args.action](args.directory)
    print(
        "Native snapshot identity step completed; runtime/isolation acceptance is still required."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # SDK/build exceptions can contain registry or account data. Never print them.
        raise SystemExit(
            "Native profile step failed; no new readiness assertion was made."
        ) from None
````
