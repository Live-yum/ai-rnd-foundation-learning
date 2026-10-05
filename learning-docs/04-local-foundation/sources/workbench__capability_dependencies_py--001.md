# workbench/capability_dependencies.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_isolation`、`workbench.capability_verification`、`workbench.domain`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_descriptor_roles`（L26–L43）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Keep this wheel-owned data policy equal to both isolated image-side tables.。 返回路径：L28的`{ "runtime": [ "backend/pyproject.toml", "backend/uv.lock", "frontend/web/package.json", "…`。
- `_profile`（L46–L51）：接收`plan`。 控制顺序：L49按`profile not in supported or plan.selection.database != supported[profile]`分支；L50抛异常，停止当前正常路径。 调用`CheckFailure`。 返回路径：L51的`profile`。
- `require_dependency_manifest`（L54–L101）：接收`value`、`profile`。 控制顺序：L63按`profile == "fastapiadmin"`分支；L65按`type(value) is not dict or set(value) != fields or type(value.get("schema")) is not i…`分支；L82抛异常，停止当前正常路径；L87按`profile not in descriptors or set(value["original_descriptors"]) != descriptors[profi…`分支；L88抛异常，停止当前正常路径；L89遍历`value["original_descriptors"].items()`；L90按`type(name) is not str or not name or str(PurePosixPath(name)) != name or PurePosixPat…`分支；L100抛异常，停止当前正常路径。 调用`fields.add`、`type`、`set`、`value.get`、`re.fullmatch`、`any`、`native_descriptor_roles`、`CheckFailure`、`native_descriptor_roles().values`等。 返回路径：L101的`value`。
- `require_dependency_descriptors`（L104–L129）：接收`product`、`plan`、`record`。 源码说明：Local fail-closed preflight before even creating/uploading a sandbox.。 控制顺序：L110按`expected["image_id"] != record["snapshot"].get("image_id")`分支；L111抛异常，停止当前正常路径；L116遍历`roots`；L118按`raw.is_symlink()`分支；L119抛异常，停止当前正常路径；L121按`path.exists()`分支；L122抛异常，停止当前正常路径；L127按`observed != expected["original_descriptors"]`分支。后续分支沿下方源码相同行号继续阅读。 调用`_profile`、`type`、`record.get`、`snapshot.get`、`require_dependency_manifest`、`record["snapshot"].get`、`CheckFailure`、`readonly_prepare_commands`、`readonly_start_command`等。 返回路径：L129的`expected`。
- `readonly_prepare_commands`（L132–L162）：接收`plan`。 源码说明：Only these exact install contracts are satisfied by verified image data.。 控制顺序：L134按`_profile(plan) == "fastapiadmin"`分支；L143按`plan.runtime.prepare and plan.runtime.prepare != trusted`分支；L144抛异常，停止当前正常路径；L160按`plan.runtime.prepare != expected`分支；L161抛异常，停止当前正常路径。 调用`_profile`、`native_start_command`、`native_prepare_commands`、`CheckFailure`、`native_frontend_build_command`、`TaskCommand`。 返回路径：L145的`[ native_frontend_build_command(), TaskCommand( cwd="frontend/web", argv=[ NODE, NATIVE_NO…`；L162的`[]`。
- `readonly_start_command`（L165–L193）：接收`plan`、`command`。 源码说明：Translate a validated launcher, never arbitrary command prefixes.。 控制顺序：L168按`profile == "fastapiadmin"`分支；L172按`command is not None and command == frontend_start_command()`分支；L174按`command is not None and command != native`分支；L175抛异常，停止当前正常路径；L181按`command != plan.runtime.start or command.cwd != "." or len(argv) != 8 or argv[0] not …`分支；L192抛异常，停止当前正常路径。 调用`_profile`、`native_start_command`、`frontend_start_command`、`TaskCommand`、`CheckFailure`、`len`、`re.fullmatch`、`str`。 返回路径：L173的`TaskCommand(cwd="frontend/web", argv=[NODE, CONTROL + "/native-preview.mjs"])`；L176的`TaskCommand( cwd=native.cwd, argv=[NATIVE_PYTHON_ROOT + "/bin/python", *native.argv[1:]] )`；L193的`TaskCommand(cwd=".", argv=[PYTHON_ROOT + "/bin/python", *argv[1:]])`。
- `_verify_image`（L298–L336）：接收`sandbox`、`plan`、`timeout`、`expected`。 控制顺序：L317按`type(result.exit_code) is not int or result.exit_code != 0`分支；L318抛异常，停止当前正常路径；L319按`type(result.result) is not str or len(result.result) > 4096`分支；L320抛异常，停止当前正常路径；L322按`type(value) is not dict or set(value) != {"schema", "profile", "manifest_sha256", "in…`分支；L333抛异常，停止当前正常路径；L335抛异常，停止当前正常路径。 调用`_profile`、`require_dependency_manifest`、`control_exec`、`type`、`len`、`json.loads`、`set`、`value.get`、`any`等。 返回路径：L336的`value`。
- `_source_contract`（L425–L467）：接收`plan`、`source_inventory`。 控制顺序：L426按`type(source_inventory) is not dict or not source_inventory`分支；L427抛异常，停止当前正常路径；L428遍历`source_inventory.items()`；L429按`type(name) is not str or not name or str(PurePosixPath(name)) != name or PurePosixPat…`分支；L439抛异常，停止当前正常路径；L440按`plan.selection.database == "sqlite"`分支；L444按`str(database) != value or database.is_absolute() or ".." in database.parts or "\\" in…`分支；L461抛异常，停止当前正常路径。 调用`type`、`CheckFailure`、`source_inventory.items`、`str`、`PurePosixPath`、`PurePosixPath(name).is_absolute`、`re.fullmatch`、`database.parent.as_posix`、`database.is_absolute`等。 返回路径：L462的`{ "profile": _profile(plan), "database": plan.selection.database, "database_path": plan.ru…`。
- `_verify_sources`（L470–L477）：接收`sandbox`、`plan`、`timeout`、`source_inventory`、`initial`。 控制顺序：L475按`result.exit_code != 0`分支；L476抛异常，停止当前正常路径。 调用`_source_contract`、`sandbox.fs.upload_file`、`json.dumps(contract).encode`、`json.dumps`、`repr`、`control_exec`、`CheckFailure`、`digest`。 返回路径：L477的`{"source_inventory_sha256": digest(source_inventory), "source_inventory_verified": True}`。
- `prepare_readonly_dependencies`（L480–L491）：接收`sandbox`、`plan`、`timeout`、`expected`、`source_inventory`。 控制顺序：L485按`_profile(plan) == "fastapiadmin"`分支；L489按`result.exit_code != 0`分支；L490抛异常，停止当前正常路径。 调用`readonly_prepare_commands`、`readonly_start_command`、`_verify_image`、`_verify_sources`、`_profile`、`control_exec`、`CheckFailure`。 返回路径：L491的`{**receipt, **source, "product_links_verified": True}`。
- `verify_readonly_dependencies`（L494–L497）：接收`sandbox`、`plan`、`timeout`、`expected`、`source_inventory`。 调用`_verify_image`、`_verify_sources`。 返回路径：L497的`{**receipt, **source, "product_links_verified": True}`。

