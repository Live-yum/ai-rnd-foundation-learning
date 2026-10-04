# tests/test_daytona_dependency_image.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `graph`（L16–L26）：接收`tmp_path`。 调用`root.mkdir`、`(root / "lib").mkdir`、`(root / "lib/native.so").write_bytes`、`(root / "bin").mkdir`、`(root / "bin/tool").write_bytes`、`(root / "bin/tool").chmod`、`(root / "alias").symlink_to`、`(root / "nested").symlink_to`。 返回路径：L26的`root`。
- `test_inventory_hashes_every_file_directory_mode_and_complete_link_graph`（L30–L43）：接收`tmp_path`。 控制顺序：L33断言`len(entries) == 7`；L34断言`entries[str(root / "lib/native.so")]["sha256"] == hashlib.sha256(b"complete native pa…`；L38断言`entries[str(root / "bin/tool")]["mode"] == 0o755`；L39断言`entries[str(root / "alias")]["target"] == "lib"`；L40断言`entries[str(root / "nested")]["target"] == "alias/native.so"`；L43断言`image.digest(image.inventory([str(root)], readonly=False)) != before`。 调用`graph`、`image.inventory`、`str`、`len`、`hashlib.sha256(b"complete native payload").hexdigest`、`hashlib.sha256`、`image.digest`、`(root / "lib/native.so").write_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_symlink_graph_fails_before_any_privileged_mutation`（L48–L55）：接收`tmp_path`、`monkeypatch`、`target`。 控制顺序：L55断言`calls == []`。 调用`graph`、`(root / "cycle").symlink_to`、`monkeypatch.setattr`、`calls.append`、`pytest.raises`、`image.seal`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cross_root_managed_interpreter_link_is_recorded_without_following`（L59–L69）：接收`tmp_path`。 控制顺序：L66断言`entries[str(root / "bin/python")]["type"] == "symlink"`；L67断言`entries[str(interpreter / "python")]["type"] == "file"`。 调用`graph`、`interpreter.mkdir`、`(interpreter / "python").write_bytes`、`(root / "bin/python").symlink_to`、`image.inventory`、`str`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_hardlinks_devices_and_setid_are_rejected`（L73–L85）：接收`tmp_path`。 调用`graph`、`os.link`、`pytest.raises`、`image.inventory`、`str`、`(root / "duplicate.so").unlink`、`os.mkfifo`、`(root / "fifo").unlink`、`(root / "bin/tool").chmod`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_regular_descriptor_rejects_symlink_ancestors_leaf_and_hardlinks`（L89–L97）：接收`tmp_path`。 调用`graph`、`pytest.raises`、`image.regular_bytes`、`os.link`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inventory_rejects_nonroot_ownership_or_writable_ancestors`（L101–L104）：接收`tmp_path`。 调用`graph`、`pytest.raises`、`image.inventory`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `manifest_fixture`（L107–L123）：接收`tmp_path`。 调用`product.mkdir`、`(product / "pyproject.toml").write_text`、`hashlib.sha256(b"locked descriptor").hexdigest`、`hashlib.sha256`、`image.digest`。 返回路径：L123的`product, value, record`。
- `test_manifest_drift_fails_closed`（L139–L144）：接收`tmp_path`、`mutation`。 调用`manifest_fixture`、`image.validate_manifest`、`mutation`、`pytest.raises`、`pytest.mark.parametrize`、`record.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bounded_runtime_receipt_checks_original_descriptors_and_exposes_no_tree`（L147–L166）：接收`tmp_path`、`monkeypatch`。 控制顺序：L155断言`actual == { "schema": 1, "profile": "python-basic", "manifest_sha256": hashlib.sha256…`。 调用`manifest_fixture`、`image.canonical`、`monkeypatch.setattr`、`path.read_bytes`、`image.receipt`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`image.digest`、`(product / "pyproject.toml").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_image_inventory_runs_unprivileged_offline_and_binds_immutable_id`（L169–L207）：接收`monkeypatch`。 控制顺序：L186断言`actual == {**expected, "image_id": "sha256:" + "d" * 64}`；L188遍历`( "--network=none", "--read-only", "--cap-drop=ALL", "--user=6553…`；L195断言`flag in command`；L196断言`"sha256:" + "d" * 64 in command`。 调用`monkeypatch.setattr`、`calls.append`、`json.dumps`、`profile.inspect_dependency_manifest`、`copy.deepcopy`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_outer_binding_rejects_stale_image_and_descriptor_receipts`（L221–L241）：接收`mutation`。 调用`copy.deepcopy`、`profile.validate_dependency_binding`、`mutation`、`pytest.raises`、`pytest.mark.parametrize`、`record.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_manifest_has_classified_value_error`（L264–L268）：接收`tmp_path`、`mutation`。 调用`manifest_fixture`、`mutation`、`pytest.raises`、`image.validate_manifest`、`pytest.mark.parametrize`、`value.update`、`value["profiles"]["python-basic"].update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_dependency_image.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L268。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10227`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_dependency_image.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2cab08cfaeebdf3254ae0067d290b628fffd41edfed8dae0fbd8976f28eb951c"} -->
````python
# tests/test_daytona_dependency_image.py
"""Data-only dependency graph tests. These are not live noexec/runtime proof."""

import copy
import hashlib
import json
import os

import pytest

from scripts import daytona_capability_profile as profile
from scripts import daytona_dependency_image as image

posix_graph = pytest.mark.skipif(os.name == "nt", reason="POSIX no-follow image filesystem")


def graph(tmp_path):
    root = tmp_path / "runtime"
    root.mkdir()
    (root / "lib").mkdir()
    (root / "lib/native.so").write_bytes(b"complete native payload")
    (root / "bin").mkdir()
    (root / "bin/tool").write_bytes(b"#!/immutable/python\n")
    (root / "bin/tool").chmod(0o755)
    (root / "alias").symlink_to("lib")
    (root / "nested").symlink_to("alias/native.so")
    return root


@posix_graph
def test_inventory_hashes_every_file_directory_mode_and_complete_link_graph(tmp_path):
    root = graph(tmp_path)
    entries = image.inventory([str(root)], readonly=False)
    assert len(entries) == 7
    assert (
        entries[str(root / "lib/native.so")]["sha256"]
        == hashlib.sha256(b"complete native payload").hexdigest()
    )
    assert entries[str(root / "bin/tool")]["mode"] == 0o755
    assert entries[str(root / "alias")]["target"] == "lib"
    assert entries[str(root / "nested")]["target"] == "alias/native.so"
    before = image.digest(entries)
    (root / "lib/native.so").write_bytes(b"changed native payload")
    assert image.digest(image.inventory([str(root)], readonly=False)) != before


@posix_graph
@pytest.mark.parametrize("target", ["../../escape", "/usr/bin/sh", "missing", "cycle"])
def test_invalid_symlink_graph_fails_before_any_privileged_mutation(tmp_path, monkeypatch, target):
    root = graph(tmp_path)
    (root / "cycle").symlink_to(target)
    calls = []
    monkeypatch.setattr(os, "fchown", lambda *args: calls.append(args))
    with pytest.raises(ValueError, match="symlink|link target"):
        image.seal([str(root)])
    assert calls == []


@posix_graph
def test_cross_root_managed_interpreter_link_is_recorded_without_following(tmp_path):
    root = graph(tmp_path)
    interpreter = tmp_path / "python"
    interpreter.mkdir()
    (interpreter / "python").write_bytes(b"python executable")
    (root / "bin/python").symlink_to(interpreter / "python")
    entries = image.inventory([str(root), str(interpreter)], readonly=False)
    assert entries[str(root / "bin/python")]["type"] == "symlink"
    assert entries[str(interpreter / "python")]["type"] == "file"
    with pytest.raises(ValueError, match="escapes"):
        image.inventory([str(root)], readonly=False)


@posix_graph
def test_hardlinks_devices_and_setid_are_rejected(tmp_path):
    root = graph(tmp_path)
    os.link(root / "lib/native.so", root / "duplicate.so")
    with pytest.raises(ValueError, match="Hardlinked"):
        image.inventory([str(root)], readonly=False)
    (root / "duplicate.so").unlink()
    os.mkfifo(root / "fifo")
    with pytest.raises(ValueError, match="Special"):
        image.inventory([str(root)], readonly=False)
    (root / "fifo").unlink()
    (root / "bin/tool").chmod(0o4755)
    with pytest.raises(ValueError, match="Set-ID"):
        image.inventory([str(root)], readonly=False)


@posix_graph
def test_regular_descriptor_rejects_symlink_ancestors_leaf_and_hardlinks(tmp_path):
    root = graph(tmp_path)
    with pytest.raises(OSError):
        image.regular_bytes(root / "alias/native.so")
    with pytest.raises(OSError):
        image.regular_bytes(root / "nested")
    os.link(root / "lib/native.so", root / "duplicate.so")
    with pytest.raises(ValueError, match="independent regular"):
        image.regular_bytes(root / "duplicate.so")


@posix_graph
def test_inventory_rejects_nonroot_ownership_or_writable_ancestors(tmp_path):
    root = graph(tmp_path)
    with pytest.raises(ValueError, match="ancestor|root-owned|writable"):
        image.inventory([str(root)])


def manifest_fixture(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "pyproject.toml").write_text("locked descriptor")
    original = {"pyproject.toml": hashlib.sha256(b"locked descriptor").hexdigest()}
    record = {
        "roots": image.ROOTS["python-basic"],
        "groups": image.GROUPS["python-basic"],
        "recipe_identity": "a" * 64,
        "original_descriptors": original,
        "normalized_descriptors": original,
        "platform": {"os": "linux", "architecture": "amd64", "python": "3.14.7"},
        "entries": {},
        "installed_tree_sha256": image.digest({}),
    }
    value = {"schema": 1, "profiles": {"python-basic": record}}
    return product, value, record


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(roots=["/tmp/deps"]),
        lambda record: record.update(groups={"python": ["--all-extras"]}),
        lambda record: record.update(
            platform={"os": "linux", "architecture": "arm64", "python": "3.14.7"}
        ),
        lambda record: record.update(installed_tree_sha256="b" * 64),
        lambda record: record.update(original_descriptors={"../secret": "a" * 64}),
        lambda record: record.update(normalized_descriptors={}),
    ],
)
def test_manifest_drift_fails_closed(tmp_path, mutation):
    _, value, record = manifest_fixture(tmp_path)
    image.validate_manifest(value, "python-basic")
    mutation(record)
    with pytest.raises(ValueError):
        image.validate_manifest(value, "python-basic")


def test_bounded_runtime_receipt_checks_original_descriptors_and_exposes_no_tree(
    tmp_path, monkeypatch
):
    product, value, record = manifest_fixture(tmp_path)
    raw = image.canonical(value)
    monkeypatch.setattr(image, "inspect_manifest", lambda *args, **kwargs: (raw, record))
    monkeypatch.setattr(image, "regular_bytes", lambda path: path.read_bytes())
    actual = image.receipt("python-basic", product=product)
    assert actual == {
        "schema": 1,
        "profile": "python-basic",
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "installed_tree_sha256": image.digest({}),
        "descriptors_verified": True,
        "installed_tree_verified": True,
        "readonly_verified": True,
    }
    (product / "pyproject.toml").write_text("candidate drift")
    with pytest.raises(ValueError, match="descriptor changed"):
        image.receipt("python-basic", product=product)


def test_image_inventory_runs_unprivileged_offline_and_binds_immutable_id(monkeypatch):
    calls = []
    expected = {
        "schema": 1,
        "profile": "python-basic",
        "manifest_sha256": "a" * 64,
        "installed_tree_sha256": "b" * 64,
        "original_descriptors": {"uv.lock": "c" * 64},
    }
    monkeypatch.setattr(
        profile.local,
        "docker",
        lambda *args, **kwargs: calls.append((args, kwargs)) or json.dumps(expected),
    )
    actual = profile.inspect_dependency_manifest(
        "sha256:" + "d" * 64, "python-basic", expected["original_descriptors"]
    )
    assert actual == {**expected, "image_id": "sha256:" + "d" * 64}
    command = calls[0][0]
    for flag in (
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--user=65534:65534",
        "--security-opt=no-new-privileges",
    ):
        assert flag in command
    assert "sha256:" + "d" * 64 in command
    bad = copy.deepcopy(expected)
    bad["original_descriptors"]["uv.lock"] = "e" * 64
    monkeypatch.setattr(profile.local, "docker", lambda *args, **kwargs: json.dumps(bad))
    with pytest.raises(ValueError, match="descriptor inputs"):
        profile.inspect_dependency_manifest(
            "sha256:" + "d" * 64, "python-basic", expected["original_descriptors"]
        )
    with pytest.raises(ValueError, match="immutable image ID"):
        profile.inspect_dependency_manifest(
            "mutable:tag", "python-basic", expected["original_descriptors"]
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(image_id="sha256:" + "b" * 64),
        lambda record: record.update(profile="fastapiadmin"),
        lambda record: record.update(schema=0),
        lambda record: record.update(original_descriptors={"uv.lock": "c" * 64}),
        lambda record: record.update(manifest_sha256="mutable"),
        lambda record: record.update(installed_tree_sha256=None),
    ],
)
def test_outer_binding_rejects_stale_image_and_descriptor_receipts(mutation):
    expected = {
        "schema": 1,
        "profile": "python-basic",
        "image_id": "sha256:" + "a" * 64,
        "manifest_sha256": "b" * 64,
        "installed_tree_sha256": "c" * 64,
        "original_descriptors": {"uv.lock": "d" * 64},
    }
    original = copy.deepcopy(expected)
    profile.validate_dependency_binding(
        expected, original["image_id"], "python-basic", original["original_descriptors"]
    )
    mutation(expected)
    with pytest.raises(ValueError, match="binding"):
        profile.validate_dependency_binding(
            expected,
            original["image_id"],
            "python-basic",
            original["original_descriptors"],
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(schema=True),
        lambda value: value.update(profiles=[]),
        lambda value: value.update(extra="unsupported"),
        lambda value: value["profiles"]["python-basic"].update(recipe_identity=None),
        lambda value: value["profiles"]["python-basic"].update(entries=[]),
        lambda value: value["profiles"]["python-basic"].update(original_descriptors=[]),
        lambda value: value["profiles"]["python-basic"].update(
            original_descriptors={"./uv.lock": "a" * 64}
        ),
        lambda value: value["profiles"]["python-basic"].update(
            original_descriptors={"backend//uv.lock": "a" * 64}
        ),
        lambda value: value["profiles"]["python-basic"].update(
            original_descriptors={"backend\\uv.lock": "a" * 64}
        ),
    ],
)
def test_malformed_manifest_has_classified_value_error(tmp_path, mutation):
    _, value, _ = manifest_fixture(tmp_path)
    mutation(value)
    with pytest.raises(ValueError):
        image.validate_manifest(value, "python-basic")
````
