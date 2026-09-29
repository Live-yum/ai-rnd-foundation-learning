"""Render a complete, reconstructable handbook from tracked source, never from memory."""

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "从零实现AI研发平台_逐步实操手册_完整版_v3.md"
GUIDES = ["docs/guide.md", "docs/native-baseline.md"]
GROUPS = [
    (
        "项目配置",
        [
            ".python-version",
            ".gitignore",
            ".gitattributes",
            ".env.example",
            "pyproject.toml",
            "README.md",
            "SECURITY.md",
            "alembic.ini",
        ],
    ),
    (
        "数据库与输入契约",
        [
            "workbench/__init__.py",
            "workbench/settings.py",
            "workbench/domain.py",
            "workbench/store.py",
            "migrations",
        ],
    ),
    (
        "文件、模型、代码规则与知识包",
        [
            "workbench/filesystem.py",
            "workbench/tools.py",
            "workbench/llm.py",
            "workbench/rules.py",
            "workbench/knowledge.py",
            "workbench/coding.py",
        ],
    ),
    (
        "默认产品与原生模板",
        [
            "workbench/generator.py",
            "workbench/verification.py",
            "workbench/native.py",
            "templates/product",
        ],
    ),
    (
        "原生基线的实际运行与验证",
        [
            "workbench/native_environment.py",
            "workbench/native_checks.py",
            "workbench/native_frontend.py",
            "workbench/native_vben.py",
            "workbench/native_modules.py",
            "workbench/native_compatibility.py",
            "workbench/native_acceptance.py",
            "workbench/native_lab.py",
            "workbench/native_delivery.py",
        ],
    ),
    (
        "完整工作流与操作入口",
        ["workbench/flow.py", "workbench/runtime.py", "workbench/api.py", "workbench/cli.py"],
    ),
    ("自动化测试", ["tests"]),
    (
        "构建与CI",
        [
            "scripts",
            ".github/workflows/test.yml",
            ".github/workflows/native-runtime.yml",
            ".github/workflows/native-probe.yml",
        ],
    ),
    ("平台真实依赖锁", ["uv.lock"]),
    ("手册正文源文件", GUIDES),
]


def sources():
    seen = set()
    for title, paths in GROUPS:
        rows = []
        for relative in paths:
            path = ROOT / relative
            if not path.exists():
                raise FileNotFoundError(f"Handbook source missing: {relative}")
            items = (
                sorted(path.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix())
                if path.is_dir()
                else [path]
            )
            for item in items:
                if not item.is_file() or "__pycache__" in item.parts or item.suffix == ".pyc":
                    continue
                name = item.relative_to(ROOT).as_posix()
                if name not in seen:
                    rows.append((name, item.read_text(encoding="utf-8")))
                    seen.add(name)
        yield title, rows


def render():
    text = "\n\n".join((ROOT / name).read_text(encoding="utf-8").rstrip() for name in GUIDES)
    text += "\n\n# 完整源码附录\n"
    for title, rows in sources():
        text += "\n## " + title + "\n"
        for name, content in rows:
            code_sha = hashlib.sha256(content.encode()).hexdigest()
            fence = "`" * max(
                4,
                max(
                    (len(line) for line in content.splitlines() if line and set(line) == {"`"}),
                    default=0,
                )
                + 1,
            )
            language = {
                ".py": "python",
                ".md": "markdown",
                ".toml": "toml",
                ".yml": "yaml",
                ".json": "json",
                ".cjs": "javascript",
            }.get(Path(name).suffix, "text")
            text += f"\n### `{name}`\n\n<!-- source-file: {name} sha256: {code_sha} -->\n{fence}{language}\n{content.rstrip(chr(10))}\n{fence}\n"
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("手册与源码不一致：执行 uv run python -m scripts.build_handbook")
        print("Handbook source consistency PASS")
    else:
        OUTPUT.write_text(expected, encoding="utf-8", newline="\n")
        print("Handbook written successfully")


if __name__ == "__main__":
    main()
