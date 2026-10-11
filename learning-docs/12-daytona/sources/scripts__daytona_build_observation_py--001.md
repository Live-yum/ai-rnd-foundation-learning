# scripts/daytona_build_observation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_build_observation；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `version`（L25–L30）：接收`value`。 调用`type`、`re.fullmatch`。 返回路径：L26的`value if type(value) is str and re.fullmatch(r"\d{1,5}\.\d{1,5}\.\d{1,5}", value) else "un…`。
- `script_fact`（L33–L51）：接收`value`。 控制顺序：L34按`not isinstance(value, dict)`分支；L39按`not ( type(identifier) is str and re.fullmatch(r"[a-f0-9]{64}", identifier) and type(…`分支。 调用`isinstance`、`value.get`、`type`、`re.fullmatch`、`version`。 返回路径：L35的`None`；L45的`None`；L46的`{ "id": identifier, "script": script, "package": package if type(package) is str and packa…`。
- `observation`（L54–L125）：接收`log`。 控制顺序：L65按`not isinstance(log, str)`分支；L67遍历`log[:64064].splitlines()`；L72按`match`分支；L74按`len(line) > 16000 or "RND_BUILD_OBSERVATION " not in line`分支；L80按`not isinstance(data, dict)`分支；L83按`type(session) is not str or not re.fullmatch(r"[a-f0-9]{16}", session)`分支；L85按`session not in result["sessions"]`分支；L86按`len(result["sessions"]) == 4`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`log[:64064].splitlines`、`re.search`、`len`、`json.loads`、`line.split`、`data.get`、`type`、`re.fullmatch`等。 返回路径：L66的`result`；L125的`result`。
- `retain`（L128–L136）：接收`directory`、`log`。 源码说明：Diagnostics never replace a build result or authorize an image.。 调用`observation`、`json.dumps`、`(directory / "api-build-observation.json").write_text`、`print`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_build_observation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L136。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4786`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_build_observation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6ce65830ccc1d505f0a2d2f8cae5c2cada9a0d2b2631f11cd219e791b6d3acff"} -->
````python
# scripts/daytona_build_observation.py
"""Bounded optional facts from this build's output, never admission evidence."""

import json
import re

PACKAGES = {
    "@nestjs/core",
    "@swc/core",
    "esbuild",
    "sharp",
    "msw",
    "nx",
    "core-js",
    "sqlite3",
    "@parcel/watcher",
    "protobufjs",
    "@scarf/scarf",
    "unrs-resolver",
    "cpu-features",
    "core-js-pure",
    "other",
}


def version(value):
    return (
        value
        if type(value) is str and re.fullmatch(r"\d{1,5}\.\d{1,5}\.\d{1,5}", value)
        else "unknown"
    )


def script_fact(value):
    if not isinstance(value, dict):
        return None
    identifier = value.get("id")
    script = value.get("script")
    package = value.get("package")
    if not (
        type(identifier) is str
        and re.fullmatch(r"[a-f0-9]{64}", identifier)
        and type(script) is str
        and script in {"preinstall", "install", "postinstall"}
    ):
        return None
    return {
        "id": identifier,
        "script": script,
        "package": package if type(package) is str and package in PACKAGES else "other",
        "version": version(value.get("version")),
    }


def observation(log):
    result = {
        "schema": 1,
        "coverage": "manifest_scripts_only",
        "log_excerpt": True,
        "session_limit_reached": False,
        "bases": {},
        "sessions": {},
        "events": [],
    }
    # run_command already supplies only the bounded head/tail of its own output.
    if not isinstance(log, str):
        return result
    for line in log[:64064].splitlines():
        match = re.search(
            r"\[(builder|daytona) [^\]]{1,32}\] FROM (?:docker\.io/)?library/node:24-slim@(sha256:[a-f0-9]{64})(?:\s|$)",
            line,
        )
        if match:
            result["bases"][match[1]] = match[2]
        if len(line) > 16000 or "RND_BUILD_OBSERVATION " not in line:
            continue
        try:
            data = json.loads(line.split("RND_BUILD_OBSERVATION ", 1)[1])
        except ValueError, RecursionError:
            continue
        if not isinstance(data, dict):
            continue
        session = data.get("session")
        if type(session) is not str or not re.fullmatch(r"[a-f0-9]{16}", session):
            continue
        if session not in result["sessions"]:
            if len(result["sessions"]) == 4:
                result["session_limit_reached"] = True
                continue
            result["sessions"][session] = {"tools": None, "pending": None}
        current = result["sessions"][session]
        event = data.get("event")
        if event == "tools":
            current["tools"] = {key: version(data.get(key)) for key in ("node", "yarn", "corepack")}
        elif event == "pending":
            pending = {}
            for key in ("started", "completed", "active_count"):
                value = data.get(key)
                pending[key] = value if type(value) is int and 0 <= value <= 256 else None
            pending["overflow"] = (
                data.get("overflow") if type(data.get("overflow")) is bool else None
            )
            pending["scripts"] = []
            items = data.get("scripts")
            for item in items[:32] if isinstance(items, list) else []:
                safe = script_fact(item)
                elapsed = item.get("elapsed_seconds") if isinstance(item, dict) else None
                if safe and type(elapsed) is int and 0 <= elapsed <= 2400:
                    pending["scripts"].append(
                        {**safe, "state": "awaiting_script_exit", "elapsed_seconds": elapsed}
                    )
            current["pending"] = pending
            pending["scripts_truncated"] = pending["active_count"] is not None and pending[
                "active_count"
            ] > len(pending["scripts"])
        elif event in ("start", "end") and (safe := script_fact(data)):
            safe["session"] = session
            safe["event"] = event
            if event == "end":
                safe["state"] = (
                    data.get("state") if data.get("state") in ("returned", "threw") else "unknown"
                )
                code = data.get("exit_code")
                safe["exit_code"] = code if type(code) is int and 0 <= code <= 255 else None
            result["events"] = (result["events"] + [safe])[-64:]
    return result


def retain(directory, log):
    """Diagnostics never replace a build result or authorize an image."""
    try:
        safe = observation(log)
        text = json.dumps(safe, sort_keys=True)
        (directory / "api-build-observation.json").write_text(text + "\n", encoding="utf-8")
        print("Local Daytona API build observation: " + text, flush=True)
    except OSError, ValueError, TypeError:
        pass
````
