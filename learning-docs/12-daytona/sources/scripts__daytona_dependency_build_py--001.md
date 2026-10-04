# scripts/daytona_dependency_build.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_dependency_build；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `sha`（L31–L32）：接收`path`。 调用`hashlib.sha256(Path(path).read_bytes()).hexdigest`、`hashlib.sha256`、`Path(path).read_bytes`、`Path`。 返回路径：L32的`hashlib.sha256(Path(path).read_bytes()).hexdigest()`。
- `normalize`（L35–L41）：接收`raw`。 控制顺序：L38遍历`MIRRORS.items()`。 调用`raw.decode`、`tomllib.loads`、`MIRRORS.items`、`text.replace`、`text.encode`。 返回路径：L41的`text.encode("utf-8")`。
- `public_url`（L44–L55）：接收`url`、`hosts`。 控制顺序：L46按`value.scheme != "https" or value.hostname not in hosts or value.username is not None …`分支；L55抛异常，停止当前正常路径。 调用`urlsplit`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_python`（L58–L100）：接收`project_raw`、`lock_raw`、`trusted_project`。 控制顺序：L61按`project.get("project", {}).get("dynamic")`分支；L62抛异常，停止当前正常路径；L63按`project.get("build-system") and not trusted_project`分支；L64抛异常，停止当前正常路径；L66遍历`project.get("project", {}).get("optional-dependencies", {}).value…`；L68遍历`project.get("dependency-groups", {}).values()`；L70按`any( not isinstance(value, str) or "@" in value or re.search(r"(?:https?:\|git[+:]\|f…`分支；L76抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`tomllib.loads`、`project_raw.decode`、`lock_raw.decode`、`project.get("project", {}).get`、`project.get`、`ValueError`、`list`、`project.get("project", {}).get("optional-dependencies", {}).value…`、`requirements.extend`等。 返回路径：L100的`lock`。
- `validate_node`（L103–L144）：接收`package_raw`、`lock_raw`。 控制顺序：L107遍历`( "dependencies", "devDependencies", "optionalDependencies", "pee…`；L113遍历`package.get(group, {}).values()`；L114按`not isinstance(spec, str) or re.search( r"(?:https?:\|git[+:]\|file:\|link:\|workspac…`分支；L117抛异常，停止当前正常路径；L119按`set(pnpm) - {"overrides"} or package.get("workspaces")`分支；L120抛异常，停止当前正常路径；L121遍历`pnpm.get("overrides", {}).values()`；L122按`not isinstance(spec, str) or not re.fullmatch(r"[0-9A-Za-z.^~*<>=\| +_-]+", spec)`分支。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`package.get(group, {}).values`、`package.get`、`isinstance`、`re.search`、`ValueError`、`set`、`pnpm.get("overrides", {}).values`、`pnpm.get`等。 返回路径：L144的`lock`。
- `limits`（L147–L154）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`resource.setrlimit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run`（L157–L187）：接收`command`、`cwd`、`offline`。 控制顺序：L158按`os.geteuid() == 0`分支；L159抛异常，停止当前正常路径。 调用`os.geteuid`、`ValueError`、`str`、`subprocess.run`。 返回路径：L178的`subprocess.run( command, cwd=cwd, env=env, check=True, timeout=1800, preexec_fn=limits, te…`。
- `download`（L190–L200）：接收`record`、`destination`。 控制顺序：L196按`len(raw) > 64 * 1024**2 or hashlib.sha256(raw).hexdigest() != record["sha256"]`分支；L197抛异常，停止当前正常路径。 调用`public_url`、`urllib.request.build_opener`、`urllib.request.ProxyHandler`、`opener.open`、`response.read`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`ValueError`等。 返回路径：L200的`path`。
- `extract_source`（L203–L223）：接收`path`、`destination`。 控制顺序：L206按`len(members) > 10000 or sum(item.size for item in members) > 128 * 1024**2`分支；L207抛异常，停止当前正常路径；L209遍历`members`；L211按`name.is_absolute() or ".." in name.parts or not (item.isdir() or item.isfile()) or ".…`分支；L218抛异常，停止当前正常路径；L220按`len(top) != 1`分支；L221抛异常，停止当前正常路径。 调用`tarfile.open`、`archive.getmembers`、`len`、`sum`、`ValueError`、`set`、`PurePosixPath`、`name.is_absolute`、`item.isdir`等。 返回路径：L223的`destination / top.pop()`。
- `fetch`（L226–L292）：接收`lock_path`、`backend`。 控制顺序：L227按`os.geteuid() == 0`分支；L228抛异常，停止当前正常路径；L234遍历`spec["tools"]`；L263遍历`spec["sdists"]`；L265按`package.get("version") != record["version"] or package.get("sdist", {}).get("hash") !…`分支；L269抛异常，停止当前正常路径；L272按`record["name"] == "sqlglotrs"`分支；L274遍历`cargo["package"]`。后续分支沿下方源码相同行号继续阅读。 调用`os.geteuid`、`ValueError`、`json.loads`、`Path(lock_path).read_bytes`、`Path`、`tomllib.loads`、`(Path(backend) / "uv.lock").read_text`、`downloads.mkdir`、`download`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `wheel_outputs`（L295–L318）：接收`path`、`package`。 源码说明：Record real native payloads; do not accept crcmod's silent C-build fallback.。 控制顺序：L300遍历`archive.infolist()`；L302按`name.is_absolute() or ".." in name.parts or ((item.external_attr >> 16) & 0o170000) =…`分支；L307抛异常，停止当前正常路径；L308按`item.filename.endswith(".so")`分支；L310按`item.filename.endswith(".dist-info/WHEEL")`分支；L316按`not tags or (package in {"crcmod", "sqlglotrs"} and not native)`分支；L317抛异常，停止当前正常路径。 调用`zipfile.ZipFile`、`archive.infolist`、`PurePosixPath`、`name.is_absolute`、`ValueError`、`item.filename.endswith`、`hashlib.sha256(archive.read(item)).hexdigest`、`hashlib.sha256`、`archive.read`等。 返回路径：L318的`{"wheel_tags": tags, "native_extensions": native}`。
- `build_sources`（L321–L359）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L325遍历`json.loads((BUILD / "sources.json").read_bytes())`；L338按`item["name"] == "sqlglotrs"`分支；L341按`item.get("cargo_lock_sha256") and sha(source / "Cargo.lock") != item["cargo_lock_sha2…`分支；L345抛异常，停止当前正常路径；L349按`len(matches) != 1`分支；L350抛异常，停止当前正常路径。 调用`output.mkdir`、`json.loads`、`(BUILD / "sources.json").read_bytes`、`Path`、`str`、`run`、`item.get`、`sha`、`ValueError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `replace_source_requirements`（L362–L386）：接收`raw`、`builds`。 控制顺序：L363遍历`builds`；L384按`count != 1`分支；L385抛异常，停止当前正常路径。 调用`re.escape`、`re.subn`、`ValueError`。 返回路径：L386的`raw`。
- `replace_source_requirements.replace`（L372–L381）：接收`match`。 调用`match[1].rstrip().removesuffix("\\").strip`、`match[1].rstrip().removesuffix`、`match[1].rstrip`、`Path(item["wheel"]).as_uri`、`Path`。 返回路径：L374的`item["name"] + " @ " + Path(item["wheel"]).as_uri() + (" " + marker if marker else "") + "…`。
- `install`（L389–L433）：接收`project`、`basic`、`harness`。 控制顺序：L405按`basic`分支；L407按`harness`分支；L413按`environment.is_symlink() or (environment.exists() and any(environment.iterdir()))`分支；L414抛异常，停止当前正常路径；L432按`original != {name: sha(project / name) for name in original}`分支；L433抛异常，停止当前正常路径。 调用`Path`、`sha`、`str`、`run`、`json.loads`、`(BUILD / "source-builds.json").read_bytes`、`export.write_text`、`replace_source_requirements`、`export.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `collect`（L436–L503）：接收`inputs`、`output`、`native`。 控制顺序：L450按`python_runtime["version"] != [3, 14, 7] or python_runtime["machine"] != "x86_64" or p…`分支；L455抛异常，停止当前正常路径；L456遍历`value["normalized_descriptors"].items()`；L457按`native and name.startswith("deployment/")`分支；L464按`sha(target) != expected`分支；L465抛异常，停止当前正常路径；L466遍历`value.get("harness_descriptors", {}).items()`；L467按`sha(Path("/opt/rnd/harness") / name) != expected`分支。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`Path(inputs).read_bytes`、`Path`、`subprocess.check_output`、`ValueError`、`value["normalized_descriptors"].items`、`name.startswith`、`name.replace`、`sha`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L506–L524）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L517按`args.action == "fetch"`分支；L519按`args.action == "build-sources"`分支；L521按`args.action == "install"`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`fetch`、`build_sources`、`install`、`collect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_dependency_build.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L528。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`20099`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_dependency_build.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4a2d33685e41df4f7a42aeaa1cb861a51763f35a15fc1753167aae9f6c70e33e"} -->
````python
# scripts/daytona_dependency_build.py
"""Reviewed descriptor-only dependency build; never import candidate code.

Registry sdists are an explicit hash allowlist. Fetch and build are separate
Docker stages/steps: build runs non-root, offline, without secrets or host mounts.
Unsupported source builds fail; locks, source and ABI compatibility are not edited.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import tarfile
import tomllib
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

BUILD = Path("/opt/rnd/build")
TOOLS = Path("/opt/rnd/build-tools")
PYTHON = "3.14.7"
UV = "/usr/local/bin/uv"
MIRRORS = {
    "https://pypi.tuna.tsinghua.edu.cn/simple": "https://pypi.org/simple",
    "https://pypi.tuna.tsinghua.edu.cn/packages/": "https://files.pythonhosted.org/packages/",
}


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


def run(command, cwd, *, offline=False):
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
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        timeout=1800,
        preexec_fn=limits,
        text=True,
        capture_output=False,
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
    python_runtime = json.loads(
        subprocess.check_output(
            [
                "/opt/rnd/bin/python-build",
                "-I",
                "-S",
                "-c",
                'import json,sys,sysconfig,platform;print(json.dumps({"version":list(sys.version_info[:3]),"build":sys.version,"soabi":sysconfig.get_config_var("SOABI"),"machine":platform.machine(),"system":platform.system()}))',
            ],
            text=True,
        )
    )
    if (
        python_runtime["version"] != [3, 14, 7]
        or python_runtime["machine"] != "x86_64"
        or python_runtime["system"] != "Linux"
    ):
        raise ValueError("Actual build interpreter/platform differs from the reviewed target")
    for name, expected in value["normalized_descriptors"].items():
        if native and name.startswith("deployment/"):
            continue
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
        "python": [UV, "python", "find", PYTHON],
        "system_packages": ["/usr/bin/dpkg-query", "-W", "-f=${Package}=${Version}\\n"],
    }
    if native:
        commands.update(
            rust=["/usr/local/cargo/bin/rustc", "--version"],
            cc=["/usr/bin/cc", "--version"],
            pnpm=["/usr/local/bin/pnpm", "--version"],
        )
    value["toolchain"] = {
        name: subprocess.check_output(argv, text=True).strip() for name, argv in commands.items()
    }
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
    Path(output).write_text(json.dumps(value, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["fetch", "build-sources", "install", "collect"])
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
    else:
        collect(args.inputs, args.output, native=args.native)


if __name__ == "__main__":
    main()
````
