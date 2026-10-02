# tools/aider/offline_runner.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Aider本机禁网入口。** 校验独立Python版本、Aider版本、依赖中Token数据与模型元数据，再安装审计钩子并调用真实CLI；--check-local-deps只做离线自检。

**对应关系：** aider_tool.command → 本文件 → Aider Repo Map/apply；tests/test_aider_offline和ci_toolchain分别验证拒绝路径与实际工具。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `packaged_encodings`（L21–L29）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L23遍历`ENCODINGS.items()`；L25按`not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected`分支；L26抛异常，停止当前正常路径。 调用`Path`、`distribution("litellm").locate_file`、`distribution`、`ENCODINGS.items`、`path.is_file`、`hashlib.sha256(path.read_bytes()).hexdigest`、`hashlib.sha256`、`path.read_bytes`、`RuntimeError`。 返回路径：L29的`cache`。
- `install_offline_guard`（L32–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`sys.addaudithook`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `install_offline_guard.audit`（L33–L38）：接收`event`、`args`。 控制顺序：L34按`event.startswith(("socket.getaddrinfo", "socket.gethostby", "socket.getnameinfo"))`分支；L35抛异常，停止当前正常路径；L36按`event in {"socket.connect", "socket.sendto", "socket.bind"}`分支；L37按`args[0].family in {socket.AF_INET, socket.AF_INET6}`分支；L38抛异常，停止当前正常路径。 调用`event.startswith`、`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L43–L84）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L44按`sys.version_info[:2] != (3, 12) or version("aider-chat") != "0.86.2"`分支；L45抛异常，停止当前正常路径；L55按`sys.argv[1:] == ["--check-local-deps"]`分支；L58遍历`("cl100k_base", "o200k_base")`；L59断言`tiktoken.get_encoding(name).encode("本机编码检查")`；L76按`hashlib.sha256(metadata.read_bytes()).hexdigest() != "e8da995ddcffc05a8dcbe4a8504326a…`分支；L80抛异常，停止当前正常路径。 调用`version`、`RuntimeError`、`packaged_encodings`、`os.environ.update`、`str`、`install_offline_guard`、`tiktoken.get_encoding(name).encode`、`tiktoken.get_encoding`、`print`等。 返回路径：L70的`0`；L84的`aider_main()`。

</details>

**创建路径：** `tools/aider/offline_runner.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L88。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3208`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/aider/offline_runner.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "eb22fd95ca5844c5a7c05dc9f09b2c26fee1274b6267bc23a4f7d3fa0c132193"} -->
````python
# tools/aider/offline_runner.py
"""Python 3.12 entry for real Aider, with packaged token data and no network.

This guards the registered Repo Map/apply CLI modes. It is not a sandbox for
arbitrary Python supplied by a model. Installation is a separate uv operation.
"""

import hashlib
import json
import os
import socket
import sys
from importlib.metadata import distribution, version
from pathlib import Path

ENCODINGS = {
    "9b5ad71b2ce5302211f9c61530b329a4922fc6a4": "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7",
    "fb374d419588a4632f3f557e76b4b70aebbca790": "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d",
}


def packaged_encodings():
    cache = Path(distribution("litellm").locate_file("litellm/litellm_core_utils/tokenizers"))
    for name, expected in ENCODINGS.items():
        path = cache / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(
                "Aider packaged tokenizer integrity failure; reinstall tools/aider with uv sync --locked"
            )
    return cache


def install_offline_guard():
    def audit(event, args):
        if event.startswith(("socket.getaddrinfo", "socket.gethostby", "socket.getnameinfo")):
            raise PermissionError("Aider local tool network access is disabled")
        if event in {"socket.connect", "socket.sendto", "socket.bind"}:
            if args[0].family in {socket.AF_INET, socket.AF_INET6}:
                raise PermissionError("Aider local tool network access is disabled")

    sys.addaudithook(audit)


def main():
    if sys.version_info[:2] != (3, 12) or version("aider-chat") != "0.86.2":
        raise RuntimeError("Use the pinned Python 3.12 tools/aider environment")
    cache = packaged_encodings()
    os.environ.update(
        CUSTOM_TIKTOKEN_CACHE_DIR=str(cache),
        TIKTOKEN_CACHE_DIR=str(cache),
        LITELLM_LOCAL_MODEL_COST_MAP="True",
        AIDER_ANALYTICS="false",
        DO_NOT_TRACK="1",
    )
    install_offline_guard()
    if sys.argv[1:] == ["--check-local-deps"]:
        import tiktoken

        for name in ("cl100k_base", "o200k_base"):
            assert tiktoken.get_encoding(name).encode("本机编码检查")
        print(
            json.dumps(
                {
                    "aider": "0.86.2",
                    "python": "3.12",
                    "packaged_encodings_verified": True,
                    "network": "disabled",
                }
            )
        )
        return 0
    # Aider accepts a local metadata file. Use the locked package's own data,
    # instead of its otherwise automatic model-price URL lookup.
    metadata = Path(
        distribution("litellm").locate_file("litellm/model_prices_and_context_window_backup.json")
    )
    if (
        hashlib.sha256(metadata.read_bytes()).hexdigest()
        != "e8da995ddcffc05a8dcbe4a8504326a6e352ba9e38151e147cbb5b4b694c937d"
    ):
        raise RuntimeError("Aider packaged model metadata integrity failure")
    sys.argv.extend(["--model-metadata-file", str(metadata)])
    from aider.main import main as aider_main

    return aider_main()


if __name__ == "__main__":
    raise SystemExit(main())
````