</details>

**创建路径：** `workbench/capability_dependencies.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L497。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21708`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_dependencies.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a0eb524d2a97ffdad56e7e2ad5bf2b84545ddddad0d554d0b82777d8a5ca7047"} -->
````python
# workbench/capability_dependencies.py
"""Admit pinned, immutable dependencies without executing candidate install code.

The trusted image verifier reads descriptors as data under system Python -I -S.
No candidate Python, package manager, build hook or virtualenv is run as root.
"""

import json
import re
from pathlib import Path, PurePosixPath

from workbench.capability_contracts import TaskCommand
from workbench.capability_isolation import CONTROL, PRODUCT, control_exec
from workbench.capability_verification import CheckFailure
from workbench.domain import digest
from workbench.filesystem import inside, manifest

IMAGE_VERIFIER = "/opt/rnd/bin/dependency-image.py"
PYTHON_ROOT = "/opt/rnd/runtime/python-basic/.venv"
NATIVE_PYTHON_ROOT = "/opt/rnd/runtime/fastapiadmin/backend/.venv"
NATIVE_NODE_ROOT = "/opt/rnd/runtime/fastapiadmin/frontend/node_modules"
NODE = "/usr/local/bin/node"
LINK_MANIFEST = CONTROL + "/private/dependency-links.json"
RECEIPT_FLAGS = ("descriptors_verified", "installed_tree_verified", "readonly_verified")


