# tests/test_daytona_snapshot.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `snapshot`（L17–L18）：接收`**overrides`。 调用`SimpleNamespace`。 返回路径：L18的`SimpleNamespace(name=NAME, image_name=IMAGE, state="active", **overrides)`。
- `page`（L21–L22）：接收`number`、`items`、`total_pages`。 调用`SimpleNamespace`。 返回路径：L22的`SimpleNamespace(page=number, items=items, total_pages=total_pages)`。
- `test_exact_name_lookup_reads_every_page_and_never_uses_uuid_route`（L25–L38）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L33断言`bootstrap.snapshot_named(service, NAME) is wanted`；L34断言`[call.kwargs for call in service.list.call_args_list] == [ {"page": number, "limit": …`。 调用`snapshot`、`Mock`、`page`、`SimpleNamespace`、`bootstrap.snapshot_named`、`range`、`service.get.assert_not_called`、`service.create.assert_not_called`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_confirmed_empty_listing_means_absent`（L42–L45）：接收`total_pages`。 控制顺序：L45断言`bootstrap.snapshot_named(service, NAME) is None`。 调用`Mock`、`page`、`bootstrap.snapshot_named`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_or_excessive_pagination_fails_closed`（L49–L54）：接收`result`。 调用`Mock`、`pytest.raises`、`bootstrap.snapshot_named`、`service.create.assert_not_called`、`pytest.mark.parametrize`、`page`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_names_across_pages_are_not_guessed`（L57–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Mock`、`page`、`snapshot`、`pytest.raises`、`bootstrap.snapshot_named`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_listing_failure_is_not_interpreted_as_absence`（L64–L69）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Mock`、`RuntimeError`、`pytest.raises`、`bootstrap.snapshot_named`、`service.create.assert_not_called`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `worker`（L73–L96）：接收`tmp_path`、`monkeypatch`。 调用`(tmp_path / "snapshot-image.json").write_text`、`json.dumps`、`(tmp_path / "api-key.json").write_text`、`SimpleNamespace`、`Mock`、`httpx.Client`、`urllib3.PoolManager`、`page`、`snapshot`等。 返回路径：L96的`tmp_path, client`。
- `test_worker_creates_or_reuses_only_matching_active_local_snapshot`（L100–L117）：接收`worker`、`reuse`。 控制顺序：L102按`reuse`分支；L106按`reuse`分支；L110断言`params.name == NAME and params.image == IMAGE and params.region_id == "local"`；L111断言`client.snapshot.create.call_args.kwargs == {"timeout": 600}`；L113断言`"DAYTONA_API_URL=http://127.0.0.1:3000/api" in env`；L114断言`f"DAYTONA_SNAPSHOT={NAME}" in env`；L115断言`client._http_client.is_closed`；L116遍历`("_api_client", "_toolbox_api_client")`。后续分支沿下方源码相同行号继续阅读。 调用`page`、`snapshot`、`bootstrap.snapshot_worker`、`client.snapshot.get.assert_not_called`、`client.snapshot.create.assert_not_called`、`(directory / "workbench.env").read_text`、`len`、`getattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_never_writes_ready_config_for_wrong_or_unready_snapshot`（L130–L145）：接收`worker`、`monkeypatch`、`reuse`、`field`、`value`、`message`。 控制顺序：L142断言`not (directory / "workbench.env").exists()`；L143断言`client._http_client.is_closed`；L144遍历`("_api_client", "_toolbox_api_client")`；L145断言`len(getattr(client, name).rest_client.pool_manager.pools) == 0`。 调用`snapshot`、`setattr`、`monkeypatch.setattr`、`pytest.raises`、`bootstrap.snapshot_worker`、`(directory / "workbench.env").exists`、`len`、`getattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_preserves_existing_credentials_and_closes_on_list_failure`（L148–L159）：接收`worker`。 控制顺序：L155断言`(directory / "workbench.env").read_text(encoding="utf-8") == existing`；L157断言`client._http_client.is_closed`；L158遍历`("_api_client", "_toolbox_api_client")`；L159断言`len(getattr(client, name).rest_client.pool_manager.pools) == 0`。 调用`(directory / "workbench.env").write_text`、`RuntimeError`、`pytest.raises`、`bootstrap.snapshot_worker`、`(directory / "workbench.env").read_text`、`client.snapshot.create.assert_not_called`、`len`、`getattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `clock`（L163–L169）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`now.__setitem__`。 返回路径：L169的`now`。
- `test_default_snapshot_warmup_is_observed_before_create`（L172–L182）：接收`clock`。 控制顺序：L180断言`bootstrap.wait_default_snapshot(service, IMAGE, timeout=10) is ready`；L181断言`clock[0] == 4`。 调用`Mock`、`SimpleNamespace`、`page`、`bootstrap.wait_default_snapshot`、`service.create.assert_not_called`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_default_snapshot_failure_never_becomes_ready`（L186–L194）：接收`state`、`clock`。 控制顺序：L193断言`clock[0] == 0`。 调用`Mock`、`page`、`SimpleNamespace`、`pytest.raises`、`bootstrap.wait_default_snapshot`、`service.create.assert_not_called`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_default_snapshot_warmup_has_a_hard_deadline`（L197–L203）：接收`clock`。 控制顺序：L202断言`clock[0] == 5`。 调用`Mock`、`page`、`pytest.raises`、`bootstrap.wait_default_snapshot`、`service.create.assert_not_called`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_warmup_failure_leaves_config_untouched_and_closes_client`（L206–L215）：接收`worker`、`monkeypatch`。 控制顺序：L214断言`not (directory / "workbench.env").exists()`；L215断言`client._http_client.is_closed`。 调用`monkeypatch.setattr`、`Mock`、`TimeoutError`、`pytest.raises`、`bootstrap.snapshot_worker`、`client.snapshot.create.assert_not_called`、`(directory / "workbench.env").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_snapshot.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L215。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8269`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_snapshot.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0be11d4abf0b6b473df8e2902ea5ac6fc5d7e4b985dbba1ef1dda74823d565bd"} -->
````python
# tests/test_daytona_snapshot.py
"""Pinned local snapshot lookup contracts; real service acceptance runs separately."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
import urllib3

from scripts import daytona_bootstrap as bootstrap

NAME = "rnd-python-0123456789abcdef"
IMAGE = "registry:6000/rnd-python:0123456789abcdef"


def snapshot(**overrides):
    return SimpleNamespace(name=NAME, image_name=IMAGE, state="active", **overrides)


def page(number, items, total_pages=1):
    return SimpleNamespace(page=number, items=items, total_pages=total_pages)


def test_exact_name_lookup_reads_every_page_and_never_uses_uuid_route():
    wanted = snapshot()
    service = Mock()
    service.list.side_effect = [
        page(1, [SimpleNamespace(name=NAME + "-other")], 3),
        page(2, [wanted], 3),
        page(3, [], 3),
    ]
    assert bootstrap.snapshot_named(service, NAME) is wanted
    assert [call.kwargs for call in service.list.call_args_list] == [
        {"page": number, "limit": 100} for number in range(1, 4)
    ]
    service.get.assert_not_called()
    service.create.assert_not_called()


@pytest.mark.parametrize("total_pages", [0, 1])
def test_confirmed_empty_listing_means_absent(total_pages):
    service = Mock()
    service.list.return_value = page(1, [], total_pages)
    assert bootstrap.snapshot_named(service, NAME) is None


@pytest.mark.parametrize("result", [page(2, []), page(1, [], -1), page(1, [], 101)])
def test_invalid_or_excessive_pagination_fails_closed(result):
    service = Mock()
    service.list.return_value = result
    with pytest.raises(ValueError, match="分页"):
        bootstrap.snapshot_named(service, NAME)
    service.create.assert_not_called()


def test_duplicate_names_across_pages_are_not_guessed():
    service = Mock()
    service.list.side_effect = [page(1, [snapshot()], 2), page(2, [snapshot()], 2)]
    with pytest.raises(ValueError, match="多个同名"):
        bootstrap.snapshot_named(service, NAME)


def test_listing_failure_is_not_interpreted_as_absence():
    service = Mock()
    service.list.side_effect = RuntimeError("explicit local authentication failure")
    with pytest.raises(RuntimeError, match="authentication"):
        bootstrap.snapshot_named(service, NAME)
    service.create.assert_not_called()


@pytest.fixture
def worker(tmp_path, monkeypatch):
    (tmp_path / "snapshot-image.json").write_text(
        json.dumps({"image": IMAGE, "snapshot": NAME}), encoding="utf-8"
    )
    (tmp_path / "api-key.json").write_text(
        json.dumps({"value": "local-test-key-not-a-real-credential"}), encoding="utf-8"
    )
    client = SimpleNamespace(
        snapshot=Mock(),
        _http_client=httpx.Client(trust_env=False),
        _api_client=SimpleNamespace(
            rest_client=SimpleNamespace(pool_manager=urllib3.PoolManager())
        ),
        _toolbox_api_client=SimpleNamespace(
            rest_client=SimpleNamespace(pool_manager=urllib3.PoolManager())
        ),
    )
    client.snapshot.list.return_value = page(
        1, [SimpleNamespace(name=IMAGE, image_name=IMAGE, state="active")]
    )
    client.snapshot.create.return_value = snapshot()
    monkeypatch.setattr(bootstrap, "install_loopback_guard", lambda: None)
    monkeypatch.setattr(bootstrap, "client_for", lambda settings: client)
    return tmp_path, client


@pytest.mark.parametrize("reuse", [False, True])
def test_worker_creates_or_reuses_only_matching_active_local_snapshot(worker, reuse):
    directory, client = worker
    if reuse:
        client.snapshot.list.return_value = page(1, [snapshot()])
    bootstrap.snapshot_worker(directory)
    client.snapshot.get.assert_not_called()
    if reuse:
        client.snapshot.create.assert_not_called()
    else:
        params = client.snapshot.create.call_args.args[0]
        assert params.name == NAME and params.image == IMAGE and params.region_id == "local"
        assert client.snapshot.create.call_args.kwargs == {"timeout": 600}
    env = (directory / "workbench.env").read_text(encoding="utf-8")
    assert "DAYTONA_API_URL=http://127.0.0.1:3000/api" in env
    assert f"DAYTONA_SNAPSHOT={NAME}" in env
    assert client._http_client.is_closed
    for name in ("_api_client", "_toolbox_api_client"):
        assert len(getattr(client, name).rest_client.pool_manager.pools) == 0


@pytest.mark.parametrize("reuse", [False, True])
@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", "other", "来源"),
        ("image_name", "other:image", "来源"),
        ("state", "building", "尚未就绪"),
        ("state", "build_failed", "尚未就绪"),
    ],
)
def test_worker_never_writes_ready_config_for_wrong_or_unready_snapshot(
    worker, monkeypatch, reuse, field, value, message
):
    directory, client = worker
    invalid = snapshot()
    setattr(invalid, field, value)
    # Inject the lookup result to test validation independently of exact-name filtering.
    monkeypatch.setattr(bootstrap, "snapshot_named", lambda *args: invalid if reuse else None)
    monkeypatch.setattr(bootstrap, "wait_default_snapshot", lambda *args: None)
    client.snapshot.create.return_value = invalid
    with pytest.raises(ValueError, match=message):
        bootstrap.snapshot_worker(directory)
    assert not (directory / "workbench.env").exists()
    assert client._http_client.is_closed
    for name in ("_api_client", "_toolbox_api_client"):
        assert len(getattr(client, name).rest_client.pool_manager.pools) == 0


def test_worker_preserves_existing_credentials_and_closes_on_list_failure(worker):
    directory, client = worker
    existing = "DAYTONA_API_KEY=existing-local-test-key\n"
    (directory / "workbench.env").write_text(existing, encoding="utf-8")
    client.snapshot.list.side_effect = RuntimeError("explicit local service failure")
    with pytest.raises(RuntimeError, match="service"):
        bootstrap.snapshot_worker(directory)
    assert (directory / "workbench.env").read_text(encoding="utf-8") == existing
    client.snapshot.create.assert_not_called()
    assert client._http_client.is_closed
    for name in ("_api_client", "_toolbox_api_client"):
        assert len(getattr(client, name).rest_client.pool_manager.pools) == 0


@pytest.fixture
def clock(monkeypatch):
    now = [0.0]
    monkeypatch.setattr(bootstrap.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        bootstrap.time, "sleep", lambda seconds: now.__setitem__(0, now[0] + seconds)
    )
    return now


def test_default_snapshot_warmup_is_observed_before_create(clock):
    service = Mock()
    ready = SimpleNamespace(name=IMAGE, image_name=IMAGE, state="active")
    service.list.side_effect = [
        page(1, []),
        page(1, [SimpleNamespace(name=IMAGE, image_name=IMAGE, state="building")]),
        page(1, [ready]),
    ]
    assert bootstrap.wait_default_snapshot(service, IMAGE, timeout=10) is ready
    assert clock[0] == 4
    service.create.assert_not_called()


@pytest.mark.parametrize("state", ["error", "failed", "build_failed", "inactive", "removing"])
def test_default_snapshot_failure_never_becomes_ready(state, clock):
    service = Mock()
    service.list.return_value = page(
        1, [SimpleNamespace(name=IMAGE, image_name=IMAGE, state=state)]
    )
    with pytest.raises(ValueError, match="默认快照"):
        bootstrap.wait_default_snapshot(service, IMAGE)
    assert clock[0] == 0
    service.create.assert_not_called()


def test_default_snapshot_warmup_has_a_hard_deadline(clock):
    service = Mock()
    service.list.return_value = page(1, [])
    with pytest.raises(TimeoutError, match="未就绪"):
        bootstrap.wait_default_snapshot(service, IMAGE, timeout=5)
    assert clock[0] == 5
    service.create.assert_not_called()


def test_warmup_failure_leaves_config_untouched_and_closes_client(worker, monkeypatch):
    directory, client = worker
    monkeypatch.setattr(
        bootstrap, "wait_default_snapshot", Mock(side_effect=TimeoutError("warm-up"))
    )
    with pytest.raises(TimeoutError, match="warm-up"):
        bootstrap.snapshot_worker(directory)
    client.snapshot.create.assert_not_called()
    assert not (directory / "workbench.env").exists()
    assert client._http_client.is_closed
````
