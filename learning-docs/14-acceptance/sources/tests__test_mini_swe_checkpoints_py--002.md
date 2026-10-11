# tests/test_mini_swe_checkpoints.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_mini_swe_checkpoints_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.sla_fixture`、`workbench.coding`、`workbench.coding.ports`、`workbench.core.contracts`、`workbench.errors`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_file_cleanup_tracks_expected_candidate_even_after_partial_upload.run`（L896–L908）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L907按`fail_write`分支；L908抛异常，停止当前正常路径。 调用`coding._local_environment`、`plan.selection.model_dump`、`time.monotonic`、`environment.bind_candidate`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_parent_kills_child_and_freezes_early_success`（L918–L968）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L965断言`children[0].poll() is not None`；L967断言`value["passed"] is False and value["cleanup"] == "unconfirmed"`；L968断言`value["checkpoint"] == checkpoint and "repairable_failure" not in value`。 调用`fixed_application`、`monkeypatch.setattr`、`digest`、`plan.tasks[0].model_dump`、`time.monotonic`、`pytest.raises`、`verifier.verify_capabilities`、`plan.selection.model_dump`、`children[0].poll`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_parent_kills_child_and_freezes_early_success.launch`（L944–L947）：接收`command`、`**kwargs`。 调用`original`、`children.append`。 返回路径：L947的`process`。
- `test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline`（L972–L987）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L987断言`10 <= elapsed < 11.5`。 调用`time.monotonic`、`CheckpointDeadline`、`controller.enter_cleanup`、`pytest.raises`、`cleanup_call`、`pytest.mark.skipif`、`hasattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline.cleanup_call`（L978–L979）：接收`timeout`。 调用`time.sleep`、`with_timeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preview_gateway_errors_cannot_authorize_business_repair`（L991–L1005）：接收`status`。 控制顺序：L1005断言`not isinstance(error.value, BusinessCheckFailure)`。 调用`httpx.Client`、`httpx.MockTransport`、`httpx.Response`、`httpx.ByteStream`、`pytest.raises`、`run_steps`、`HttpStep`、`isinstance`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entire_file_sdk_lifecycle_is_supervised`（L1009–L1133）：接收`settings`、`tmp_path`、`monkeypatch`、`phase`。 源码说明：Event-blocked real SDK refresh/API transport in a real child, no external network.。 控制顺序：L1101按`phase == "success"`分支；L1102断言`environment.snapshot(task.allowed_paths) == { p: "" for p in task.allowed_paths }`；L1105按`phase == "write"`分支；L1113按`phase == "snapshot"`分支；L1115按`phase == "idle"`分支；L1116断言`environment.done.wait(12)`；L1118断言`time.monotonic() - start < 14`；L1119断言`len(cleaned) == 1 and cleaned[0][1] < start + 25`。后续分支沿下方源码相同行号继续阅读。 调用`cleanup_binding`、`monkeypatch.setattr`、`time.monotonic`、`nullcontext`、`pytest.raises`、`coding_environment`、`plan.selection.model_dump`、`environment.snapshot`、`environment.bind_candidate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entire_file_sdk_lifecycle_is_supervised.launch`（L1065–L1070）：接收`command`、`**kwargs`。 调用`(tmp_path / "child-errors").open`、`original`、`str`、`children.append`。 返回路径：L1070的`process`。
- `test_entire_file_sdk_lifecycle_is_supervised.cleanup`（L1075–L1084）：接收`settings`、`name`、`identifier`、`bound`、`path`、`deadline`。 控制顺序：L1080按`identifier is not None`分支；L1083按`identifier is None`分支；L1084抛异常，停止当前正常路径。 调用`cleaned.append`、`time.monotonic`、`dict`、`file_session.receipt`、`value.update`、`write_json`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_file_entrypoint_rechecks_forwarded_scope`（L1137–L1262）：接收`settings`、`tmp_path`、`monkeypatch`、`mutation`。 源码说明：Real Session/main/local-environment/browser gate; stop before SDK/network use.。 控制顺序：L1152遍历`("API_KEY", "GITHUB_TOKEN", "HTTP_PROXY", "HTTPS_PROXY")`；L1256断言`len(children) == 1 and children[0].poll() is not None`；L1257断言`marker.exists() is (mutation is None)`；L1259断言`value["failure_phase"] == ("client" if mutation is None else "admission")`；L1260断言`value["failure_kind"] in {"UnsupportedScope", "PrerequisiteError", "ValueError"}`；L1261断言`value["status"] == "unconfirmed" and value["reason"] == "create_unconfirmed"`；L1262断言`"private" not in path.read_text()`。 调用`monkeypatch.setattr`、`approved_manual`、`monkeypatch.setenv`、`browser.write_text`、`json.dumps`、`isolation.browser_source_identity`、`isolation.image_source_identity`、`dict.fromkeys`、`cleanup_binding`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_file_entrypoint_rechecks_forwarded_scope.launch`（L1221–L1236）：接收`command`、`**kwargs`。 控制顺序：L1223断言`env["GITHUB_SHA"] == env["REVIEWED_SHA"] == env["GITHUB_WORKFLOW_SHA"]`；L1224按`mutation == "missing"`分支；L1226按`mutation is not None`分支。 调用`env.pop`、`original`、`str`、`children.append`。 返回路径：L1236的`process`。
- `test_real_file_entrypoint_rechecks_forwarded_scope.unresolved`（L1240–L1241）：接收`*args`。 控制顺序：L1241抛异常，停止当前正常路径。 调用`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_file_session_rejects_extra_scope_before_launch`（L1269–L1293）：接收`settings`、`tmp_path`、`monkeypatch`、`bad_scope`。 控制顺序：L1293断言`not launches and not path.exists()`。 调用`monkeypatch.setattr`、`approved_manual`、`monkeypatch.setenv`、`launches.append`、`cleanup_binding`、`pytest.raises`、`file_session.Session`、`plan.selection.model_dump`、`time.monotonic`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_deletion_requires_timely_typed_absence`（L1297–L1385）：接收`monkeypatch`、`mode`。 源码说明：Actual pinned SDK get/delete/error interception, only HTTP transport synthesized.。 控制顺序：L1371按`mode in {"absent", "eventual"}`分支；L1373断言`calls[-1] == ("GET", 404)`；L1383断言`("DELETE", 204) in calls`。 调用`monkeypatch.setattr`、`Daytona`、`DaytonaConfig`、`client.get`、`confirm_deleted`、`time.monotonic`、`pytest.raises`、`close_client`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_deletion_requires_timely_typed_absence.deny`（L1309–L1310）：接收`*a`、`**k`。 控制顺序：L1310抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_deletion_requires_timely_typed_absence.request`（L1342–L1366）：接收`method`、`url`、`**kwargs`。 控制顺序：L1344按`method == "DELETE"`分支；L1347按`state["deleted"]`分支；L1349按`mode == "late"`分支。 调用`time.sleep`、`calls.append`、`HTTPResponse`、`io.BytesIO`、`json.dumps(body).encode`、`json.dumps`。 返回路径：L1361的`HTTPResponse( status=status, body=io.BytesIO(json.dumps(body).encode() if body else b""), …`。
- `test_windows_job_owns_subtree_and_fails_closed`（L1399–L1450）：接收`failure`。 控制顺序：L1430按`failure is None`分支；L1435断言`[name for name, _ in calls] == [ "CreateJobObjectW", "SetInformationJobObject", "Assi…`；L1442断言`calls[2][1] == (99, 7)`；L1443断言`calls[3][1] == (99, 1)`；L1449按`failure in {"SetInformationJobObject", "AssignProcessToJobObject"}`分支；L1450断言`calls[-1][0] == "CloseHandle"`。 调用`SimpleNamespace`、`Function`、`WindowsJob`、`job.terminate`、`job.close`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_job_owns_subtree_and_fails_closed.Function`（L1406–L1416）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_windows_job_owns_subtree_and_fails_closed.Function.__init__`（L1407–L1408）：接收`name`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_job_owns_subtree_and_fails_closed.Function.__call__`（L1410–L1416）：接收`*args`。 控制顺序：L1412按`self.name == "SetInformationJobObject"`分支；L1414断言`limits.BasicLimitInformation.LimitFlags == 0x2000`；L1415断言`args[1] == 9 and args[3] == ctypes.sizeof(ExtendedLimits)`。 调用`calls.append`、`ctypes.cast`、`ctypes.POINTER`、`ctypes.sizeof`。 返回路径：L1416的`0 if self.name == failure else 99 if self.name == "CreateJobObjectW" else 1`。
- `test_native_windows_job_kills_pipe_holding_descendant`（L1454–L1507）：接收`tmp_path`。 控制顺序：L1488在`not marker.exists() and time.monotonic() < deadline`成立时循环；L1490断言`marker.exists()`；L1492断言`descendant`；L1496断言`api.WaitForSingleObject(descendant, 2000) == 0`；L1498断言`time.monotonic() - start < 4`；L1500按`job is not None`分支；L1504按`descendant`分支。 调用`subprocess.Popen`、`str`、`ctypes.WinDLL`、`WindowsJob`、`process.stdin.write`、`process.stdin.flush`、`time.monotonic`、`marker.exists`、`time.sleep`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pipe_reaping_has_independent_bound`（L1510–L1526）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1524断言`time.monotonic() - start < 1`。 调用`threading.Event`、`SimpleNamespace`、`release.wait`、`time.monotonic`、`pytest.raises`、`close_pipes_bounded`、`release.set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_child_exports_only_bound_failure_kind`（L1530–L1575）：接收`settings`、`tmp_path`、`monkeypatch`、`known`。 控制顺序：L1569断言`value["status"] == "unconfirmed"`；L1570断言`value["reason"] == ("deletion_unconfirmed" if known else "create_unconfirmed")`；L1571断言`value["cleanup_failure_kind"] == "DaytonaAuthorizationError"`；L1572断言`"private" not in path.read_text()`；L1574断言`exported["cleanup_failure_kind"] == "DaytonaAuthorizationError"`；L1575断言`exported["status"] == "unconfirmed"`。 调用`monkeypatch.setattr`、`original`、`cleanup_binding`、`pytest.raises`、`cleanup.delete_owned`、`time.monotonic`、`json.loads`、`path.read_text`、`cleanup.public_receipt`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_mini_swe_checkpoints.py`；**本文件共有 2 段**。本段覆盖源文件 L896–L1575。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26263`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_mini_swe_checkpoints.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "8cc42d782f9489d8d7e8170b72e87541d77e04ddb2f6757a5c3fbbae35025633"} -->
````python
# tests/test_mini_swe_checkpoints.py
    def run():
        with coding._local_environment(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            deadline=time.monotonic() + 30,
            cleanup_record=path,
            cleanup_binding=binding,
        ) as environment:
            environment.bind_candidate("c" * 64)
            if fail_write:
                raise RuntimeError("partial upload failed")

    if fail_write:
        with pytest.raises(RuntimeError):
            run()
    else:
        run()
    assert operations == ["delete", "closed"]


