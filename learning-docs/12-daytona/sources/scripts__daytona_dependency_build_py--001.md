# scripts/daytona_dependency_build.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_dependency_build；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `adapt_native_preview_source`（L44–L94）：接收`raw`。 源码说明：Patch the reviewed advisory call only, never a catch around preview/hooks. Upstream: vitejs/vite v7.3.3, packages/vite/src/node/{utils,preview}.ts. The official published dist file is hash-bound befor。 控制顺序：L51按`hashlib.sha256(raw).hexdigest() != VITE_PREVIEW_UPSTREAM_SHA256`分支；L52抛异常，停止当前正常路径；L87遍历`changes`；L88按`source.count(old) != 1`分支；L89抛异常，停止当前正常路径；L92按`hashlib.sha256(result).hexdigest() != VITE_PREVIEW_PATCHED_SHA256`分支；L93抛异常，停止当前正常路径。 调用`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`ValueError`、`raw.decode`、`source.count`、`source.replace`、`source.encode`、`hashlib.sha256(result).hexdigest`。 返回路径：L94的`result`。
- `_preview_patch_record`（L97–L105）：接收`relative`。 返回路径：L98的`{ "id": "vite-preview-interface-eperm-v1", "package": "vite", "version": "7.3.3", "relativ…`。
- `_native_preview_file`（L109–L153）：接收`writable`。 源码说明：Resolve one known pnpm link as data, then open every component no-follow.。 控制顺序：L112按`not root.is_absolute() or ".." in root.parts`分支；L113抛异常，停止当前正常路径；L117遍历`root.parts[1:]`；L122按`not stat.S_ISLNK(link.st_mode) or link.st_nlink != 1`分支；L123抛异常，停止当前正常路径；L125按`not re.fullmatch(VITE_PREVIEW_PACKAGE_PATH, target)`分支；L126抛异常，停止当前正常路径；L128遍历`PurePosixPath(relative).parts[:-1]`。后续分支沿下方源码相同行号继续阅读。 调用`root.is_absolute`、`ValueError`、`os.open`、`os.close`、`os.stat`、`stat.S_ISLNK`、`os.readlink`、`re.fullmatch`、`PurePosixPath`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_preview_source_bytes`（L156–L162）：接收`descriptor`。 控制顺序：L160按`len(raw) > 2_000_000 or os.fstat(descriptor).st_nlink != 1`分支；L161抛异常，停止当前正常路径。 调用`os.lseek`、`os.fdopen`、`os.dup`、`stream.read`、`len`、`os.fstat`、`ValueError`。 返回路径：L162的`raw`。
- `patch_native_preview`（L165–L185）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Data-only mutation in the existing non-root, credential-free builder.。 控制顺序：L167按`os.geteuid() == 0`分支；L168抛异常，停止当前正常路径；L173在`remaining`成立时循环；L175按`written <= 0`分支；L176抛异常，停止当前正常路径；L180按`hashlib.sha256(_preview_source_bytes(descriptor)).hexdigest() != VITE_PREVIEW_PATCHED…`分支；L184抛异常，停止当前正常路径。 调用`os.geteuid`、`ValueError`、`_native_preview_file`、`adapt_native_preview_source`、`_preview_source_bytes`、`os.lseek`、`memoryview`、`os.write`、`os.ftruncate`等。 返回路径：L185的`_preview_patch_record(relative)`。
- `native_preview_patch_provenance`（L188–L196）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：The collector reopens the installed bytes; a patch sidecar is insufficient.。 控制顺序：L191按`hashlib.sha256(_preview_source_bytes(descriptor)).hexdigest() != VITE_PREVIEW_PATCHED…`分支；L195抛异常，停止当前正常路径。 调用`_native_preview_file`、`hashlib.sha256(_preview_source_bytes(descriptor)).hexdigest`、`hashlib.sha256`、`_preview_source_bytes`、`ValueError`、`_preview_patch_record`。 返回路径：L196的`[_preview_patch_record(relative)]`。
- `native_descriptor_roles`（L199–L220）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Exact source metadata roles; only runtime projects have image install paths. Keep the standalone image verifier's data-only table identical. Both scripts run with -I -S in the image and cannot import 。 返回路径：L205的`{ "runtime": [ "backend/pyproject.toml", "backend/uv.lock", "frontend/web/package.json", "…`。
- `validate_native_descriptor_inputs`（L223–L261）：接收`value`。 源码说明：Hash inert source descriptor bytes without parsing or running their projects.。 控制顺序：L227按`type(value) is not dict or value.get("descriptor_roles") != roles`分支；L228抛异常，停止当前正常路径；L229遍历`("original_descriptors", "normalized_descriptors")`；L231按`type(observed) is not dict or set(observed) != names or any( type(item) is not str or…`分支；L239抛异常，停止当前正常路径；L242按`type(contents) is not dict or set(contents) != source_names`分支；L243抛异常，停止当前正常路径；L245遍历`source_names`。后续分支沿下方源码相同行号继续阅读。 调用`native_descriptor_roles`、`roles.values`、`type`、`value.get`、`ValueError`、`set`、`any`、`re.fullmatch`、`observed.values`等。 返回路径：L261的`roles`。
- `sha`（L264–L265）：接收`path`。 调用`hashlib.sha256(Path(path).read_bytes()).hexdigest`、`hashlib.sha256`、`Path(path).read_bytes`、`Path`。 返回路径：L265的`hashlib.sha256(Path(path).read_bytes()).hexdigest()`。
- `normalize`（L268–L274）：接收`raw`。 控制顺序：L271遍历`MIRRORS.items()`。 调用`raw.decode`、`tomllib.loads`、`MIRRORS.items`、`text.replace`、`text.encode`。 返回路径：L274的`text.encode("utf-8")`。
- `public_url`（L277–L288）：接收`url`、`hosts`。 控制顺序：L279按`value.scheme != "https" or value.hostname not in hosts or value.username is not None …`分支；L288抛异常，停止当前正常路径。 调用`urlsplit`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_python`（L291–L333）：接收`project_raw`、`lock_raw`、`trusted_project`。 控制顺序：L294按`project.get("project", {}).get("dynamic")`分支；L295抛异常，停止当前正常路径；L296按`project.get("build-system") and not trusted_project`分支；L297抛异常，停止当前正常路径；L299遍历`project.get("project", {}).get("optional-dependencies", {}).value…`；L301遍历`project.get("dependency-groups", {}).values()`；L303按`any( not isinstance(value, str) or "@" in value or re.search(r"(?:https?:\|git[+:]\|f…`分支；L309抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`tomllib.loads`、`project_raw.decode`、`lock_raw.decode`、`project.get("project", {}).get`、`project.get`、`ValueError`、`list`、`project.get("project", {}).get("optional-dependencies", {}).value…`、`requirements.extend`等。 返回路径：L333的`lock`。
- `validate_node`（L336–L377）：接收`package_raw`、`lock_raw`。 控制顺序：L340遍历`( "dependencies", "devDependencies", "optionalDependencies", "pee…`；L346遍历`package.get(group, {}).values()`；L347按`not isinstance(spec, str) or re.search( r"(?:https?:\|git[+:]\|file:\|link:\|workspac…`分支；L350抛异常，停止当前正常路径；L352按`set(pnpm) - {"overrides"} or package.get("workspaces")`分支；L353抛异常，停止当前正常路径；L354遍历`pnpm.get("overrides", {}).values()`；L355按`not isinstance(spec, str) or not re.fullmatch(r"[0-9A-Za-z.^~*<>=\| +_-]+", spec)`分支。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`package.get(group, {}).values`、`package.get`、`isinstance`、`re.search`、`ValueError`、`set`、`pnpm.get("overrides", {}).values`、`pnpm.get`等。 返回路径：L377的`lock`。
- `limits`（L380–L387）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`resource.setrlimit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run`（L390–L443）：接收`command`、`cwd`、`offline`、`metadata`。 控制顺序：L391按`os.geteuid() == 0`分支；L392抛异常，停止当前正常路径；L413按`metadata`分支。 调用`os.geteuid`、`ValueError`、`str`、`TemporaryDirectory`、`nullcontext`、`Path`、`env.update`、`subprocess.run`。 返回路径：L434的`subprocess.run( command, cwd=cwd, env=env, check=True, timeout=60 if metadata else 1800, p…`。
- `download`（L446–L456）：接收`record`、`destination`。 控制顺序：L452按`len(raw) > 64 * 1024**2 or hashlib.sha256(raw).hexdigest() != record["sha256"]`分支；L453抛异常，停止当前正常路径。 调用`public_url`、`urllib.request.build_opener`、`urllib.request.ProxyHandler`、`opener.open`、`response.read`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`ValueError`等。 返回路径：L456的`path`。
- `extract_source`（L459–L479）：接收`path`、`destination`。 控制顺序：L462按`len(members) > 10000 or sum(item.size for item in members) > 128 * 1024**2`分支；L463抛异常，停止当前正常路径；L465遍历`members`；L467按`name.is_absolute() or ".." in name.parts or not (item.isdir() or item.isfile()) or ".…`分支；L474抛异常，停止当前正常路径；L476按`len(top) != 1`分支；L477抛异常，停止当前正常路径。 调用`tarfile.open`、`archive.getmembers`、`len`、`sum`、`ValueError`、`set`、`PurePosixPath`、`name.is_absolute`、`item.isdir`等。 返回路径：L479的`destination / top.pop()`。
- `fetch`（L482–L548）：接收`lock_path`、`backend`。 控制顺序：L483按`os.geteuid() == 0`分支；L484抛异常，停止当前正常路径；L490遍历`spec["tools"]`；L519遍历`spec["sdists"]`；L521按`package.get("version") != record["version"] or package.get("sdist", {}).get("hash") !…`分支；L525抛异常，停止当前正常路径；L528按`record["name"] == "sqlglotrs"`分支；L530遍历`cargo["package"]`。后续分支沿下方源码相同行号继续阅读。 调用`os.geteuid`、`ValueError`、`json.loads`、`Path(lock_path).read_bytes`、`Path`、`tomllib.loads`、`(Path(backend) / "uv.lock").read_text`、`downloads.mkdir`、`download`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `wheel_outputs`（L551–L574）：接收`path`、`package`。 源码说明：Record real native payloads; do not accept crcmod's silent C-build fallback.。 控制顺序：L556遍历`archive.infolist()`；L558按`name.is_absolute() or ".." in name.parts or ((item.external_attr >> 16) & 0o170000) =…`分支；L563抛异常，停止当前正常路径；L564按`item.filename.endswith(".so")`分支；L566按`item.filename.endswith(".dist-info/WHEEL")`分支；L572按`not tags or (package in {"crcmod", "sqlglotrs"} and not native)`分支；L573抛异常，停止当前正常路径。 调用`zipfile.ZipFile`、`archive.infolist`、`PurePosixPath`、`name.is_absolute`、`ValueError`、`item.filename.endswith`、`hashlib.sha256(archive.read(item)).hexdigest`、`hashlib.sha256`、`archive.read`等。 返回路径：L574的`{"wheel_tags": tags, "native_extensions": native}`。
- `build_sources`（L577–L615）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L581遍历`json.loads((BUILD / "sources.json").read_bytes())`；L594按`item["name"] == "sqlglotrs"`分支；L597按`item.get("cargo_lock_sha256") and sha(source / "Cargo.lock") != item["cargo_lock_sha2…`分支；L601抛异常，停止当前正常路径；L605按`len(matches) != 1`分支；L606抛异常，停止当前正常路径。 调用`output.mkdir`、`json.loads`、`(BUILD / "sources.json").read_bytes`、`Path`、`str`、`run`、`item.get`、`sha`、`ValueError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `replace_source_requirements`（L618–L642）：接收`raw`、`builds`。 控制顺序：L619遍历`builds`；L640按`count != 1`分支；L641抛异常，停止当前正常路径。 调用`re.escape`、`re.subn`、`ValueError`。 返回路径：L642的`raw`。
- `replace_source_requirements.replace`（L628–L637）：接收`match`。 调用`match[1].rstrip().removesuffix("\\").strip`、`match[1].rstrip().removesuffix`、`match[1].rstrip`、`Path(item["wheel"]).as_uri`、`Path`。 返回路径：L630的`item["name"] + " @ " + Path(item["wheel"]).as_uri() + (" " + marker if marker else "") + "…`。
- `install`（L645–L689）：接收`project`、`basic`、`harness`。 控制顺序：L661按`basic`分支；L663按`harness`分支；L669按`environment.is_symlink() or (environment.exists() and any(environment.iterdir()))`分支；L670抛异常，停止当前正常路径；L688按`original != {name: sha(project / name) for name in original}`分支；L689抛异常，停止当前正常路径。 调用`Path`、`sha`、`str`、`run`、`json.loads`、`(BUILD / "source-builds.json").read_bytes`、`export.write_text`、`replace_source_requirements`、`export.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `collect`（L692–L771）：接收`inputs`、`output`、`native`。 控制顺序：L710按`python_runtime["version"] != [3, 14, 7] or python_runtime["machine"] != "x86_64" or p…`分支；L715抛异常，停止当前正常路径；L717遍历`runtime_names`；L724按`sha(target) != expected`分支；L725抛异常，停止当前正常路径；L726遍历`value.get("harness_descriptors", {}).items()`；L727按`sha(Path("/opt/rnd/harness") / name) != expected`分支；L728抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`Path(inputs).read_bytes`、`Path`、`validate_native_descriptor_inputs`、`run`、`str`、`ValueError`、`name.replace`、`sha`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L774–L796）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L787按`args.action == "fetch"`分支；L789按`args.action == "build-sources"`分支；L791按`args.action == "install"`分支；L793按`args.action == "patch-native-preview"`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`fetch`、`build_sources`、`install`、`patch_native_preview`、`collect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_dependency_build.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L800。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`32645`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_dependency_build.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "50cff37756e9cd482f6afd45a68f68c60b6101e6923a94276508577d3f2ed3e9"} -->
````python
# scripts/daytona_dependency_build.py
"""Reviewed descriptor-only dependency build; never import candidate code.

Registry sdists are an explicit hash allowlist. Fetch and build are separate
Docker stages/steps: build runs non-root, offline, without secrets or host mounts.
Unsupported Python source builds fail without lock, source or ABI workarounds.
Native Vite preview has one separately hash-bound, data-only advisory URL patch.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import stat
import subprocess
import tarfile
import tomllib
import urllib.request
import zipfile
from contextlib import contextmanager, nullcontext
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

BUILD = Path("/opt/rnd/build")
TOOLS = Path("/opt/rnd/build-tools")
PYTHON = "3.14.7"
PYTHON_BUILD = Path("/opt/rnd/bin/python-build")
UV = "/usr/local/bin/uv"
MIRRORS = {
    "https://pypi.tuna.tsinghua.edu.cn/simple": "https://pypi.org/simple",
    "https://pypi.tuna.tsinghua.edu.cn/packages/": "https://files.pythonhosted.org/packages/",
}

SOURCE_DESCRIPTOR_BYTES = 8_000_000
NATIVE_FRONTEND_MODULES = Path("/opt/rnd/runtime/fastapiadmin/frontend/node_modules")
VITE_PREVIEW_UPSTREAM_SHA256 = "339ee4656b2ca976ca320b48cffba04361f91ad0899a32a1c60ba9b2910e772e"
VITE_PREVIEW_PATCHED_SHA256 = "8df548e7d1456f542321e05139faec50f23f15e64afc5a434c57583308bcc86e"
VITE_PREVIEW_PACKAGE_PATH = r"\.pnpm/vite@7\.3\.3(?:_[A-Za-z0-9@+_.-]+)?/node_modules/vite"
VITE_PREVIEW_SUFFIX = "/dist/node/chunks/config.js"


def adapt_native_preview_source(raw):
    """Patch the reviewed advisory call only, never a catch around preview/hooks.

    Upstream: vitejs/vite v7.3.3, packages/vite/src/node/{utils,preview}.ts.
    The official published dist file is hash-bound before and after these exact
    substitutions. Socket restrictions and the real listener are unchanged.
    """
    if hashlib.sha256(raw).hexdigest() != VITE_PREVIEW_UPSTREAM_SHA256:
        raise ValueError("Native preview Vite upstream source hash mismatch")
    source = raw.decode("utf-8")
    changes = (
        (
            "function resolveServerUrls(server, options$1, hostname, httpsOptions, config$2) {",
            "function resolveServerUrls(server, options$1, hostname, httpsOptions, config$2, "
            "rndNativePreview = false) {",
        ),
        (
            "} else Object.values(os.networkInterfaces()).flatMap",
            """} else {
  let rndInterfaces;
  try { rndInterfaces = os.networkInterfaces(); }
  catch (error) {
   if (!rndNativePreview || error?.code !== 'ERR_SYSTEM_ERROR' ||
       error.info?.syscall !== 'uv_interface_addresses' || error.info?.errno !== 1 ||
       options$1 !== config$2.preview || options$1.host !== '0.0.0.0' ||
       options$1.port !== 5173 || options$1.strictPort !== true || options$1.open !== false ||
       options$1.https || hostname.host !== '0.0.0.0' || !server.listening ||
       address.address !== '0.0.0.0' || address.family !== 'IPv4' || address.port !== 5173) throw error;
   return {local:[`http://127.0.0.1:5173${base}`],network:[]};
  }
  Object.values(rndInterfaces).flatMap""",
        ),
        (
            "\tconst hostnamesFromCert = extractHostnamesFromCerts(httpsOptions?.cert);",
            "\t}\n\tconst hostnamesFromCert = extractHostnamesFromCerts(httpsOptions?.cert);",
        ),
        (
            "server.resolvedUrls = resolveServerUrls(httpServer, config$2.preview, "
            "hostname, httpsOptions, config$2);",
            "server.resolvedUrls = resolveServerUrls(httpServer, config$2.preview, "
            "hostname, httpsOptions, config$2, true);",
        ),
    )
    for old, new in changes:
        if source.count(old) != 1:
            raise ValueError("Native preview Vite patch anchor is missing or ambiguous")
        source = source.replace(old, new)
    result = source.encode("utf-8")
    if hashlib.sha256(result).hexdigest() != VITE_PREVIEW_PATCHED_SHA256:
        raise ValueError("Native preview Vite derived source hash mismatch")
    return result


def _preview_patch_record(relative):
    return {
        "id": "vite-preview-interface-eperm-v1",
        "package": "vite",
        "version": "7.3.3",
        "relative_path": relative,
        "upstream_sha256": VITE_PREVIEW_UPSTREAM_SHA256,
        "patched_sha256": VITE_PREVIEW_PATCHED_SHA256,
    }


@contextmanager
def _native_preview_file(*, writable=False):
    """Resolve one known pnpm link as data, then open every component no-follow."""
    root = NATIVE_FRONTEND_MODULES
    if not root.is_absolute() or ".." in root.parts:
        raise ValueError("Native preview dependency root is not absolute and normalized")
    parent = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    descriptor = None
    try:
        for part in root.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent)
            parent = child
        link = os.stat("vite", dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISLNK(link.st_mode) or link.st_nlink != 1:
            raise ValueError("Native preview Vite package must be one independent pnpm link")
        target = os.readlink("vite", dir_fd=parent)
        if not re.fullmatch(VITE_PREVIEW_PACKAGE_PATH, target):
            raise ValueError("Native preview Vite package link escapes its exact pinned scope")
        relative = target + VITE_PREVIEW_SUFFIX
        for part in PurePosixPath(relative).parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent)
            parent = child
        before = os.stat("config.js", dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_mode & 0o6000:
            raise ValueError("Native preview Vite source is not an independent regular file")
        descriptor = os.open(
            "config.js",
            (os.O_RDWR if writable else os.O_RDONLY) | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=parent,
        )
        opened = os.fstat(descriptor)
        if (
            (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
            or not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or opened.st_mode & 0o6000
            or not 0 < opened.st_size <= 2_000_000
        ):
            raise ValueError("Native preview Vite source identity or size changed")
        yield descriptor, relative
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent)


def _preview_source_bytes(descriptor):
    os.lseek(descriptor, 0, os.SEEK_SET)
    with os.fdopen(os.dup(descriptor), "rb") as stream:
        raw = stream.read(2_000_001)
    if len(raw) > 2_000_000 or os.fstat(descriptor).st_nlink != 1:
        raise ValueError("Native preview Vite source size or link identity changed")
    return raw


def patch_native_preview():
    """Data-only mutation in the existing non-root, credential-free builder."""
    if os.geteuid() == 0:
        raise ValueError("Native preview patch must run in the separate non-root builder")
    with _native_preview_file(writable=True) as (descriptor, relative):
        patched = adapt_native_preview_source(_preview_source_bytes(descriptor))
        os.lseek(descriptor, 0, os.SEEK_SET)
        remaining = memoryview(patched)
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:
                raise ValueError("Native preview Vite source write did not progress")
            remaining = remaining[written:]
        os.ftruncate(descriptor, len(patched))
        os.fsync(descriptor)
        if (
            hashlib.sha256(_preview_source_bytes(descriptor)).hexdigest()
            != VITE_PREVIEW_PATCHED_SHA256
        ):
            raise ValueError("Native preview Vite installed patch hash mismatch")
        return _preview_patch_record(relative)


def native_preview_patch_provenance():
    """The collector reopens the installed bytes; a patch sidecar is insufficient."""
    with _native_preview_file() as (descriptor, relative):
        if (
            hashlib.sha256(_preview_source_bytes(descriptor)).hexdigest()
            != VITE_PREVIEW_PATCHED_SHA256
        ):
            raise ValueError("Native preview Vite installed patch is missing or stale")
        return [_preview_patch_record(relative)]


def native_descriptor_roles():
    """Exact source metadata roles; only runtime projects have image install paths.

    Keep the standalone image verifier's data-only table identical. Both scripts
    run with -I -S in the image and cannot import arbitrary sibling modules.
    """
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


def validate_native_descriptor_inputs(value):
    """Hash inert source descriptor bytes without parsing or running their projects."""
    roles = native_descriptor_roles()
    names = {name for paths in roles.values() for name in paths}
    if type(value) is not dict or value.get("descriptor_roles") != roles:
        raise ValueError("Native descriptor roles differ from the exact registered policy")
    for key in ("original_descriptors", "normalized_descriptors"):
        observed = value.get(key)
        if (
            type(observed) is not dict
            or set(observed) != names
            or any(
                type(item) is not str or not re.fullmatch(r"[a-f0-9]{64}", item)
                for item in observed.values()
            )
        ):
            raise ValueError("Native descriptor inventory must bind all eleven exact source paths")
    source_names = {*roles["portable_launcher"], *roles["auxiliary_source"]}
    contents = value.get("source_descriptor_bytes")
    if type(contents) is not dict or set(contents) != source_names:
        raise ValueError("Native source-only descriptors require complete inert byte evidence")
    total = 0
    for name in source_names:
        encoded = contents[name]
        if type(encoded) is not str or len(encoded) > (SOURCE_DESCRIPTOR_BYTES + 2) // 3 * 4:
            raise ValueError("Native source descriptor bytes exceed their input budget")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except ValueError:
            raise ValueError("Native source descriptor byte encoding is invalid") from None
        total += len(raw)
        if (
            total > SOURCE_DESCRIPTOR_BYTES
            or base64.b64encode(raw).decode("ascii") != encoded
            or hashlib.sha256(raw).hexdigest() != value["original_descriptors"][name]
            or value["normalized_descriptors"][name] != value["original_descriptors"][name]
        ):
            raise ValueError("Native source-only descriptor bytes or immutable hashes changed")
    return roles


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(raw):
    text = raw.decode("utf-8")
    tomllib.loads(text)
    for old, new in MIRRORS.items():
        text = text.replace(old, new)
    tomllib.loads(text)
    return text.encode("utf-8")


def public_url(url, hosts):
    value = urlsplit(url)
    if (
        value.scheme != "https"
        or value.hostname not in hosts
        or value.username is not None
        or value.password is not None
        or value.query
        or value.fragment
        or value.port
    ):
        raise ValueError("Only unauthenticated official registry URLs are build inputs")


def validate_python(project_raw, lock_raw, *, trusted_project=False):
    project = tomllib.loads(project_raw.decode())
    lock = tomllib.loads(lock_raw.decode())
    if project.get("project", {}).get("dynamic"):
        raise ValueError("Candidate dynamic metadata is not a dependency build input")
    if project.get("build-system") and not trusted_project:
        raise ValueError("Candidate build backend is not a dependency build input")
    requirements = list(project.get("project", {}).get("dependencies", []))
    for values in project.get("project", {}).get("optional-dependencies", {}).values():
        requirements.extend(values)
    for values in project.get("dependency-groups", {}).values():
        requirements.extend(value for value in values if isinstance(value, str))
    if any(
        not isinstance(value, str)
        or "@" in value
        or re.search(r"(?:https?:|git[+:]|file:|[/\\])", value)
        for value in requirements
    ):
        raise ValueError("Candidate direct/local dependency references are not build inputs")
    uv = project.get("tool", {}).get("uv", {})
    if set(uv) - {"package", "default-groups", "index"}:
        raise ValueError("Unreviewed uv configuration or local/workspace sources")
    for index in uv.get("index", []):
        if set(index) - {"name", "url", "default", "explicit"}:
            raise ValueError("Unreviewed registry configuration")
        public_url(index["url"], {"pypi.org"})
    for package in lock.get("package", []):
        source = package.get("source", {})
        if source == {"virtual": "."}:
            continue
        if source == {"editable": "."} and trusted_project:
            continue
        if set(source) != {"registry"}:
            raise ValueError("Only hashed registry dependencies are supported")
        public_url(source["registry"], {"pypi.org"})
        artifacts = ([package["sdist"]] if "sdist" in package else []) + package.get("wheels", [])
        if not artifacts:
            raise ValueError("Registry dependency has no hash-bound artifacts")
        for artifact in artifacts:
            public_url(artifact["url"], {"files.pythonhosted.org"})
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", artifact.get("hash", "")):
                raise ValueError("Dependency artifact is not SHA-256 locked")
    return lock


def validate_node(package_raw, lock_raw):
    import yaml

    package = json.loads(package_raw)
    for group in (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    ):
        for spec in package.get(group, {}).values():
            if not isinstance(spec, str) or re.search(
                r"(?:https?:|git[+:]|file:|link:|workspace:|[/\\])", spec
            ):
                raise ValueError("Candidate Node dependencies must be registry version ranges")
    pnpm = package.get("pnpm", {})
    if set(pnpm) - {"overrides"} or package.get("workspaces"):
        raise ValueError("Candidate package manager hooks/workspaces are not build inputs")
    for spec in pnpm.get("overrides", {}).values():
        if not isinstance(spec, str) or not re.fullmatch(r"[0-9A-Za-z.^~*<>=| +_-]+", spec):
            raise ValueError("Node overrides must be registry version ranges")
    lock = yaml.safe_load(lock_raw)
    if not isinstance(lock, dict):
        raise ValueError("Missing Node lock")
    if set(lock) - {
        "lockfileVersion",
        "settings",
        "overrides",
        "importers",
        "packages",
        "snapshots",
    }:
        raise ValueError("Node lock hooks/patches are not build inputs")
    if set(lock.get("importers", {".": {}})) != {"."}:
        raise ValueError("Workspace Node dependency input rejected")
    for entry in lock.get("packages", {}).values():
        resolution = entry.get("resolution", {})
        if set(resolution) != {"integrity"} or not re.fullmatch(
            r"sha(?:256|512)-[A-Za-z0-9+/]+={0,2}", resolution["integrity"]
        ):
            raise ValueError("Only integrity-bound Node registry packages are supported")
    return lock


def limits():
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (1800, 1800))
    resource.setrlimit(resource.RLIMIT_AS, (6 * 1024**3, 6 * 1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024**3, 1024**3))
    resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))
    resource.setrlimit(resource.RLIMIT_NPROC, (384, 384))


def run(command, cwd, *, offline=False, metadata=False):
    if os.geteuid() == 0:
        raise ValueError("Dependency subprocess must run in the separate non-root builder")
    env = {
        "PATH": "/opt/rnd/build-tools/bin:/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin",
        "HOME": "/home/daytona",
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_PYTHON_INSTALL_DIR": "/opt/rnd/python",
        "UV_PYTHON_PREFERENCE": "only-managed",
        "UV_CACHE_DIR": str(BUILD / "uv-cache"),
        "UV_LINK_MODE": "copy",
        "UV_NO_PROGRESS": "1",
        "UV_PYTHON_DOWNLOADS": "never",
        "CARGO_HOME": str(BUILD / "cargo"),
        "RUSTUP_HOME": "/usr/local/rustup",
        "CARGO_NET_OFFLINE": "true" if offline else "false",
        "UV_OFFLINE": "1" if offline else "0",
        "CI": "true",
        "HUSKY": "0",
    }
    context = TemporaryDirectory(prefix="metadata-", dir=BUILD) if metadata else nullcontext()
    with context as directory:
        if metadata:
            # Version probes must not discover project/user configuration or install
            # toolchains. Keep every writable location inside the existing builder
            # area, never the inherited root-owned interpreter/tool/cache trees.
            home = Path(directory)
            cwd = home
            env.update(
                HOME=str(home),
                XDG_CONFIG_HOME=str(home / ".config"),
                XDG_CACHE_HOME=str(home / ".cache"),
                XDG_DATA_HOME=str(home / ".local/share"),
                UV_NO_CONFIG="1",
                UV_OFFLINE="1",
                CARGO_NET_OFFLINE="true",
                RUSTUP_AUTO_INSTALL="0",
                COREPACK_ENABLE_NETWORK="0",
                DISABLE_V8_COMPILE_CACHE="1",
                NODE_DISABLE_COMPILE_CACHE="1",
                npm_config_userconfig=str(home / "user.npmrc"),
                npm_config_globalconfig=str(home / "global.npmrc"),
            )
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=True,
            timeout=60 if metadata else 1800,
            preexec_fn=limits,
            text=True,
            capture_output=metadata,
        )


def download(record, destination):
    public_url(record["url"], {"files.pythonhosted.org"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(record["url"], timeout=90) as response:
        public_url(response.url, {"files.pythonhosted.org"})
        raw = response.read(64 * 1024**2 + 1)
    if len(raw) > 64 * 1024**2 or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError("Source/build-tool artifact checksum mismatch")
    path = destination / record["url"].rsplit("/", 1)[1]
    path.write_bytes(raw)
    return path


def extract_source(path, destination):
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        if len(members) > 10000 or sum(item.size for item in members) > 128 * 1024**2:
            raise ValueError("Registry source archive exceeds limits")
        top = set()
        for item in members:
            name = PurePosixPath(item.name)
            if (
                name.is_absolute()
                or ".." in name.parts
                or not (item.isdir() or item.isfile())
                or ".cargo" in name.parts
                or item.mode & 0o6000
            ):
                raise ValueError("Unsafe registry source archive")
            top.add(name.parts[0])
        if len(top) != 1:
            raise ValueError("Registry source needs one package directory")
        archive.extractall(destination, members=members, filter="data")
    return destination / top.pop()


def fetch(lock_path, backend):
    if os.geteuid() == 0:
        raise ValueError("Source preparation requires non-root builder")
    spec = json.loads(Path(lock_path).read_bytes())
    selected = tomllib.loads((Path(backend) / "uv.lock").read_text())
    packages = {item["name"]: item for item in selected["package"]}
    downloads = BUILD / "downloads"
    downloads.mkdir(parents=True)
    for record in spec["tools"]:
        download(record, downloads)
    run([UV, "venv", "--allow-existing", "--python", PYTHON, str(TOOLS)], BUILD)
    requirements = BUILD / "build-tools.txt"
    requirements.write_text(
        "\n".join(
            str(downloads / record["url"].rsplit("/", 1)[1]) + " --hash=sha256:" + record["sha256"]
            for record in spec["tools"]
        )
        + "\n"
    )
    run(
        [
            UV,
            "pip",
            "install",
            "--python",
            str(TOOLS / "bin/python"),
            "--no-deps",
            "--no-build",
            "--require-hashes",
            "--no-index",
            "-r",
            str(requirements),
        ],
        BUILD,
        offline=True,
    )
    sources = []
    for record in spec["sdists"]:
        package = packages.get(record["name"], {})
        if (
            package.get("version") != record["version"]
            or package.get("sdist", {}).get("hash") != "sha256:" + record["sha256"]
        ):
            raise ValueError("Reviewed registry sdist differs from current dependency lock")
        source = extract_source(download(record, downloads), BUILD / "sources")
        item = {**record, "source": str(source)}
        if record["name"] == "sqlglotrs":
            cargo = tomllib.loads((source / "Cargo.lock").read_text())
            for dependency in cargo["package"]:
                if dependency.get("source") and (
                    dependency["source"] != "registry+https://github.com/rust-lang/crates.io-index"
                    or not re.fullmatch(r"[a-f0-9]{64}", dependency.get("checksum", ""))
                ):
                    raise ValueError("Unpinned/non-registry Rust build dependency")
            item["cargo_lock_sha256"] = sha(source / "Cargo.lock")
            run(
                [
                    "cargo",
                    "fetch",
                    "--locked",
                    "--manifest-path",
                    str(source / "Cargo.toml"),
                ],
                BUILD,
            )
        sources.append(item)
    (BUILD / "sources.json").write_text(json.dumps(sources, sort_keys=True))


def wheel_outputs(path, package):
    """Record real native payloads; do not accept crcmod's silent C-build fallback."""
    native = {}
    tags = []
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            name = PurePosixPath(item.filename)
            if (
                name.is_absolute()
                or ".." in name.parts
                or ((item.external_attr >> 16) & 0o170000) == 0o120000
            ):
                raise ValueError("Unsafe built wheel path or symlink")
            if item.filename.endswith(".so"):
                native[item.filename] = hashlib.sha256(archive.read(item)).hexdigest()
            if item.filename.endswith(".dist-info/WHEEL"):
                tags.extend(
                    line.removeprefix("Tag: ")
                    for line in archive.read(item).decode().splitlines()
                    if line.startswith("Tag: ")
                )
    if not tags or (package in {"crcmod", "sqlglotrs"} and not native):
        raise ValueError("Required native source build produced no native extension")
    return {"wheel_tags": tags, "native_extensions": native}


def build_sources():
    output = BUILD / "wheels"
    output.mkdir()
    result = []
    for item in json.loads((BUILD / "sources.json").read_bytes()):
        source = Path(item["source"])
        command = [
            UV,
            "build",
            "--wheel",
            "--no-build-isolation",
            "--offline",
            "--python",
            str(TOOLS / "bin/python"),
            "--out-dir",
            str(output),
        ]
        if item["name"] == "sqlglotrs":
            command += ["--config-setting", "build-args=--locked --offline"]
        run(command + [str(source)], BUILD, offline=True)
        if (
            item.get("cargo_lock_sha256")
            and sha(source / "Cargo.lock") != item["cargo_lock_sha256"]
        ):
            raise ValueError("Source build changed its Rust lock")
        matches = list(
            output.glob(item["name"].replace("-", "_") + "-" + item["version"] + "-*.whl")
        )
        if len(matches) != 1:
            raise ValueError("Source build did not produce one exact wheel")
        result.append(
            {
                **item,
                "wheel": str(matches[0]),
                "wheel_sha256": sha(matches[0]),
                **wheel_outputs(matches[0], item["name"]),
            }
        )
    (BUILD / "source-builds.json").write_text(json.dumps(result, sort_keys=True))


def replace_source_requirements(raw, builds):
    for item in builds:
        pattern = (
            r"(?m)^"
            + re.escape(item["name"])
            + r"=="
            + re.escape(item["version"])
            + r"([^\n]*)(?:\n[ \t]+[^\n]*)*"
        )

        def replace(match):
            marker = match[1].rstrip().removesuffix("\\").strip()
            return (
                item["name"]
                + " @ "
                + Path(item["wheel"]).as_uri()
                + (" " + marker if marker else "")
                + " \\\n    --hash=sha256:"
                + item["wheel_sha256"]
            )

        raw, count = re.subn(pattern, replace, raw)
        if count != 1:
            raise ValueError("Reviewed sdist must be selected exactly once by runtime groups")
    return raw


def install(project, *, basic=False, harness=False):
    project = Path(project)
    original = {name: sha(project / name) for name in ("pyproject.toml", "uv.lock")}
    export = BUILD / (project.name + "-requirements.lock.txt")
    command = [
        UV,
        "export",
        "--locked",
        "--format",
        "requirements-txt",
        "--no-emit-project",
        "--no-header",
        "--no-annotate",
        "--output-file",
        str(export),
    ]
    if basic:
        command += ["--no-dev"]
    if harness:
        command += ["--all-extras"]
    run(command, project)
    builds = [] if basic or harness else json.loads((BUILD / "source-builds.json").read_bytes())
    export.write_text(replace_source_requirements(export.read_text(), builds))
    environment = project / ".venv"
    if environment.is_symlink() or (environment.exists() and any(environment.iterdir())):
        raise ValueError("Runtime environment must start empty after source builds have exited")
    run([UV, "venv", "--allow-existing", "--python", PYTHON, str(environment)], project)
    run(
        [
            UV,
            "pip",
            "sync",
            "--python",
            str(project / ".venv/bin/python"),
            "--require-hashes",
            "--no-build",
            "--index-url",
            "https://pypi.org/simple",
            # Unlike `pip install -r`, `pip sync` takes positional source files.
            str(export),
        ],
        project,
    )
    if original != {name: sha(project / name) for name in original}:
        raise ValueError("Locked dependency installation changed descriptors")


def collect(inputs, output, *, native=False):
    value = json.loads(Path(inputs).read_bytes())
    roles = validate_native_descriptor_inputs(value) if native else None
    python_runtime = json.loads(
        run(
            [
                str(PYTHON_BUILD),
                "-I",
                "-S",
                "-B",
                "-c",
                'import json,sys,sysconfig,platform;print(json.dumps({"version":list(sys.version_info[:3]),"build":sys.version,"soabi":sysconfig.get_config_var("SOABI"),"machine":platform.machine(),"system":platform.system()}))',
            ],
            BUILD,
            offline=True,
            metadata=True,
        ).stdout
    )
    if (
        python_runtime["version"] != [3, 14, 7]
        or python_runtime["machine"] != "x86_64"
        or python_runtime["system"] != "Linux"
    ):
        raise ValueError("Actual build interpreter/platform differs from the reviewed target")
    runtime_names = roles["runtime"] if native else value["normalized_descriptors"]
    for name in runtime_names:
        expected = value["normalized_descriptors"][name]
        target = (
            Path("/opt/rnd/runtime/fastapiadmin") / name.replace("frontend/web/", "frontend/", 1)
            if native
            else Path("/opt/rnd/runtime/python-basic") / name
        )
        if sha(target) != expected:
            raise ValueError("Normalized descriptor changed during dependency preparation")
    for name, expected in value.get("harness_descriptors", {}).items():
        if sha(Path("/opt/rnd/harness") / name) != expected:
            raise ValueError("Trusted harness descriptor changed during dependency preparation")
    commands = {
        "uv": [UV, "--version"],
        "node": ["/usr/local/bin/node", "--version"],
        "system_packages": ["/usr/bin/dpkg-query", "-W", "-f=${Package}=${Version}\\n"],
    }
    if native:
        commands.update(
            rust=["/usr/local/cargo/bin/rustc", "--version"],
            cc=["/usr/bin/cc", "--version"],
            pnpm=["/usr/local/bin/pnpm", "--version"],
        )
    value["toolchain"] = {
        name: run(argv, BUILD, offline=True, metadata=True).stdout.strip()
        for name, argv in commands.items()
    }
    # The foundation already fixed this interpreter identity. Rediscovering it
    # with `uv python find` initializes uv's cache even for a metadata lookup.
    value["toolchain"]["python"] = str(PYTHON_BUILD.resolve(strict=True))
    if value["toolchain"]["node"] != "v22.23.2" or not re.fullmatch(
        r"uv 0\.12\.20(?: .*)?", value["toolchain"]["uv"]
    ):
        raise ValueError("Actual Node/uv toolchain differs from the reviewed target")
    value["toolchain"]["python_runtime"] = python_runtime
    value["platform"] = {"os": "linux", "architecture": "amd64", "python": PYTHON}
    value["build_tool_artifacts"] = (
        json.loads(Path("/opt/rnd/bin/dependency-build.lock.json").read_bytes())["tools"]
        if native
        else []
    )
    value["build_tool_installed_sha256"] = (
        json.loads(Path("/opt/rnd/build-tools-manifest.json").read_bytes())["installed_tree_sha256"]
        if native
        else None
    )
    value["source_builds"] = (
        json.loads((BUILD / "source-builds.json").read_bytes()) if native else []
    )
    if native:
        # Retain all eleven hashes and exact roles in the sealed image manifest.
        # The seven source-only projects never become install/runtime directories.
        del value["source_descriptor_bytes"]
        value["runtime_patches"] = native_preview_patch_provenance()
    Path(output).write_text(json.dumps(value, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["fetch", "build-sources", "install", "patch-native-preview", "collect"]
    )
    parser.add_argument("--project", type=Path)
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--basic", action="store_true")
    parser.add_argument("--harness", action="store_true")
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args()
    if args.action == "fetch":
        fetch(args.lock, args.project)
    elif args.action == "build-sources":
        build_sources()
    elif args.action == "install":
        install(args.project, basic=args.basic, harness=args.harness)
    elif args.action == "patch-native-preview":
        patch_native_preview()
    else:
        collect(args.inputs, args.output, native=args.native)


if __name__ == "__main__":
    main()
````
