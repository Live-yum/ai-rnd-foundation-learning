# tests/test_local_only.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_local`、`workbench.local_only`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_tool_urls_reject_cloud_and_ambiguous_hosts`（L42–L48）：接收`url`。 调用`pytest.raises`、`local_http_url`、`Settings`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_unambiguous_loopback_is_accepted`（L59–L60）：接收`url`、`expected`。 控制顺序：L60断言`local_http_url(url) == expected`。 调用`local_http_url`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chat_model_is_the_only_configurable_external_compute`（L63–L80）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L70断言`local_database_url("postgresql://u:p@localhost:5432/db").startswith( "postgresql://u:…`；L73遍历`[ "postgresql://u:p@db.cloud.test/db", "postgresql://u:p@localhos…`。 调用`ModelProfile( stage="coding", base_url="https://model.example/v1"…`、`ModelProfile`、`SecretStr`、`local_database_url("postgresql://u:p@localhost:5432/db").startswi…`、`local_database_url`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inherited_tracing_and_cloud_context_cannot_be_reenabled`（L83–L91）：接收`monkeypatch`。 控制顺序：L87断言`env["LANGSMITH_TRACING"] == "false" and env["DAYTONA_OTEL_ENABLED"] == "false"`；L88断言`"LANGSMITH_API_KEY" not in env and "DOCKER_HOST" not in env`；L89断言`local_docker_command(["docker", "ps"])[1] == "--host"`。 调用`monkeypatch.setenv`、`clean_env`、`local_docker_command`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_daytona_child_blocks_external_dns_tcp_udp_and_redirect`（L94–L134）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L133断言`result.returncode == 0`；L134断言`"loopback-only PASS" in result.stdout`。 调用`subprocess.run`、`clean_env`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_daytona_sdk_and_params_are_pinned`（L137–L146）：接收`settings`、`monkeypatch`。 控制顺序：L142断言`params.network_block_all is True and params.public is False`；L143断言`params.name == "rnd-test"`。 调用`params_for`、`monkeypatch.setattr`、`pytest.raises`、`client_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deployment_transformation_has_no_cloud_services`（L149–L206）：接收`tmp_path`。 控制顺序：L178断言`not rendered["services"]["api"].get("privileged", False)`；L179断言`rendered["services"]["runner"]["privileged"] is True`；L180断言`rendered["services"]["dex"]["user"] == "0:0"`；L181断言`"no-new-privileges:true" in rendered["services"]["dex"]["security_opt"]`；L182断言`rendered["services"]["minio"]["environment"]["MINIO_UPDATE"] == "off"`；L183断言`set(rendered["services"]) == KEEP`；L184断言`"cloud.example" not in json.dumps(rendered)`；L185断言`rendered["services"]["api"]["image"] == IMAGES["api"]`。后续分支沿下方源码相同行号继续阅读。 调用`dict.fromkeys`、`render_compose`、`rendered["services"]["api"].get`、`set`、`json.dumps`、`len`、`int`、`credentials.values`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_portable_launcher_carries_local_policy`（L209–L213）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L212断言`"local_only.py" in HELPERS`；L213断言`(ROOT / "workbench/local_only.py").is_file()`。 调用`(ROOT / "workbench/local_only.py").is_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_one_complete_handbook_is_generated`（L216–L223）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L219断言`OUTPUT.name == "从零实现AI研发平台_逐步实操手册_完整版.md"`；L220断言`"LEGACY" not in (ROOT / "scripts/build_handbook.py").read_text(encoding="utf-8")`；L222断言`"空文件夹" in text and "source-file: workbench/local_only.py" in text`；L223断言`len(list(ROOT.glob("从零实现AI研发平台_逐步实操手册_完整版*.md"))) == 1`。 调用`(ROOT / "scripts/build_handbook.py").read_text`、`render`、`len`、`list`、`ROOT.glob`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_local_only.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L223。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8588`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_local_only.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2c58dff865077fc1cc5733712e3d915598bdc17ae2407cda0a052019997609b7"} -->
````python
# tests/test_local_only.py
"""Local policy tests; these do not pretend that a mocked SDK is a live service."""

import json
import subprocess
import sys

import pytest
from pydantic import SecretStr