def test_checkpoint_parent_kills_child_and_freezes_early_success(settings, tmp_path, monkeypatch):
    import subprocess
    import sys

    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_sandbox as verifier
    from workbench.generator import PrerequisiteError

    product = tmp_path / "product"
    plan = fixed_application(product)
    monkeypatch.setattr(
        "workbench.capability_execution.capability_execution_prerequisites",
        lambda *a: (tmp_path, {}),
    )
    monkeypatch.setattr(
        "workbench.capability_dependencies.require_dependency_descriptors", lambda *a: None
    )
    child = """import json,sys,time
from pathlib import Path
p=json.loads(sys.stdin.buffer.read())
Path(p['receipt']).write_text(json.dumps({'passed':True,'cleanup':'deleted','checkpoint':p['checkpoint'],'repairable_failure':'application_startup'}))
time.sleep(30)
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        process = original([sys.executable, "-c", child], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(verifier.subprocess, "Popen", launch)
    checkpoint = {
        "task": digest(plan.tasks[0].model_dump()),
        "nonce": "a" * 32,
        "deadline": time.monotonic() + 0.5,
    }
    with pytest.raises(PrerequisiteError, match="超时"):
        verifier.verify_capabilities(
            product,
            plan,
            plan.scenarios,
            settings,
            aggregate=False,
            checkpoint=checkpoint,
            selection=plan.selection.model_dump(),
        )
    assert children[0].poll() is not None
    value = json.loads((tmp_path / "product-node-verification.json").read_text())
    assert value["passed"] is False and value["cleanup"] == "unconfirmed"
    assert value["checkpoint"] == checkpoint and "repairable_failure" not in value


@pytest.mark.skipif(not hasattr(signal, "SIGUSR1"), reason="dedicated POSIX deadline")
def test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline():
    from daytona._utils.timeout import with_timeout

    from workbench.infrastructure.sandbox.deadline import CheckpointDeadline, CheckpointExpired

    @with_timeout()
    def cleanup_call(timeout):
        time.sleep(12)

    start = time.monotonic()
    with CheckpointDeadline(start + 10.1) as controller:
        controller.enter_cleanup()
        with pytest.raises(CheckpointExpired):
            cleanup_call(timeout=20)
    elapsed = time.monotonic() - start
    assert 10 <= elapsed < 11.5


@pytest.mark.parametrize("status", [502, 503, 504])
def test_preview_gateway_errors_cannot_authorize_business_repair(status):
    import httpx

    from workbench.capability_contracts import HttpStep
    from workbench.capability_verification import BusinessCheckFailure, CheckFailure, run_steps

    with httpx.Client(
        base_url="http://fixture.invalid",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(status, stream=httpx.ByteStream(b"upstream unavailable"))
        ),
    ) as client:
        with pytest.raises(CheckFailure) as error:
            run_steps(client, [HttpStep(path="/check", status=200)], {})
    assert not isinstance(error.value, BusinessCheckFailure)


@pytest.mark.parametrize("phase", ["create", "refresh", "write", "snapshot", "idle", "success"])
def test_entire_file_sdk_lifecycle_is_supervised(settings, tmp_path, monkeypatch, phase):
    """Event-blocked real SDK refresh/API transport in a real child, no external network."""
    import subprocess
    import sys

    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import file_session
    from workbench.infrastructure.sandbox.coding import coding_environment
    from workbench.planning.contracts import CapabilityEdits

    task, plan, binding = cleanup_binding()
    marker = tmp_path / "blocked"
    child = r"""
