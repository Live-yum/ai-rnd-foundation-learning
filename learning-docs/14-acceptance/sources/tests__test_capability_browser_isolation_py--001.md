# tests/test_capability_browser_isolation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_browser_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `frame`（L20–L29）：接收`**updates`。 返回路径：L21的`{ "type": "request", "id": 1, "method": "GET", "path": "/hello", "headers": {}, "body": ""…`。
- `test_worker_has_no_host_escape_surface`（L32–L50）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L34遍历`( "--network=none", "--read-only", "--cap-drop=ALL", "--memory=76…`；L45断言`required in args`；L46断言`not any( arg.startswith(("--mount", "--volume", "--privileged", "--publish")) for arg…`。 调用`worker_command`、`any`、`arg.startswith`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_image_default_off`（L53–L58）：接收`monkeypatch`。 控制顺序：L58断言`browser_image_identity() == IMAGE`。 调用`monkeypatch.delenv`、`pytest.raises`、`browser_image_identity`、`monkeypatch.setenv`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepared_official_seccomp_profile_is_pinned_but_never_silently_selected`（L61–L85）：接收`monkeypatch`。 控制顺序：L69断言`hashlib.sha256(raw).hexdigest() == "cc3e61cabda6bbc1e53e54d27ba4d55a9d3be829b6dd1a596…`；L74断言`profile["defaultAction"] == "SCMP_ACT_ERRNO"`；L75断言`profile["syscalls"][0] == { "comment": "Allow create user namespaces", "names": ["clo…`；L83断言`source in isolation.BROWSER_SOURCES and source in isolation.IMAGE_SOURCES`；L85断言`not any(arg.startswith("--security-opt=seccomp=") for arg in worker_command(IMAGE, NA…`。 调用`(isolation.ROOT / source).read_bytes`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`json.loads`、`monkeypatch.setenv`、`str`、`any`、`arg.startswith`、`worker_command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_origin_escape_denied`（L89–L95）：接收`path`。 调用`httpx.Client`、`httpx.MockTransport`、`pytest.fail`、`pytest.raises`、`relay_request`、`frame`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_request_never_forwarded`（L111–L117）：接收`updates`。 调用`httpx.Client`、`httpx.MockTransport`、`pytest.fail`、`pytest.raises`、`relay_request`、`frame`、`pytest.mark.parametrize`、`base64.b64encode(b"x" * (MAX_BODY + 1)).decode`、`base64.b64encode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preview_token_stays_controller_owned`（L120–L141）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L137断言`str(seen[0].url) == "http://127.0.0.1:4567/hello"`；L138断言`seen[0].headers["x-daytona-preview-token"] == "private"`；L139断言`seen[0].headers["accept-encoding"] == "identity"`；L140断言`"private" not in str(result) and "hidden" not in str(result)`；L141断言`base64.b64decode(result["body"]) == b"hello" and size == 5`。 调用`httpx.Client`、`httpx.MockTransport`、`relay_request`、`frame`、`str`、`base64.b64decode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preview_token_stays_controller_owned.respond`（L123–L129）：接收`request`。 调用`seen.append`、`httpx.Response`、`httpx.ByteStream`。 返回路径：L125的`httpx.Response( 200, stream=httpx.ByteStream(b"hello"), headers={"content-type": "text/pla…`。
- `test_response_budgets_and_redirects`（L152–L157）：接收`response`。 调用`httpx.Client`、`httpx.MockTransport`、`pytest.raises`、`relay_request`、`frame`、`pytest.mark.parametrize`、`httpx.Response`、`httpx.ByteStream`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inspection_never_accepts_missing_or_privileged_profile`（L160–L163）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L161遍历`(None, [], [{}], [{"Image": IMAGE, "HostConfig": {"Privileged": T…`。 调用`pytest.raises`、`require_worker_inspection`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failures_always_remove_owned_container`（L169–L211）：接收`monkeypatch`、`mode`。 控制顺序：L199按`mode != "bad-inspection"`分支；L210断言`any("rm" in args and "-f" in args for args in calls)`；L211断言`all("secret-test-preview-token" not in str(args) for args in calls)`。 调用`monkeypatch.setattr`、`pytest.raises`、`isolation.execute_worker`、`any`、`all`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failures_always_remove_owned_container.fake_run`（L180–L186）：接收`args`、`**kwargs`。 控制顺序：L182按`"inspect" in args`分支；L184按`"rm" in args and mode == "cleanup-fails"`分支。 调用`calls.append`、`SimpleNamespace`、`json.dumps([{}]).encode`、`json.dumps`。 返回路径：L183的`SimpleNamespace(returncode=0, stdout=json.dumps([{}]).encode())`；L185的`SimpleNamespace(returncode=1, stdout=b"")`；L186的`SimpleNamespace(returncode=0, stdout=b"owned")`。
- `test_failures_always_remove_owned_container.fake_popen`（L188–L195）：接收`args`、`**kwargs`。 调用`real_popen`。 返回路径：L195的`real_popen([sys.executable, "-c", script], **kwargs)`。
- `test_live_receipt_binds_image_sources_and_all_real_checks`（L214–L260）：接收`monkeypatch`、`tmp_path`。 控制顺序：L248断言`isolation.require_browser_acceptance() == IMAGE`；L249遍历`( ("mocked", True), ("image", "sha256:" + "c" * 64), ("sources", …`。 调用`monkeypatch.setattr`、`monkeypatch.setenv`、`isolation.browser_source_identity`、`isolation.image_source_identity`、`path.write_text`、`json.dumps`、`isolation.require_browser_acceptance`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_context_cookies_cannot_leak_from_relay_jar`（L263–L277）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L277断言`seen == ["sid=explicit", None]`。 调用`httpx.Client`、`httpx.MockTransport`、`relay_request`、`frame`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_context_cookies_cannot_leak_from_relay_jar.respond`（L266–L270）：接收`request`。 调用`seen.append`、`request.headers.get`、`httpx.Response`、`httpx.ByteStream`。 返回路径：L268的`httpx.Response( 200, stream=httpx.ByteStream(b"ok"), headers={"set-cookie": "sid=old; Path…`。
- `test_json_size_is_proved_before_encoding`（L295–L303）：接收`value`。 控制顺序：L301断言`bounded_json(value, len(expected)) == expected`。 调用`json.dumps(value, ensure_ascii=True, allow_nan=False, separators=…`、`json.dumps`、`bounded_json`、`len`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oversize_json_is_not_serialized_and_creates_no_worker`（L306–L322）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`isolation.execute_worker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_capture_expansion_is_rejected_before_worker_or_large_string_allocation`（L325–L353）：接收`monkeypatch`。 控制顺序：L353断言`result["value"] == "123"`。 调用`monkeypatch.setattr`、`pytest.fail`、`SimpleNamespace`、`BrowserStep`、`range`、`pytest.raises`、`isolation.run_isolated_browser`、`isolation.bounded_browser_step`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cumulative_contract_budget_covers_many_individually_valid_steps`（L356–L370）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`BrowserStep`、`range`、`pytest.raises`、`isolation.browser_contract`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `tar_source`（L373–L387）：接收`name`、`body`、`link`、`duplicate`。 控制顺序：L381按`link`分支；L385按`duplicate`分支。 调用`io.BytesIO`、`tarfile.open`、`tarfile.TarInfo`、`len`、`archive.addfile`、`output.getvalue`。 返回路径：L387的`output.getvalue()`。
- `test_image_provenance_rejects_wrong_or_unbounded_tar_members`（L391–L405）：接收`mode`。 控制顺序：L402按`mode == "compressed"`分支。 调用`tar_source`、`gzip.compress`、`pytest.raises`、`isolation.image_archive_digest`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_image_files_must_match_current_sources_and_stale_image_cannot_start`（L408–L454）：接收`monkeypatch`。 控制顺序：L424断言`isolation.require_image_sources(NAME) == isolation.image_source_identity()`；L425断言`isolation.image_archive_digest(tar_source("x", b"hello"), "x") == hashlib.sha256(b"he…`；L454断言`any("rm" in args and "-f" in args for args in calls)`。 调用`monkeypatch.setattr`、`isolation.require_image_sources`、`isolation.image_source_identity`、`isolation.image_archive_digest`、`tar_source`、`hashlib.sha256(b"hello").hexdigest`、`hashlib.sha256`、`pytest.fail`、`path.rsplit`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_image_files_must_match_current_sources_and_stale_image_cannot_start.current`（L415–L421）：接收`name`、`path`。 控制顺序：L416断言`name == NAME`。 调用`next`、`isolation.IMAGE_SOURCES.items`、`(isolation.ROOT / source).read_bytes`、`tar_source`、`path.rsplit`。 返回路径：L421的`tar_source(path.rsplit("/", 1)[1], body)`。
- `test_actual_image_files_must_match_current_sources_and_stale_image_cannot_start.fake_run`（L432–L434）：接收`args`、`**kwargs`。 调用`calls.append`、`SimpleNamespace`、`json.dumps([{}]).encode`、`json.dumps`。 返回路径：L434的`SimpleNamespace(returncode=0, stdout=json.dumps([{}]).encode())`。
- `test_provenance_pipe_is_bounded_without_buffering_an_entire_archive`（L457–L479）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`isolation._image_file_archive`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_provenance_pipe_is_bounded_without_buffering_an_entire_archive.fake_popen`（L465–L475）：接收`args`、`**kwargs`。 调用`real_popen`。 返回路径：L466的`real_popen( [ sys.executable, "-I", "-S", "-c", "import sys;sys.stdout.buffer.write(b'x'*6…`。
- `test_live_probe_rejects_refusal_timeout_and_dac_errors_without_network_calls`（L482–L529）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L489按`node is None`分支；L528断言`result.returncode == 0`；L529断言`result.stdout == "specific-probe-errors-passed"`。 调用`shutil.which`、`pytest.skip`、`subprocess.run`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_isolation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L529。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18273`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_isolation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "94dd3ce39bc9e4833ad048b6217d6ee26350aad3d0849edcaf97f4a8ce819d06"} -->
````python
# tests/test_capability_browser_isolation.py
"""Policy and protocol tests; these do not certify actual Docker confinement."""

import base64

import httpx
import pytest

from workbench.capability_browser_isolation import (
    MAX_BODY,
    browser_image_identity,
    relay_request,
    require_worker_inspection,
    worker_command,
)

IMAGE = "sha256:" + "a" * 64
NAME = "rnd-browser-" + "b" * 32


def frame(**updates):
    return {
        "type": "request",
        "id": 1,
        "method": "GET",
        "path": "/hello",
        "headers": {},
        "body": "",
        **updates,
    }


def test_worker_has_no_host_escape_surface():
    args = worker_command(IMAGE, NAME)
    for required in (
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--memory=768m",
        "--memory-swap=768m",
        "--pids-limit=128",
        "--user=1000:1000",
        "--security-opt=no-new-privileges:true",
        "--pull=never",
    ):
        assert required in args
    assert not any(
        arg.startswith(("--mount", "--volume", "--privileged", "--publish")) for arg in args
    )
    with pytest.raises(ValueError):
        worker_command("mutable:latest", NAME)


def test_image_default_off(monkeypatch):
    monkeypatch.delenv("CAPABILITY_BROWSER_IMAGE", raising=False)
    with pytest.raises(ValueError):
        browser_image_identity()
    monkeypatch.setenv("CAPABILITY_BROWSER_IMAGE", IMAGE)
    assert browser_image_identity() == IMAGE


def test_prepared_official_seccomp_profile_is_pinned_but_never_silently_selected(monkeypatch):
    import hashlib
    import json

    from workbench import capability_browser_isolation as isolation

    source = "tools/browser/seccomp.playwright-1.56.1.json"
    raw = (isolation.ROOT / source).read_bytes()
    assert (
        hashlib.sha256(raw).hexdigest()
        == "cc3e61cabda6bbc1e53e54d27ba4d55a9d3be829b6dd1a596f4a7b31b1cc7849"
    )
    profile = json.loads(raw)
    assert profile["defaultAction"] == "SCMP_ACT_ERRNO"
    assert profile["syscalls"][0] == {
        "comment": "Allow create user namespaces",
        "names": ["clone", "setns", "unshare"],
        "action": "SCMP_ACT_ALLOW",
        "args": [],
        "includes": {},
        "excludes": {},
    }
    assert source in isolation.BROWSER_SOURCES and source in isolation.IMAGE_SOURCES
    monkeypatch.setenv("CAPABILITY_BROWSER_SECCOMP_PROFILE", str(isolation.ROOT / source))
    assert not any(arg.startswith("--security-opt=seccomp=") for arg in worker_command(IMAGE, NAME))


@pytest.mark.parametrize("path", ["https://evil/", "//evil/", "/\\evil/", "/x\r\ny", "/x#fragment"])
def test_origin_escape_denied(path):
    with httpx.Client(
        base_url="http://127.0.0.1",
        transport=httpx.MockTransport(lambda r: pytest.fail("network reached")),
    ) as client:
        with pytest.raises(ValueError):
            relay_request(client, frame(path=path))


@pytest.mark.parametrize(
    "updates",
    [
        {"method": "CONNECT"},
        {"headers": {"host": "evil"}},
        {"headers": {"x-daytona-preview-token": "evil"}},
        {"headers": {"accept": "a\r\nb"}},
        {"body": "!"},
        {"body": base64.b64encode(b"x" * (MAX_BODY + 1)).decode()},
        {"id": True},
        {"id": 257},
    ],
)
def test_invalid_request_never_forwarded(updates):
    with httpx.Client(
        base_url="http://127.0.0.1",
        transport=httpx.MockTransport(lambda r: pytest.fail("network reached")),
    ) as client:
        with pytest.raises(ValueError):
            relay_request(client, frame(**updates))


def test_preview_token_stays_controller_owned():
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(
            200,
            stream=httpx.ByteStream(b"hello"),
            headers={"content-type": "text/plain", "x-secret": "hidden"},
        )

    with httpx.Client(
        base_url="http://127.0.0.1:4567",
        headers={"x-daytona-preview-token": "private"},
        transport=httpx.MockTransport(respond),
    ) as client:
        result, size = relay_request(client, frame())
    assert str(seen[0].url) == "http://127.0.0.1:4567/hello"
    assert seen[0].headers["x-daytona-preview-token"] == "private"
    assert seen[0].headers["accept-encoding"] == "identity"
    assert "private" not in str(result) and "hidden" not in str(result)
    assert base64.b64decode(result["body"]) == b"hello" and size == 5


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(302, stream=httpx.ByteStream(b""), headers={"location": "http://evil"}),
        httpx.Response(200, headers={"content-encoding": "gzip"}),
        httpx.Response(200, stream=httpx.ByteStream(b"x" * (MAX_BODY + 1))),
    ],
)
def test_response_budgets_and_redirects(response):
    with httpx.Client(
        base_url="http://127.0.0.1", transport=httpx.MockTransport(lambda r: response)
    ) as client:
        with pytest.raises(ValueError):
            relay_request(client, frame())


def test_inspection_never_accepts_missing_or_privileged_profile():
    for value in (None, [], [{}], [{"Image": IMAGE, "HostConfig": {"Privileged": True}}]):
        with pytest.raises(ValueError):
            require_worker_inspection(value, IMAGE)


@pytest.mark.parametrize(
    "mode", ["invalid-json", "timeout", "oversized", "bad-inspection", "cleanup-fails"]
)
def test_failures_always_remove_owned_container(monkeypatch, mode):
    import json
    import subprocess
    import sys
    from types import SimpleNamespace

    from workbench import capability_browser_isolation as isolation

    real_popen = subprocess.Popen
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if "inspect" in args:
            return SimpleNamespace(returncode=0, stdout=json.dumps([{}]).encode())
        if "rm" in args and mode == "cleanup-fails":
            return SimpleNamespace(returncode=1, stdout=b"")
        return SimpleNamespace(returncode=0, stdout=b"owned")

    def fake_popen(args, **kwargs):
        script = {
            "invalid-json": "import sys;sys.stdin.readline();print('invalid-json',flush=True)",
            "oversized": "import sys;sys.stdin.readline();sys.stdout.write('x'*7000000);sys.stdout.flush()",
            "timeout": "import sys,time;sys.stdin.readline();time.sleep(10)",
            "cleanup-fails": "import sys;sys.stdin.readline();print('invalid-json',flush=True)",
        }[mode]
        return real_popen([sys.executable, "-c", script], **kwargs)

    monkeypatch.setattr(isolation.subprocess, "run", fake_run)
    monkeypatch.setattr(isolation.subprocess, "Popen", fake_popen)
    if mode != "bad-inspection":
        monkeypatch.setattr(isolation, "require_worker_inspection", lambda *args: {})
        monkeypatch.setattr(isolation, "require_image_sources", lambda *args: {})
    with pytest.raises((ValueError, RuntimeError, TimeoutError)):
        isolation.execute_worker(
            {"request_id": "a" * 32, "scenarios": []},
            "http://127.0.0.1:3456",
            "secret-test-preview-token",
            1,
            image=IMAGE,
        )
    assert any("rm" in args and "-f" in args for args in calls)
    assert all("secret-test-preview-token" not in str(args) for args in calls)


def test_live_receipt_binds_image_sources_and_all_real_checks(monkeypatch, tmp_path):
    import json

    from workbench import capability_browser_isolation as isolation

    path = tmp_path / "acceptance.json"
    monkeypatch.setattr(isolation, "BROWSER_ACCEPTANCE", path)
    monkeypatch.setenv("CAPABILITY_BROWSER_IMAGE", IMAGE)
    valid = {
        "protocol": "offline-browser-isolation-v3",
        "runtime": {"policy_sha256": None, "mode": "docker-default"},
        "passed": True,
        "image": IMAGE,
        "mocked": False,
        "sources": isolation.browser_source_identity(),
        "image_sources": isolation.image_source_identity(),
        "checks": {
            "kernel_and_network": {
                "passed": True,
                "kernel_resource_limits": True,
                "network_none": True,
                "tmpfs_exhaustion": True,
                "pid_exhaustion": True,
                "readonly_root": True,
                "browser_build": True,
            },
            "positive": True,
            "error": True,
            "abuse": True,
            "failure_cleanup": True,
            "memory_exhaustion": True,
        },
    }
    path.write_text(json.dumps(valid))
    assert isolation.require_browser_acceptance() == IMAGE
    for key, replacement in (
        ("mocked", True),
        ("image", "sha256:" + "c" * 64),
        ("sources", {}),
        ("image_sources", {}),
        ("protocol", "offline-browser-isolation-v1"),
        ("checks", {}),
        ("passed", 1),
    ):
        path.write_text(json.dumps({**valid, key: replacement}))
        with pytest.raises(ValueError):
            isolation.require_browser_acceptance()


def test_browser_context_cookies_cannot_leak_from_relay_jar():
    seen = []

    def respond(request):
        seen.append(request.headers.get("cookie"))
        return httpx.Response(
            200, stream=httpx.ByteStream(b"ok"), headers={"set-cookie": "sid=old; Path=/"}
        )

    with httpx.Client(
        base_url="http://127.0.0.1", transport=httpx.MockTransport(respond)
    ) as client:
        relay_request(client, frame(headers={"cookie": "sid=explicit"}))
        relay_request(client, frame())
    assert seen == ["sid=explicit", None]


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        False,
        123,
        -123,
        1.25,
        [],
        {},
        '"\\\b\f\n\r\t\x00\x1f\x7f汉🙂',
        {"k": ["abc", 2]},
    ],
)
def test_json_size_is_proved_before_encoding(value):
    import json

    from workbench.capability_browser_isolation import bounded_json

    expected = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode()
    assert bounded_json(value, len(expected)) == expected
    with pytest.raises(ValueError):
        bounded_json(value, len(expected) - 1)


def test_oversize_json_is_not_serialized_and_creates_no_worker(monkeypatch):
    from workbench import capability_browser_isolation as isolation

    monkeypatch.setattr(
        isolation.json, "dumps", lambda *a, **k: pytest.fail("encoded before bound")
    )
    monkeypatch.setattr(
        isolation.subprocess, "run", lambda *a, **k: pytest.fail("created before bound")
    )
    with pytest.raises(ValueError, match="budget"):
        isolation.execute_worker(
            {"capture": "x" * (isolation.MAX_CONTRACT + 1)},
            "http://127.0.0.1:3456",
            "not-transmitted",
            1,
            image=IMAGE,
        )


def test_capture_expansion_is_rejected_before_worker_or_large_string_allocation(monkeypatch):
    from types import SimpleNamespace

    from workbench import capability_browser_isolation as isolation
    from workbench.capability_contracts import BrowserStep
    from workbench.capability_verification import BrowserFailure

    monkeypatch.setattr(isolation.shutil, "which", lambda name: "/trusted/docker")
    monkeypatch.setattr(isolation, "execute_worker", lambda *a, **k: pytest.fail("worker started"))
    scenario = SimpleNamespace(
        id="sample",
        browser=[BrowserStep(action="fill", selector="#x", value="${captured}") for _ in range(4)],
    )
    with pytest.raises(BrowserFailure):
        isolation.run_isolated_browser(
            "http://127.0.0.1:3456",
            "not-transmitted",
            [scenario],
            {"sample": {"captured": "A" * 400000}},
            1,
            image=IMAGE,
        )
    small = BrowserStep(action="fill", selector="#x", value="${v}" * 2000)
    with pytest.raises(ValueError, match="substitution"):
        isolation.bounded_browser_step(small, {"v": "x" * 10})
    result = isolation.bounded_browser_step(
        BrowserStep(action="fill", selector="#x", value="${id}"), {"id": 123}
    )
    assert result["value"] == "123"


def test_cumulative_contract_budget_covers_many_individually_valid_steps():
    from types import SimpleNamespace

    from workbench import capability_browser_isolation as isolation
    from workbench.capability_contracts import BrowserStep

    selected = [
        SimpleNamespace(
            id=f"s{i}",
            browser=[BrowserStep(action="fill", selector="#x", value="${v}") for _ in range(60)],
        )
        for i in range(3)
    ]
    with pytest.raises(ValueError, match="contract budget"):
        isolation.browser_contract("a" * 32, selected, {s.id: {"v": "A" * 8000} for s in selected})


def tar_source(name, body, *, link=False, duplicate=False):
    import io
    import tarfile

    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        member = tarfile.TarInfo(name)
        member.size = len(body)
        if link:
            member.type = tarfile.SYMTYPE
            member.linkname = "/elsewhere"
        archive.addfile(member, io.BytesIO(body))
        if duplicate:
            archive.addfile(member, io.BytesIO(body))
    return output.getvalue()


@pytest.mark.parametrize("mode", ["name", "symlink", "duplicate", "size", "compressed"])
def test_image_provenance_rejects_wrong_or_unbounded_tar_members(mode):
    import gzip

    from workbench import capability_browser_isolation as isolation

    raw = tar_source(
        "wrong" if mode == "name" else "worker.cjs",
        b"x" * (isolation.MAX_IMAGE_FILE + 1) if mode == "size" else b"source",
        link=mode == "symlink",
        duplicate=mode == "duplicate",
    )
    if mode == "compressed":
        raw = gzip.compress(raw)
    with pytest.raises((ValueError, isolation.tarfile.TarError)):
        isolation.image_archive_digest(raw, "worker.cjs")


def test_actual_image_files_must_match_current_sources_and_stale_image_cannot_start(monkeypatch):
    import hashlib
    import json
    from types import SimpleNamespace

    from workbench import capability_browser_isolation as isolation

    def current(name, path):
        assert name == NAME
        source = next(
            source for source, destination in isolation.IMAGE_SOURCES.items() if destination == path
        )
        body = (isolation.ROOT / source).read_bytes()
        return tar_source(path.rsplit("/", 1)[1], body)

    monkeypatch.setattr(isolation, "_image_file_archive", current)
    assert isolation.require_image_sources(NAME) == isolation.image_source_identity()
    assert (
        isolation.image_archive_digest(tar_source("x", b"hello"), "x")
        == hashlib.sha256(b"hello").hexdigest()
    )

    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout=json.dumps([{}]).encode())

    monkeypatch.setattr(isolation.subprocess, "run", fake_run)
    monkeypatch.setattr(
        isolation.subprocess, "Popen", lambda *a, **k: pytest.fail("stale worker started")
    )
    monkeypatch.setattr(isolation, "require_worker_inspection", lambda *a: {})
    monkeypatch.setattr(
        isolation,
        "_image_file_archive",
        lambda name, path: tar_source(path.rsplit("/", 1)[1], b"stale image source"),
    )
    with pytest.raises(ValueError, match="stale"):
        isolation.execute_worker(
            {"request_id": "a" * 32, "scenarios": []},
            "http://127.0.0.1:3456",
            "not-transmitted",
            1,
            image=IMAGE,
        )
    assert any("rm" in args and "-f" in args for args in calls)


def test_provenance_pipe_is_bounded_without_buffering_an_entire_archive(monkeypatch):
    import subprocess
    import sys

    from workbench import capability_browser_isolation as isolation

    real_popen = subprocess.Popen

    def fake_popen(args, **kwargs):
        return real_popen(
            [
                sys.executable,
                "-I",
                "-S",
                "-c",
                "import sys;sys.stdout.buffer.write(b'x'*600000);sys.stdout.flush()",
            ],
            **kwargs,
        )

    monkeypatch.setattr(isolation.subprocess, "Popen", fake_popen)
    with pytest.raises(ValueError, match="too large"):
        isolation._image_file_archive(NAME, "/opt/verifier/worker.cjs")


def test_live_probe_rejects_refusal_timeout_and_dac_errors_without_network_calls():
    import shutil
    import subprocess

    from workbench.settings import ROOT

    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required by mandatory browser CI")
    script = r"""
const assert = require('node:assert/strict')
const {EventEmitter} = require('node:events')
const {requireNoRoute, requireReadOnly} = require(process.argv[1])
function connector(event, code) {
 return () => {
  const socket = new EventEmitter()
  socket.setTimeout = () => {}
  socket.destroy = () => {}
  queueMicrotask(() => socket.emit(event, {code}))
  return socket
 }
}
async function main() {
 await requireNoRoute('never-resolved.invalid', 1, connector('error','ENETUNREACH'))
 for (const code of ['ECONNREFUSED','EACCES','ENOTFOUND','ETIMEDOUT']) {
  await assert.rejects(requireNoRoute('never-resolved.invalid', 1, connector('error',code)))
 }
 await assert.rejects(requireNoRoute('never-resolved.invalid', 1, connector('timeout')))
 await assert.rejects(requireNoRoute('never-resolved.invalid', 1, connector('connect')))
 function fakeFs(code) { return {
  lstatSync: () => ({uid:1000,mode:0o40700,isDirectory:()=>true}),
  writeFileSync: () => {if(code)throw Object.assign(new Error('synthetic'),{code})}
 } }
 requireReadOnly(fakeFs('EROFS'),1000)
 assert.throws(() => requireReadOnly(fakeFs('EACCES'),1000))
 assert.throws(() => requireReadOnly(fakeFs(null),1000))
 process.stdout.write('specific-probe-errors-passed')
}
main().catch(error => {console.error(error);process.exitCode=1})
"""
    result = subprocess.run(
        [node, "-e", script, str(ROOT / "scripts/capability_browser_network_probe.cjs")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "specific-probe-errors-passed"
````
