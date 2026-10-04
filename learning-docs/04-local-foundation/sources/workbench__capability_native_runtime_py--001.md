# workbench/capability_native_runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_isolation`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_start_command`（L17–L33）：接收`plan`。 控制顺序：L29按`plan.runtime.start.cwd != "backend" or plan.runtime.start.argv != expected`分支；L30抛异常，停止当前正常路径。 调用`str`、`CheckFailure`。 返回路径：L33的`plan.runtime.start`。
- `native_prepare_commands`（L36–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`TaskCommand`。 返回路径：L37的`[ TaskCommand( cwd="backend", argv=["uv", "sync", "--locked", "--offline", "--python", "3.…`。
- `frontend_start_command`（L61–L62）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`TaskCommand`。 返回路径：L62的`TaskCommand(cwd="frontend/web", argv=["node", CONTROL + "/native-preview.mjs"])`。
- `verify_and_freeze_native_sources`（L65–L127）：接收`sandbox`、`inventory`、`timeout`。 控制顺序：L126按`result.exit_code != 0`分支；L127抛异常，停止当前正常路径。 调用`inventory.items`、`sandbox.fs.upload_file`、`json.dumps(expected).encode`、`json.dumps`、`launcher.encode`、`control_exec`、`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/capability_native_runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L127。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5369`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_native_runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f5f129985c572bd1e37082b2b0e3c316861632bac160cb2d6d3b2aeb1316229b"} -->
````python
# workbench/capability_native_runtime.py
"""Controller-owned native build/launch contract; candidate code stays sandboxed."""

import json

from workbench.capability_contracts import TaskCommand
from workbench.capability_isolation import CONTROL, control_exec
from workbench.capability_verification import CheckFailure

FRONTEND_PORT = 5173
GENERATED_TYPES = {
    "frontend/web/src/types/auto-imports.d.ts",
    "frontend/web/src/types/components.d.ts",
    "frontend/web/.eslintrc-auto-import.json",
}


def native_start_command(plan):
    expected = [
        ".venv/bin/python",
        "-m",
        "uvicorn",
        "app:create_app",
        "--factory",
        "--host",
        "0.0.0.0",
        "--port",
        str(plan.runtime.port),
    ]
    if plan.runtime.start.cwd != "backend" or plan.runtime.start.argv != expected:
        raise CheckFailure(
            "原生启动必须使用backend/.venv的准确app:create_app工厂命令，不能添加替代入口选项"
        )
    return plan.runtime.start


def native_prepare_commands():
    return [
        TaskCommand(
            cwd="backend", argv=["uv", "sync", "--locked", "--offline", "--python", "3.14"]
        ),
        TaskCommand(
            cwd="frontend/web",
            argv=[
                "pnpm",
                "install",
                "--offline",
                "--frozen-lockfile",
                "--store-dir",
                "/tmp/rnd-capability/pnpm-store",
            ],
        ),
        TaskCommand(
            cwd="frontend/web", argv=["pnpm", "exec", "vite", "build", "--mode", "production"]
        ),
        TaskCommand(
            cwd="frontend/web", argv=["pnpm", "exec", "vue-tsc", "--noEmit", "--skipLibCheck"]
        ),
    ]


def frontend_start_command():
    return TaskCommand(cwd="frontend/web", argv=["node", CONTROL + "/native-preview.mjs"])


def verify_and_freeze_native_sources(sandbox, inventory, timeout):
    expected = {name: value for name, value in inventory.items() if name not in GENERATED_TYPES}
    path = CONTROL + "/private/source-manifest.json"
    sandbox.fs.upload_file(json.dumps(expected).encode(), path, timeout=timeout)
    # Vite preview otherwise inherits server.open=true from the pinned native
    # config and may try to spawn another browser. Use its public JS API with an
    # explicit closed preview policy; this trusted launcher runs as app UID.
    launcher = """import {preview} from '/tmp/rnd-capability/product/frontend/web/node_modules/vite/dist/node/index.js';
await preview({root:'/tmp/rnd-capability/product/frontend/web',mode:'production',preview:{host:'0.0.0.0',port:5173,strictPort:true,open:false}});
"""
    sandbox.fs.upload_file(launcher.encode(), CONTROL + "/native-preview.mjs", timeout=timeout)
    script = r"""
import hashlib,json,os,pathlib,stat
root=pathlib.Path('/tmp/rnd-capability/product')
expected=json.loads(pathlib.Path('/tmp/rnd-module-control/private/source-manifest.json').read_text())
for name,digest in expected.items():
 p=root/name
 current=root
 for part in pathlib.PurePosixPath(name).parts:
  current=current/part;assert not current.is_symlink()
 assert not p.is_symlink() and p.resolve().is_relative_to(root.resolve()) and p.is_file()
 with p.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==digest
assert (root/'frontend/web/dist/index.html').is_file()
writable=('backend/data','backend/logs','backend/static/upload','frontend/web/node_modules/.vite-temp')
# The app UID has already been drained by the trusted supervisor. Check every
# existing component BEFORE root mkdir/chown, including an absent leaf's parent.
# No candidate process may race these checks while sources are being frozen.
for relative in writable:
 current=root
 assert not current.is_symlink() and current.is_dir()
 for part in pathlib.PurePosixPath(relative).parts:
  current=current/part
  assert not current.is_symlink()
  if current.exists():assert current.is_dir()
 assert current.resolve().is_relative_to(root.resolve())
 if current.exists():
  for directory,dirs,names in os.walk(current,followlinks=False):
   for name in [*dirs,*names]:
    child=pathlib.Path(directory)/name;entry=child.lstat()
    assert not stat.S_ISLNK(entry.st_mode)
    assert stat.S_ISDIR(entry.st_mode) or (stat.S_ISREG(entry.st_mode) and entry.st_nlink==1)
# Freeze code and dependencies only after successful offline build/typecheck.
# A bounded writable area remains for logs/uploads/data and Vite's config cache.
for directory,dirs,names in os.walk(root,followlinks=False):
 for name in [*dirs,*names]:
  p=pathlib.Path(directory)/name
  if p.is_symlink():continue
  os.chown(p,0,0)
  p.chmod(0o755 if p.is_dir() or os.access(p,os.X_OK) else 0o644)
os.chown(root,0,0);root.chmod(0o755)
for relative in writable:
 p=root/relative;p.mkdir(parents=True,exist_ok=True)
 assert not p.is_symlink() and p.resolve().is_relative_to(root.resolve())
 for directory,dirs,names in os.walk(p,followlinks=False):
  for name in [*dirs,*names]:
   child=pathlib.Path(directory)/name
   assert not child.is_symlink()
   os.chown(child,20000,20000)
 os.chown(p,20000,20000);p.chmod(0o700)
"""
    result = control_exec(sandbox, ["/usr/bin/python3", "-I", "-S", "-c", script], timeout)
    if result.exit_code != 0:
        raise CheckFailure("原生构建改变受保护源码、缺少真实前端构建产物或无法冻结源码")
````
