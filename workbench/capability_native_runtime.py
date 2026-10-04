"""Controller-owned native build/launch contract; candidate code stays sandboxed."""

import json

from workbench.capability_contracts import TaskCommand
from workbench.capability_dependencies import NATIVE_LINK_CODE, NATIVE_NODE_ROOT
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
    launcher = (
        "import {preview} from '"
        + NATIVE_NODE_ROOT
        + "/vite/dist/node/index.js';\n"
        + """
await preview({root:'/tmp/rnd-capability/product/frontend/web',mode:'production',preview:{host:'0.0.0.0',port:5173,strictPort:true,open:false}});
"""
    )
    sandbox.fs.upload_file(launcher.encode(), CONTROL + "/native-preview.mjs", timeout=timeout)
    script = (
        NATIVE_LINK_CODE
        + r"""
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
# A whole-tree inventory is required: hashing only the original files lets a
# build add importable Python/JS, replace dependency links, or hide hardlinks.
# Only actual frontend output and the known Vite/config generation paths vary.
generated={
 'frontend/web/src/types/auto-imports.d.ts',
 'frontend/web/src/types/components.d.ts',
 'frontend/web/.eslintrc-auto-import.json',
}
variable=('frontend/web/dist','frontend/web/node_modules/.vite-temp')
allowed_directories={'.'}
for relative in [*expected,*generated]:
 p=pathlib.PurePosixPath(relative).parent
 while str(p)!='.':allowed_directories.add(str(p));p=p.parent
for relative in ('backend/data','backend/logs','backend/static/upload',*variable):
 p=pathlib.PurePosixPath(relative)
 while str(p)!='.':allowed_directories.add(str(p));p=p.parent
for directory,dirs,names in os.walk(root,followlinks=False):
 for name in [*dirs,*names]:
  p=pathlib.Path(directory)/name;relative=p.relative_to(root).as_posix();entry=p.lstat()
  dependency=relative=='frontend/web/node_modules' or relative.startswith('frontend/web/node_modules/')
  varying=any(relative==prefix or relative.startswith(prefix+'/') for prefix in variable)
  if stat.S_ISLNK(entry.st_mode):
   assert dependency
  elif stat.S_ISDIR(entry.st_mode):
   assert dependency or varying or relative in allowed_directories
  else:
   assert stat.S_ISREG(entry.st_mode) and entry.st_nlink==1
   assert relative in expected or relative in generated or varying
assert link_manifest.is_file() and not link_manifest.is_symlink()
validate_links()
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
  os.chown(p,0,0,follow_symlinks=False)
  p.chmod(0o755 if p.is_dir() or os.access(p,os.X_OK) else 0o644)
os.chown(root,0,0,follow_symlinks=False);root.chmod(0o755)
for relative in writable:
 p=root/relative;p.mkdir(parents=True,exist_ok=True)
 assert not p.is_symlink() and p.resolve().is_relative_to(root.resolve())
 for directory,dirs,names in os.walk(p,followlinks=False):
  for name in [*dirs,*names]:
   child=pathlib.Path(directory)/name
   assert not child.is_symlink()
   os.chown(child,20000,20000,follow_symlinks=False)
 os.chown(p,20000,20000,follow_symlinks=False);p.chmod(0o700)
"""
    )
    result = control_exec(sandbox, ["/usr/bin/python3", "-I", "-S", "-c", script], timeout)
    if result.exit_code != 0:
        raise CheckFailure("原生构建改变受保护源码、缺少真实前端构建产物或无法冻结源码")