def native_descriptor_roles():
    """Keep this wheel-owned data policy equal to both isolated image-side tables."""
    return {
        "runtime": [
            "backend/pyproject.toml",
            "backend/uv.lock",
            "frontend/web/package.json",
            "frontend/web/pnpm-lock.yaml",
        ],
        "portable_launcher": ["deployment/pyproject.toml", "deployment/uv.lock"],
        "auxiliary_source": [
            "frontend/app/package.json",
            "frontend/app/pnpm-lock.yaml",
            "frontend/app/src/uni_modules/mp-html/package.json",
            "frontend/docs/package.json",
            "frontend/docs/pnpm-lock.yaml",
        ],
    }


def _profile(plan):
    profile = plan.selection.template
    supported = {"python-basic": "sqlite", "fastapiadmin": "postgresql"}
    if profile not in supported or plan.selection.database != supported[profile]:
        raise CheckFailure("所选技术栈没有登记的只读依赖运行契约")
    return profile


def require_dependency_manifest(value, profile):
    fields = {
        "schema",
        "profile",
        "image_id",
        "manifest_sha256",
        "installed_tree_sha256",
        "original_descriptors",
    }
    if profile == "fastapiadmin":
        fields.add("descriptor_roles")
    if (
        type(value) is not dict
        or set(value) != fields
        or type(value.get("schema")) is not int
        or value["schema"] != 1
        or value.get("profile") != profile
        or type(value.get("image_id")) is not str
        or not re.fullmatch(r"sha256:[a-f0-9]{64}", value["image_id"])
        or any(
            type(value.get(key)) is not str or not re.fullmatch(r"[a-f0-9]{64}", value[key])
            for key in ("manifest_sha256", "installed_tree_sha256")
        )
        or type(value.get("original_descriptors")) is not dict
        or not value["original_descriptors"]
        or profile == "fastapiadmin"
        and value.get("descriptor_roles") != native_descriptor_roles()
    ):
        raise CheckFailure("缺少与当前镜像绑定的只读依赖清单")
    descriptors = {
        "python-basic": {"pyproject.toml", "uv.lock"},
        "fastapiadmin": {name for paths in native_descriptor_roles().values() for name in paths},
    }
    if profile not in descriptors or set(value["original_descriptors"]) != descriptors[profile]:
        raise CheckFailure("只读依赖描述符集合不属于已登记技术栈")
    for name, sha256 in value["original_descriptors"].items():
        if (
            type(name) is not str
            or not name
            or str(PurePosixPath(name)) != name
            or PurePosixPath(name).is_absolute()
            or ".." in PurePosixPath(name).parts
            or "\\" in name
            or type(sha256) is not str
            or not re.fullmatch(r"[a-f0-9]{64}", sha256)
        ):
            raise CheckFailure("只读依赖描述符清单无效")
    return value


def require_dependency_descriptors(product, plan, record):
    """Local fail-closed preflight before even creating/uploading a sandbox."""
    profile = _profile(plan)
    snapshot = record.get("snapshot") if type(record) is dict else None
    expected = snapshot.get("dependency_manifest") if type(snapshot) is dict else None
    require_dependency_manifest(expected, profile)
    if expected["image_id"] != record["snapshot"].get("image_id"):
        raise CheckFailure("只读依赖清单与已登记镜像不一致")
    readonly_prepare_commands(plan)
    readonly_start_command(plan)
    # Reject imported/local dependency trees even if general source inventories exclude them.
    roots = (".venv", "node_modules", "backend/.venv", "frontend/web/node_modules")
    for relative in roots:
        raw = Path(product) / relative
        if raw.is_symlink():
            raise CheckFailure("候选依赖路径不能是符号链接")
        path = inside(product, relative)
        if path.exists():
            raise CheckFailure("候选源码不能携带虚拟环境或依赖目录")
    names = {"pyproject.toml", "uv.lock", "pnpm-lock.yaml", "package.json", "pom.xml"}
    inventory = manifest(product)
    _source_contract(plan, inventory)
    observed = {name: digest for name, digest in inventory.items() if Path(name).name in names}
    if observed != expected["original_descriptors"]:
        raise CheckFailure("候选依赖描述符与已登记只读镜像不一致")
    return expected