import io,json,socket,sys,threading,subprocess
from pathlib import Path
from unittest.mock import patch
from daytona import Daytona,DaytonaConfig
from daytona._utils.timeout import with_timeout
from urllib3.response import HTTPResponse
from workbench.infrastructure.sandbox import file_session,coding
phase,marker=sys.argv[1:]
def deny(*a,**k):raise AssertionError('offline only')
socket.socket.connect=deny;socket.create_connection=deny
client=Daytona(DaytonaConfig(api_url='http://127.0.0.1:1/api',api_key='offline-fixture',target='local',otel_enabled=False))
state={'name':None,'count':0}
def block():
 if phase=='refresh':
  descendant=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
  Path(marker+'.pid').write_text(str(descendant.pid))
 Path(marker).write_text('entered')
 threading.Event().wait(60)
def request(method,url,**kw):
 state['count']+=1
 if state['count']>1 and phase=='refresh':block()
 dto={'id':'owned','organizationId':'fixture','name':state['name'],'user':'root','env':{},'labels':{},'public':False,'networkBlockAll':True,'target':'local','cpu':1,'gpu':0,'memory':1,'disk':1,'toolboxProxyUrl':'http://127.0.0.1:1/toolbox','state':'started'}
 return HTTPResponse(status=200,body=io.BytesIO(json.dumps(dto).encode()),headers={'content-type':'application/json'},preload_content=False)
