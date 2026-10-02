# workbench/native_style.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生UI壳、主题和组件族的身份检查。** 先比较固定上游与生成目录中受保护布局/主题文件的内容清单，再解析生成Vue页应使用的真实框架组件；输出绑定模板、来源和Plan的回执。静态身份检查之后仍须真实浏览器检查，不能用一张通用页面替代原生风格。

**对应关系：** native_lab → verify_native_style → native_style.json → 原生浏览器与managed_verify。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.native_recovery`、`workbench.symbols`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_page_contracts`（L30–L64）：接收`template`、`entities`、`business`。 控制顺序：L32遍历`entities`；L33按`template == "fastapiadmin"`分支；L35按`business`分支；L48按`business and template == "yudao-vben"`分支。 调用`entity.replace`、`set`。 返回路径：L64的`required`。
- `verify_native_style`（L67–L129）：接收`template`、`source_frontend`、`generated_frontend`、`plan`、`reports`。 源码说明：Source identity plus parsed component contracts, followed by browser UI checks. Source roots are the original pinned frontend and its generated copy, not project metadata labels. New entity pages may 。 控制顺序：L74按`template not in PROFILES`分支；L75抛异常，停止当前正常路径；L80遍历`profile["protected"]`；L91按`not selected or selected != actual`分支；L92抛异常，停止当前正常路径；L98遍历`required.items()`；L100按`not path.is_file()`分支；L101抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`Path`、`manifest`、`before.items`、`prefix.endswith`、`name.startswith`、`after.items`、`NativeIntegrityError`、`protected.update`等。 返回路径：L129的`evidence`。

</details>

**创建路径：** `workbench/native_style.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L129。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5321`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_style.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c1e071994187c62ea08aa01140091b48645576d365f258983820d7bfbec899dc"} -->
````python
# workbench/native_style.py
"""Keep generated pages inside the selected native frontend and its unchanged UI shell."""

from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.native_recovery import NativeIntegrityError
from workbench.symbols import parse_file

PROFILES = {
    "fastapiadmin": {
        "protected": ["src/layouts/", "src/styles/", "src/main.ts"],
        "family": "FastapiAdmin Vue / Fa components / Element Plus",
    },
    "yudao-vben": {
        "protected": [
            "apps/web-antd/src/layouts/",
            "apps/web-antd/src/main.ts",
            "apps/web-antd/src/bootstrap.ts",
            "packages/@core/ui-kit/layout-ui/",
            "packages/@core/base/design/",
            "packages/effects/layouts/",
            "packages/styles/",
        ],
        "family": "Vben5 web-antd / Ant Design Vue / VXE",
    },
}


def native_page_contracts(template, entities, business=False):
    required = {}
    for entity in entities:
        if template == "fastapiadmin":
            components = {"FaSearchBar", "FaTable", "FaDialog", "FaForm"}
            if business:
                components |= {"ElCard", "ElTimeline", "ElTimelineItem", "ElStatistic"}
            required[f"src/views/module_rnd/{entity}/index.vue"] = (components, [])
        else:
            root = "apps/web-antd/src/views/infra/wb" + entity.replace("_", "")
            required[root + "/index.vue"] = (
                {"Page", "Grid", "TableAction"} | ({"RndBusinessPanel"} if business else set()),
                ["@vben/common-ui", "#/adapter/vxe-table", "ant-design-vue"],
            )
            required[root + "/modules/form.vue"] = (
                {"Modal", "Form"},
                ["@vben/common-ui", "#/adapter/form", "ant-design-vue"],
            )
    if business and template == "yudao-vben":
        root = "apps/web-antd/src/views/infra/rnd-business/"
        required[root + "panel.vue"] = (
            {
                "Card",
                "Table",
                "Timeline",
                "TimelineItem",
                "Statistic",
                "MetricChart",
                "ActionModal",
                "ActionForm",
            },
            ["ant-design-vue", "@vben/common-ui", "#/adapter/form", "#/api/request"],
        )
        required[root + "metric-chart.vue"] = ({"EchartsUI"}, ["@vben/plugins/echarts"])
    return required


def verify_native_style(template, source_frontend, generated_frontend, plan, reports):
    """Source identity plus parsed component contracts, followed by browser UI checks.

    Source roots are the original pinned frontend and its generated copy, not
    project metadata labels. New entity pages may be added; shell/theme changes
    or substitution with a generic CRUD frontend are rejected.
    """
    if template not in PROFILES:
        raise ValueError("Native UI verification requires a registered native template")
    source_frontend, generated_frontend = Path(source_frontend), Path(generated_frontend)
    profile = PROFILES[template]
    before, after = manifest(source_frontend), manifest(generated_frontend)
    protected = {}
    for prefix in profile["protected"]:
        selected = {
            name: value
            for name, value in before.items()
            if name == prefix or (prefix.endswith("/") and name.startswith(prefix))
        }
        actual = {
            name: value
            for name, value in after.items()
            if name == prefix or (prefix.endswith("/") and name.startswith(prefix))
        }
        if not selected or selected != actual:
            raise NativeIntegrityError("Selected native UI shell/theme changed: " + prefix)
        protected.update(selected)
    pages = []
    required = native_page_contracts(
        template, [entity.name for entity in plan.entities], bool(getattr(plan, "business", None))
    )
    for relative, (components, imports) in required.items():
        path = generated_frontend / relative
        if not path.is_file():
            raise NativeIntegrityError("Native-generated UI page missing: " + relative)
        parsed = parse_file(path)
        actual = {
            row["name"] for row in parsed.get("symbols", []) if row["kind"] == "vue_component_usage"
        }
        import_text = "\n".join(parsed.get("imports", []))
        if not components <= actual or any(name not in import_text for name in imports):
            raise NativeIntegrityError("Generated page replaced native UI components: " + relative)
        pages.append(
            {
                "path": relative,
                "sha256": after[relative],
                "native_components": sorted(components),
                "native_imports": imports,
            }
        )
    evidence = {
        "passed": True,
        "template": template,
        "ui_family": profile["family"],
        "shell_and_theme_unchanged": True,
        "protected_files": protected,
        "protected_source_digest": digest(protected),
        "generated_pages": pages,
        "generic_frontend_substitution": False,
        "evidence_scope": "native source identity and parsed Vue components; browser evidence separate",
    }
    write_json(Path(reports) / "native-style.json", evidence)
    return evidence
````
