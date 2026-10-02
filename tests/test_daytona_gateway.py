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
