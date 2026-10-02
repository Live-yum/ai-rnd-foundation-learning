# scripts/native_coding_fixture.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：故意先出错的原生编码测试模型。** 对已登记规则区域返回可审查SEARCH/REPLACE；首轮总为true，后轮是数量非负表达式。它不直接写代码，实际应用与失败回滚仍由Plop/Aider及平台执行。

**对应关系：** ci_native_tools注入 → native_coding调用 → 真实工具和反例检查。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native_coding`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `NativeCodingFixture`（L6–L42）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `NativeCodingFixture.__init__`（L7–L9）：接收`fail_first`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NativeCodingFixture.complete`（L11–L42）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L12按`schema is not NativeEdits`分支；L13抛异常，停止当前正常路径；L17遍历`payload["registered_files"].items()`；L20按`failed`分支；L22按`name.endswith(".py")`分支；L24按`name.endswith(".java")`分支。 调用`AssertionError`、`self.calls.append`、`len`、`payload["registered_files"].items`、`region`、`name.endswith`、`source.index`、`source.rfind`、`before.replace`等。 返回路径：L42的`schema(files=rows, explanation="Explicit local test fixture: nonnegative quantity")`。

</details>

**创建路径：** `scripts/native_coding_fixture.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L42。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1794`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/native_coding_fixture.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "30a7930d43e29e2ebe3f36831426db3495988a1359e15b4ab85cd88de6bb4355"} -->
````python
# scripts/native_coding_fixture.py
"""Explicit deterministic model response for native integration acceptance, never live mode."""

from workbench.native_coding import NativeEdits, region


class NativeCodingFixture:
    def __init__(self, fail_first=True):
        self.calls = []
        self.fail_first = fail_first

    def complete(self, run_id, key, instruction, payload, schema):
        if schema is not NativeEdits:
            raise AssertionError(schema)
        self.calls.append(key)
        failed = self.fail_first and len(self.calls) == 1
        rows = []
        for name, data in payload["registered_files"].items():
            source = data["source"]
            prefix, expression, suffix = region(source)
            if failed:
                result = "True" if name.endswith(".py") else "true"
            elif name.endswith(".py"):
                result = 'data.get("quantity") is None or data["quantity"] >= 0'
            elif name.endswith(".java"):
                result = "quantity == null || quantity >= 0"
            else:
                result = "data.quantity == null || Number(data.quantity) >= 0"
            position = (
                source.index("# RND_RULE_BEGIN")
                if name.endswith(".py")
                else source.index("// RND_RULE_BEGIN")
            )
            before = source[source.rfind("\n", 0, position) + 1 :]
            after = before.replace(expression, result, 1)
            rows.append(
                {
                    "path": name,
                    "before_sha256": data["sha256"],
                    "blocks": f"{name}\n<<<<<<< SEARCH\n{before.rstrip()}\n=======\n{after.rstrip()}\n>>>>>>> REPLACE\n",
                }
            )
        return schema(files=rows, explanation="Explicit local test fixture: nonnegative quantity")
````
