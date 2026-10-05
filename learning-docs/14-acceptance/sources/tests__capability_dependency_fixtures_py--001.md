# tests/capability_dependency_fixtures.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_dependency_build`、`scripts.daytona_native_capability_profile`、`workbench.catalog`、`workbench.domain`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `dependency_profile`（L12–L22）：接收`template`、`descriptors`。 调用`dict.fromkeys`、`native_descriptor_roles`。 返回路径：L14的`{ "schema": 1, "profile": template, "image_id": "sha256:" + "3" * 64, "manifest_sha256": "…`。
- `profile_record`（L25–L48）：接收`product`、`template`。 控制顺序：L27按`product is not None`分支。 调用`manifest(product).items`、`manifest`、`Path`、`dependency_profile`、`Selection(template=template).model_dump`、`Selection`。 返回路径：L35的`{ "recipe_identity": "1" * 64, "selection": Selection(template=template).model_dump(), "ru…`。
- `dependency_evidence`（L51–L64）：接收`profile`、`inventory`。 调用`dependency_profile`、`digest`。 返回路径：L53的`{ **{ name: profile[name] for name in ("schema", "profile", "manifest_sha256", "installed_…`。
- `container_binding`（L67–L73）：接收`record`。 返回路径：L68的`{ "runner_image_id": record["runner"]["image_id"], "snapshot_image_id": record["snapshot"]…`。

</details>

**创建路径：** `tests/capability_dependency_fixtures.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L73。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2637`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/capability_dependency_fixtures.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "59aa673e63e2a068b89f45b44c88a15ce17890497d55be75760e5d36a99c3e43"} -->
````python
# tests/capability_dependency_fixtures.py
"""Synthetic provenance for contract tests only; never a live image attestation."""

from pathlib import Path

from scripts.daytona_dependency_build import native_descriptor_roles
from scripts.daytona_native_capability_profile import DESCRIPTORS
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.filesystem import manifest


def dependency_profile(template="python-basic", descriptors=None):
    names = DESCRIPTORS if template == "fastapiadmin" else ("pyproject.toml", "uv.lock")
    return {
        "schema": 1,
        "profile": template,
        "image_id": "sha256:" + "3" * 64,
        "manifest_sha256": "6" * 64,
        "installed_tree_sha256": "7" * 64,
        "original_descriptors": descriptors or dict.fromkeys(names, "8" * 64),
        **({"descriptor_roles": native_descriptor_roles()} if template == "fastapiadmin" else {}),
    }


def profile_record(product=None, template="python-basic"):
    descriptors = None
    if product is not None:
        descriptors = {
            name: value
            for name, value in manifest(product).items()
            if Path(name).name
            in {"pyproject.toml", "uv.lock", "package.json", "pnpm-lock.yaml", "pom.xml"}
        }
    profile = dependency_profile(template, descriptors)
    return {
        "recipe_identity": "1" * 64,
        "selection": Selection(template=template).model_dump(),
        "runner": {"image_id": "sha256:" + "2" * 64},
        "snapshot": {
            "image_id": profile["image_id"],
            "digest": "registry:6000/"
            + ("rnd-native-fastapiadmin" if template == "fastapiadmin" else "rnd-python")
            + "@sha256:"
            + "4" * 64,
            "snapshot": "rnd-python-test",
            "dependency_manifest": profile,
        },
    }


def dependency_evidence(profile=None, inventory=None):
    profile = profile or dependency_profile()
    return {
        **{
            name: profile[name]
            for name in ("schema", "profile", "manifest_sha256", "installed_tree_sha256")
        },
        "descriptors_verified": True,
        "installed_tree_verified": True,
        "readonly_verified": True,
        "product_links_verified": True,
        "source_inventory_verified": True,
        "source_inventory_sha256": digest(inventory or {}),
    }


def container_binding(record):
    return {
        "runner_image_id": record["runner"]["image_id"],
        "snapshot_image_id": record["snapshot"]["image_id"],
        "snapshot_digest": record["snapshot"]["digest"],
        "dependency_manifest": record["snapshot"]["dependency_manifest"],
    }
````
