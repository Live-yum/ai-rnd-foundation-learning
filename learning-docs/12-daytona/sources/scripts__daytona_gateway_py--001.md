# scripts/daytona_gateway.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：固定端口的本机网络入口。** TARGETS静态列出容器服务，异步转发只连接这些固定目标；不读取用户URL、代理主机或模型密钥，不把它当任意TCP代理。

**对应关系：** 本机Compose回环发布端口 → 只读网关容器 → 内部服务。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `pipe`（L21–L28）：接收`reader`、`writer`。 源码说明：Preserve bytes and half-close semantics; never interpret HTTP credentials.。 控制顺序：L23在`block := await asyncio.wait_for(reader.read(65536), timeout=300)`成立时循环；L26按`writer.can_write_eof()`分支。 调用`asyncio.wait_for`、`reader.read`、`writer.write`、`writer.drain`、`writer.can_write_eof`、`writer.write_eof`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `relay`（L31–L59）：接收`reader`、`writer`、`port`。本机入口只按固定端口选择内部服务，逐字节转发并保留半关闭语义；不解析用户传入URL、目标地址或模型密钥，超时与退出时关闭两侧连接。 控制顺序：L35按`port not in TARGETS`分支；L36抛异常，停止当前正常路径；L49遍历`tasks`；L51按`tasks`分支；L53遍历`(writer, upstream)`；L54按`stream is not None`分支。 调用`ValueError`、`asyncio.wait_for`、`asyncio.open_connection`、`asyncio.create_task`、`pipe`、`asyncio.gather`、`print`、`task.cancel`、`stream.close`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L62–L75）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L65遍历`TARGETS`；L73遍历`servers`。 调用`asyncio.start_server`、`relay`、`servers.append`、`print`、`asyncio.gather`、`server.serve_forever`、`server.close`、`server.wait_closed`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_gateway.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L79。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2537`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_gateway.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d20ba6745a61ba57913e8728034d78bd160f832e8b0c0252adc5eb07f9e1f6a3"} -->
````python
# scripts/daytona_gateway.py
"""Fixed TCP ingress for an otherwise internal-only Daytona Docker network.

This file runs alone in a read-only, unprivileged local container. It does not
read URLs, environment configuration, model keys or requested upstream names.
Only the Docker host's loopback-published ports can reach these listeners.
"""

import asyncio

TARGETS = {
    3000: "api",
    4000: "proxy",
    3003: "runner",
    5556: "dex",
    6000: "registry",
    9001: "minio",
    1080: "maildev",
}


async def pipe(reader, writer):
    """Preserve bytes and half-close semantics; never interpret HTTP credentials."""
    while block := await asyncio.wait_for(reader.read(65536), timeout=300):
        writer.write(block)
        await writer.drain()
    if writer.can_write_eof():
        writer.write_eof()
        await writer.drain()


async def relay(reader, writer, port):
    upstream = None
    tasks = []
    try:
        if port not in TARGETS:
            raise ValueError("Unregistered local ingress port")
        incoming, upstream = await asyncio.wait_for(
            asyncio.open_connection(TARGETS[port], port), timeout=10
        )
        tasks = [
            asyncio.create_task(pipe(reader, upstream)),
            asyncio.create_task(pipe(incoming, writer)),
        ]
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=3600)
    except OSError, TimeoutError, ValueError:
        # Do not log request bodies, tokens or source content.
        print("Local ingress connection closed on registered port", port, flush=True)
    finally:
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        for stream in (writer, upstream):
            if stream is not None:
                stream.close()
                try:
                    await stream.wait_closed()
                except OSError:
                    pass


async def main():
    servers = []
    try:
        for port in TARGETS:
            server = await asyncio.start_server(
                lambda reader, writer, p=port: relay(reader, writer, p), "0.0.0.0", port
            )
            servers.append(server)
        print("Local ingress ready; fixed internal targets only", flush=True)
        await asyncio.gather(*(server.serve_forever() for server in servers))
    finally:
        for server in servers:
            server.close()
        await asyncio.gather(*(server.wait_closed() for server in servers))


if __name__ == "__main__":
    asyncio.run(main())
````