from scripts.daytona_local import IMAGES, KEEP, assert_local_compose, render_compose
from workbench.local_only import (
    DAYTONA_VERSION,
    local_database_url,
    local_docker_command,
    local_http_url,
)
from workbench.settings import ROOT, ModelProfile, Settings
from workbench.tools import clean_env


@pytest.mark.parametrize(
    "url",
    [
        "https://app.daytona.io/api",
        "https://embeddings.example/v1",
        "http://192.168.1.1/api",
        "http://127.0.0.1.evil.test/api",
        "http://localhost@evil.test/api",
        "http://evil.test@localhost/api",
        "http://127.1/api",
        "http://2130706433/api",
        "http://0.0.0.0/api",
        "http://[::ffff:127.0.0.1]/api",
        "http://127.0.0.1/?host=remote",
        "http://127.0.0.1/#remote",
        "http://127.0.0.1:0/api",
        " http://localhost/api",
        "http://localhost/api\n",
        "http://localhost\\evil/api",
    ],
)
def test_tool_urls_reject_cloud_and_ambiguous_hosts(url):
    with pytest.raises(ValueError):
        local_http_url(url)
    with pytest.raises(ValueError):
        Settings(_env_file=None, daytona_api_url=url)
    with pytest.raises(ValueError):
        Settings(_env_file=None, embedding_base_url=url)


@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://localhost:3000/api", "http://127.0.0.1:3000/api"),
        ("https://127.0.0.1:11434/v1", "https://127.0.0.1:11434/v1"),
        ("http://[::1]:3000/api", "http://[::1]:3000/api"),
    ],
)
def test_only_unambiguous_loopback_is_accepted(url, expected):
    assert local_http_url(url) == expected


def test_chat_model_is_the_only_configurable_external_compute():
    ModelProfile(
        stage="coding",
        base_url="https://model.example/v1",
        model="fixture",
        api_key=SecretStr("test-only"),
    ).validate_endpoint()
    assert local_database_url("postgresql://u:p@localhost:5432/db").startswith(
        "postgresql://u:p@127.0.0.1"
    )
    for url in [
        "postgresql://u:p@db.cloud.test/db",
        "postgresql://u:p@localhost/db?hostaddr=8.8.8.8",
        "postgresql://u:p@127.0.0.1/db?service=remote",
        "sqlite://///server/share/db",
    ]:
        with pytest.raises(ValueError):
            local_database_url(url)


