"""Build a local per-stack offline snapshot from credential-filtered product sources."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.daytona_local import HOME, compose, docker, private_json, wait_for_registry
from workbench.daytona_profiles import dependency_identity, profile_key
from workbench.domain import digest
from workbench.filesystem import files, inside, manifest, sha
from workbench.settings import ROOT


def build(template, database, product, directory=HOME):
    profile_key(template, {"database": database})
    product, directory = Path(product).resolve(), Path(directory).resolve()
    before = manifest(product)
    profile = {"template": template, "database": database, "dependency_identity": dependency_identity(product)}
    inputs = {name: sha(ROOT / name) for name in ("tools/daytona/matrix.Dockerfile", "tools/daytona/warm.py", "pyproject.toml", "uv.lock")}
    stamp = digest({"profile": profile, "inputs": inputs})[:16]
    family = "rnd-" + template
    tag = "127.0.0.1:6000/" + family + ":" + stamp
    compose(directory, "up", "-d", "--pull", "never", "registry", "gateway")
    wait_for_registry()
    with tempfile.TemporaryDirectory(prefix="rnd-snapshot-", dir=directory) as temp:
        context = Path(temp)
        (context / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
        shutil.copyfile(ROOT / "tools/daytona/matrix.Dockerfile", context / "Dockerfile")
        shutil.copyfile(ROOT / "tools/daytona/warm.py", context / "warm.py")
        (context / "harness").mkdir()
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copyfile(ROOT / name, context / "harness" / name)
        for name, source in files(product):
            if source.name == ".npmrc" and any(word in source.read_text().lower() for word in ("_auth", "password", "username", "${")):
                raise ValueError("Cannot copy authenticated npm configuration into a snapshot")
            target = inside(context / "product", name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if manifest(product) != before:
            raise ValueError("Product changed while preparing a local snapshot")
        pnpm = "11.16.0" if template == "yudao-vben" else "9.15.3"
        try:
            docker("build", "--build-arg", "PNPM_VERSION=" + pnpm, "--tag", tag, str(context), timeout=3600)
        except subprocess.CalledProcessError as exc:
            from workbench.filesystem import atomic_text
            output = (exc.stderr or b"").decode("utf-8", errors="replace")[-30000:]
            atomic_text(ROOT / "reports/daytona-matrix-image-build.log", output)
            raise RuntimeError("Local matrix image build failed; see daytona-matrix-image-build.log") from None
    docker("push", tag, timeout=1200)
    inspected = json.loads(docker("image", "inspect", tag))[0]
    image_id = inspected["Id"]
    if not image_id.startswith("sha256:"):
        raise ValueError("Missing immutable local image identity")
    value = {"image": "registry:6000/" + family + ":" + stamp, "snapshot": family + "-" + stamp,
             "source_hash": stamp, "image_id": image_id, "profile": profile, "build_inputs": inputs,
             "resources": {"cpu": 2, "memory": 10 if template == "yudao-vben" else 4, "disk": 30}, "wait_for_default": False}
    private_json(directory / "snapshot-image.json", value)
    print(json.dumps({"snapshot": value["snapshot"], "profile": profile, "image_id": image_id}))
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", choices=["python-basic", "fastapiadmin", "yudao-vben"])
    parser.add_argument("--database", choices=["sqlite", "postgresql"], default="postgresql")
    parser.add_argument("--product", type=Path, required=True)
    parser.add_argument("--directory", type=Path, default=HOME)
    args = parser.parse_args()
    build(args.template, args.database, args.product, args.directory)


if __name__ == "__main__":
    main()
