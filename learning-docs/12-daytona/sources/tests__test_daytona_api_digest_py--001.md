# tests/test_daytona_api_digest.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `exported_api`（L24–L29）：接收`tmp_path`。 调用`target.parent.mkdir`、`target.write_bytes`、`FIXTURE.read_bytes`。 返回路径：L29的`context, target`。
- `test_api_digest_patch_has_exact_upstream_and_patch_identities`（L32–L55）：接收`exported_api`。 控制顺序：L35断言`build.DAYTONA_SOURCE == "01c502bb1f1ff8f2885d0cd490e043736083dca8"`；L36断言`build.DAYTONA_VERSION == "0.190.0"`；L37断言`build.API_IMAGE_BLOB == "b0b03b28ce08b2865db9d2dc291c1745cb6492cf"`；L38断言`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == build.AP…`；L43断言`result == { "path": build.API_IMAGE_FILE, "preimage_blob": build.API_IMAGE_BLOB, "pat…`；L49断言`target.read_bytes() == raw.replace( build.API_IMAGE_OLD.encode(), build.API_IMAGE_NEW…`；L52断言`hashlib.sha256(target.read_bytes()).hexdigest() == PATCHED_SHA256`；L53断言`FIXTURE.read_bytes() == raw`。 调用`target.read_bytes`、`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hex…`、`hashlib.sha1`、`str(len(raw)).encode`、`str`、`len`、`build.patch_api_image_reference`、`raw.replace`、`build.API_IMAGE_OLD.encode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_api_digest_patch_rejects_drift_before_writing_or_building`（L59–L80）：接收`exported_api`、`monkeypatch`、`tmp_path`、`drift`。 控制顺序：L63按`drift == "source"`分支；L65按`drift == "revision"`分支；L67按`drift == "version"`分支；L79断言`target.read_bytes() == before`；L80断言`not (tmp_path / "build-recipes").exists()`。 调用`target.write_bytes`、`target.read_bytes`、`monkeypatch.setattr`、`patch.parent.mkdir`、`patch.write_bytes`、`(build.ROOT / build.API_IMAGE_PATCH).read_bytes`、`pytest.fail`、`pytest.raises`、`build.build_exported`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run_utility`（L83–L121）：接收`source`、`references`、`registry`。 控制顺序：L85按`not node`分支；L86按`os.environ.get("RND_REQUIRE_NODE_TESTS") == "1"`分支。 调用`shutil.which`、`os.environ.get`、`pytest.fail`、`pytest.skip`、`subprocess.run`、`source.as_uri`、`json.dumps`、`json.loads`。 返回路径：L121的`json.loads(result.stdout)`。
- `test_real_upstream_digest_roundtrips_and_non_digest_behavior`（L124–L174）：接收`exported_api`。 控制顺序：L153断言`[item["serialized"] for item in original_digest] == [ value.replace("@", ":") for val…`；L157断言`all("error" in item for item in before[len(ordinary) :])`；L159断言`run_utility(target, digests) == [ {"serialized": value, "roundtrip": value} for value…`；L162断言`run_utility(target, ordinary + malformed) == before`；L163断言`[item["serialized"] for item in before[: len(ordinary)]] == ordinary`；L166断言`run_utility(target, [malformed_separator]) == [ {"serialized": malformed_separator, "…`；L172断言`run_utility(target, [value], "registry:6000") == [ {"serialized": expected, "roundtri…`。 调用`run_utility`、`value.replace`、`all`、`len`、`build.patch_api_image_reference`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_api_build_binds_patch_to_image_and_lock`（L180–L237）：接收`exported_api`、`tmp_path`、`monkeypatch`、`bad_label`。 控制顺序：L185遍历`build.SOURCE_RECIPES.items()`；L219按`bad_label`分支；L222断言`len(calls) == 1`；L225断言`len(calls) == 3`；L226断言`metadata["api"]["source_sha"] == build.API_PATCH_SOURCE`；L227断言`metadata["api"]["source_patch"] == { "path": build.API_IMAGE_FILE, "preimage_blob": b…`；L233断言`labels[build.local_tag("api")]["rnd.daytona.api-source-sha256"] == PATCHED_SHA256`；L234断言`labels[build.local_tag("api")]["rnd.daytona.api-patch-sha256"] == PATCH_SHA256`。后续分支沿下方源码相同行号继续阅读。 调用`build.SOURCE_RECIPES.items`、`path.parent.mkdir`、`path.write_bytes`、`hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hex…`、`hashlib.sha1`、`str(len(raw)).encode`、`str`、`len`、`monkeypatch.setattr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_api_build_binds_patch_to_image_and_lock.run`（L201–L209）：接收`argv`、`_cwd`、`**_kwargs`。 控制顺序：L202断言`hashlib.sha256(target.read_bytes()).hexdigest() == PATCHED_SHA256`；L208断言`argv[-1] == str(context if len(calls) < 3 else tmp_path / "runner-context")`。 调用`hashlib.sha256(target.read_bytes()).hexdigest`、`hashlib.sha256`、`target.read_bytes`、`calls.append`、`argv.index`、`dict`、`argv[index + 1].split`、`enumerate`、`str`等。 返回路径：L209的`{"log": "fixture build only"}`。
- `test_actual_api_build_binds_patch_to_image_and_lock.docker`（L211–L216）：接收`*args`。 控制顺序：L212断言`args[:2] == ("image", "inspect")`；L214按`args[2] == build.local_tag("api") and bad_label`分支。 调用`dict`、`build.local_tag`、`json.dumps`。 返回路径：L216的`json.dumps([{"Id": "sha256:" + "b" * 64, "Config": {"Labels": actual}}])`。
- `test_runtime_rejects_old_or_tampered_api_before_start_or_admission`（L260–L354）：接收`tmp_path`、`monkeypatch`、`boundary`、`mutation`。 控制顺序：L266遍历`local.IMAGES.items()`；L273按`name == "gateway"`分支；L289按`mutation == "missing-patch"`分支；L291按`mutation == "missing-field"`分支；L293按`mutation == "stale-source"`分支；L295按`mutation == "changed-preimage"`分支；L297按`mutation == "changed-patch"`分支；L299按`mutation == "changed-output"`分支。后续分支沿下方源码相同行号继续阅读。 调用`copy.deepcopy`、`local.IMAGES.items`、`tag.rsplit`、`local.gateway_service`、`record.update`、`build.api_patch_identity`、`build.api_patch_labels`、`build.local_tag`、`image["Config"]["Labels"].pop`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_rejects_old_or_tampered_api_before_start_or_admission.docker`（L330–L336）：接收`*args`、`**kwargs`。 控制顺序：L332按`args[0] == "image"`分支；L333断言`args == ("image", "inspect", api_id)`；L335断言`mutation is None and args[0] == "compose"`。 调用`calls.append`、`json.dumps`。 返回路径：L334的`json.dumps([image])`；L336的`"fixture start only"`。
- `test_runtime_rejects_old_or_tampered_api_before_start_or_admission.run`（L340–L345）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`local.compose`、`profile.read_base`。 返回路径：L341的`local.compose(tmp_path, "up", "-d") if boundary == "compose" else profile.read_base(tmp_pa…`。
- `test_profile_ci_executes_upstream_digest_regression_before_builds`（L358–L365）：接收`name`。 控制顺序：L360断言`"tests/test_daytona_api_digest.py" in text`；L361断言`text.index("actions/setup-node@") < text.index("tests/test_daytona_api_digest.py")`；L362断言`text.index("tests/test_daytona_api_digest.py") < text.index( "scripts.daytona_local i…`；L365断言`"RND_REQUIRE_NODE_TESTS: '1'" in text`。 调用`(build.ROOT / ".github/workflows" / name).read_text`、`text.index`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_api_digest.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L365。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14207`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_api_digest.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "093ba211d6a6ea6c6d426d246665e9aed84da1d0d23ad4a9f9330f10f27ba4e9"} -->
````python
# tests/test_daytona_api_digest.py
"""Execute the pinned API utility; no registry, Docker or runtime acceptance is faked."""

import copy
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import daytona_build as build
from scripts import daytona_capability_profile as profile
from scripts import daytona_local as local

FIXTURE = Path(__file__).parent / "fixtures/daytona/docker-image.util.ts"
PATCH_SHA256 = "d547f0e6dc75aea73b1fd907fd7cebe928d11782f18230ffec212c4cbc31a437"
PATCHED_SHA256 = "28a51752e5a1d12a6172723b27612b07917fd4612b49d48874dcc18a1b7736b9"


@pytest.fixture
def exported_api(tmp_path):
    context = tmp_path / "exported"
    target = context / build.API_IMAGE_FILE
    target.parent.mkdir(parents=True)
    target.write_bytes(FIXTURE.read_bytes())
    return context, target


def test_api_digest_patch_has_exact_upstream_and_patch_identities(exported_api):
    context, target = exported_api
    raw = target.read_bytes()
    assert build.DAYTONA_SOURCE == "01c502bb1f1ff8f2885d0cd490e043736083dca8"
    assert build.DAYTONA_VERSION == "0.190.0"
    assert build.API_IMAGE_BLOB == "b0b03b28ce08b2865db9d2dc291c1745cb6492cf"
    assert (
        hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        == build.API_IMAGE_BLOB
    )
    result = build.patch_api_image_reference(context)
    assert result == {
        "path": build.API_IMAGE_FILE,
        "preimage_blob": build.API_IMAGE_BLOB,
        "patched_sha256": PATCHED_SHA256,
        "patch_sha256": PATCH_SHA256,
    }
    assert target.read_bytes() == raw.replace(
        build.API_IMAGE_OLD.encode(), build.API_IMAGE_NEW.encode()
    )
    assert hashlib.sha256(target.read_bytes()).hexdigest() == PATCHED_SHA256
    assert FIXTURE.read_bytes() == raw
    with pytest.raises(ValueError, match="preimage"):
        build.patch_api_image_reference(context)


@pytest.mark.parametrize("drift", ["source", "revision", "version", "patch"])
def test_api_digest_patch_rejects_drift_before_writing_or_building(
    exported_api, monkeypatch, tmp_path, drift
):
    context, target = exported_api
    if drift == "source":
        target.write_bytes(target.read_bytes() + b"// unexpected source change\n")
    elif drift == "revision":
        monkeypatch.setattr(build, "DAYTONA_SOURCE", "0" * 40)
    elif drift == "version":
        monkeypatch.setattr(build, "DAYTONA_VERSION", "0.190.1")
    else:
        patch = tmp_path / build.API_IMAGE_PATCH
        patch.parent.mkdir(parents=True)
        patch.write_bytes((build.ROOT / build.API_IMAGE_PATCH).read_bytes() + b"\n")
        monkeypatch.setattr(build, "ROOT", tmp_path)
    before = target.read_bytes()
    monkeypatch.setattr(build, "download_runner", lambda *_: pytest.fail("no download on drift"))
    monkeypatch.setattr(build, "run_command", lambda *_a, **_k: pytest.fail("no build on drift"))
    with pytest.raises(ValueError, match="preimage|revision|reviewed change"):
        build.build_exported(tmp_path, context, lambda *_: pytest.fail("no Docker on drift"))
    assert target.read_bytes() == before
    assert not (tmp_path / "build-recipes").exists()


def run_utility(source, references, registry=None):
    node = shutil.which("node")
    if not node:
        if os.environ.get("RND_REQUIRE_NODE_TESTS") == "1":
            pytest.fail("Node is required to execute the pinned API image-reference utility")
        pytest.skip("Node unavailable; pinned upstream TypeScript was not executed")
    # Use Node's parser, not a copied Python/JavaScript rewrite of the utility.
    script = """const { parseDockerImage } = await import(process.argv[1]);
const references = JSON.parse(process.argv[2]);
const registry = JSON.parse(process.argv[3]);
const results = references.map(reference => {
  try {
    const image = parseDockerImage(reference);
    if (registry && !image.registry) image.registry = registry;
    const serialized = image.getFullName();
    return { serialized, roundtrip: parseDockerImage(serialized).getFullName() };
  } catch (error) {
    return { error: error.message };
  }
});
process.stdout.write(JSON.stringify(results));
"""
    result = subprocess.run(
        [
            node,
            "--experimental-strip-types",
            "--input-type=module",
            "-e",
            script,
            source.as_uri(),
            json.dumps(references),
            json.dumps(registry),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return json.loads(result.stdout)


def test_real_upstream_digest_roundtrips_and_non_digest_behavior(exported_api):
    context, target = exported_api
    digest = "sha256:" + "a" * 64
    repositories = [
        "ubuntu",
        "team/image",
        "docker.io/library/ubuntu",
        "registry:6000/rnd-native-fastapiadmin",
        "registry:6000/team/nested/image",
        "localhost:6000/team/nested/image",
        "registry.example/team/nested/image",
    ]
    digests = [name + "@" + digest for name in repositories]
    digests += [name + ":latest@" + digest for name in repositories]
    ordinary = [
        name + suffix for name in repositories for suffix in ("", ":latest", ":v1", ":sha256")
    ]
    malformed = [
        "",
        "image@sha256:",
        "image@sha256:" + "a" * 63,
        "image@sha256:" + "a" * 65,
        "image@sha256:" + "A" * 64,
        "image@sha256:" + "g" * 64,
        "@" + digest,
        "registry:6000//image@" + digest,
        "/image@" + digest,
    ]
    original_digest = run_utility(target, digests)
    assert [item["serialized"] for item in original_digest] == [
        value.replace("@", ":") for value in digests
    ]
    before = run_utility(target, ordinary + malformed)
    assert all("error" in item for item in before[len(ordinary) :])
    build.patch_api_image_reference(context)
    assert run_utility(target, digests) == [
        {"serialized": value, "roundtrip": value} for value in digests
    ]
    assert run_utility(target, ordinary + malformed) == before
    assert [item["serialized"] for item in before[: len(ordinary)]] == ordinary
    malformed_separator = "registry:6000/team/image:" + digest
    # Do not reinterpret the original invalid ':sha256:hash' string as a digest.
    assert run_utility(target, [malformed_separator]) == [
        {"serialized": malformed_separator, "roundtrip": malformed_separator}
    ]
    # SnapshotManager may add the resolved registry to an unqualified image.
    value = "team/nested/image@" + digest
    expected = "registry:6000/" + value
    assert run_utility(target, [value], "registry:6000") == [
        {"serialized": expected, "roundtrip": expected}
    ]


@pytest.mark.parametrize(
    "bad_label", [None, "rnd.daytona.api-source-sha256", "rnd.daytona.api-patch-sha256"]
)
def test_actual_api_build_binds_patch_to_image_and_lock(
    exported_api, tmp_path, monkeypatch, bad_label
):
    context, target = exported_api
    recipes = {}
    for name, (stage, _) in build.SOURCE_RECIPES.items():
        path = context / f"apps/{name}/Dockerfile"
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = b"FROM node:24-slim AS fixture\nENV CI=true\nRUN echo fixture\n"
        path.write_bytes(raw)
        recipes[name] = (
            stage,
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
        )
    monkeypatch.setattr(build, "SOURCE_RECIPES", recipes)
    monkeypatch.setattr(
        build, "download_runner", lambda path: path.write_bytes(b"not-executable-fixture")
    )
    calls = []
    labels = {}

    def run(argv, _cwd, **_kwargs):
        assert hashlib.sha256(target.read_bytes()).hexdigest() == PATCHED_SHA256
        calls.append(argv)
        tag = argv[argv.index("--tag") + 1]
        labels[tag] = dict(
            argv[index + 1].split("=", 1) for index, arg in enumerate(argv) if arg == "--label"
        )
        assert argv[-1] == str(context if len(calls) < 3 else tmp_path / "runner-context")
        return {"log": "fixture build only"}

    def docker(*args):
        assert args[:2] == ("image", "inspect")
        actual = dict(labels[args[2]])
        if args[2] == build.local_tag("api") and bad_label:
            actual[bad_label] = "0" * 64
        return json.dumps([{"Id": "sha256:" + "b" * 64, "Config": {"Labels": actual}}])

    monkeypatch.setattr(build, "run_command", run)
    if bad_label:
        with pytest.raises(ValueError, match="标签"):
            build.build_exported(tmp_path, context, docker)
        assert len(calls) == 1
        return
    metadata = build.build_exported(tmp_path, context, docker)
    assert len(calls) == 3
    assert metadata["api"]["source_sha"] == build.API_PATCH_SOURCE
    assert metadata["api"]["source_patch"] == {
        "path": build.API_IMAGE_FILE,
        "preimage_blob": build.API_IMAGE_BLOB,
        "patched_sha256": PATCHED_SHA256,
        "patch_sha256": PATCH_SHA256,
    }
    assert labels[build.local_tag("api")]["rnd.daytona.api-source-sha256"] == PATCHED_SHA256
    assert labels[build.local_tag("api")]["rnd.daytona.api-patch-sha256"] == PATCH_SHA256
    for name in ("proxy", "runner"):
        assert "source_patch" not in metadata[name]
        assert not any(key.startswith("rnd.daytona.api-") for key in labels[build.local_tag(name)])


@pytest.mark.parametrize("boundary", ["compose", "profile"])
@pytest.mark.parametrize(
    "mutation",
    [
        None,
        "missing-patch",
        "missing-field",
        "stale-source",
        "changed-preimage",
        "changed-patch",
        "changed-output",
        "extra-field",
        "mutable-id",
        "wrong-id",
        "missing-label",
        "wrong-label",
        "wrong-revision",
        "wrong-version",
    ],
)
def test_runtime_rejects_old_or_tampered_api_before_start_or_admission(
    tmp_path, monkeypatch, boundary, mutation
):
    api_id = "sha256:" + "b" * 64
    config = {"services": {}, "networks": copy.deepcopy(local.NETWORKS)}
    records = {}
    for name, tag in local.IMAGES.items():
        immutable = api_id if name in build.BUILT else tag.rsplit(":", 1)[0] + "@sha256:" + "c" * 64
        service = {
            "image": immutable,
            "networks": ["daytona-network"],
            "environment": {"OTEL_ENABLED": "false"},
        }
        if name == "gateway":
            service = local.gateway_service() | {"image": immutable}
        config["services"][name] = service
        records[name] = {"tag": tag, "image_id" if name in build.BUILT else "digest": immutable}
    record = records["api"]
    record.update(source_sha=build.DAYTONA_SOURCE, source_patch=build.api_patch_identity())
    image = {
        "Id": api_id,
        "Config": {
            "Labels": {
                "org.opencontainers.image.revision": build.DAYTONA_SOURCE,
                "org.opencontainers.image.version": build.DAYTONA_VERSION,
                **build.api_patch_labels(),
            }
        },
    }
    if mutation == "missing-patch":
        del record["source_patch"]
    elif mutation == "missing-field":
        del record["source_patch"]["path"]
    elif mutation == "stale-source":
        record["source_sha"] = "0" * 40
    elif mutation == "changed-preimage":
        record["source_patch"]["preimage_blob"] = "0" * 40
    elif mutation == "changed-patch":
        record["source_patch"]["patch_sha256"] = "0" * 64
    elif mutation == "changed-output":
        record["source_patch"]["patched_sha256"] = "0" * 64
    elif mutation == "extra-field":
        record["source_patch"]["other"] = "unreviewed"
    elif mutation == "mutable-id":
        record["image_id"] = build.local_tag("api")
        config["services"]["api"]["image"] = record["image_id"]
    elif mutation == "wrong-id":
        image["Id"] = "sha256:" + "d" * 64
    elif mutation == "missing-label":
        image["Config"]["Labels"].pop("rnd.daytona.api-source-sha256")
    elif mutation == "wrong-label":
        image["Config"]["Labels"]["rnd.daytona.api-patch-sha256"] = "0" * 64
    elif mutation == "wrong-revision":
        image["Config"]["Labels"]["org.opencontainers.image.revision"] = "0" * 40
    elif mutation == "wrong-version":
        image["Config"]["Labels"]["org.opencontainers.image.version"] = "0.190.1"
    (tmp_path / "compose.lock.yaml").write_text(yaml.safe_dump(config))
    (tmp_path / "images.lock.json").write_text(json.dumps(records))
    (tmp_path / "installation.json").write_text(
        json.dumps(
            {
                "source_sha": build.DAYTONA_SOURCE,
                "release": "v" + build.DAYTONA_VERSION,
                "deployment": "local-development-only",
                "cloud_account": False,
            }
        )
    )
    calls = []

    def docker(*args, **kwargs):
        calls.append(args)
        if args[0] == "image":
            assert args == ("image", "inspect", api_id)
            return json.dumps([image])
        assert mutation is None and args[0] == "compose"
        return "fixture start only"

    monkeypatch.setattr(local, "docker", docker)

    def run():
        return (
            local.compose(tmp_path, "up", "-d")
            if boundary == "compose"
            else profile.read_base(tmp_path)
        )

    if mutation:
        with pytest.raises(ValueError, match="API image|镜像未固定"):
            run()
        assert all(args[0] == "image" for args in calls)
    else:
        run()
        assert calls[0] == ("image", "inspect", api_id)
        assert len(calls) == (2 if boundary == "compose" else 1)


@pytest.mark.parametrize("name", ["native-capability-profile.yml", "capability-profile.yml"])
def test_profile_ci_executes_upstream_digest_regression_before_builds(name):
    text = (build.ROOT / ".github/workflows" / name).read_text()
    assert "tests/test_daytona_api_digest.py" in text
    assert text.index("actions/setup-node@") < text.index("tests/test_daytona_api_digest.py")
    assert text.index("tests/test_daytona_api_digest.py") < text.index(
        "scripts.daytona_local images"
    )
    assert "RND_REQUIRE_NODE_TESTS: '1'" in text
````
