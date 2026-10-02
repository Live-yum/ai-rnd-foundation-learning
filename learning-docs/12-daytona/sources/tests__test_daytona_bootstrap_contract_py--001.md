# tests/test_daytona_bootstrap_contract.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_bootstrap`、`workbench.sandbox`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `organization`（L19–L20）：接收`region`。 返回路径：L20的`{"id": ORG, "personal": True, "defaultRegionId": region}`。
- `test_region_initialization_uses_signed_local_api_and_confirms_write`（L24–L43）：接收`current`。 控制顺序：L41断言`[request.method for request in seen] == ( ["GET"] if current == "local" else ["PATCH"…`。 调用`httpx.Client`、`httpx.MockTransport`、`configure_personal_region`、`organization`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_region_initialization_uses_signed_local_api_and_confirms_write.handler`（L27–L37）：接收`request`。 控制顺序：L29断言`request.url.host == "127.0.0.1" and request.url.port == 3000`；L30断言`request.headers["Authorization"] == HEADERS["Authorization"]`；L31断言`request.headers["X-Daytona-Organization-ID"] == ORG`；L32按`request.method == "PATCH"`分支；L33断言`request.url.path == f"/api/organizations/{ORG}/default-region"`；L34断言`json.loads(request.content) == {"defaultRegionId": "local"}`；L36断言`request.method == "GET" and request.url.path == "/api/organizations"`。 调用`seen.append`、`json.loads`、`httpx.Response`、`organization`。 返回路径：L35的`httpx.Response(204)`；L37的`httpx.Response(200, json=[organization("local")])`。
- `test_other_region_nonpersonal_or_malformed_organization_never_written`（L49–L54）：接收`change`。 调用`Mock`、`pytest.raises`、`configure_personal_region`、`organization`、`client.patch.assert_not_called`、`client.get.assert_not_called`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_region_auth_or_server_failure_propagates`（L58–L63）：接收`status`。 调用`httpx.Client`、`httpx.MockTransport`、`httpx.Response`、`pytest.raises`、`configure_personal_region`、`organization`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_region_is_not_ready_until_server_confirms_exact_organization`（L69–L75）：接收`rows`。 调用`httpx.Client`、`httpx.MockTransport`、`pytest.raises`、`configure_personal_region`、`organization`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_region_is_not_ready_until_server_confirms_exact_organization.handler`（L70–L71）：接收`request`。 调用`httpx.Response`。 返回路径：L71的`httpx.Response(204) if request.method == "PATCH" else httpx.Response(200, json=rows)`。
- `test_actual_installed_sdk_transports_can_be_closed_without_a_network_request`（L78–L120）：接收`settings`、`monkeypatch`。 控制顺序：L88遍历`( "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_…`；L102断言`not hasattr(client, "close")`；L103断言`client._http_client.is_closed is False`；L105遍历`(client._api_client, client._toolbox_api_client)`；L106断言`not hasattr(api, "close")`；L115断言`len(manager.pools) == 2`；L117断言`client._http_client.is_closed is True`；L118断言`all(len(manager.pools) == 0 for manager in managers)`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.delenv`、`monkeypatch.setattr`、`SecretStr`、`client_for`、`hasattr`、`managers.append`、`pools.extend`、`manager.connection_from_url`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_installed_sdk_transports_can_be_closed_without_a_network_request.no_network`（L83–L84）：接收`*args`、`**kwargs`。 控制顺序：L84抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_cleanup_attempts_all_and_does_not_hide_the_original_failure`（L123–L140）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L135抛异常，停止当前正常路径；L138断言`caught.value is original and "RuntimeError" in original.__notes__[0]`；L139断言`all(pool.pool is None for pool in pools)`；L140断言`all(len(manager.pools) == 0 for manager in managers)`。 调用`urllib3.PoolManager`、`manager.connection_from_url`、`SimpleNamespace`、`Mock`、`RuntimeError`、`ValueError`、`pytest.raises`、`close_client`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_failure_after_success_still_fails_the_operation`（L143–L147）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Mock`、`RuntimeError`、`pytest.raises`、`close_client`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pool_failure_does_not_prevent_other_pool_cleanup`（L150–L162）：接收`monkeypatch`。 控制顺序：L161断言`second.pool is None and len(manager.pools) == 0`。 调用`urllib3.PoolManager`、`manager.connection_from_url`、`monkeypatch.setattr`、`Mock`、`OSError`、`SimpleNamespace`、`pytest.raises`、`close_client`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_bootstrap_contract.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L162。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6777`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_bootstrap_contract.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a7c0e339427e3e798247b0fea79cc41de35b601c3a8d0f93790d19a7690bae31"} -->
````python
# tests/test_daytona_bootstrap_contract.py
"""Real installed SDK shape plus local bootstrap HTTP contracts; no cloud calls."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
import urllib3
from pydantic import SecretStr

from scripts.daytona_bootstrap import configure_personal_region
from workbench.sandbox import client_for, close_client

ORG = "717b182c-a636-45f0-893c-37499a1b9e32"
HEADERS = {"Authorization": "Bearer local-test-only", "X-Daytona-Organization-ID": ORG}


def organization(region=None):
    return {"id": ORG, "personal": True, "defaultRegionId": region}


@pytest.mark.parametrize("current", [None, "", "local"])
def test_region_initialization_uses_signed_local_api_and_confirms_write(current):
    seen = []

    def handler(request):
        seen.append(request)
        assert request.url.host == "127.0.0.1" and request.url.port == 3000
        assert request.headers["Authorization"] == HEADERS["Authorization"]
        assert request.headers["X-Daytona-Organization-ID"] == ORG
        if request.method == "PATCH":
            assert request.url.path == f"/api/organizations/{ORG}/default-region"
            assert json.loads(request.content) == {"defaultRegionId": "local"}
            return httpx.Response(204)
        assert request.method == "GET" and request.url.path == "/api/organizations"
        return httpx.Response(200, json=[organization("local")])

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        configure_personal_region(client, HEADERS, organization(current))
    assert [request.method for request in seen] == (
        ["GET"] if current == "local" else ["PATCH", "GET"]
    )


@pytest.mark.parametrize(
    "change", [{"defaultRegionId": "us"}, {"personal": False}, {"id": "../other"}]
)
def test_other_region_nonpersonal_or_malformed_organization_never_written(change):
    client = Mock()
    with pytest.raises(ValueError):
        configure_personal_region(client, HEADERS, organization() | change)
    client.patch.assert_not_called()
    client.get.assert_not_called()


@pytest.mark.parametrize("status", [401, 403, 500])
def test_region_auth_or_server_failure_propagates(status):
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(status))
    ) as client:
        with pytest.raises(httpx.HTTPStatusError):
            configure_personal_region(client, HEADERS, organization())


@pytest.mark.parametrize(
    "rows", [[], [organization()], [organization("local"), organization("local")]]
)
def test_region_is_not_ready_until_server_confirms_exact_organization(rows):
    def handler(request):
        return httpx.Response(204) if request.method == "PATCH" else httpx.Response(200, json=rows)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="未保存"):
            configure_personal_region(client, HEADERS, organization())


def test_actual_installed_sdk_transports_can_be_closed_without_a_network_request(
    settings, monkeypatch
):
    import socket

    def no_network(*args, **kwargs):
        raise AssertionError("SDK construction/transport cleanup must not use a network")

    # Production client construction runs inside clean_env()'s isolated child.
    # Mirror that boundary instead of inheriting the test runner's HTTP/SOCKS proxy.
    for variable in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setattr(socket, "getaddrinfo", no_network)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    settings.daytona_api_key = SecretStr("local-test-key")
    settings.daytona_target = "local"
    client = client_for(settings)
    assert not hasattr(client, "close"), "Pinned SDK contract changed; review the transport adapter"
    assert client._http_client.is_closed is False
    managers, pools = [], []
    for api in (client._api_client, client._toolbox_api_client):
        assert not hasattr(api, "close")
        manager = api.rest_client.pool_manager
        managers.append(manager)
        # Construct real pools without opening sockets. Retain references so GC
        # cannot accidentally make a broken explicit cleanup look successful.
        pools.extend(
            manager.connection_from_url(url)
            for url in ("http://127.0.0.1:3000", "http://127.0.0.1:3001")
        )
        assert len(manager.pools) == 2
    close_client(client)
    assert client._http_client.is_closed is True
    assert all(len(manager.pools) == 0 for manager in managers)
    assert all(pool.pool is None for pool in pools)
    close_client(client)  # Repeat cleanup is safe and remains entirely local.


def test_transport_cleanup_attempts_all_and_does_not_hide_the_original_failure():
    managers = [urllib3.PoolManager(), urllib3.PoolManager()]
    pools = [manager.connection_from_url("http://127.0.0.1:3000") for manager in managers]
    client = SimpleNamespace(
        _http_client=Mock(),
        _api_client=SimpleNamespace(rest_client=SimpleNamespace(pool_manager=managers[0])),
        _toolbox_api_client=SimpleNamespace(rest_client=SimpleNamespace(pool_manager=managers[1])),
    )
    client._http_client.close.side_effect = RuntimeError("local cleanup fixture")
    original = ValueError("original snapshot failure")
    with pytest.raises(ValueError, match="original snapshot") as caught:
        try:
            raise original
        finally:
            close_client(client)
    assert caught.value is original and "RuntimeError" in original.__notes__[0]
    assert all(pool.pool is None for pool in pools)
    assert all(len(manager.pools) == 0 for manager in managers)


def test_transport_failure_after_success_still_fails_the_operation():
    client = SimpleNamespace(_http_client=Mock())
    client._http_client.close.side_effect = RuntimeError("local cleanup fixture")
    with pytest.raises(RuntimeError, match="传输资源关闭失败"):
        close_client(client)


def test_pool_failure_does_not_prevent_other_pool_cleanup(monkeypatch):
    manager = urllib3.PoolManager()
    first = manager.connection_from_url("http://127.0.0.1:3000")
    second = manager.connection_from_url("http://127.0.0.1:3001")
    original_close = first.close
    monkeypatch.setattr(first, "close", Mock(side_effect=OSError("local fixture")))
    client = SimpleNamespace(
        _api_client=SimpleNamespace(rest_client=SimpleNamespace(pool_manager=manager))
    )
    with pytest.raises(RuntimeError, match="传输资源关闭失败"):
        close_client(client)
    assert second.pool is None and len(manager.pools) == 0
    original_close()
````
