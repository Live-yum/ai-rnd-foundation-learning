# tests/test_daytona_matrix.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_bootstrap`、`workbench.daytona_profiles`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.sandbox`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_exact_registered_profiles`（L34–L44）：接收`template`、`database`、`settings`。 控制顺序：L35断言`profile_key(template, {"database": database}) == template + "/" + database`；L38断言`snapshot_for(settings, template, {"database": database}) == "selected-local-snapshot"`；L40断言`params.network_block_all is True and params.public is False`；L41断言`params.snapshot == "selected-local-snapshot"`；L42断言`params.auto_stop_interval >= ( 5 if database == "sqlite" else settings.daytona_runtim…`。 调用`profile_key`、`snapshot_for`、`params_for`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unregistered_profiles_are_not_guessed`（L51–L55）：接收`template`、`database`。 调用`pytest.raises`、`profile_key`、`checks_for`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `report`（L58–L82）：接收`template`。 返回路径：L59的`{ key: True for key in ( "passed", "http", "restart", "fresh_database", "locked_install", …`。
- `test_every_runtime_gate_requires_actual_boolean_success`（L104–L108）：接收`key`、`bad`。 调用`report`、`pytest.raises`、`require_runtime_report`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_identity_and_no_host_database_must_match`（L122–L126）：接收`key`、`bad`。 调用`report`、`pytest.raises`、`require_runtime_report`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_accepts_complete_matching_report_only`（L129–L130）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`require_runtime_report`、`report`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dependency_identity_does_not_use_host_keys_or_cached_binaries`（L133–L141）：接收`tmp_path`。 控制顺序：L139断言`dependency_identity(tmp_path) == initial`；L141断言`dependency_identity(tmp_path) != initial`。 调用`atomic_text`、`dependency_identity`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `snapshot_metadata`（L144–L157）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L145的`{ "image": "registry:6000/rnd-yudao-vben:" + "a" * 16, "snapshot": "rnd-yudao-vben-" + "a"…`。
- `test_matrix_snapshot_is_independent_of_the_default_python_warmup`（L160–L163）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L162断言`resources == {"cpu": 2, "memory": 10, "disk": 30}`；L163断言`wait is False`。 调用`snapshot_resources`、`snapshot_metadata`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matrix_snapshot_cannot_select_cloud_or_unbounded_resources`（L177–L181）：接收`key`、`value`。 调用`snapshot_metadata`、`pytest.raises`、`snapshot_resources`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_offline_subprocess_policy_preserves_only_explicit_local_cache`（L184–L192）：接收`monkeypatch`。 控制顺序：L190断言`value["UV_OFFLINE"] == "1" and value["COREPACK_ENABLE_NETWORK"] == "0"`；L191断言`value["UV_CACHE_DIR"] == "/local/cache"`；L192断言`"API_KEY" not in value and "HTTP_PROXY" not in value`。 调用`monkeypatch.setenv`、`clean_env`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_trusted_harness_contains_only_allowlisted_source`（L195–L203）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L198断言`"harness/scripts/daytona_matrix_probe.py" in names`；L199断言`"harness/scripts/native_browser.cjs" in names`；L200断言`all(name.endswith((".py", ".cjs")) for name in names)`；L201断言`not any( ".env" in name or "node_modules" in name or "/.git/" in name for name in nam…`。 调用`zipfile.ZipFile`、`io.BytesIO`、`harness_archive`、`archive.namelist`、`all`、`name.endswith`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back`（L209–L283）：接收`settings`、`tmp_path`、`failure`。 控制顺序：L220按`failure == "report"`分支；L271按`failure`分支；L276断言`result["passed"] and result["scope"] == "independent-runtime"`；L277断言`events[-1] == "delete"`；L279断言`saved["passed"] is (failure is None)`；L280按`failure in {"session", "timeout", "command"}`分支；L281断言`events.count("session-submit") == 1`；L282断言`saved["checks"][0]["mode"] == "async-session"`。后续分支沿下方源码相同行号继续阅读。 调用`product.mkdir`、`atomic_text`、`SecretStr`、`report`、`digest`、`manifest`、`pytest.raises`、`verify_in_daytona`、`Client`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Files`（L223–L232）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Files.create_folder`（L224–L225）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Files.upload_file`（L227–L229）：接收`data`、`path`、`**kwargs`。 控制顺序：L228断言`b"local-test-token" not in data`。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Files.download_file_stream`（L231–L232）：接收`*args`、`**kwargs`。 调用`json.dumps(value).encode`、`json.dumps`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Process`（L234–L257）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Process.exec`（L235–L239）：接收`command`、`**kwargs`。 调用`events.append`、`SimpleNamespace`。 返回路径：L237的`SimpleNamespace( exit_code=1 if failure == "exec" else 0, result="explicit-protocol-fixtur…`。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Process.create_session`（L241–L242）：接收`session_id`。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Process.execute_session_command`（L244–L251）：接收`session_id`、`request`、`**kwargs`。 控制顺序：L245断言`request.run_async is True`；L247按`failure == "session"`分支；L248抛异常，停止当前正常路径；L249按`failure == "timeout"`分支；L250抛异常，停止当前正常路径。 调用`events.append`、`ConnectionError`、`TimeoutError`、`SimpleNamespace`。 返回路径：L251的`SimpleNamespace(cmd_id="command-fixture")`。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Process.get_session_command`（L253–L254）：接收`session_id`、`command_id`。 调用`SimpleNamespace`。 返回路径：L254的`SimpleNamespace(exit_code=3 if failure == "command" else 0)`。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Process.get_session_command_logs`（L256–L257）：接收`session_id`、`command_id`。 调用`SimpleNamespace`。 返回路径：L257的`SimpleNamespace(output="explicit-protocol-fixture")`。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Client`（L259–L269）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Client.create`（L260–L263）：接收`params`、`**kwargs`。 控制顺序：L261断言`params.network_block_all and params.snapshot == "registered-matrix"`。 调用`events.append`、`SimpleNamespace`、`Files`、`Process`。 返回路径：L263的`SimpleNamespace(id="owned", fs=Files(), process=Process())`。
- `test_matrix_always_deletes_its_sandbox_and_never_falls_back.Client.delete`（L265–L269）：接收`sandbox`、`**kwargs`。 控制顺序：L266断言`sandbox.id == "owned"`；L268按`failure == "cleanup"`分支；L269抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_python_runtime_descriptor_does_not_replace_matrix_database_identity`（L287–L297）：接收`database`。 控制顺序：L292断言`result["database"] == database`；L293断言`result["runtime_database"] == "real-isolated-" + database`；L294断言`result["fresh_database"] is True`；L295断言`raw["database"] == "real-isolated-" + database`。 调用`basic_runtime_evidence`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_python_runtime_descriptor_normalization_never_hides_failed_checks`（L302–L313）：接收`key`、`bad`。 调用`pytest.raises`、`basic_runtime_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_matrix_pnpm_install_is_not_shadowed_by_base_nvm_prefix`（L316–L327）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L320断言`"/usr/local/bin/node /usr/local/lib/node_modules/npm/bin/npm-cli.js install" in docke…`；L323断言`"--global --prefix /usr/local" in dockerfile`；L327断言`user < assertion < warm`。 调用`(ROOT / "tools/daytona/matrix.Dockerfile").read_text`、`dockerfile.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_matrix.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L327。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11787`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_matrix.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "785274754ff5b5a07e13b76001b4c0180afc9f4e2cef5ef22b808db12da0da89"} -->
````python
# tests/test_daytona_matrix.py
"""Fail-closed registered runtime profiles; actual services run in the matrix Action."""

import io
import json
import zipfile
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from scripts.daytona_bootstrap import snapshot_resources
from workbench.daytona_profiles import (
    dependency_identity,
    profile_key,
    require_runtime_report,
    snapshot_for,
)
from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest
from workbench.generator import PrerequisiteError
from workbench.sandbox import checks_for, harness_archive, params_for, verify_in_daytona
from workbench.tools import clean_env


@pytest.mark.parametrize(
    "template,database",
    [
        ("python-basic", "sqlite"),
        ("python-basic", "postgresql"),
        ("fastapiadmin", "postgresql"),
        ("yudao-vben", "postgresql"),
    ],
)
def test_exact_registered_profiles(template, database, settings):
    assert profile_key(template, {"database": database}) == template + "/" + database
    settings.daytona_snapshot = "fallback-local-snapshot"
    settings.daytona_snapshots = {template + "/" + database: "selected-local-snapshot"}
    assert snapshot_for(settings, template, {"database": database}) == "selected-local-snapshot"
    params = params_for(settings, "test-local", template, {"database": database})
    assert params.network_block_all is True and params.public is False
    assert params.snapshot == "selected-local-snapshot"
    assert params.auto_stop_interval >= (
        5 if database == "sqlite" else settings.daytona_runtime_timeout // 60
    )


@pytest.mark.parametrize(
    "template,database",
    [("yudao-vben", "sqlite"), ("fastapiadmin", "mysql"), ("shell", "postgresql")],
)
def test_unregistered_profiles_are_not_guessed(template, database):
    with pytest.raises(ValueError):
        profile_key(template, {"database": database})
    with pytest.raises(PrerequisiteError):
        checks_for(template, {"database": database})


def report(template="yudao-vben"):
    return {
        key: True
        for key in (
            "passed",
            "http",
            "restart",
            "fresh_database",
            "locked_install",
            "offline",
            "services_stopped",
            "frontend_build",
            "frontend_typecheck",
            "browser",
            "permissions",
            "standalone_launcher",
            "business_rules",
        )
    } | {
        "template": template,
        "database": "postgresql",
        "source_digest": "f" * 64,
        "host_database_used": False,
        "host_credentials_used": False,
    }


@pytest.mark.parametrize(
    "key",
    [
        "passed",
        "http",
        "restart",
        "fresh_database",
        "locked_install",
        "offline",
        "services_stopped",
        "frontend_build",
        "frontend_typecheck",
        "browser",
        "permissions",
        "standalone_launcher",
        "business_rules",
    ],
)
@pytest.mark.parametrize("bad", [None, False, "true", 1])
def test_every_runtime_gate_requires_actual_boolean_success(key, bad):
    value = report()
    value[key] = bad
    with pytest.raises(ValueError):
        require_runtime_report(value, "yudao-vben", {"database": "postgresql"}, "f" * 64)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("template", "fastapiadmin"),
        ("database", "sqlite"),
        ("source_digest", "wrong"),
        ("host_database_used", True),
        ("host_credentials_used", True),
        ("host_database_used", 0),
    ],
)
def test_runtime_identity_and_no_host_database_must_match(key, bad):
    value = report()
    value[key] = bad
    with pytest.raises(ValueError):
        require_runtime_report(value, "yudao-vben", {"database": "postgresql"}, "f" * 64)


