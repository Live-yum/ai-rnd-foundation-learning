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

</details>

**创建路径：** `tests/test_mini_swe_checkpoints.py`；**本文件共有 2 段**。本段覆盖源文件 L896–L1133。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9816`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_mini_swe_checkpoints.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "e3dac901efb1a41f6ef5c7b7eedaa1beac2290f6bcb6476434fb03f32b006a14"} -->
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
````
