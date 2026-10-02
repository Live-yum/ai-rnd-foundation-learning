# scripts/daytona_matrix_image.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：为每个技术栈制作离线依赖快照。** 从已生成项目提取受限公开构建输入和依赖锁，排除运行数据与秘密，按profile预热工具后推到本机registry，记录来源/资源/锁身份。

**对应关系：** 真实原生产品 → matrix.Dockerfile/warm.py → snapshot-image.json。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_local`、`workbench.daytona_profiles`、`workbench.domain`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `build`（L17–L95）：接收`template`、`database`、`product`、`directory`。 控制顺序：L46遍历`("pyproject.toml", "uv.lock")`；L48遍历`files(product)`；L49按`source.name == ".npmrc" and any( word in source.read_text().lower() for word in ("_au…`分支；L53抛异常，停止当前正常路径；L57按`manifest(product) != before`分支；L58抛异常，停止当前正常路径；L75抛异常，停止当前正常路径；L81按`not image_id.startswith("sha256:")`分支。后续分支沿下方源码相同行号继续阅读。 调用`profile_key`、`Path(product).resolve`、`Path`、`Path(directory).resolve`、`manifest`、`dependency_identity`、`sha`、`digest`、`compose`等。 返回路径：L95的`value`。
- `main`（L98–L105）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`build`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_matrix_image.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L109。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4484`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_matrix_image.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "dd8209b27f69926fda2f2fc428803f2909c543c54e1d0e0376c2b76f0673c193"} -->
````python
# scripts/daytona_matrix_image.py
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
    profile = {
        "template": template,
        "database": database,
        "dependency_identity": dependency_identity(product),
    }
    inputs = {
        name: sha(ROOT / name)
        for name in (
            "tools/daytona/matrix.Dockerfile",
            "tools/daytona/warm.py",
            "pyproject.toml",
            "uv.lock",
        )
    }
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
            if source.name == ".npmrc" and any(
                word in source.read_text().lower()
                for word in ("_auth", "password", "username", "${")
            ):
                raise ValueError("Cannot copy authenticated npm configuration into a snapshot")
            target = inside(context / "product", name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if manifest(product) != before:
            raise ValueError("Product changed while preparing a local snapshot")
        pnpm = "11.16.0" if template == "yudao-vben" else "9.15.3"
        try:
            docker(
                "build",
                "--build-arg",
                "PNPM_VERSION=" + pnpm,
                "--tag",
                tag,
                str(context),
                timeout=3600,
            )
        except subprocess.CalledProcessError as exc:
            from workbench.filesystem import atomic_text

            output = (exc.stderr or b"").decode("utf-8", errors="replace")[-30000:]
            atomic_text(ROOT / "reports/daytona-matrix-image-build.log", output)
            raise RuntimeError(
                "Local matrix image build failed; see daytona-matrix-image-build.log"
            ) from None
    docker("push", tag, timeout=1200)
    inspected = json.loads(docker("image", "inspect", tag))[0]
    image_id = inspected["Id"]
    if not image_id.startswith("sha256:"):
        raise ValueError("Missing immutable local image identity")
    value = {
        "image": "registry:6000/" + family + ":" + stamp,
        "snapshot": family + "-" + stamp,
        "source_hash": stamp,
        "image_id": image_id,
        "profile": profile,
        "build_inputs": inputs,
        "resources": {"cpu": 2, "memory": 10 if template == "yudao-vben" else 4, "disk": 30},
        "wait_for_default": False,
    }
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
````