def test_runtime_accepts_complete_matching_report_only():
    require_runtime_report(report(), "yudao-vben", {"database": "postgresql"}, "f" * 64)


def test_dependency_identity_does_not_use_host_keys_or_cached_binaries(tmp_path):
    atomic_text(tmp_path / "pyproject.toml", "project")
    atomic_text(tmp_path / "uv.lock", "locked")
    initial = dependency_identity(tmp_path)
    atomic_text(tmp_path / ".env", "secret")
    atomic_text(tmp_path / "target/pom.xml", "cache")
    assert dependency_identity(tmp_path) == initial
    atomic_text(tmp_path / "uv.lock", "different")
    assert dependency_identity(tmp_path) != initial


def snapshot_metadata():
    return {
        "image": "registry:6000/rnd-yudao-vben:" + "a" * 16,
        "snapshot": "rnd-yudao-vben-" + "a" * 16,
        "source_hash": "a" * 16,
        "profile": {
            "template": "yudao-vben",
            "database": "postgresql",
            "dependency_identity": "b" * 64,
        },
        "resources": {"cpu": 2, "memory": 10, "disk": 30},
        "wait_for_default": False,
        "image_id": "sha256:" + "c" * 64,
    }


def test_matrix_snapshot_is_independent_of_the_default_python_warmup():
    resources, wait = snapshot_resources(snapshot_metadata())
    assert resources == {"cpu": 2, "memory": 10, "disk": 30}
    assert wait is False