def readonly_prepare_commands(plan):
    """Only these exact install contracts are satisfied by verified image data."""
    if _profile(plan) == "fastapiadmin":
        from workbench.capability_native_runtime import (
            native_frontend_build_command,
            native_prepare_commands,
            native_start_command,
        )

        native_start_command(plan)
        trusted = native_prepare_commands()
        if plan.runtime.prepare and plan.runtime.prepare != trusted:
            raise CheckFailure("原生构建只允许登记的准确prepare契约")
        return [
            native_frontend_build_command(),
            TaskCommand(
                cwd="frontend/web",
                argv=[
                    NODE,
                    NATIVE_NODE_ROOT + "/vue-tsc/bin/vue-tsc.js",
                    "--noEmit",
                    "--skipLibCheck",
                ],
            ),
        ]
    expected = [
        TaskCommand(argv=["uv", "sync", "--locked", "--offline", "--no-dev", "--python", "3.14"])
    ]
    if plan.runtime.prepare != expected:
        raise CheckFailure("Python只读依赖仅接受登记的准确离线安装契约")
    return []


def readonly_start_command(plan, command=None):
    """Translate a validated launcher, never arbitrary command prefixes."""
    profile = _profile(plan)
    if profile == "fastapiadmin":
        from workbench.capability_native_runtime import frontend_start_command, native_start_command

        native = native_start_command(plan)
        if command is not None and command == frontend_start_command():
            return TaskCommand(cwd="frontend/web", argv=[NODE, CONTROL + "/native-preview.mjs"])
        if command is not None and command != native:
            raise CheckFailure("未登记的原生启动契约")
        return TaskCommand(
            cwd=native.cwd, argv=[NATIVE_PYTHON_ROOT + "/bin/python", *native.argv[1:]]
        )
    command = command or plan.runtime.start
    argv = command.argv
    if (
        command != plan.runtime.start
        or command.cwd != "."
        or len(argv) != 8
        or argv[0] not in {"./.venv/bin/python", ".venv/bin/python"}
        or argv[1:3] != ["-m", "uvicorn"]
        or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*:[A-Za-z_][A-Za-z0-9_]*", argv[3]
        )
        or argv[4:] != ["--host", "0.0.0.0", "--port", str(plan.runtime.port)]
    ):
        raise CheckFailure("Python只读依赖仅接受准确的uvicorn模块启动契约")
    return TaskCommand(cwd=".", argv=[PYTHON_ROOT + "/bin/python", *argv[1:]])


