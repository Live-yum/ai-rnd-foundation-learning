# tests/test_native_ports.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_established_source_socket_blocks_later_server_bind`（L15–L25）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`closing`、`socket.socket`、`upstream.bind`、`upstream.listen`、`client.connect`、`upstream.getsockname`、`upstream.accept`、`pytest.raises`、`backend.bind`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_lease_excludes_dynamic_range_and_survives_restart`（L28–L40）：接收`tmp_path`、`monkeypatch`。 控制顺序：L32断言`1024 <= selected < 12000`；L33断言`json.loads(state.read_text())["port"] == selected`；L35断言`selected != other`；L40断言`restarted == selected`。 调用`monkeypatch.setattr`、`ports.backend_port_lease`、`json.loads`、`state.read_text`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_receipt_from_another_copy_is_reallocated`（L43–L50）：接收`tmp_path`、`monkeypatch`。 控制顺序：L49断言`other != selected`；L50断言`json.loads(second.read_text())["owner"] == str(second.resolve())`。 调用`monkeypatch.setattr`、`ports.backend_port_lease`、`second.write_bytes`、`first.read_bytes`、`json.loads`、`second.read_text`、`str`、`second.resolve`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_port_conflict_is_fail_closed`（L53–L60）：接收`tmp_path`。 控制顺序：L60断言`listener.fileno() >= 0`。 调用`closing`、`socket.socket`、`listener.bind`、`listener.listen`、`pytest.raises`、`ports.backend_port_lease`、`listener.getsockname`、`listener.fileno`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_ephemeral_port_is_preserved_and_released`（L63–L71）：接收`tmp_path`。 控制顺序：L69断言`port == selected`；L71断言`port == selected`。 调用`closing`、`socket.socket`、`listener.bind`、`listener.getsockname`、`ports.backend_port_lease`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_dynamic_range_fails_closed_for_saved_port`（L74–L82）：接收`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`ports.backend_port_lease`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_server_time_wait_does_not_prevent_reacquiring_saved_port`（L86–L101）：接收`tmp_path`。 控制顺序：L98断言`client.recv(1) == b""`；L99断言`loopback_port_bindable(selected)`；L101断言`restarted == selected`。 调用`ports.backend_port_lease`、`closing`、`socket.socket`、`server.setsockopt`、`server.bind`、`server.listen`、`client.connect`、`server.getsockname`、`server.accept`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_platform_dynamic_range_discovery`（L105–L113）：接收`system`、`monkeypatch`。 控制顺序：L113断言`ports.dynamic_tcp_range() == (49152, 65535)`。 调用`monkeypatch.setattr`、`iter`、`"起始端口 : 49152\n端口数 : 16384\n".encode`、`next`、`ports.dynamic_tcp_range`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_or_malformed_dynamic_range_is_not_guessed`（L116–L123）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`ports.dynamic_tcp_range`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_port_receipt_symlink_rejected`（L126–L134）：接收`tmp_path`。 控制顺序：L134断言`target.read_text() == "{}"`。 调用`target.write_text`、`link.symlink_to`、`pytest.raises`、`ports.backend_port_lease`、`target.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_skip_build_rejects_changed_target`（L137–L147）：接收`tmp_path`。 调用`dist.mkdir`、`pytest.raises`、`require_frontend_backend`、`(dist / "native-backend.json").write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_portable_export_includes_allocator_and_no_runtime_receipt`（L150–L155）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L154断言`"native_ports.py" in HELPERS`；L155断言`".deployment" in EXCLUDED_DIRS`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delivered_launcher_propagates_one_port_and_skip_build_is_bound_to_copy`（L159–L267）：接收`tmp_path`、`monkeypatch`、`template`。 控制顺序：L242断言`backend_ports == [selected, selected]`；L243断言`frontend_urls == [f"http://127.0.0.1:{selected}"]`；L245断言`outcome["backend_port"] == selected and outcome["backend_url"] == frontend_urls[0]`；L248断言`backend_ports == [selected] * 4 and len(service_calls) == 2`；L256断言`len(service_calls) == 2`；L257断言`ports.saved_backend_port(product / ".deployment/backend-port.json") == selected`；L267断言`len(service_calls) == 2`。 调用`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`、`deployment.mkdir`、`write_json`、`monkeypatch.setattr`、`launcher.main`、`ports.saved_backend_port`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delivered_launcher_propagates_one_port_and_skip_build_is_bound_to_copy.services`（L183–L185）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`service_calls.append`。 返回路径：L185的`"postgresql+psycopg://native:unused@127.0.0.1:5432/test_codegen", 6379`。
- `test_delivered_launcher_propagates_one_port_and_skip_build_is_bound_to_copy.backend`（L199–L222）：接收`template`、`root`、`env`、`reports`。 控制顺序：L200按`template == "fastapiadmin"`分支；L213断言`f"spring.cloud.openfeign.client.config.yudao-system.url=http://127.0.0.1:{port}" in p…`；L217断言`f"spring.cloud.openfeign.client.config.yudao-infra.url=http://127.0.0.1:{port}" in pr…`。 调用`int`、`( root / "yudao-server/src/main/resources/application-native.prop…`、`next`、`row.split`、`properties.splitlines`、`row.startswith`、`backend_ports.append`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_delivered_launcher_propagates_one_port_and_skip_build_is_bound_to_copy.build`（L227–L230）：接收`template`、`root`、`env`、`reports`、`**kwargs`。 调用`frontend_urls.append`、`write_json`、`frontend_app`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delivered_launcher_propagates_one_port_and_skip_build_is_bound_to_copy.frontend`（L235–L236）：接收`*args`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_pinned_vben_relative_api_proxy_uses_selected_backend`（L270–L321）：接收`tmp_path`、`monkeypatch`。 控制顺序：L291断言`"VITE_GLOB_API_URL" in hooks`；L299断言`config.read_text(encoding="utf-8") == adapted`；L318断言`json.loads(result.stdout) == { "target": "http://127.0.0.1:18081/admin-api", "path": …`。 调用`monkeypatch.setattr`、`app.mkdir`、`zipfile.ZipFile`、`archive.read("apps/web-antd/vite.config.ts").decode`、`archive.read`、`archive.read("packages/effects/hooks/src/use-app-config.ts").deco…`、`pytest.raises`、`(tmp_path / "legacy-default.txt").write_text`、`config.write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_vben_relative_api_proxy_uses_selected_backend.legacy_text_encoding`（L282–L283）：接收`encoding`、`stacklevel`。 调用`text_encoding`。 返回路径：L283的`"cp1252" if encoding in {None, "locale"} else text_encoding(encoding, stacklevel)`。
- `test_independent_process_cannot_take_a_live_copy_port_lease`（L324–L349）：接收`tmp_path`。 控制顺序：L349断言`result.stdout.strip() == "independent-copy lease PASS"`。 调用`ports.backend_port_lease`、`subprocess.run`、`str`、`result.stdout.strip`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unreadable_or_oversized_port_receipt_is_not_replaced`（L352–L359）：接收`tmp_path`。 控制顺序：L354遍历`("[]", '{"format": 99}', '"' + "x" * 5000 + '"')`；L359断言`state.read_text() == contents`。 调用`state.write_text`、`pytest.raises`、`ports.backend_port_lease`、`state.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_managed_preview_requires_existing_build_port_before_source_changes`（L362–L387）：接收`tmp_path`、`monkeypatch`。 调用`str`、`uuid.uuid4`、`write_json`、`monkeypatch.setattr`、`pytest.fail`、`SimpleNamespace`、`pytest.raises`、`native_delivery.serve_managed`、`ports.backend_port_lease`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_ports.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L387。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16068`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_ports.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f7d372df331df880ce535016aea4be179d818b5676191605fdb494a2341865c2"} -->
````python
# tests/test_native_ports.py
"""Non-ephemeral backend leases and real source-socket collision regressions."""

import json
import os
import socket
import sys
from contextlib import closing

import pytest

from workbench import native_ports as ports


@pytest.mark.skipif(sys.platform != "linux", reason="Linux client-source/listener bind collision")
def test_established_source_socket_blocks_later_server_bind():
    # Reproduce the observed Java-owned ESTABLISHED socket, without a foreign
    # listener or readiness request: an outbound source port can block bind.
    with closing(socket.socket()) as upstream, closing(socket.socket()) as client:
        upstream.bind(("127.0.0.1", 0))
        upstream.listen()
        client.connect(upstream.getsockname())
        accepted, _ = upstream.accept()
        with accepted, closing(socket.socket()) as backend:
            with pytest.raises(OSError):
                backend.bind(client.getsockname())


def test_lease_excludes_dynamic_range_and_survives_restart(tmp_path, monkeypatch):
    monkeypatch.setattr(ports, "dynamic_tcp_range", lambda: (12000, 65535))
    state = tmp_path / "state.json"
    with ports.backend_port_lease(state) as selected:
        assert 1024 <= selected < 12000
        assert json.loads(state.read_text())["port"] == selected
        with ports.backend_port_lease(tmp_path / "other.json") as other:
            assert selected != other
        with pytest.raises(RuntimeError, match="in use"):
            with ports.backend_port_lease(state):
                pass
    with ports.backend_port_lease(state) as restarted:
        assert restarted == selected


def test_receipt_from_another_copy_is_reallocated(tmp_path, monkeypatch):
    monkeypatch.setattr(ports, "dynamic_tcp_range", lambda: (32768, 60999))
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    with ports.backend_port_lease(first) as selected:
        second.write_bytes(first.read_bytes())
        with ports.backend_port_lease(second) as other:
            assert other != selected
            assert json.loads(second.read_text())["owner"] == str(second.resolve())


def test_explicit_port_conflict_is_fail_closed(tmp_path):
    with closing(socket.socket()) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        with pytest.raises(RuntimeError, match="occupied"):
            with ports.backend_port_lease(tmp_path / "state.json", listener.getsockname()[1]):
                pass
        assert listener.fileno() >= 0


def test_explicit_ephemeral_port_is_preserved_and_released(tmp_path):
    with closing(socket.socket()) as listener:
        listener.bind(("127.0.0.1", 0))
        selected = listener.getsockname()[1]
    state = tmp_path / "state.json"
    with ports.backend_port_lease(state, selected) as port:
        assert port == selected
    with ports.backend_port_lease(state, selected) as port:
        assert port == selected


def test_changed_dynamic_range_fails_closed_for_saved_port(tmp_path, monkeypatch):
    monkeypatch.setattr(ports, "dynamic_tcp_range", lambda: (32768, 60999))
    state = tmp_path / "state.json"
    with ports.backend_port_lease(state) as selected:
        pass
    monkeypatch.setattr(ports, "dynamic_tcp_range", lambda: (selected, selected))
    with pytest.raises(ValueError, match="dynamic"):
        with ports.backend_port_lease(state):
            pass


@pytest.mark.skipif(os.name == "nt", reason="POSIX server-side TIME_WAIT reuse semantics")
def test_server_time_wait_does_not_prevent_reacquiring_saved_port(tmp_path):
    from workbench.native_environment import loopback_port_bindable

    state = tmp_path / "state.json"
    with ports.backend_port_lease(state) as selected:
        with closing(socket.socket()) as server, closing(socket.socket()) as client:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", selected))
            server.listen()
            client.connect(server.getsockname())
            accepted, _ = server.accept()
            accepted.close()  # server active-close creates server-side TIME_WAIT
            assert client.recv(1) == b""
        assert loopback_port_bindable(selected)
    with ports.backend_port_lease(state) as restarted:
        assert restarted == selected


@pytest.mark.parametrize("system", ["Darwin", "Windows"])
def test_platform_dynamic_range_discovery(system, monkeypatch):
    monkeypatch.setattr(ports.platform, "system", lambda: system)
    output = iter(
        ["49152\n", "65535\n"]
        if system == "Darwin"
        else ["起始端口 : 49152\n端口数 : 16384\n".encode("gbk")]
    )
    monkeypatch.setattr(ports.subprocess, "check_output", lambda *a, **k: next(output))
    assert ports.dynamic_tcp_range() == (49152, 65535)


def test_unknown_or_malformed_dynamic_range_is_not_guessed(monkeypatch):
    monkeypatch.setattr(ports.platform, "system", lambda: "Unknown")
    with pytest.raises(ValueError, match="Unknown"):
        ports.dynamic_tcp_range()
    monkeypatch.setattr(ports.platform, "system", lambda: "Windows")
    monkeypatch.setattr(ports.subprocess, "check_output", lambda *a, **k: b"unavailable")
    with pytest.raises(ValueError, match="Cannot read"):
        ports.dynamic_tcp_range()


def test_port_receipt_symlink_rejected(tmp_path):
    target = tmp_path / "target.json"
    target.write_text("{}")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(ValueError, match="link"):
        with ports.backend_port_lease(link):
            pass
    assert target.read_text() == "{}"


def test_frontend_skip_build_rejects_changed_target(tmp_path):
    from workbench.native_frontend import require_frontend_backend

    dist = tmp_path / "dist"
    dist.mkdir()
    with pytest.raises(ValueError, match="receipt missing"):
        require_frontend_backend("fastapiadmin", tmp_path, "http://127.0.0.1:18080")
    (dist / "native-backend.json").write_text('{"backend_url":"http://127.0.0.1:18080"}')
    require_frontend_backend("fastapiadmin", tmp_path, "http://127.0.0.1:18080")
    with pytest.raises(ValueError, match="port changed"):
        require_frontend_backend("fastapiadmin", tmp_path, "http://127.0.0.1:18081")


def test_portable_export_includes_allocator_and_no_runtime_receipt():
    from workbench.filesystem import EXCLUDED_DIRS
    from workbench.portable import HELPERS

    assert "native_ports.py" in HELPERS
    assert ".deployment" in EXCLUDED_DIRS


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_delivered_launcher_propagates_one_port_and_skip_build_is_bound_to_copy(
    tmp_path, monkeypatch, template
):
    import importlib.util
    from contextlib import contextmanager

    from workbench.filesystem import write_json
    from workbench.native_frontend import frontend_app
    from workbench.settings import ROOT

    spec = importlib.util.spec_from_file_location(
        "delivered_run", ROOT / "templates/deployment/run.py"
    )
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    product = tmp_path / "product"
    deployment = product / "deployment"
    deployment.mkdir(parents=True)
    write_json(deployment / "manifest.json", {"template": template, "targets": [], "plan": {}})
    monkeypatch.setattr(launcher, "HERE", deployment)
    monkeypatch.setattr(launcher, "PRODUCT", product)
    monkeypatch.setattr(launcher, "verify_manifest", lambda _: None)
    service_calls = []

    def services():
        service_calls.append(True)
        return "postgresql+psycopg://native:unused@127.0.0.1:5432/test_codegen", 6379

    monkeypatch.setattr(launcher, "services", services)
    monkeypatch.setattr(launcher, "ownership", lambda *a: ("marker", True))
    monkeypatch.setattr(launcher, "install_backend", lambda *a: None)
    monkeypatch.setattr(launcher, "login", lambda *a: "token")
    import workbench.portable_checks

    monkeypatch.setattr(
        workbench.portable_checks, "check_restored_product", lambda *a: {"passed": True}
    )
    backend_ports = []

    @contextmanager
    def backend(template, root, env, reports):
        if template == "fastapiadmin":
            port = int(env["SERVER_PORT"])
        else:
            properties = (
                root / "yudao-server/src/main/resources/application-native.properties"
            ).read_text()
            port = int(
                next(
                    row.split("=", 1)[1]
                    for row in properties.splitlines()
                    if row.startswith("server.port=")
                )
            )
            assert (
                f"spring.cloud.openfeign.client.config.yudao-system.url=http://127.0.0.1:{port}"
                in properties
            )
            assert (
                f"spring.cloud.openfeign.client.config.yudao-infra.url=http://127.0.0.1:{port}"
                in properties
            )
        backend_ports.append(port)
        yield f"http://127.0.0.1:{port}", "/openapi.json"

    monkeypatch.setattr(launcher, "running_backend", backend)
    frontend_urls = []

    def build(template, root, env, reports, **kwargs):
        url = env["VITE_API_BASE_URL" if template == "fastapiadmin" else "VITE_BASE_URL"]
        frontend_urls.append(url)
        write_json(frontend_app(template, root) / "dist/native-backend.json", {"backend_url": url})

    monkeypatch.setattr(launcher, "build_frontend", build)

    @contextmanager
    def frontend(*args):
        yield "http://127.0.0.1:5173"

    monkeypatch.setattr(launcher, "frontend_preview", frontend)
    monkeypatch.setattr("sys.argv", ["run.py", "--check"])
    launcher.main()
    selected = ports.saved_backend_port(product / ".deployment/backend-port.json")
    assert backend_ports == [selected, selected]
    assert frontend_urls == [f"http://127.0.0.1:{selected}"]
    outcome = json.loads((product / ".deployment/reports/portable-start.json").read_text())
    assert outcome["backend_port"] == selected and outcome["backend_url"] == frontend_urls[0]
    monkeypatch.setattr("sys.argv", ["run.py", "--check", "--skip-build"])
    launcher.main()
    assert backend_ports == [selected] * 4 and len(service_calls) == 2
    with ports.backend_port_lease(tmp_path / "other-port.json") as changed:
        # Release the other lease first: this tests the stale bundle check,
        # rather than failing earlier on an actively held port lease.
        pass
    monkeypatch.setenv("NATIVE_DELIVERY_PORT", str(changed))
    with pytest.raises(ValueError, match="port changed"):
        launcher.main()
    assert len(service_calls) == 2
    assert ports.saved_backend_port(product / ".deployment/backend-port.json") == selected
    monkeypatch.delenv("NATIVE_DELIVERY_PORT")
    copy = tmp_path / "copy"
    (copy / ".deployment").mkdir(parents=True)
    (copy / ".deployment/backend-port.json").write_bytes(
        (product / ".deployment/backend-port.json").read_bytes()
    )
    monkeypatch.setattr(launcher, "PRODUCT", copy)
    with pytest.raises(ValueError, match="this copy"):
        launcher.main()
    assert len(service_calls) == 2


def test_pinned_vben_relative_api_proxy_uses_selected_backend(tmp_path, monkeypatch):
    # Force the legacy Windows default even when Python UTF-8 mode is enabled.
    # Explicit UTF-8 requests still use Python's original encoding resolution.
    import io
    import subprocess
    import zipfile

    from workbench.native_vben import configure_vben_backend_proxy
    from workbench.settings import ROOT

    text_encoding = io.text_encoding

    def legacy_text_encoding(encoding, stacklevel=2):
        return "cp1252" if encoding in {None, "locale"} else text_encoding(encoding, stacklevel)

    monkeypatch.setattr(io, "text_encoding", legacy_text_encoding)
    app = tmp_path / "apps/web-antd"
    app.mkdir(parents=True)
    with zipfile.ZipFile(ROOT / "templates/vendor/yudao-frontend.zip") as archive:
        original = archive.read("apps/web-antd/vite.config.ts").decode()
        hooks = archive.read("packages/effects/hooks/src/use-app-config.ts").decode()
    assert "VITE_GLOB_API_URL" in hooks
    with pytest.raises(UnicodeEncodeError):
        (tmp_path / "legacy-default.txt").write_text(original)
    config = app / "vite.config.ts"
    config.write_text(original, encoding="utf-8", newline="\n")
    configure_vben_backend_proxy(tmp_path)
    adapted = config.read_text(encoding="utf-8")
    configure_vben_backend_proxy(tmp_path)
    assert config.read_text(encoding="utf-8") == adapted
    script = adapted.replace(
        "import { defineConfig } from '@vben/vite-config';", "const defineConfig = fn => fn();"
    ).replace("export default", "const pending =")
    # Execute the exact pinned proxy configuration with only its build-tool
    # wrapper stubbed; no copied implementation of target/rewrite expressions.
    result = subprocess.run(
        [
            "node",
            "-e",
            "process.env.VITE_BASE_URL='http://127.0.0.1:18081';\n"
            + script
            + "\npending.then(c => { const p=c.vite.server.proxy['/admin-api']; console.log(JSON.stringify({target:p.target,path:p.rewrite('/admin-api/system/auth/login')})); });",
        ],
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == {
        "target": "http://127.0.0.1:18081/admin-api",
        "path": "/system/auth/login",
    }


def test_independent_process_cannot_take_a_live_copy_port_lease(tmp_path):
    import subprocess
    import sys

    state = tmp_path / "state.json"
    with ports.backend_port_lease(state) as selected:
        code = """import sys
from pathlib import Path
from workbench.native_ports import backend_port_lease
try:
    with backend_port_lease(Path(sys.argv[1])):
        raise AssertionError('same copy acquired twice')
except RuntimeError as error:
    assert 'in use' in str(error)
with backend_port_lease(Path(sys.argv[2])) as other:
    assert other != int(sys.argv[3])
print('independent-copy lease PASS')
"""
        result = subprocess.run(
            [sys.executable, "-c", code, str(state), str(tmp_path / "second.json"), str(selected)],
            text=True,
            capture_output=True,
            check=True,
            timeout=20,
        )
        assert result.stdout.strip() == "independent-copy lease PASS"


def test_unreadable_or_oversized_port_receipt_is_not_replaced(tmp_path):
    state = tmp_path / "state.json"
    for contents in ("[]", '{"format": 99}', '"' + "x" * 5000 + '"'):
        state.write_text(contents)
        with pytest.raises(ValueError):
            with ports.backend_port_lease(state):
                pass
        assert state.read_text() == contents


def test_managed_preview_requires_existing_build_port_before_source_changes(tmp_path, monkeypatch):
    import uuid
    from types import SimpleNamespace

    from workbench import native_delivery
    from workbench.filesystem import write_json
    from workbench.generator import PrerequisiteError

    run_id = str(uuid.uuid4())
    run = tmp_path / "runs" / run_id
    write_json(
        run / "native-generation.json", {"execution": "managed-runtime", "template": "fastapiadmin"}
    )
    monkeypatch.setattr(native_delivery, "managed_verify", lambda *a: None)
    monkeypatch.setattr(native_delivery, "runtime_config", lambda *a, **k: ({}, "unused"))
    monkeypatch.setattr(native_delivery, "check_database_identity", lambda *a: None)
    monkeypatch.setattr(
        native_delivery, "native_environment", lambda *a: pytest.fail("must not change source")
    )
    settings = SimpleNamespace(data_dir=tmp_path)
    with pytest.raises(PrerequisiteError, match="端口回执"):
        native_delivery.serve_managed(settings, run_id)
    with ports.backend_port_lease(run / "native-evidence/backend-port.json"):
        pass
    with pytest.raises(ValueError, match="receipt missing"):
        native_delivery.serve_managed(settings, run_id)
````
