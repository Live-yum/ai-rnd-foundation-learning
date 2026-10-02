# workbench/catalog.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：技术栈组合目录。** Selection把前端、后端、数据库当作一个整体校验，而不是三个互不相关的文本。网页和CLI从同一目录取得可选项，生成器也读取同一个已验证选择，避免页面允许选但后端不能生成。

**对应关系：** api/cli → Selection → Run.options → generator/native_delivery；test_guided_selection。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Selection`（L63–L109）：继承`BaseModel`。声明的数据项为`template`、`backend`、`frontend`、`database`；类型约束/数据库列参数以完整定义为准。
- `Selection.supported`（L71–L84）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L72按`self.template not in PAIRS`分支；L73抛异常，停止当前正常路径；L78按`self.backend != spec["backend"] or self.frontend not in spec["frontends"] or self.dat…`分支；L83抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L84的`self`。
- `Selection.capabilities`（L86–L109）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.model_dump`。 返回路径：L89的`{ **PAIRS[self.template], **self.model_dump(), "date_range_inclusive": True, "scopes": [ P…`。
- `options_for_run`（L112–L113）：接收`run`。 调用`Selection.model_validate`、`run.get`。 返回路径：L113的`Selection.model_validate(run.get("options") or {"template": run["template"]})`。
- `selections`（L116–L117）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Selection(template=template).capabilities`、`Selection`。 返回路径：L117的`[Selection(template=template).capabilities() for template in PAIRS]`。

</details>

**创建路径：** `workbench/catalog.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L117。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3938`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/catalog.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1ef0f0410dfbf4b231e8758dcb1d69c80f873193b396dfaf0b362c3f233ffce8"} -->
````python
# workbench/catalog.py
"""Executable, deterministic template capabilities. The LLM cannot invent support flags."""

from pydantic import BaseModel, ConfigDict, model_validator

PAIRS = {
    "python-basic": {
        "backend": "fastapi",
        "frontends": ["simple-admin", "api-only"],
        "databases": ["sqlite", "postgresql"],
        "name": "FastAPI + 轻量管理页面",
        "scope": "per_user",
        "features": [
            "typed-crud",
            "authentication",
            "user-isolation",
            "keyword-search",
            "exact-filter",
            "date-range",
            "enum",
            "field-length",
            "single-record-rules",
        ],
        "field_kinds": ["text", "integer", "boolean", "date", "enum"],
        "not_supported": [
            "web-scraping",
            "external-payments",
            "cross-entity-transactions",
            "business-rbac",
            "public-anonymous-site",
        ],
    },
    "fastapiadmin": {
        "backend": "fastapiadmin",
        "frontends": ["fastapiadmin-vue"],
        "databases": ["postgresql"],
        "name": "FastapiAdmin 原生后端 + Vue 管理端",
        "scope": "shared",
        "features": ["native-crud", "native-rbac", "menu-integration", "native-record-rules"],
        "field_kinds": ["text", "integer", "boolean"],
        "not_supported": [
            "per-user-isolation",
            "arbitrary-code-execution",
            "cross-entity-transactions",
        ],
    },
    "yudao-vben": {
        "backend": "yudao-java",
        "frontends": ["vben-antd"],
        "databases": ["postgresql"],
        "name": "芋道 Java 后端 + Vben5 Ant Design",
        "scope": "shared",
        "features": ["native-crud", "native-rbac", "menu-integration", "native-record-rules"],
        "field_kinds": ["text", "integer", "boolean"],
        "not_supported": [
            "per-user-isolation",
            "arbitrary-code-execution",
            "cross-entity-transactions",
        ],
    },
}


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = "python-basic"
    backend: str = ""
    frontend: str = ""
    database: str = ""

    @model_validator(mode="after")
    def supported(self):
        if self.template not in PAIRS:
            raise ValueError("未知模板")
        spec = PAIRS[self.template]
        self.backend = self.backend or spec["backend"]
        self.frontend = self.frontend or spec["frontends"][0]
        self.database = self.database or spec["databases"][0]
        if (
            self.backend != spec["backend"]
            or self.frontend not in spec["frontends"]
            or self.database not in spec["databases"]
        ):
            raise ValueError("前后端与数据库组合不兼容；从模板目录中选择已验证的组合")
        return self

    def capabilities(self):
        from workbench.business_capabilities import BUSINESS

        return {
            **PAIRS[self.template],
            **self.model_dump(),
            "date_range_inclusive": True,
            "scopes": [
                PAIRS[self.template]["scope"],
                *(["shared"] if self.template == "python-basic" else []),
            ],
            "business_contract": BUSINESS,
            "not_supported": [
                item
                for item in PAIRS[self.template]["not_supported"]
                if item not in {"business-rbac", "cross-entity-transactions"}
            ],
            "defaults": {
                "title_max_length": 250,
                "body_max_length": 3000,
                "date_format": "YYYY-MM-DD",
                "category_required": False,
            },
        }


def options_for_run(run):
    return Selection.model_validate(run.get("options") or {"template": run["template"]})


def selections():
    return [Selection(template=template).capabilities() for template in PAIRS]
````
