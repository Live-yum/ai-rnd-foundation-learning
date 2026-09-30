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
