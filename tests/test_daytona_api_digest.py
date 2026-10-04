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