# Executed only by the trusted system interpreter. All candidate processes must
# be stopped before post-build verification. No os.walk follows a symbolic link.
NATIVE_LINK_CODE = r"""
import json,os,pathlib,re,stat
root=pathlib.Path('/tmp/rnd-capability/product')
image=pathlib.Path('/opt/rnd/runtime/fastapiadmin/frontend/node_modules')
link_manifest=pathlib.Path('/tmp/rnd-module-control/private/dependency-links.json')
modules=root/'frontend/web/node_modules'
def owned_path(path):
 current=path
 while True:
  st=current.lstat()
  assert not stat.S_ISLNK(st.st_mode) and st.st_uid==0 and not st.st_mode & 0o022
  if current==pathlib.Path('/'):break
  current=current.parent
def ordinary(path):
 current=root
 assert current.is_dir() and not current.is_symlink()
 for part in path.relative_to(root).parts:
  current=current/part
  assert not current.is_symlink()
  if current.exists():assert current.is_dir()
def image_links():
 owned_path(image)
 links={};directories=['.']
 for entry in sorted(image.iterdir()):
  if entry.name in {'.bin','.vite-temp'}:continue
  if entry.name.startswith('@'):
   assert entry.is_dir() and not entry.is_symlink()
   owned_path(entry)
   directories.append(entry.name)
   for child in sorted(entry.iterdir()):links[entry.name+'/'+child.name]=str(child)
  else:links[entry.name]=str(entry)
 assert '.pnpm' in links and 'vite' in links and 'vue-tsc' in links
 for name,target in links.items():
  final=pathlib.Path(target).resolve(strict=True)
  assert final.is_relative_to(image)
  owned_path(final)
 return links,directories
def validate_links():
 expected=json.loads(link_manifest.read_text())
 links,directories=image_links()
 assert set(expected)=={'links','directories','identities','cache_identity'}
 assert expected['links']==links and expected['directories']==directories
 ordinary(modules)
 seen=set();actual_directories=set()
 for directory,dirs,names in os.walk(modules,followlinks=False):
  relative=pathlib.Path(directory).relative_to(modules).as_posix()
  if relative=='.vite-temp' or relative.startswith('.vite-temp/'):
   assert relative=='.vite-temp' and not dirs
   for name in names:
    assert re.fullmatch(r'vite\.config\.(?:ts|mts|cts|js|mjs|cjs)\.timestamp-[0-9]+-[a-f0-9]+\.mjs',name)
    child=pathlib.Path(directory)/name;st=child.lstat()
    assert not stat.S_ISLNK(st.st_mode)
    assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size<=32_000_000
   continue
  assert relative in directories
  actual_directories.add(relative)
  st=pathlib.Path(directory).lstat()
  assert st.st_uid==0 and not st.st_mode & 0o022
  assert [st.st_dev,st.st_ino]==expected['identities'][relative]
  for name in [*dirs,*names]:
   child=pathlib.Path(directory)/name;rel=child.relative_to(modules).as_posix();st=child.lstat()
   if rel in directories:assert stat.S_ISDIR(st.st_mode)
   elif rel=='.vite-temp':
    assert stat.S_ISDIR(st.st_mode) and st.st_uid==20000 and stat.S_IMODE(st.st_mode)==0o700
    assert [st.st_dev,st.st_ino]==expected['cache_identity']
   else:
    assert rel in links and stat.S_ISLNK(st.st_mode) and st.st_uid==0
    assert os.readlink(child)==links[rel]
    assert [st.st_dev,st.st_ino]==expected['identities'][rel]
    seen.add(rel)
 assert seen==set(links) and actual_directories==set(directories)
 assert (modules/'.vite-temp').is_dir()
 return links
"""

CREATE_NATIVE_LINKS = (
    NATIVE_LINK_CODE
    + r"""
links,directories=image_links()
ordinary(modules.parent)
assert not modules.exists() and not modules.is_symlink()
modules.mkdir(mode=0o755)
for relative in directories:
 p=modules/relative
 if relative!='.':p.mkdir(mode=0o755)
 os.chown(p,0,0);p.chmod(0o755)
for relative,target in links.items():
 p=modules/relative;p.symlink_to(target);os.lchown(p,0,0)
cache=modules/'.vite-temp';cache.mkdir(mode=0o700);os.chown(cache,20000,20000)
identities={}
for relative in [*directories,*links]:
 st=(modules/relative).lstat();identities[relative]=[st.st_dev,st.st_ino]
st=cache.lstat()
link_manifest.write_text(json.dumps({'links':links,'directories':directories,'identities':identities,'cache_identity':[st.st_dev,st.st_ino]}))
link_manifest.chmod(0o600)
validate_links()
"""
)


def _verify_image(sandbox, plan, timeout, expected):
    profile = _profile(plan)
    require_dependency_manifest(expected, profile)
    result = control_exec(
        sandbox,
        [
            "/usr/bin/python3",
            "-I",
            "-S",
            IMAGE_VERIFIER,
            "verify-runtime",
            "--profile",
            profile,
            "--product",
            PRODUCT,
        ],
        timeout,
    )
    try:
        if type(result.exit_code) is not int or result.exit_code != 0:
            raise ValueError
        if type(result.result) is not str or len(result.result) > 4096:
            raise ValueError
        value = json.loads(result.result)
        if (
            type(value) is not dict
            or set(value)
            != {"schema", "profile", "manifest_sha256", "installed_tree_sha256", *RECEIPT_FLAGS}
            or type(value.get("schema")) is not int
            or any(
                value.get(key) != expected[key]
                for key in ("schema", "profile", "manifest_sha256", "installed_tree_sha256")
            )
            or any(value.get(key) is not True for key in RECEIPT_FLAGS)
        ):
            raise ValueError
    except ValueError, TypeError:
        raise CheckFailure("只读镜像依赖、描述符或安装产物与可信清单不一致") from None
    return value


