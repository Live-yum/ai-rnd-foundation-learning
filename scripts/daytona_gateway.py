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
