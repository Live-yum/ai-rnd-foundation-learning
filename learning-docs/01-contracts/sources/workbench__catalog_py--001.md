# workbench/catalog.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：技术栈组合目录。** Selection把前端、后端、数据库当作一个整体校验，而不是三个互不相关的文本。网页和CLI从同一目录取得可选项，生成器也读取同一个已验证选择，避免页面允许选但后端不能生成。

**对应关系：** api/cli → Selection → Run.options → generator/native_delivery；test_guided_selection。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.template_adapters`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Selection`（L11–L28）：继承`BaseModel`。声明的数据项为`template`、`backend`、`frontend`、`database`；类型约束/数据库列参数以完整定义为准。
- `Selection.supported`（L19–L25）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`get_adapter`、`adapter.validate_selection`、`model_validator`。 返回路径：L25的`self`。
- `Selection.capabilities`（L27–L28）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`get_adapter(self.template).capabilities`、`get_adapter`、`self.model_dump`。 返回路径：L28的`{**get_adapter(self.template).capabilities(), **self.model_dump()}`。
- `options_for_run`（L31–L34）：接收`run`。 调用`dict`、`run.get`、`options.pop`、`Selection.model_validate`。 返回路径：L34的`Selection.model_validate(options)`。
- `selections`（L37–L38）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Selection(template=template).capabilities`、`Selection`、`template_ids`。 返回路径：L38的`[Selection(template=template).capabilities() for template in template_ids()]`。

</details>

**创建路径：** `workbench/catalog.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L38。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1376`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/catalog.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d8ebaf8824aa12c5f4f436e42bcecd45929e14b97e6cf896775bc6531d6fed2c"} -->
````python
# workbench/catalog.py
"""Validated selection uses the same executable catalog exposed by all discovery surfaces."""

from pydantic import BaseModel, ConfigDict, model_validator

from workbench.template_adapters import get_adapter, template_ids

# Compatibility view for integrations that used PAIRS; never a second source of truth.
PAIRS = {template: get_adapter(template).selection_spec() for template in template_ids()}


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = "python-basic"
    backend: str = ""
    frontend: str = ""
    database: str = ""

    @model_validator(mode="after")
    def supported(self):
        adapter = get_adapter(self.template)
        self.backend = self.backend or adapter.backend
        self.frontend = self.frontend or adapter.frontends[0]
        self.database = self.database or adapter.databases[0]
        adapter.validate_selection(self.backend, self.frontend, self.database)
        return self

    def capabilities(self):
        return {**get_adapter(self.template).capabilities(), **self.model_dump()}


def options_for_run(run):
    options = dict(run.get("options") or {"template": run["template"]})
    options.pop("allow_custom_extensions", None)
    return Selection.model_validate(options)


def selections():
    return [Selection(template=template).capabilities() for template in template_ids()]
````