@pytest.mark.parametrize(
    "key,value",
    [
        ("image", "docker.io/remote:latest"),
        ("snapshot", "rnd-python-old"),
        ("source_hash", "unlocked"),
        ("image_id", "latest"),
        ("resources", {"cpu": 999}),
        ("wait_for_default", 0),
    ],
)
def test_matrix_snapshot_cannot_select_cloud_or_unbounded_resources(key, value):
    item = snapshot_metadata()
    item[key] = value
    with pytest.raises(ValueError):
        snapshot_resources(item)


def test_offline_subprocess_policy_preserves_only_explicit_local_cache(monkeypatch):
    monkeypatch.setenv("RND_OFFLINE_TOOLS", "1")
    monkeypatch.setenv("UV_CACHE_DIR", "/local/cache")
    monkeypatch.setenv("API_KEY", "private-model-key")
    monkeypatch.setenv("HTTP_PROXY", "https://not-allowed")
    value = clean_env()
    assert value["UV_OFFLINE"] == "1" and value["COREPACK_ENABLE_NETWORK"] == "0"
    assert value["UV_CACHE_DIR"] == "/local/cache"
    assert "API_KEY" not in value and "HTTP_PROXY" not in value


def test_trusted_harness_contains_only_allowlisted_source():
    with zipfile.ZipFile(io.BytesIO(harness_archive())) as archive:
        names = archive.namelist()
        assert "harness/scripts/daytona_matrix_probe.py" in names
        assert "harness/scripts/native_browser.cjs" in names
        assert all(name.endswith((".py", ".cjs")) for name in names)
        assert not any(
            ".env" in name or "node_modules" in name or "/.git/" in name for name in names
        )


