"""Render a complete, reconstructable handbook from tracked source, never from memory."""

import argparse
import hashlib
from pathlib import Path

from scripts.handbook_notes import notes

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "从零实现AI研发平台_逐步实操手册_完整版.md"
GUIDES = [
    "docs/guide.md",
    "docs/implementation.md",
    "docs/implementation-labs.md",
    "docs/native-baseline.md",
    "docs/toolchain.md",
    "docs/recommendation-recovery.md",
    "docs/native-toolchain.md",
    "docs/business-platform.md",
    "docs/real-model-acceptance.md",
    "docs/from-zero-checkpoints.md",
    "docs/acceptance-checklist.md",
]
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
    ("后端全部实现与控制台", ["workbench"]),
    ("冻结数据库迁移", ["migrations"]),
    ("默认产品与前端", ["templates/product", "templates/frontends"]),
    ("独立原生交付启动器", ["templates/deployment"]),
    ("业务合同的原生适配模板", ["templates/business"]),
    ("完整需求与结构化验收案例", ["examples"]),
    (
        "自带原生源码的版本与许可证",
        [
            "templates/vendor/manifest.json",
            "templates/vendor/fastapiadmin.LICENSE",
            "templates/vendor/yudao-backend.LICENSE",
            "templates/vendor/yudao-frontend.LICENSE",
        ],
    ),
    ("全部测试", ["tests"]),
    (
        "工具及Actions",
        [
            "scripts",
            ".github/workflows",
            "tools/aider/pyproject.toml",
            "tools/aider/offline_runner.py",
            "tools/aider/.python-version",
            "tools/aider/uv.lock",
            "tools/daytona",
            "tools/embeddings/pyproject.toml",
            "tools/embeddings/uv.lock",
        ],
    ),
    (
        "本机Continue组件、适配器及Node依赖锁",
        [
            "tools/node/package.json",
            "tools/node/package-lock.json",
            "tools/node/build.mjs",
            "tools/node/continue-host.mjs",
            "tools/node/continue-runner.mjs",
            "tools/node/no-network.cjs",
            "tools/node/plop-runner.mjs",
            "tools/node/templates",
            "tools/node/upstream/manifest.json",
            "tools/node/upstream/FullTextSearchCodebaseIndex.ts",
            "tools/node/upstream/LICENSE",
        ],
    ),
    ("平台依赖锁", ["uv.lock"]),
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
                if (
                    not item.is_file()
                    or item.suffix == ".pyc"
                    or any(
                        part
                        in {
                            "__pycache__",
                            ".venv",
                            "node_modules",
                            ".git",
                            ".data",
                            ".native",
                            ".built",
                            ".pytest_cache",
                            ".ruff_cache",
                        }
                        for part in item.relative_to(ROOT).parts
                    )
                ):
                    continue
                name = item.relative_to(ROOT).as_posix()
                if name in {
                    ".github/workflows/prepare-local-tools.yml",
                    ".github/workflows/runtime-contract.yml",
                }:
                    continue  # Temporary review infrastructure is not part of the product.
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
                ".mjs": "javascript",
                ".ts": "typescript",
                ".java": "java",
                ".vue": "vue",
                ".js": "javascript",
                ".html": "html",
                ".css": "css",
                ".yaml": "yaml",
            }.get(Path(name).suffix, "text")
            # A fence needs its own line, but the source may be empty or omit its
            # final newline. The extractor uses the SHA to recover that distinction.
            body = content if content.endswith("\n") else content + "\n"
            text += f"\n### `{name}`\n\n{notes(name, content)}<!-- source-file: {name} sha256: {code_sha} -->\n{fence}{language}\n{body}{fence}\n"
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("手册与源码不一致：执行 uv run python -m scripts.build_handbook")
        if len(list(ROOT.glob("从零实现AI研发平台_逐步实操手册_完整版*.md"))) != 1:
            raise SystemExit("只能保留一份正式完整手册")
        print("Single handbook source consistency PASS")
    else:
        OUTPUT.write_text(expected, encoding="utf-8", newline="\n")
        print("Handbook written successfully")


if __name__ == "__main__":
    main()
