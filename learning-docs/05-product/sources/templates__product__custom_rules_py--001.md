# templates/product/custom_rules.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 唯一允许自动定制的业务规则文件；生成前后的约束、例子与SHA由平台检查。其他身份、存储和启动代码不开放给模型任意编辑。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `validate`（L1–L2）：接收`entity`、`data`。 返回路径：L2的`None`。

</details>

**创建路径：** `templates/product/custom_rules.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L2。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`44`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/custom_rules.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "811c6791507671dedc40464517acb6abd828017681f1b4d979f8aa7e3380b5c4"} -->
````python
# templates/product/custom_rules.py
def validate(entity, data):
    return None
````