@pytest.mark.parametrize(
    "failure", [None, "exec", "report", "cleanup", "session", "timeout", "command"]
)
def test_matrix_always_deletes_its_sandbox_and_never_falls_back(settings, tmp_path, failure):
    product = tmp_path / "product"
    product.mkdir()
    atomic_text(product / "pyproject.toml", "project")
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_local_execution = True
    settings.daytona_api_key = SecretStr("local-test-token")
    settings.daytona_snapshot = "registered-matrix"
    events = []
    value = report("fastapiadmin")
    value["source_digest"] = digest(manifest(product))
    if failure == "report":
        value["browser"] = False

    class Files:
        def create_folder(self, *args):
            pass

        def upload_file(self, data, path, **kwargs):
            assert b"local-test-token" not in data
            events.append("upload")

        def download_file_stream(self, *args, **kwargs):
            yield json.dumps(value).encode()

    class Process:
        def exec(self, command, **kwargs):
            events.append(command)
            return SimpleNamespace(
                exit_code=1 if failure == "exec" else 0, result="explicit-protocol-fixture"
            )

        def create_session(self, session_id):
            events.append("session-create")

        def execute_session_command(self, session_id, request, **kwargs):
            assert request.run_async is True
            events.append("session-submit")
            if failure == "session":
                raise ConnectionError("lost submission response")
            if failure == "timeout":
                raise TimeoutError("session deadline")
            return SimpleNamespace(cmd_id="command-fixture")

        def get_session_command(self, session_id, command_id):
            return SimpleNamespace(exit_code=3 if failure == "command" else 0)

        def get_session_command_logs(self, session_id, command_id):
            return SimpleNamespace(output="explicit-protocol-fixture")

    class Client:
        def create(self, params, **kwargs):
            assert params.network_block_all and params.snapshot == "registered-matrix"
            events.append("create")
            return SimpleNamespace(id="owned", fs=Files(), process=Process())

        def delete(self, sandbox, **kwargs):
            assert sandbox.id == "owned"
            events.append("delete")
            if failure == "cleanup":
                raise RuntimeError("explicit fixture cleanup failure")

    if failure:
        with pytest.raises(PrerequisiteError):
            verify_in_daytona(product, "fastapiadmin", settings, client=Client())
    else:
        result = verify_in_daytona(product, "fastapiadmin", settings, client=Client())
        assert result["passed"] and result["scope"] == "independent-runtime"
    assert events[-1] == "delete"
    saved = json.loads((tmp_path / "daytona-verification.json").read_text(encoding="utf-8"))
    assert saved["passed"] is (failure is None)
    if failure in {"session", "timeout", "command"}:
        assert events.count("session-submit") == 1
        assert saved["checks"][0]["mode"] == "async-session"
        assert saved["checks"][0]["session_id"].startswith("rnd-check-")


@pytest.mark.parametrize("database", ["sqlite", "postgresql"])
def test_python_runtime_descriptor_does_not_replace_matrix_database_identity(database):
    from scripts.daytona_matrix_probe import basic_runtime_evidence

    raw = {"passed": True, "http": True, "restart": True, "database": "real-isolated-" + database}
    result = basic_runtime_evidence(raw, database)
    assert result["database"] == database
    assert result["runtime_database"] == "real-isolated-" + database
    assert result["fresh_database"] is True
    assert raw["database"] == "real-isolated-" + database
    with pytest.raises(ValueError, match="does not match"):
        basic_runtime_evidence({**raw, "database": "real-isolated-mysql"}, database)


@pytest.mark.parametrize("key", ["passed", "http", "restart"])
@pytest.mark.parametrize("bad", [False, "true", 1, None])
def test_python_runtime_descriptor_normalization_never_hides_failed_checks(key, bad):
    from scripts.daytona_matrix_probe import basic_runtime_evidence

    raw = {
        "passed": True,
        "http": True,
        "restart": True,
        "database": "real-isolated-postgresql",
        key: bad,
    }
    with pytest.raises(ValueError):
        basic_runtime_evidence(raw, "postgresql")


def test_matrix_pnpm_install_is_not_shadowed_by_base_nvm_prefix():
    from workbench.settings import ROOT

    dockerfile = (ROOT / "tools/daytona/matrix.Dockerfile").read_text(encoding="utf-8")
    assert (
        "/usr/local/bin/node /usr/local/lib/node_modules/npm/bin/npm-cli.js install" in dockerfile
    )
    assert "--global --prefix /usr/local" in dockerfile
    user = dockerfile.index("USER daytona")
    warm = dockerfile.index(".venv/bin/python /opt/rnd/warm.py")
    assertion = dockerfile.index('test "$(pnpm --version)" = "${PNPM_VERSION}"')
    assert user < assertion < warm
````
