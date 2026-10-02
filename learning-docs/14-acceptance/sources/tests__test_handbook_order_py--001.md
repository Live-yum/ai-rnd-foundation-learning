# tests/test_handbook_order.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_handbook`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_directory_order_is_case_sensitive_and_platform_independent`（L4–L10）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L9断言`names == sorted(names)`；L10断言`names.index("templates/product/README.md") < names.index("templates/product/app.py")`。 调用`sources`、`name.startswith`、`sorted`、`names.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_handbook_order.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L10。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`438`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_handbook_order.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "24e45e7085dd3201a614531dbdb5b20ae52b9286af7bb365368debd93fce436d"} -->
````python
# tests/test_handbook_order.py
from scripts.build_handbook import sources


def test_directory_order_is_case_sensitive_and_platform_independent():
    # WindowsPath comparisons ignore case; documentation order must not.
    names = [
        name for _, rows in sources() for name, _ in rows if name.startswith("templates/product/")
    ]
    assert names == sorted(names)
    assert names.index("templates/product/README.md") < names.index("templates/product/app.py")
````