SOURCE_INVENTORY = CONTROL + "/private/dependency-source-inventory.json"
SOURCE_CODE = (
    NATIVE_LINK_CODE
    + r"""
import hashlib
contract=json.loads(pathlib.Path('/tmp/rnd-module-control/private/dependency-source-inventory.json').read_text())
expected=contract['inventory'];native=contract['profile']=='fastapiadmin'
assert (contract['profile'],contract['database']) in {('python-basic','sqlite'),('fastapiadmin','postgresql')}
initial=MODE=='initial'
generated={
 'frontend/web/src/types/auto-imports.d.ts',
 'frontend/web/src/types/components.d.ts',
 'frontend/web/.eslintrc-auto-import.json',
} if native and not initial else set()
variable=('frontend/web/dist','frontend/web/node_modules/.vite-temp') if native and not initial else ()
writable=('backend/data','backend/logs','backend/static/upload') if native else ()
database=pathlib.PurePosixPath(contract['database_path'])
data_directory=str(database.parent)
if not native and contract['database']=='sqlite':
 assert str(database)==contract['database_path'] and data_directory!='.' and not database.is_absolute() and '..' not in database.parts
 assert '\\' not in contract['database_path'] and ':' not in contract['database_path']
 assert database.suffix.lower() in {'.db','.sqlite','.sqlite3'}
 assert not any(part.lower() in {'.git','.venv','node_modules','__pycache__'} for part in database.parts)
 assert not any(name==data_directory or name.startswith(data_directory+'/') or data_directory.startswith(name+'/') for name in expected)
 writable=(data_directory,)
# A writable data subtree is not permission to add importable source. Runtime
# data are narrowly typed; neither symlinks nor hardlinks are ever accepted.
data_suffixes={'.db','.sqlite','.sqlite3','.db-wal','.db-shm','.db-journal','.sqlite-wal','.sqlite-shm','.sqlite-journal','.sqlite3-wal','.sqlite3-shm','.sqlite3-journal'}
upload_suffixes={'.png','.jpg','.jpeg','.gif','.webp','.svg','.pdf','.txt','.csv','.xlsx','.docx'}
def runtime_data(relative):
 if initial:return False
 if not native:
  return relative in {str(database)+suffix for suffix in ('','-wal','-shm','-journal')}
 name=pathlib.PurePosixPath(relative)
 if relative.startswith('backend/logs/'):
  # The native logger uses timestamped .log files and compressed rotations.
  return '.log' in name.name and name.suffix in {'.log','.gz','.zip'}
 if relative.startswith('backend/data/'):
  return any(name.name.endswith(suffix) for suffix in data_suffixes)
 if relative.startswith('backend/static/upload/'):
  return name.suffix.lower() in upload_suffixes
 return False
allowed_directories={'.'}
for relative in [*expected,*generated]:
 p=pathlib.PurePosixPath(relative).parent
 while str(p)!='.':allowed_directories.add(str(p));p=p.parent
for relative in [*variable,*writable]:
 p=pathlib.PurePosixPath(relative)
 while str(p)!='.':allowed_directories.add(str(p));p=p.parent
assert root.is_dir() and not root.is_symlink()
seen=set();ordinary_entries=[root]
for directory,dirs,names in os.walk(root,followlinks=False):
 for name in [*dirs,*names]:
  p=pathlib.Path(directory)/name;relative=p.relative_to(root).as_posix();st=p.lstat()
  dependency=native and not initial and (relative=='frontend/web/node_modules' or relative.startswith('frontend/web/node_modules/'))
  varying=any(relative==prefix or relative.startswith(prefix+'/') for prefix in variable)
  data_directory_allowed=native and not initial and any(relative.startswith(prefix+'/') for prefix in writable)
  if stat.S_ISLNK(st.st_mode):assert dependency
  elif stat.S_ISDIR(st.st_mode):
   assert relative in allowed_directories or dependency or varying or data_directory_allowed
   ordinary_entries.append(p)
  else:
   assert stat.S_ISREG(st.st_mode) and st.st_nlink==1
   assert relative in expected or relative in generated or varying or runtime_data(relative)
   if relative in expected:
    seen.add(relative)
    if relative not in generated:
     with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected[relative]
   ordinary_entries.append(p)
assert set(expected)-generated==seen-generated
if native and not initial:validate_links()
# Freeze the base product before its first command, granting only the dedicated
# SQLite directory. A root-level database would require a writable source root
# and therefore cannot be accepted under this profile.
if not native and initial:
 for path in ordinary_entries:
  os.chown(path,0,0,follow_symlinks=False)
  path.chmod(0o755 if path.is_dir() else 0o644)
 for relative in writable:
  target=root/relative;ordinary(target)
  target.mkdir(parents=True,exist_ok=True)
  os.chown(target,20000,20000,follow_symlinks=False);target.chmod(0o700)
"""
)


