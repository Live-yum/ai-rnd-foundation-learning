# tests/test_daytona_gateway.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_fixed_ingress_preserves_bytes_and_half_close`（L8–L40）：接收`monkeypatch`。 调用`asyncio.run`、`exercise`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_ingress_preserves_bytes_and_half_close.exercise`（L9–L38）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L31断言`await asyncio.wait_for(reader.read(), timeout=10) == b"echo:" + payload`。 调用`asyncio.start_server`、`upstream.sockets[0].getsockname`、`monkeypatch.setitem`、`gateway.relay`、`asyncio.open_connection`、`ingress.sockets[0].getsockname`、`writer.write`、`writer.drain`、`writer.write_eof`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_ingress_preserves_bytes_and_half_close.exercise.echo`（L10–L15）：接收`reader`、`writer`。 调用`reader.read`、`writer.write`、`writer.drain`、`writer.close`、`writer.wait_closed`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_production_targets_are_only_registered_docker_services`（L43–L53）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L44断言`set(gateway.TARGETS.values()) == { "api", "proxy", "runner", "dex", "registry", "mini…`；L53断言`set(gateway.TARGETS) == {3000, 4000, 3003, 5556, 6000, 9001, 1080}`。 调用`set`、`gateway.TARGETS.values`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_gateway.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L53。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1777`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_gateway.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6adeaf768dc38769ad81e48faea8a5cee6f8dd83c281af03d52efb7ff4052437"} -->
````python
# tests/test_daytona_gateway.py
"""Real local TCP transport, including half-close; no cloud or SDK fixture involved."""

import asyncio

from scripts import daytona_gateway as gateway


def test_fixed_ingress_preserves_bytes_and_half_close(monkeypatch):
    async def exercise():
        async def echo(reader, writer):
            payload = await reader.read()
            writer.write(b"echo:" + payload)
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        upstream = await asyncio.start_server(echo, "127.0.0.1", 0)
        upstream_port = upstream.sockets[0].getsockname()[1]
        monkeypatch.setitem(gateway.TARGETS, upstream_port, "127.0.0.1")
        ingress = await asyncio.start_server(
            lambda r, w: gateway.relay(r, w, upstream_port), "127.0.0.1", 0
        )
        try:
            reader, writer = await asyncio.open_connection(
                "127.0.0.1", ingress.sockets[0].getsockname()[1]
            )
            payload = b"explicit test bytes\x00" * 10000
            writer.write(payload)
            await writer.drain()
            writer.write_eof()
            assert await asyncio.wait_for(reader.read(), timeout=10) == b"echo:" + payload
            writer.close()
            await writer.wait_closed()
        finally:
            ingress.close()
            upstream.close()
            await ingress.wait_closed()
            await upstream.wait_closed()

    asyncio.run(exercise())


def test_production_targets_are_only_registered_docker_services():
    assert set(gateway.TARGETS.values()) == {
        "api",
        "proxy",
        "runner",
        "dex",
        "registry",
        "minio",
        "maildev",
    }
    assert set(gateway.TARGETS) == {3000, 4000, 3003, 5556, 6000, 9001, 1080}
````
