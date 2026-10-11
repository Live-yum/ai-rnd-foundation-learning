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
- `test_checkpoint_parent_kills_child_and_freezes_early_success`（L918–L972）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L968断言`len(children) == 1 and children[0].poll() is not None`；L969断言`auxiliary == (["taskkill"] if os.name == "nt" else [])`；L971断言`value["passed"] is False and value["cleanup"] == "unconfirmed"`；L972断言`value["checkpoint"] == checkpoint and "repairable_failure" not in value`。 调用`fixed_application`、`monkeypatch.setattr`、`digest`、`plan.tasks[0].model_dump`、`time.monotonic`、`pytest.raises`、`verifier.verify_capabilities`、`plan.selection.model_dump`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_parent_kills_child_and_freezes_early_success.launch`（L944–L950）：接收`command`、`**kwargs`。 控制顺序：L945按`command != [sys.executable, "-m", "workbench.capability_sandbox"]`分支。 调用`auxiliary.append`、`original`、`children.append`。 返回路径：L947的`original(command, **kwargs)`；L950的`process`。
- `test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline`（L976–L991）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L991断言`10 <= elapsed < 11.5`。 调用`time.monotonic`、`CheckpointDeadline`、`controller.enter_cleanup`、`pytest.raises`、`cleanup_call`、`pytest.mark.skipif`、`hasattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline.cleanup_call`（L982–L983）：接收`timeout`。 调用`time.sleep`、`with_timeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preview_gateway_errors_cannot_authorize_business_repair`（L995–L1009）：接收`status`。 控制顺序：L1009断言`not isinstance(error.value, BusinessCheckFailure)`。 调用`httpx.Client`、`httpx.MockTransport`、`httpx.Response`、`httpx.ByteStream`、`pytest.raises`、`run_steps`、`HttpStep`、`isinstance`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entire_file_sdk_lifecycle_is_supervised`（L1013–L1148）：接收`settings`、`tmp_path`、`monkeypatch`、`phase`。 源码说明：Event-blocked real SDK refresh/API transport in a real child, no external network.。 控制顺序：L1105按`phase == "success"`分支；L1106断言`environment.snapshot(task.allowed_paths) == { p: "" for p in task.allowed_paths }`；L1109按`phase == "write"`分支；L1117按`phase == "snapshot"`分支；L1119按`phase == "idle"`分支；L1120断言`environment.done.wait(12)`；L1122断言`time.monotonic() - start < 14`；L1123断言`len(cleaned) == 1 and cleaned[0][1] < start + 25`。后续分支沿下方源码相同行号继续阅读。 调用`cleanup_binding`、`monkeypatch.setattr`、`time.monotonic`、`nullcontext`、`pytest.raises`、`coding_environment`、`plan.selection.model_dump`、`environment.snapshot`、`environment.bind_candidate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entire_file_sdk_lifecycle_is_supervised.launch`（L1069–L1074）：接收`command`、`**kwargs`。 调用`(tmp_path / "child-errors").open`、`original`、`str`、`children.append`。 返回路径：L1074的`process`。
- `test_entire_file_sdk_lifecycle_is_supervised.cleanup`（L1079–L1088）：接收`settings`、`name`、`identifier`、`bound`、`path`、`deadline`。 控制顺序：L1084按`identifier is not None`分支；L1087按`identifier is None`分支；L1088抛异常，停止当前正常路径。 调用`cleaned.append`、`time.monotonic`、`dict`、`file_session.receipt`、`value.update`、`write_json`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_file_entrypoint_rechecks_forwarded_scope`（L1152–L1277）：接收`settings`、`tmp_path`、`monkeypatch`、`mutation`。 源码说明：Real Session/main/local-environment/browser gate; stop before SDK/network use.。 控制顺序：L1167遍历`("API_KEY", "GITHUB_TOKEN", "HTTP_PROXY", "HTTPS_PROXY")`；L1271断言`len(children) == 1 and children[0].poll() is not None`；L1272断言`marker.exists() is (mutation is None)`；L1274断言`value["failure_phase"] == ("client" if mutation is None else "admission")`；L1275断言`value["failure_kind"] in {"UnsupportedScope", "PrerequisiteError", "ValueError"}`；L1276断言`value["status"] == "unconfirmed" and value["reason"] == "create_unconfirmed"`；L1277断言`"private" not in path.read_text()`。 调用`monkeypatch.setattr`、`approved_manual`、`monkeypatch.setenv`、`browser.write_text`、`json.dumps`、`isolation.browser_source_identity`、`isolation.image_source_identity`、`dict.fromkeys`、`cleanup_binding`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_file_entrypoint_rechecks_forwarded_scope.launch`（L1236–L1251）：接收`command`、`**kwargs`。 控制顺序：L1238断言`env["GITHUB_SHA"] == env["REVIEWED_SHA"] == env["GITHUB_WORKFLOW_SHA"]`；L1239按`mutation == "missing"`分支；L1241按`mutation is not None`分支。 调用`env.pop`、`original`、`str`、`children.append`。 返回路径：L1251的`process`。
- `test_real_file_entrypoint_rechecks_forwarded_scope.unresolved`（L1255–L1256）：接收`*args`。 控制顺序：L1256抛异常，停止当前正常路径。 调用`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_file_session_rejects_extra_scope_before_launch`（L1284–L1308）：接收`settings`、`tmp_path`、`monkeypatch`、`bad_scope`。 控制顺序：L1308断言`not launches and not path.exists()`。 调用`monkeypatch.setattr`、`approved_manual`、`monkeypatch.setenv`、`launches.append`、`cleanup_binding`、`pytest.raises`、`file_session.Session`、`plan.selection.model_dump`、`time.monotonic`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_deletion_requires_timely_typed_absence`（L1312–L1400）：接收`monkeypatch`、`mode`。 源码说明：Actual pinned SDK get/delete/error interception, only HTTP transport synthesized.。 控制顺序：L1386按`mode in {"absent", "eventual"}`分支；L1388断言`calls[-1] == ("GET", 404)`；L1398断言`("DELETE", 204) in calls`。 调用`monkeypatch.setattr`、`Daytona`、`DaytonaConfig`、`client.get`、`confirm_deleted`、`time.monotonic`、`pytest.raises`、`close_client`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_deletion_requires_timely_typed_absence.deny`（L1324–L1325）：接收`*a`、`**k`。 控制顺序：L1325抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_deletion_requires_timely_typed_absence.request`（L1357–L1381）：接收`method`、`url`、`**kwargs`。 控制顺序：L1359按`method == "DELETE"`分支；L1362按`state["deleted"]`分支；L1364按`mode == "late"`分支。 调用`time.sleep`、`calls.append`、`HTTPResponse`、`io.BytesIO`、`json.dumps(body).encode`、`json.dumps`。 返回路径：L1376的`HTTPResponse( status=status, body=io.BytesIO(json.dumps(body).encode() if body else b""), …`。
- `test_windows_job_owns_subtree_and_fails_closed`（L1414–L1465）：接收`failure`。 控制顺序：L1445按`failure is None`分支；L1450断言`[name for name, _ in calls] == [ "CreateJobObjectW", "SetInformationJobObject", "Assi…`；L1457断言`calls[2][1] == (99, 7)`；L1458断言`calls[3][1] == (99, 1)`；L1464按`failure in {"SetInformationJobObject", "AssignProcessToJobObject"}`分支；L1465断言`calls[-1][0] == "CloseHandle"`。 调用`SimpleNamespace`、`Function`、`WindowsJob`、`job.terminate`、`job.close`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_job_owns_subtree_and_fails_closed.Function`（L1421–L1431）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_windows_job_owns_subtree_and_fails_closed.Function.__init__`（L1422–L1423）：接收`name`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_job_owns_subtree_and_fails_closed.Function.__call__`（L1425–L1431）：接收`*args`。 控制顺序：L1427按`self.name == "SetInformationJobObject"`分支；L1429断言`limits.BasicLimitInformation.LimitFlags == 0x2000`；L1430断言`args[1] == 9 and args[3] == ctypes.sizeof(ExtendedLimits)`。 调用`calls.append`、`ctypes.cast`、`ctypes.POINTER`、`ctypes.sizeof`。 返回路径：L1431的`0 if self.name == failure else 99 if self.name == "CreateJobObjectW" else 1`。
- `test_native_windows_job_kills_pipe_holding_descendant`（L1469–L1522）：接收`tmp_path`。 控制顺序：L1503在`not marker.exists() and time.monotonic() < deadline`成立时循环；L1505断言`marker.exists()`；L1507断言`descendant`；L1511断言`api.WaitForSingleObject(descendant, 2000) == 0`；L1513断言`time.monotonic() - start < 4`；L1515按`job is not None`分支；L1519按`descendant`分支。 调用`subprocess.Popen`、`str`、`ctypes.WinDLL`、`WindowsJob`、`process.stdin.write`、`process.stdin.flush`、`time.monotonic`、`marker.exists`、`time.sleep`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pipe_reaping_has_independent_bound`（L1525–L1541）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1539断言`time.monotonic() - start < 1`。 调用`threading.Event`、`SimpleNamespace`、`release.wait`、`time.monotonic`、`pytest.raises`、`close_pipes_bounded`、`release.set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_child_exports_only_bound_failure_kind`（L1545–L1590）：接收`settings`、`tmp_path`、`monkeypatch`、`known`。 控制顺序：L1584断言`value["status"] == "unconfirmed"`；L1585断言`value["reason"] == ("deletion_unconfirmed" if known else "create_unconfirmed")`；L1586断言`value["cleanup_failure_kind"] == "DaytonaAuthorizationError"`；L1587断言`"private" not in path.read_text()`；L1589断言`exported["cleanup_failure_kind"] == "DaytonaAuthorizationError"`；L1590断言`exported["status"] == "unconfirmed"`。 调用`monkeypatch.setattr`、`original`、`cleanup_binding`、`pytest.raises`、`cleanup.delete_owned`、`time.monotonic`、`json.loads`、`path.read_text`、`cleanup.public_receipt`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_reap_failure_still_attempts_owned_deletion`（L1594–L1670）：接收`tmp_path`、`monkeypatch`、`phase`。 控制顺序：L1619按`os.name == "nt"`分支；L1650按`phase == "pipe"`分支；L1658断言`process.poll() is not None and session.deadline - time.monotonic() > 10`；L1659断言`calls == [session.identifier]`；L1661断言`value["status"] == "unconfirmed" and value["reason"] == "deletion_unconfirmed"`；L1662断言`value["supervision_failure_phase"] == ("reader" if phase == "reader" else "pipes")`；L1663断言`value["supervision_failure_kind"] == "UnsupportedScope"`；L1664断言`session.done.is_set()`。后续分支沿下方源码相同行号继续阅读。 调用`subprocess.Popen`、`process_options`、`file_session.Session.__new__`、`time.monotonic`、`threading.Lock`、`threading.Event`、`WindowsJob`、`SimpleNamespace`、`cleanup_binding`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_reap_failure_still_attempts_owned_deletion.deletion`（L1633–L1639）：接收`settings`、`name`、`identifier`、`binding`、`path`、`deadline`。 控制顺序：L1634断言`identifier == session.identifier and binding == session.binding`；L1635断言`deadline == session.deadline and time.monotonic() < deadline`。 调用`time.monotonic`、`calls.append`、`file_session.receipt`、`value.update`、`write_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_reap_failure_still_attempts_owned_deletion.blocked_close`（L1641–L1647）：接收`_`。 调用`original_close`、`SimpleNamespace`、`release.wait`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_turn_timing_preserves_failed_outcome_and_original_budget`（L1673–L1707）：接收`tmp_path`、`monkeypatch`。 控制顺序：L1685抛异常，停止当前正常路径；L1686断言`found.value is failure`；L1688断言`value == { "step": 0, "module_remaining_seconds": 80, "work_remaining_seconds": 65, "…`；L1700断言`"private" not in path.read_text()`；L1706抛异常，停止当前正常路径；L1707断言`found.value is failure`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`RuntimeError`、`pytest.raises`、`timing.record_turn`、`timing.read_turns`、`len`、`json.dumps`、`path.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supervision_diagnostics_are_fixed_and_cannot_upgrade_cleanup`（L1710–L1733）：接收`tmp_path`。 控制顺序：L1716遍历`file_session.SUPERVISION_PHASES`；L1724断言`result["status"] == "unconfirmed"`；L1725断言`result["supervision_failure_phase"] == phase`；L1726断言`result["supervision_failure_kind"] == "OSError"`；L1727断言`"private" not in json.dumps(result)`；L1730断言`"private" not in json.dumps(cleanup.public_receipt(path, task, plan))`；L1733断言`cleanup.public_receipt(path, task, plan)["supervision_failure_phase"] == "journal"`。 调用`cleanup_binding`、`file_session.receipt`、`value.update`、`path.write_text`、`json.dumps`、`OSError`、`file_session.supervision_failure`、`file_session.preserve_state`、`cleanup.public_receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_mini_swe_checkpoints.py`；**本文件共有 2 段**。本段覆盖源文件 L896–L1733。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`32903`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_mini_swe_checkpoints.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "d3de30af21e6f64c2096621be5878357c6b0c64b95d10bca66cddeed005d1676"} -->
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
    children, auxiliary = [], []

    def launch(command, **kwargs):
        if command != [sys.executable, "-m", "workbench.capability_sandbox"]:
            auxiliary.append(command[0])
            return original(command, **kwargs)
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
    assert len(children) == 1 and children[0].poll() is not None
    assert auxiliary == (["taskkill"] if os.name == "nt" else [])
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
    safe_failure = {
        key: value.get(key)
        for key in (
            "reason",
            "supervision_failure_phase",
            "supervision_failure_kind",
            "failure_phase",
            "failure_kind",
            "cleanup_failure_kind",
        )
    }
    assert value["status"] == ("unconfirmed" if phase == "create" else "deleted"), safe_failure
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


@pytest.mark.parametrize("phase", ["reader", "pipe"])
def test_local_reap_failure_still_attempts_owned_deletion(tmp_path, monkeypatch, phase):
    import subprocess
    import sys
    import threading

    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import file_session
    from workbench.tools import process_options

    process = subprocess.Popen(
        [sys.executable, "-c", "import time;time.sleep(30)"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        **process_options(),
    )
    session = file_session.Session.__new__(file_session.Session)
    session.process = process
    session.deadline = time.monotonic() + 15
    session.lock, session.done, session.cancel = (
        threading.Lock(),
        threading.Event(),
        threading.Event(),
    )
    session.closing, session.error, session.failure = False, None, {}
    session.windows_job = None
    if os.name == "nt":
        from workbench.infrastructure.sandbox.windows_job import WindowsJob

        session.windows_job = WindowsJob(process)
    session.settings = SimpleNamespace()
    session.path = tmp_path / "cleanup.json"
    _, _, session.binding = cleanup_binding()
    session.name, session.identifier = "rnd-source-agent-" + "e" * 32, "known-owned-id"
    write_json(
        session.path, file_session.receipt(session.binding, session.name, session.identifier)
    )
    release, calls = threading.Event(), []
    original_close = file_session.close_pipes_bounded

    def deletion(settings, name, identifier, binding, path, deadline):
        assert identifier == session.identifier and binding == session.binding
        assert deadline == session.deadline and time.monotonic() < deadline
        calls.append(identifier)
        value = file_session.receipt(binding, name, identifier)
        value.update(status="deleted", reason="confirmed_absent")
        write_json(path, value)  # Mock remote absence cannot hide a local reaping failure.

    def blocked_close(_):
        original_close(
            SimpleNamespace(
                stdin=SimpleNamespace(close=lambda: release.wait(5)),
                stdout=SimpleNamespace(close=lambda: None),
            )
        )

    monkeypatch.setattr(file_session, "delete_owned", deletion)
    if phase == "pipe":
        monkeypatch.setattr(file_session, "close_pipes_bounded", blocked_close)
    else:
        session.reader = threading.Thread(target=lambda: release.wait(5), daemon=True)
        session.reader.start()
    try:
        with pytest.raises(UnsupportedScope):
            session.finish()
        assert process.poll() is not None and session.deadline - time.monotonic() > 10
        assert calls == [session.identifier]
        value = json.loads(session.path.read_text())
        assert value["status"] == "unconfirmed" and value["reason"] == "deletion_unconfirmed"
        assert value["supervision_failure_phase"] == ("reader" if phase == "reader" else "pipes")
        assert value["supervision_failure_kind"] == "UnsupportedScope"
        assert session.done.is_set()
    finally:
        release.set()
        if hasattr(session, "reader"):
            session.reader.join(1)
        process.wait(timeout=2)
        original_close(process)


def test_model_turn_timing_preserves_failed_outcome_and_original_budget(tmp_path, monkeypatch):
    from workbench.coding import timing

    clock = [100.0]
    monkeypatch.setattr(timing, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    transport = SimpleNamespace(calls=2)
    path = tmp_path / "timing.json"
    failure = RuntimeError("private-model-failure")
    with pytest.raises(RuntimeError) as found:
        with timing.record_turn(path, 0, 180, 31.5, {"secret": "private-prompt"}, transport):
            clock[0] = 164
            transport.calls = 4
            raise failure
    assert found.value is failure
    value = timing.read_turns(path)[0]
    assert value == {
        "step": 0,
        "module_remaining_seconds": 80,
        "work_remaining_seconds": 65,
        "timeout_seconds": 31.5,
        "elapsed_seconds": 64,
        "remaining_after_seconds": 16,
        "overrun_seconds": 0,
        "payload_chars": len(json.dumps({"secret": "private-prompt"})),
        "http_attempts_before": 2,
        "http_attempts_after": 4,
    }
    assert "private" not in path.read_text()
    monkeypatch.setattr(
        timing, "write_json", lambda *a: (_ for _ in ()).throw(OSError("private-io"))
    )
    with pytest.raises(RuntimeError) as found:
        with timing.record_turn(path, 1, 180, 7, {}, transport):
            raise failure
    assert found.value is failure


def test_supervision_diagnostics_are_fixed_and_cannot_upgrade_cleanup(tmp_path):
    from workbench.infrastructure.sandbox import cleanup, file_session

    task, plan, binding = cleanup_binding()
    path = tmp_path / "cleanup.json"
    name = "rnd-source-agent-" + "a" * 32
    for phase in file_session.SUPERVISION_PHASES:
        value = file_session.receipt(binding, name, "owned-id")
        value.update(status="deleted", reason="confirmed_absent")
        path.write_text(json.dumps(value))
        error = OSError("private local details")
        failure = file_session.supervision_failure(phase, error)
        file_session.preserve_state(path, binding, name, "owned-id", error, failure)
        result = cleanup.public_receipt(path, task, plan)
        assert result["status"] == "unconfirmed"
        assert result["supervision_failure_phase"] == phase
        assert result["supervision_failure_kind"] == "OSError"
        assert "private" not in json.dumps(result)
    value.update(supervision_failure_phase="private-phase", supervision_failure_kind="private-kind")
    path.write_text(json.dumps(value))
    assert "private" not in json.dumps(cleanup.public_receipt(path, task, plan))
    path.write_text("{}")
    file_session.preserve_state(path, binding, name, "owned-id", None, {})
    assert cleanup.public_receipt(path, task, plan)["supervision_failure_phase"] == "journal"
````
