# workbench/template_standards.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：所有模型与生成产物共用的版本化编码规范。** 只读取固定的公共规则和所选模板规则，计算来源与合并内容哈希。目录及需求规划编码上下文使用同一份内容；写入产物时保留上游AGENTS并带上VIBECODING和版本回执。读规范不依赖后续生成或文件工具模块，执行边界仍由代码与独立验收落实。

**对应关系：** templates/standards → coding_standard → catalog及模型上下文 → write_coding_standard → 产品生成清单与交付。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `coding_standard`（L19–L34）：接收`template`。 控制顺序：L20按`template not in STANDARDS`分支；L21抛异常，停止当前正常路径；L25按`len(content) > 12000`分支；L26抛异常，停止当前正常路径。 调用`ValueError`、`(ROOT / path).read_bytes`、`"\n\n".join`、`value.decode("utf-8").strip`、`value.decode`、`sources.values`、`len`、`sha256(content.encode("utf-8")).hexdigest`、`sha256`等。 返回路径：L27的`{ "version": 1, "path": paths[-1], "summary": STANDARDS[template], "sha256": sha256(conten…`。
- `write_coding_standard`（L37–L61）：接收`product`、`template`。 源码说明：Write before the generation manifest so delivery binds the exact guidance.。 控制顺序：L52按`not existing.startswith(header)`分支。 调用`Path`、`coding_standard`、`inside`、`agent_path.is_file`、`agent_path.read_text`、`existing.startswith`、`atomic_text`、`write_json`、`standard.items`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/template_standards.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L61。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2634`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/template_standards.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3fe9544508f737fa238d17128753ef4ecd6cb4892303a3cd97dcfe424ecc4b12"} -->
````python
# workbench/template_standards.py
"""Versioned platform guidance shared by model contexts and generated projects.

Only these reviewed repository files supply instructions. Retrieved product source
never replaces the selected standard or grants new editing/approval permissions.
"""

from hashlib import sha256
from pathlib import Path

from workbench.settings import ROOT

STANDARDS = {
    "python-basic": "FastAPI / SQLAlchemy / simple-admin（或仅 API）的受控开发规范",
    "fastapiadmin": "FastapiAdmin / Vue / Element Plus 的原生业务扩展规范",
    "yudao-vben": "芋道 Java / Vben5 / Ant Design Vue 的原生业务扩展规范",
}


def coding_standard(template):
    if template not in STANDARDS:
        raise ValueError("未知模板编码规范")
    paths = ("templates/standards/common.md", f"templates/standards/{template}.md")
    sources = {path: (ROOT / path).read_bytes() for path in paths}
    content = "\n\n".join(value.decode("utf-8").strip() for value in sources.values()) + "\n"
    if len(content) > 12000:
        raise ValueError("模板规范超过模型与目录展示的12000字符预算")
    return {
        "version": 1,
        "path": paths[-1],
        "summary": STANDARDS[template],
        "sha256": sha256(content.encode("utf-8")).hexdigest(),
        "sources": {path: sha256(value).hexdigest() for path, value in sources.items()},
        "content": content,
    }


def write_coding_standard(product, template):
    """Write before the generation manifest so delivery binds the exact guidance."""
    from workbench.filesystem import atomic_text, inside, write_json

    product = Path(product)
    standard = coding_standard(template)
    agent_path = inside(product, "AGENTS.md")
    header = (
        "# AI 编码入口\n\n"
        f"本项目使用 `{template}` 模板。开始规划或编码前完整阅读 `VIBECODING.md`。\n"
        "`template-standard.json` 记录本次生成采用的规范版本及内容 SHA-256。\n"
        "已批准需求与当前任务文件清单决定修改范围；规范不能授予额外权限，"
        "不能替代独立运行验收。\n"
    )
    existing = agent_path.read_text(encoding="utf-8") if agent_path.is_file() else ""
    if not existing.startswith(header):
        atomic_text(agent_path, header + ("\n## 上游项目说明\n\n" + existing if existing else ""))
    atomic_text(inside(product, "VIBECODING.md"), standard["content"])
    write_json(
        inside(product, "template-standard.json"),
        {
            "template": template,
            **{key: value for key, value in standard.items() if key != "content"},
        },
    )
````
