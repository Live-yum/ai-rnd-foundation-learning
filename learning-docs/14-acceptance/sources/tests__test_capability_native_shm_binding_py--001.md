# tests/test_capability_native_shm_binding.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_execution`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_image_cannot_downgrade_or_drop_private_memory_binding`（L22–L28）：接收`mutation`。 控制顺序：L25断言`require_profile_container_binding(record, evidence) is evidence`。 调用`profile_record`、`container_binding`、`require_profile_container_binding`、`mutation`、`pytest.raises`、`pytest.mark.parametrize`、`value.pop`、`value.update`、`value["shared_memory"].update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ordinary_profile_does_not_acquire_native_shared_memory`（L31–L35）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L34断言`"shared_memory" not in evidence`；L35断言`require_profile_container_binding(record, evidence) is evidence`。 调用`profile_record`、`container_binding`、`require_profile_container_binding`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_shm_binding.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L35。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1524`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_shm_binding.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "dbf059de6442d9f216fc36a2919e522d9b0363e691372901232a3eb99cac5e72"} -->
````python
# tests/test_capability_native_shm_binding.py
"""Synthetic admission binding checks; no live shared-memory certificate."""

import pytest
from capability_dependency_fixtures import container_binding, profile_record

from workbench.capability_execution import require_profile_container_binding


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.pop("shared_memory"),
        lambda value: value.update(profile="module-container-unprivileged-v1"),
        lambda value: value["shared_memory"].update(ipc_mode="host"),
        lambda value: value["shared_memory"].update(ipc_mode="shareable"),
        lambda value: value["shared_memory"].update(size_bytes=67108864.0),
        lambda value: value["shared_memory"].update(size_bytes=True),
        lambda value: value["shared_memory"].update(size_bytes=67108865),
        lambda value: value["shared_memory"].update(extra=True),
    ],
)
def test_native_image_cannot_downgrade_or_drop_private_memory_binding(mutation):
    record = profile_record(template="fastapiadmin")
    evidence = container_binding(record)
    assert require_profile_container_binding(record, evidence) is evidence
    mutation(evidence)
    with pytest.raises(ValueError, match="private shared memory"):
        require_profile_container_binding(record, evidence)


def test_ordinary_profile_does_not_acquire_native_shared_memory():
    record = profile_record()
    evidence = container_binding(record)
    assert "shared_memory" not in evidence
    assert require_profile_container_binding(record, evidence) is evidence
````