client._api_client.rest_client.pool_manager.request=request
@with_timeout()
def create(parameters,timeout):
 state['name']=parameters.name
 if phase=='create':block()
 return client.get(parameters.name)
client.create=create
writes=[0]
def write(self,edits):
 writes[0]+=1
 if phase=='write' and writes[0]>1:block()
def snapshot(self,paths):
 if phase=='snapshot':block()
 return {p:'' for p in paths}
with patch.object(coding,'client_for',lambda *a:client),patch.object(coding,'capability_execution_prerequisites',lambda *a:(Path('/tmp'),{})),patch.object(coding,'require_container_evidence',lambda *a:{}),patch.object(coding,'require_profile_container_binding',lambda *a:None),patch('scripts.daytona_capability_profile.inspect_created_sandbox',lambda *a,**k:{}),patch.object(coding.DaytonaFiles,'write',write),patch.object(coding.DaytonaFiles,'snapshot',snapshot):
 file_session.main()
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        with (tmp_path / "child-errors").open("wb") as errors:
            kwargs["stderr"] = errors
            process = original([sys.executable, "-c", child, phase, str(marker)], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(file_session.subprocess, "Popen", launch)
    cleaned = []

    def cleanup(settings, name, identifier, bound, path, deadline):
        cleaned.append((identifier, time.monotonic(), dict(bound)))
        value = file_session.receipt(
            bound, name, identifier, "create_unconfirmed" if identifier is None else "pending"
        )
        if identifier is not None:
            value.update(status="deleted", reason="confirmed_absent")
        write_json(path, value)
        if identifier is None:
            raise UnsupportedScope("Unknown create stays unconfirmed")

    monkeypatch.setattr(file_session, "delete_owned", cleanup)
    start = time.monotonic()
    path = tmp_path / "agent-cleanup.json"
    from contextlib import nullcontext

    with nullcontext() if phase == "success" else pytest.raises(UnsupportedScope):
        with coding_environment(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            deadline=start + 25,
            cleanup_record=path,
            cleanup_binding=binding,
        ) as environment:
            if phase == "success":
                assert environment.snapshot(task.allowed_paths) == {
                    p: "" for p in task.allowed_paths
                }
            if phase == "write":
                environment.bind_candidate("c" * 64)
                environment.write(
                    CapabilityEdits(
                        explanation="fixture",
                        files=[{"path": p, "content": ""} for p in task.allowed_paths],
                    )
                )
            elif phase == "snapshot":
                environment.snapshot(task.allowed_paths)
            elif phase == "idle":
                assert environment.done.wait(12), "watchdog must clean while parent is idle"
                environment.snapshot(task.allowed_paths)
    assert time.monotonic() - start < 14
    assert len(cleaned) == 1 and cleaned[0][1] < start + 25
    assert children[0].poll() is not None
    value = json.loads(path.read_text())
    assert value["status"] == ("unconfirmed" if phase == "create" else "deleted")
    assert value["binding"]["source"] == ("c" * 64 if phase == "write" else binding["source"])
    if phase not in {"idle", "success"}:
        assert marker.read_text() == "entered"
    if phase == "refresh" and os.name == "posix":
        from pathlib import Path

        descendant = Path("/proc") / (tmp_path / "blocked.pid").read_text() / "stat"
        if descendant.exists():
            assert descendant.read_text().split()[2] == "Z", (
                "Owned inspector must not survive SDK kill"
            )


@pytest.mark.parametrize("mutation", [None, "missing", "sha", "job", "scenario", "policy"])
def test_real_file_entrypoint_rechecks_forwarded_scope(settings, tmp_path, monkeypatch, mutation):
    """Real Session/main/local-environment/browser gate; stop before SDK/network use."""
    import subprocess
    import sys

    from test_capability_browser_policy import IMAGE, approved_manual

    from workbench import capability_browser_isolation as isolation
    from workbench import capability_browser_policy as policy
    from workbench.infrastructure.sandbox import file_session

    # The selector is Linux-only; exercise that exact identity on every CI controller.
    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")
    approved_manual(monkeypatch)
    for key in ("API_KEY", "GITHUB_TOKEN", "HTTP_PROXY", "HTTPS_PROXY"):
        monkeypatch.setenv(key, "private-must-not-forward")
    browser = tmp_path / "browser.json"
    browser.write_text(
        json.dumps(
            {
                "protocol": "offline-browser-isolation-v3",
                "passed": True,
                "mocked": False,
                "image": IMAGE,
                "runtime": {"fixture_approved_runtime": True},
                "sources": isolation.browser_source_identity(),
                "image_sources": isolation.image_source_identity(),
                "checks": {
                    "kernel_and_network": dict.fromkeys(
                        (
                            "passed",
                            "kernel_resource_limits",
                            "network_none",
                            "tmpfs_exhaustion",
                            "pid_exhaustion",
                            "readonly_root",
                            "browser_build",
                            "apparmor_enforced",
                        ),
                        True,
                    ),
                    **dict.fromkeys(
                        (
                            "positive",
                            "error",
                            "abuse",
                            "failure_cleanup",
                            "memory_exhaustion",
                            "raw_syscalls",
                        ),
                        True,
                    ),
                },
            }
        )
    )
    marker = tmp_path / "admitted"
    child = r"""
import os,sys,socket
from pathlib import Path
from workbench.infrastructure.sandbox import file_session,coding
from workbench import capability_browser_isolation as isolation, capability_browser_policy as policy
from workbench.errors import UnsupportedScope
browser,marker=sys.argv[1:]
assert not any(k in os.environ for k in ('API_KEY','GITHUB_TOKEN','HTTP_PROXY','HTTPS_PROXY'))
def deny(*a,**k):raise AssertionError('offline only')
socket.socket.connect=deny;socket.create_connection=deny
policy.platform.system=lambda:'Linux'
policy.platform.machine=lambda:'x86_64'
isolation.BROWSER_ACCEPTANCE=Path(browser)
isolation.runtime_identity=lambda image: ({'fixture_approved_runtime':True} if policy.selected_policy() else {'policy_sha256':None,'mode':'docker-default'})
def prerequisites(*args):
 isolation.require_browser_acceptance('sha256:'+'a'*64)
 Path(marker).write_text('admitted')
 return Path(browser).parent,{}
def stop(*args):raise UnsupportedScope('private SDK sentinel must never be exported')
coding.capability_execution_prerequisites=prerequisites
coding.client_for=stop
file_session.main()
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        env = kwargs["env"]
        assert env["GITHUB_SHA"] == env["REVIEWED_SHA"] == env["GITHUB_WORKFLOW_SHA"]
        if mutation == "missing":
            env.pop("CAPABILITY_BROWSER_APPROVED_POLICY")
        elif mutation is not None:
            key, value = {
                "sha": ("REVIEWED_SHA", "b" * 40),
                "job": ("GITHUB_JOB", "real-model"),
                "scenario": ("LIVE_SCENARIO", "legacy"),
                "policy": ("CAPABILITY_BROWSER_APPROVED_POLICY", "0" * 64),
            }[mutation]
            env[key] = value
        process = original([sys.executable, "-c", child, str(browser), str(marker)], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(file_session.subprocess, "Popen", launch)

    def unresolved(*args):
        raise UnsupportedScope("Unknown create remains unconfirmed")

    monkeypatch.setattr(file_session, "delete_owned", unresolved)
    task, plan, binding = cleanup_binding()
    path = tmp_path / "agent-cleanup.json"
    with pytest.raises(UnsupportedScope):
        file_session.Session(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            time.monotonic() + 25,
            path,
            binding,
        )
    assert len(children) == 1 and children[0].poll() is not None
    assert marker.exists() is (mutation is None)
    value = json.loads(path.read_text())
    assert value["failure_phase"] == ("client" if mutation is None else "admission")
    assert value["failure_kind"] in {"UnsupportedScope", "PrerequisiteError", "ValueError"}
    assert value["status"] == "unconfirmed" and value["reason"] == "create_unconfirmed"
    assert "private" not in path.read_text()


@pytest.mark.parametrize(
    "bad_scope",
    [("GITHUB_JOB", "real-model"), ("GITHUB_RUN_ATTEMPT", "2"), ("REVIEWED_SHA", "b" * 40)],
)
def test_file_session_rejects_extra_scope_before_launch(settings, tmp_path, monkeypatch, bad_scope):
    from test_capability_browser_policy import approved_manual

    from workbench import capability_browser_policy as policy
    from workbench.infrastructure.sandbox import file_session

    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")
    approved_manual(monkeypatch)
    monkeypatch.setenv(*bad_scope)
    launches = []
    monkeypatch.setattr(file_session.subprocess, "Popen", lambda *a, **k: launches.append(True))
    task, plan, binding = cleanup_binding()
    path = tmp_path / "journal"
    with pytest.raises(ValueError, match="approved Actions scope"):
        file_session.Session(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            time.monotonic() + 25,
            path,
            binding,
        )
    assert not launches and not path.exists()


@pytest.mark.parametrize("mode", ["absent", "eventual", "present", "forbidden", "server", "late"])
def test_real_sdk_deletion_requires_timely_typed_absence(monkeypatch, mode):
    """Actual pinned SDK get/delete/error interception, only HTTP transport synthesized."""
    import io
    import socket

    from daytona import Daytona, DaytonaConfig
    from daytona.common.errors import DaytonaAuthorizationError, DaytonaError
    from urllib3.response import HTTPResponse

    from workbench.infrastructure.sandbox.cleanup import confirm_deleted
    from workbench.sandbox import close_client

    def deny(*a, **k):
        raise AssertionError("offline only")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    client = Daytona(
        DaytonaConfig(
            api_url="http://127.0.0.1:1/api",
            api_key="offline-fixture",
            target="local",
            otel_enabled=False,
        )
    )
    state = {"deleted": False, "gets": 0}
    calls = []
    dto = {
        "id": "owned-id",
        "organizationId": "fixture",
        "name": "rnd-source-agent-" + "a" * 32,
        "user": "root",
        "env": {},
        "labels": {},
        "public": False,
        "networkBlockAll": True,
        "target": "local",
        "cpu": 1,
        "gpu": 0,
        "memory": 1,
        "disk": 1,
        "toolboxProxyUrl": "http://127.0.0.1:1/toolbox",
        "state": "started",
    }

    def request(method, url, **kwargs):
        status, body = 200, dto
        if method == "DELETE":
            state["deleted"] = True
            status, body = 204, None
        elif state["deleted"]:
            state["gets"] += 1
            if mode == "late":
                time.sleep(0.25)
            status = {
                "absent": 404,
                "eventual": 200 if state["gets"] == 1 else 404,
                "present": 200,
                "forbidden": 403,
                "server": 500,
                "late": 404,
            }[mode]
            body = dto if status == 200 else {"message": "owned fixture"}
        calls.append((method, status))
        return HTTPResponse(
            status=status,
            body=io.BytesIO(json.dumps(body).encode() if body else b""),
            headers={"content-type": "application/json"},
            preload_content=False,
        )

    monkeypatch.setattr(client._api_client.rest_client.pool_manager, "request", request)
    try:
        target = client.get(dto["name"])
        if mode in {"absent", "eventual"}:
            confirm_deleted(client, target, time.monotonic() + 1, 1)
            assert calls[-1] == ("GET", 404)
        else:
            error = {
                "present": TimeoutError,
                "late": TimeoutError,
                "forbidden": DaytonaAuthorizationError,
                "server": DaytonaError,
            }[mode]
            with pytest.raises(error):
                confirm_deleted(client, target, time.monotonic() + 0.12, 1)
        assert ("DELETE", 204) in calls
    finally:
        close_client(client)


@pytest.mark.parametrize(
    "failure",
    [
        None,
        "CreateJobObjectW",
        "SetInformationJobObject",
        "AssignProcessToJobObject",
        "TerminateJobObject",
        "CloseHandle",
    ],
)
def test_windows_job_owns_subtree_and_fails_closed(failure):
    import ctypes

    from workbench.infrastructure.sandbox.windows_job import ExtendedLimits, WindowsJob

    calls = []

    class Function:
        def __init__(self, name):
            self.name = name

        def __call__(self, *args):
            calls.append((self.name, args))
            if self.name == "SetInformationJobObject":
                limits = ctypes.cast(args[2], ctypes.POINTER(ExtendedLimits)).contents
                assert limits.BasicLimitInformation.LimitFlags == 0x2000
                assert args[1] == 9 and args[3] == ctypes.sizeof(ExtendedLimits)
            return 0 if self.name == failure else 99 if self.name == "CreateJobObjectW" else 1

    api = SimpleNamespace(
        **{
            name: Function(name)
            for name in (
                "CreateJobObjectW",
                "SetInformationJobObject",
                "AssignProcessToJobObject",
                "TerminateJobObject",
                "CloseHandle",
            )
        }
    )
    if failure is None:
        job = WindowsJob(SimpleNamespace(_handle=7), api=api)
        job.terminate()
        job.close()
        job.close()
        assert [name for name, _ in calls] == [
            "CreateJobObjectW",
            "SetInformationJobObject",
            "AssignProcessToJobObject",
            "TerminateJobObject",
            "CloseHandle",
        ]
        assert calls[2][1] == (99, 7)
        assert calls[3][1] == (99, 1)
    else:
        with pytest.raises(UnsupportedScope):
            job = WindowsJob(SimpleNamespace(_handle=7), api=api)
            job.terminate()
            job.close()
        if failure in {"SetInformationJobObject", "AssignProcessToJobObject"}:
            assert calls[-1][0] == "CloseHandle"


@pytest.mark.skipif(os.name != "nt", reason="native Windows Job Object process-tree proof")
def test_native_windows_job_kills_pipe_holding_descendant(tmp_path):
    import ctypes
    import subprocess
    import sys

    from workbench.infrastructure.sandbox.file_session import close_pipes_bounded
    from workbench.infrastructure.sandbox.windows_job import WindowsJob

    marker = tmp_path / "pid"
    child = """import subprocess,sys
from pathlib import Path
sys.stdin.readline()
p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
marker=Path(sys.argv[1]); temporary=marker.with_suffix('.tmp')
temporary.write_text(str(p.pid)); temporary.replace(marker)
print('ready',flush=True)
p.wait()
"""
    process = subprocess.Popen(
        [sys.executable, "-c", child, str(marker)], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    job = None
    descendant = None
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    api.OpenProcess.restype = ctypes.c_void_p
    api.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    api.WaitForSingleObject.restype = ctypes.c_uint32
    api.CloseHandle.argtypes = [ctypes.c_void_p]
    try:
        job = WindowsJob(process)
        process.stdin.write(b"start\n")
        process.stdin.flush()
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert marker.exists()
        descendant = api.OpenProcess(0x00100000, False, int(marker.read_text()))
        assert descendant
        start = time.monotonic()
        job.terminate()
        process.wait(timeout=2)
        assert api.WaitForSingleObject(descendant, 2000) == 0
        close_pipes_bounded(process)
        assert time.monotonic() - start < 4
    finally:
        if job is not None:
            job.close()
        else:
            process.kill()
        if descendant:
            api.CloseHandle(descendant)
        process.wait(timeout=2)
        close_pipes_bounded(process)


def test_pipe_reaping_has_independent_bound():
    import threading

    from workbench.infrastructure.sandbox.file_session import close_pipes_bounded

    release = threading.Event()
    process = SimpleNamespace(
        stdin=SimpleNamespace(close=lambda: release.wait(5)),
        stdout=SimpleNamespace(close=lambda: None),
    )
    start = time.monotonic()
    try:
        with pytest.raises(UnsupportedScope, match="pipe close exceeded bound"):
            close_pipes_bounded(process)
        assert time.monotonic() - start < 1
    finally:
        release.set()


@pytest.mark.parametrize("known", [False, True])
def test_cleanup_child_exports_only_bound_failure_kind(settings, tmp_path, monkeypatch, known):
    import subprocess
    import sys

    from workbench.infrastructure.sandbox import cleanup

    child = r"""
import io,json,socket
from daytona import Daytona,DaytonaConfig
from urllib3.response import HTTPResponse
from workbench.infrastructure.sandbox import cleanup
from workbench import sandbox
def deny(*a,**k):raise AssertionError('offline only')
socket.socket.connect=deny;socket.create_connection=deny
client=Daytona(DaytonaConfig(api_url='http://127.0.0.1:1/api',api_key='offline-fixture',target='local',otel_enabled=False))
def request(*a,**k):
 return HTTPResponse(status=403,body=io.BytesIO(json.dumps({'message':'private server text must not escape'}).encode()),headers={'content-type':'application/json'},preload_content=False)
client._api_client.rest_client.pool_manager.request=request
sandbox.client_for=lambda *a:client
cleanup.main()
"""
    original = subprocess.Popen
    monkeypatch.setattr(
        cleanup.subprocess,
        "Popen",
        lambda command, **kw: original([sys.executable, "-c", child], **kw),
    )
    task, plan, binding = cleanup_binding()
    path = tmp_path / "cleanup.json"
    with pytest.raises(UnsupportedScope):
        cleanup.delete_owned(
            settings,
            "rnd-source-agent-" + "a" * 32,
            "owned-id" if known else None,
            binding,
            path,
            time.monotonic() + 10,
        )
    value = json.loads(path.read_text())
    assert value["status"] == "unconfirmed"
    assert value["reason"] == ("deletion_unconfirmed" if known else "create_unconfirmed")
    assert value["cleanup_failure_kind"] == "DaytonaAuthorizationError"
    assert "private" not in path.read_text()
    exported = cleanup.public_receipt(path, task, plan)
    assert exported["cleanup_failure_kind"] == "DaytonaAuthorizationError"
    assert exported["status"] == "unconfirmed"
````