def _source_contract(plan, source_inventory):
    if type(source_inventory) is not dict or not source_inventory:
        raise CheckFailure("缺少本次准确源码清单")
    for name, sha256 in source_inventory.items():
        if (
            type(name) is not str
            or not name
            or str(PurePosixPath(name)) != name
            or PurePosixPath(name).is_absolute()
            or ".." in PurePosixPath(name).parts
            or "\\" in name
            or type(sha256) is not str
            or not re.fullmatch(r"[a-f0-9]{64}", sha256)
        ):
            raise CheckFailure("本次源码清单包含无效路径或摘要")
    if plan.selection.database == "sqlite":
        value = plan.runtime.database_path
        database = PurePosixPath(value)
        parent = database.parent.as_posix()
        if (
            str(database) != value
            or database.is_absolute()
            or ".." in database.parts
            or "\\" in value
            or ":" in value
            or parent == "."
            or database.suffix.lower() not in {".db", ".sqlite", ".sqlite3"}
            or any(
                part.lower() in {".git", ".venv", "node_modules", "__pycache__"}
                for part in database.parts
            )
            or any(
                name == parent or name.startswith(parent + "/") or parent.startswith(name + "/")
                for name in source_inventory
            )
        ):
            raise CheckFailure("只读SQLite契约要求独立非源码子目录及.db/.sqlite/.sqlite3数据库文件")
    return {
        "profile": _profile(plan),
        "database": plan.selection.database,
        "database_path": plan.runtime.database_path,
        "inventory": source_inventory,
    }


def _verify_sources(sandbox, plan, timeout, source_inventory, *, initial):
    contract = _source_contract(plan, source_inventory)
    sandbox.fs.upload_file(json.dumps(contract).encode(), SOURCE_INVENTORY, timeout=timeout)
    script = "MODE=" + repr("initial" if initial else "verify") + "\n" + SOURCE_CODE
    result = control_exec(sandbox, ["/usr/bin/python3", "-I", "-S", "-c", script], timeout)
    if result.exit_code != 0:
        raise CheckFailure("源码清单出现新增模块、链接、内容漂移或不安全数据路径")
    return {"source_inventory_sha256": digest(source_inventory), "source_inventory_verified": True}


def prepare_readonly_dependencies(sandbox, plan, timeout, *, expected, source_inventory):
    readonly_prepare_commands(plan)
    readonly_start_command(plan)
    receipt = _verify_image(sandbox, plan, timeout, expected)
    source = _verify_sources(sandbox, plan, timeout, source_inventory, initial=True)
    if _profile(plan) == "fastapiadmin":
        result = control_exec(
            sandbox, ["/usr/bin/python3", "-I", "-S", "-c", CREATE_NATIVE_LINKS], timeout
        )
        if result.exit_code != 0:
            raise CheckFailure("无法创建与只读镜像完全匹配的前端依赖链接")
    return {**receipt, **source, "product_links_verified": True}


def verify_readonly_dependencies(sandbox, plan, timeout, *, expected, source_inventory):
    receipt = _verify_image(sandbox, plan, timeout, expected)
    source = _verify_sources(sandbox, plan, timeout, source_inventory, initial=False)
    return {**receipt, **source, "product_links_verified": True}
````
