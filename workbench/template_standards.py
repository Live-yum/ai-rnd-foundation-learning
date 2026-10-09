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