def test_inherited_tracing_and_cloud_context_cannot_be_reenabled(monkeypatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", "must-not-leave")
    monkeypatch.setenv("DOCKER_HOST", "tcp://remote.example:2376")
    env = clean_env({"LANGSMITH_TRACING": "true", "DAYTONA_OTEL_ENABLED": "true"})
    assert env["LANGSMITH_TRACING"] == "false" and env["DAYTONA_OTEL_ENABLED"] == "false"
    assert "LANGSMITH_API_KEY" not in env and "DOCKER_HOST" not in env
    assert local_docker_command(["docker", "ps"])[1] == "--host"
    with pytest.raises(ValueError):
        local_docker_command(["docker", "--context=cloud", "ps"])


def test_daytona_child_blocks_external_dns_tcp_udp_and_redirect():
    code = """
import socket, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from workbench.local_only import install_loopback_guard
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', 'http://203.0.113.7/blocked')
        self.end_headers()
    def log_message(self,*args): pass
server = HTTPServer(('127.0.0.1',0),Handler)
thread = threading.Thread(target=server.serve_forever,daemon=True);thread.start()
install_loopback_guard()
assert socket.getaddrinfo('3000-id.proxy.localhost',80)[0][4][0] == '127.0.0.1'
for kind in ('dns','tcp','udp','redirect'):
    try:
        if kind == 'dns': socket.getaddrinfo('cloud.example',443)
        elif kind == 'tcp':
            with socket.socket() as sock: sock.connect(('203.0.113.7',80))
        elif kind == 'udp':
            with socket.socket(type=socket.SOCK_DGRAM) as sock: sock.sendto(b'x',('203.0.113.7',53))
        else:
            import urllib.request
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            opener.open('http://127.0.0.1:'+str(server.server_port),timeout=2)
    except ValueError: pass
    else: raise AssertionError(kind+' unexpectedly permitted')
server.shutdown(); server.server_close()
print('loopback-only PASS')
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=clean_env(),
        capture_output=True,
        timeout=30,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "loopback-only PASS" in result.stdout


def test_daytona_sdk_and_params_are_pinned(settings, monkeypatch):
    from workbench.sandbox import client_for, params_for

    settings.daytona_snapshot = "fixture-local"
    params = params_for(settings, "rnd-test")
    assert params.network_block_all is True and params.public is False
    assert params.name == "rnd-test"
    monkeypatch.setattr("workbench.sandbox.version", lambda _: "999.0.0")
    with pytest.raises(RuntimeError, match=DAYTONA_VERSION):
        client_for(settings)


def test_deployment_transformation_has_no_cloud_services(tmp_path):
    source = {
        "services": {
            n: {
                "image": "mutable",
                "environment": ["POSTHOG_HOST=https://cloud.example"],
                "ports": ["3000:3000"],
                "depends_on": ["jaeger"],
            }
            for n in KEEP
        }
    }
    source["services"]["jaeger"] = {"image": "unneeded"}
    credentials = dict.fromkeys(
        [
            "encryption_key",
            "salt",
            "database_password",
            "storage_password",
            "proxy_key",
            "runner_key",
            "health_key",
            "admin_key",
        ],
        "fixture-random",
    )
    source["services"]["api"]["privileged"] = True
    source["services"]["runner"]["privileged"] = True
    rendered = render_compose(source, credentials, tmp_path)
    assert not rendered["services"]["api"].get("privileged", False)
    assert rendered["services"]["runner"]["privileged"] is True
    assert rendered["services"]["dex"]["user"] == "0:0"
    assert "no-new-privileges:true" in rendered["services"]["dex"]["security_opt"]
    assert rendered["services"]["minio"]["environment"]["MINIO_UPDATE"] == "off"
    assert set(rendered["services"]) == KEEP
    assert "cloud.example" not in json.dumps(rendered)
    assert rendered["services"]["api"]["image"] == IMAGES["api"]
    sentinel = rendered["services"]["api"]["environment"]["SSH_GATEWAY_API_KEY"]
    assert len(sentinel) == 64 and int(sentinel, 16) >= 0
    assert sentinel not in credentials.values()
    assert "ssh-gateway" not in rendered["services"]
    assert rendered["services"]["runner"]["environment"]["SSH_GATEWAY_ENABLE"] == "false"
    assert "SSH_GATEWAY_URL" not in rendered["services"]["api"]["environment"]
    repeated = render_compose(source, credentials, tmp_path)
    assert repeated["services"]["api"]["environment"]["SSH_GATEWAY_API_KEY"] == sentinel
    other = render_compose(source, {**credentials, "admin_key": "different-local-secret"}, tmp_path)
    assert other["services"]["api"]["environment"]["SSH_GATEWAY_API_KEY"] != sentinel
    assert all(
        not service.get("ports")
        for name, service in rendered["services"].items()
        if name != "gateway"
    )
    assert all(port.startswith("127.0.0.1:") for port in rendered["services"]["gateway"]["ports"])
    assert rendered["services"]["gateway"]["cap_drop"] == ["ALL"]
    assert len(IMAGES) == len(KEEP)
    rendered["services"]["api"]["ports"] = ["0.0.0.0:3000:3000"]
    with pytest.raises(ValueError):
        assert_local_compose(rendered)


def test_portable_launcher_carries_local_policy():
    from workbench.portable import HELPERS

    assert "local_only.py" in HELPERS
    assert (ROOT / "workbench/local_only.py").is_file()


def test_only_one_complete_handbook_is_generated():
    from scripts.build_handbook import OUTPUT, render

    assert OUTPUT.name == "从零实现AI研发平台_逐步实操手册_完整版.md"
    assert "LEGACY" not in (ROOT / "scripts/build_handbook.py").read_text(encoding="utf-8")
    text = render()
    assert "空文件夹" in text and "source-file: workbench/local_only.py" in text
    assert len(list(ROOT.glob("从零实现AI研发平台_逐步实操手册_完整版*.md"))) == 1
````
