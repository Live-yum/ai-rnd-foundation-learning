# scripts/build_handbook.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：生成唯一完整教材。** 按GUIDES顺序拼正文并调整图片相对路径，再按GROUPS枚举自有源码与真实截图，排除依赖/运行目录；附录写源码指纹、完整代码及可折叠Base64二进制块。--check比较全部文本与唯一输出，不改源码。

**对应关系：** 正文及真实源文件 → render → 单一Markdown；test_handbook验证独立重建。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.handbook_notes`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `generated_frontend_asset`（L106–L108）：接收`name`。 源码说明：Vite output is a lossless runtime snapshot, not handwritten lesson source.。 调用`name.startswith`。 返回路径：L108的`name.startswith(GENERATED_FRONTEND_PREFIX)`。
- `encoded_lines`（L111–L114）：接收`content`。 源码说明：Wrap ASCII Base64 at 76 characters without repeatedly slicing a long word.。 调用`base64.b64encode(content).decode`、`base64.b64encode`、`"\n".join`、`range`、`len`。 返回路径：L114的`"\n".join(encoded[index : index + 76] for index in range(0, len(encoded), 76))`。
- `sources`（L117–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L119遍历`GROUPS`；L121遍历`paths`；L123按`not path.exists()`分支；L124抛异常，停止当前正常路径；L130遍历`items`；L131按`not item.is_file() or item.suffix == ".pyc" or any( part in { "__pycache__", ".venv",…`分支；L152按`name in { ".github/workflows/prepare-local-tools.yml", ".github/workflows/runtime-con…`分支；L157按`name not in seen`分支。 调用`set`、`path.exists`、`FileNotFoundError`、`path.is_dir`、`sorted`、`path.rglob`、`item.relative_to(ROOT).as_posix`、`item.relative_to`、`item.is_file`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `guide_text`（L168–L175）：接收`name`。 源码说明：Keep image links valid in both the chapter and the root-level handbook.。 调用`(ROOT / name).read_text(encoding="utf-8").rstrip`、`(ROOT / name).read_text`、`re.sub`、`Path(name).parent.as_posix`、`Path`。 返回路径：L171的`re.sub( r"(!\[[^\]\n]*\]\()images/", lambda match: match[1] + Path(name).parent.as_posix()…`。
- `render`（L178–L232）：不接收显式业务参数，从已配置对象/模块读取依赖。生成物完全由正文源文件和实际源码计算；检查模式比较整份结果，不允许手动修改生成手册来掩盖源码不同步。 控制顺序：L181遍历`sources()`；L183遍历`rows`；L184按`isinstance(content, bytes)`分支。 调用`"\n\n".join`、`guide_text`、`sources`、`isinstance`、`hashlib.sha256(content).hexdigest`、`hashlib.sha256`、`encoded_lines`、`generated_frontend_asset`、`hashlib.sha256(content.encode()).hexdigest`等。 返回路径：L232的`text`。
- `main`（L235–L248）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L240按`args.check`分支；L241按`not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected`分支；L242抛异常，停止当前正常路径；L243按`len(list(ROOT.glob("从零实现AI研发平台_逐步实操手册_完整版*.md"))) != 1`分支；L244抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`render`、`OUTPUT.exists`、`OUTPUT.read_text`、`SystemExit`、`len`、`list`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/build_handbook.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L252。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9713`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/build_handbook.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bb9133bc0de1c2e9f916e57d65a0524fc90789c8b16338df393be78f5da3abbc"} -->
`````python
# scripts/build_handbook.py
"""Render a complete, reconstructable handbook from tracked source, never from memory."""

import argparse
import base64
import hashlib
import re
from pathlib import Path

from scripts.handbook_notes import notes

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "从零实现AI研发平台_逐步实操手册_完整版.md"
GUIDES = [
    "docs/template-platform.md",
    "docs/guide.md",
    "docs/implementation.md",
    "docs/implementation-labs.md",
    "docs/native-baseline.md",
    "docs/toolchain.md",
    "docs/recommendation-recovery.md",
    "docs/native-toolchain.md",
    "docs/business-platform.md",
    "docs/provider-structured-outputs.md",
    "docs/model-feedback-verification.md",
    "docs/real-model-acceptance.md",
    "docs/from-zero-checkpoints.md",
    "docs/acceptance-checklist.md",
    "docs/extension-acceptance-lifecycle.md",
    "docs/workflow-optimization.md",
    "docs/template-customization-roadmap.md",
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
    ("Vue操作台完整源码、构建配置与依赖锁", ["ui"]),
    ("冻结数据库迁移", ["migrations"]),
    ("默认产品与前端", ["templates/product", "templates/frontends"]),
    ("各技术模板的共享与专用编码规范", ["templates/standards"]),
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
            "tools/browser",
            "docs/candidate-browser-isolation.md",
            "docs/contest-extension-oracle.md",
            "docs/custom-source-isolation.md",
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
    ("真实操作截图与来源证据", ["docs/images"]),
]
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
GENERATED_FRONTEND_PREFIX = "workbench/web/"


def generated_frontend_asset(name):
    """Vite output is a lossless runtime snapshot, not handwritten lesson source."""
    return name.startswith(GENERATED_FRONTEND_PREFIX)


def encoded_lines(content):
    """Wrap ASCII Base64 at 76 characters without repeatedly slicing a long word."""
    encoded = base64.b64encode(content).decode("ascii")
    return "\n".join(encoded[index : index + 76] for index in range(0, len(encoded), 76))


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
                    content = (
                        item.read_bytes()
                        if item.suffix.lower() in BINARY_SUFFIXES or generated_frontend_asset(name)
                        else item.read_text(encoding="utf-8")
                    )
                    rows.append((name, content))
                    seen.add(name)
        yield title, rows


def guide_text(name):
    """Keep image links valid in both the chapter and the root-level handbook."""
    content = (ROOT / name).read_text(encoding="utf-8").rstrip()
    return re.sub(
        r"(!\[[^\]\n]*\]\()images/",
        lambda match: match[1] + Path(name).parent.as_posix() + "/images/",
        content,
    )


def render():
    text = "\n\n".join(guide_text(name) for name in GUIDES)
    text += "\n\n# 完整源码附录\n"
    for title, rows in sources():
        text += "\n## " + title + "\n"
        for name, content in rows:
            if isinstance(content, bytes):
                code_sha = hashlib.sha256(content).hexdigest()
                encoded = encoded_lines(content)
                text += (
                    f"\n### `{name}`\n\n"
                    + (
                        "这是ui源码构建出的操作台静态资产快照，不是需要手写或修改的压缩代码。"
                        "阅读ui/src与构建配置，执行npm ci --prefix ui及npm run build --prefix ui生成；"
                        "独立还原仍保留精确运行字节，干净构建须再次与此快照逐文件核对。\n\n"
                        if generated_frontend_asset(name)
                        else "真实PNG等二进制资源按原始字节收录；正文通过相对路径显示图片。"
                        "它不是模型绘制的截图。\n\n"
                    )
                    + "下列Base64仅供独立还原程序解码，并校验解码后SHA-256。\n\n"
                    "<details>\n<summary>展开二进制还原数据</summary>\n\n"
                    f"<!-- source-file: {name} sha256: {code_sha} encoding: base64 -->\n"
                    f"````base64\n{encoded}\n````\n\n</details>\n"
                )
                continue
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
`````
