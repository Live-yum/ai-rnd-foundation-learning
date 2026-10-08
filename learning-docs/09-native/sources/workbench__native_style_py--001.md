# workbench/native_style.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生UI壳、主题和组件族的身份检查。** 先比较固定上游与生成目录中受保护布局/主题文件的内容清单，再解析生成Vue页应使用的真实框架组件；输出绑定模板、来源和Plan的回执。静态身份检查之后仍须真实浏览器检查，不能用一张通用页面替代原生风格。

**对应关系：** native_lab → verify_native_style → native_style.json → 原生浏览器与managed_verify。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.native_recovery`、`workbench.symbols`、`workbench.template_adapters`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_page_contracts`（L22–L26）：接收`template`、`entities`、`business`。 控制顺序：L24按`not adapter.ui.protected`分支；L25抛异常，停止当前正常路径。 调用`get_adapter`、`ValueError`、`adapter.ui.page_contracts`。 返回路径：L26的`adapter.ui.page_contracts(entities, business)`。
- `verify_native_style`（L29–L91）：接收`template`、`source_frontend`、`generated_frontend`、`plan`、`reports`。 源码说明：Source identity plus parsed component contracts, followed by browser UI checks. Source roots are the original pinned frontend and its generated copy, not project metadata labels. New entity pages may 。 控制顺序：L36按`template not in PROFILES`分支；L37抛异常，停止当前正常路径；L42遍历`profile["protected"]`；L53按`not selected or selected != actual`分支；L54抛异常，停止当前正常路径；L60遍历`required.items()`；L62按`not path.is_file()`分支；L63抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`Path`、`manifest`、`before.items`、`prefix.endswith`、`name.startswith`、`after.items`、`NativeIntegrityError`、`protected.update`等。 返回路径：L91的`evidence`。

</details>

**创建路径：** `workbench/native_style.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L91。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3841`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_style.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "664b0b50b2caba667196096b8d76eb8dca8c81542cb9258bfbc7ba8971d041be"} -->
````python
# workbench/native_style.py
"""Keep generated pages inside the selected native frontend and its unchanged UI shell."""

from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.native_recovery import NativeIntegrityError
from workbench.symbols import parse_file
from workbench.template_adapters import get_adapter, template_ids

# Compatibility view; selection, planning and verification share one adapter.
PROFILES = {
    template: {
        "protected": list(get_adapter(template).ui.protected),
        "family": get_adapter(template).ui.family,
    }
    for template in template_ids()
    if get_adapter(template).ui.protected
}


def native_page_contracts(template, entities, business=False):
    adapter = get_adapter(template)
    if not adapter.ui.protected:
        raise ValueError("Native UI verification requires a registered native template")
    return adapter.ui.page_contracts(entities, business)


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
