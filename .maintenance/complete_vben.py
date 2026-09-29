"""Apply exact reviewed source edits on the diagnostic branch, never on upstream."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
changes = {}


def edit(name, old, new):
    source = changes.get(name, (root / name).read_text(encoding="utf-8"))
    if source.count(old) != 1:
        raise ValueError(f"Expected one reviewed context in {name}: {old!r}")
    changes[name] = source.replace(old, new)


edit("workbench/native_vben.py", "from workbench.filesystem import atomic_text, sha, write_json", "from workbench.filesystem import atomic_text, sha, write_json\nfrom workbench.tools import run_command")
edit("workbench/native_vben.py", "def prepare_vben_source(root, reports):", '''def checked_replacement(source: str, old: str, new: str, count: int, name: str) -> str:
    if source.count(old) != count:
        raise ValueError("Pinned Vben compatibility contract changed: " + name)
    return source.replace(old, new)


def initialize_vben_boundary(root: Path) -> None:
    """Create a new local scan boundary, with no upstream history/remotes/hooks."""
    root = Path(root).resolve()
    if (root / ".git").exists() or (root / ".git").is_symlink():
        raise ValueError("Vben compatibility requires a fresh source copy without .git")
    run_command(["git", "init", "--quiet", "--template=", str(root)], root, 30)


def prepare_vben_source(root: Path, reports: Path):''')
edit("workbench/native_vben.py", '''        if source.count(old) != count:
            raise ValueError("Pinned Vben compatibility contract changed: " + name)
        changed[name] = source.replace(old, new)''', '''        changed[name] = checked_replacement(source, old, new, count, name)''')
edit("workbench/native_vben.py", "    # Validate all 25 input shapes before changing the first file.", '''    edit(
        "system/dept/components/select-modal.vue",
        ".filter((id: number) => id !== undefined)",
        ".filter((id): id is number => typeof id === 'number')",
    )
    # Validate every input shape before creating the boundary or changing any file.
    initialize_vben_boundary(root)''')
edit("workbench/native_vben.py", '        "routes_removed": False,', '        "independent_git_boundary": True,\n        "routes_removed": False,')
edit("workbench/native_frontend.py", "from workbench.settings import ROOT", "from workbench.native_vben import prepare_vben_source\nfrom workbench.settings import ROOT")
edit("workbench/native_frontend.py", '    if template == "yudao-vben":\n        # Vben', '    if template == "yudao-vben":\n        prepare_vben_source(root, reports)\n        # Vben')
edit("scripts/build_handbook.py", '            "workbench/native_frontend.py",', '            "workbench/native_frontend.py",\n            "workbench/native_vben.py",')
edit("tests/test_native_frontend_lifecycle.py", '    monkeypatch.setattr(native_frontend, "run_command", tool)', '    monkeypatch.setattr(native_frontend, "run_command", tool)\n    monkeypatch.setattr(native_frontend, "prepare_vben_source", lambda *_: None)')
edit("docs/native-baseline.md", "### 19.11 兼容规则与排错\n", '''### 19.11 兼容规则与排错

Vben 固定版本 `1b14e889f529e245fd620daa720dcea6de0cc5e7` 的兼容入口为 `workbench/native_vben.py`，在业务模块挂载完成后、前端冻结安装之前自动执行，不需要读者手工拼补丁。它核对全部预期源码片段后，修复已存在组件的失效引用、表单上下文、弹窗载荷和可选值、集合/排序声明、IP 校验 API，以及部门 ID 的类型收窄。任何输入片段不匹配都会报错，不盲目替换新版本源码。

工作副本不会复制上游 `.git`、令牌或环境文件。Vben 副本单独执行 `git init --quiet --template=` 建立本地扫描边界，没有上游 remote、提交历史或 hooks；此边界也不进入源码 ZIP。缺少边界时，构建扫描可能跨入平台和兄弟工作目录，导致日志停滞与内存异常增长。不要用扩大内存、删除业务路由或禁用类型检查代替修复。保留原始仓库不变，并保存 `vben-compatibility.json` 中逐文件的 before/after SHA-256。

前端使用原始 `apps/web-antd` 入口和完整应用配置。顺序为 `pnpm install --frozen-lockfile`、`vite build --mode production`、`vue-tsc --noEmit --skipLibCheck`；最后一项检查全部应用源码和生成模块，`skipLibCheck` 仅沿用第三方声明检查边界，不排除业务目录，不加入 `@ts-ignore`、`@ts-nocheck` 或宽泛 `any` 来掩盖错误。构建、类型检查、重启持久化和真实浏览器均成功才写入最终成功回执。
''')
edit("docs/native-baseline.md", '| `native-compatibility.json` | 原生工作副本兼容修正的前后哈希 |', '| `native-compatibility.json`、`vben-compatibility.json` | 原生工作副本兼容修正的前后哈希与 Vben 独立扫描边界 |')
name = "tests/test_native_vben.py"
if (root / name).exists():
    raise FileExistsError(name)
changes[name] = '''"""Small regression contracts; full Vben verification uses the real pinned application."""

import json
from pathlib import Path

import pytest

from workbench.filesystem import manifest
from workbench.native_environment import copy_source
from workbench.native_vben import checked_replacement, initialize_vben_boundary
from workbench.tools import run_command


def test_checked_replacement_is_exact_and_preserves_unrelated_source():
    source = "before; old; after;"
    assert checked_replacement(source, "old", "new", 1, "fixture") == "before; new; after;"
    assert source == "before; old; after;"


@pytest.mark.parametrize("source", ["missing", "old old"])
def test_changed_or_ambiguous_upstream_context_fails_closed(source):
    with pytest.raises(ValueError, match="compatibility contract changed"):
        checked_replacement(source, "old", "new", 1, "fixture")


def test_vben_boundary_is_local_and_excluded_from_delivery(tmp_path):
    source = tmp_path / "upstream"
    (source / ".git").mkdir(parents=True)
    (source / ".git/config").write_text("never-copy-upstream-credentials")
    (source / ".env").write_text("API_KEY=never-copy-me")
    (source / "package.json").write_text(json.dumps({"name": "boundary-fixture"}))
    destination = tmp_path / "product"
    copy_source(source, destination)
    before = manifest(destination)
    initialize_vben_boundary(destination)
    assert manifest(destination) == before
    assert not (destination / ".env").exists()
    config = (destination / ".git/config").read_text()
    assert "remote" not in config and "never-copy" not in config
    assert not (destination / ".git/hooks").exists()
    result = run_command(["git", "rev-parse", "--show-toplevel"], destination, 30)
    assert Path(result["log"].strip()).resolve() == destination.resolve()
    with pytest.raises(ValueError, match="fresh source copy"):
        initialize_vben_boundary(destination)
'''
# Fail before writing if any reviewed context above changed.
for name, source in changes.items():
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8", newline="\n")
print("Applied reviewed Vben completion changes:", ", ".join(sorted(changes)))
