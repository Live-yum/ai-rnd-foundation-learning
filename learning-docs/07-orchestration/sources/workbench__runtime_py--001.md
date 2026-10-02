# workbench/runtime.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：持久化Worker和断点恢复。** Runtime把数据库任务和LangGraph检查点连接起来。它按run_id恢复同一流程，认领任务后执行，遇到中断等待回答；异常转成明确状态并保留报告。数据库与checkpoint连接均须在退出时关闭。

**对应关系：** api/cli启动Worker → Runtime → Workflow → Store；test_postgres及test_guided_workflow。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.errors`、`workbench.filesystem`、`workbench.flow`、`workbench.generator`、`workbench.llm`、`workbench.local_only`、`workbench.recommendation`、`workbench.store`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 队列任务只是唤醒同一run_id的理由，LangGraph检查点才说明流程停在哪。Runtime认领任务并恢复原图，遇到interrupt保存等待状态；崩溃后不能把上个任务误当下一关的新批准。一个控制库只允许一个Worker，退出时关闭锁与检查点连接，才能在Windows等平台安全恢复。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `pending_interrupt`（L30–L34）：接收`snapshot`。 控制顺序：L31遍历`snapshot.tasks`；L32按`task.interrupts`分支。 返回路径：L33的`task.interrupts[0].value`；L34的`None`。
- `Runtime`（L37–L230）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Runtime.__init__`（L38–L43）：接收`settings`、`store`、`gateway`。 调用`ModelGateway`、`threading.Event`、`ExitStack`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Runtime.__enter__`（L45–L78）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L50按`self.store.engine.dialect.name == "postgresql"`分支；L54按`not connection.scalar(text("SELECT pg_try_advisory_lock(728194602)"))`分支；L55抛异常，停止当前正常路径；L78抛异常，停止当前正常路径。 调用`self.stack.enter_context`、`FileLock`、`str`、`self.store.engine.connect().execution_options`、`self.store.engine.connect`、`connection.scalar`、`text`、`PrerequisiteError`、`self.stack.callback`等。 返回路径：L75的`self`。
- `Runtime.__exit__`（L80–L81）：接收`*args`。 调用`self.stack.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Runtime.tick`（L83–L225）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L86按`self.requires_model_configuration and not self.settings.models_ready()`分支；L90按`job is None`分支；L98按`not snapshot.values`分支；L110按`payload["action"] in {"start", "retry"} or snapshot.values.get("last_job_id") == job[…`分支；L115按`snapshot.next and not waiting`分支；L117按`waiting`分支；L118按`waiting["gate_id"] != payload.get("gate_id")`分支；L119抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`self.settings.models_ready`、`self.store.claim`、`self.graph.get_state`、`pending_interrupt`、`self.store.get_run`、`self.graph.invoke`、`snapshot.values.get`、`payload.get`、`Conflict`等。 返回路径：L91的`False`；L225的`True`。
- `Runtime.loop`（L227–L230）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L228在`not self.stop.is_set()`成立时循环；L229按`not self.tick()`分支。 调用`self.stop.is_set`、`self.tick`、`self.stop.wait`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/runtime.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L230。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10553`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/runtime.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2a9d898268687b223af1e763379569affad5cb467e8e1eb3c7916697ad0379d3"} -->
````python
# workbench/runtime.py
"""Single durable worker. A recovered job never consumes a later approval gate."""

import json
import logging
import threading
import traceback
from contextlib import ExitStack
from pathlib import Path

from filelock import FileLock
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from sqlalchemy import text
from sqlalchemy.engine import make_url

from workbench.errors import PausedLimit, UnsupportedScope
from workbench.filesystem import write_json
from workbench.flow import Workflow
from workbench.generator import PrerequisiteError
from workbench.llm import ModelFailure, ModelGateway
from workbench.local_only import local_database_url
from workbench.recommendation import blocked_report
from workbench.store import Conflict
from workbench.tools import ToolFailure

logger = logging.getLogger(__name__)


def pending_interrupt(snapshot):
    for task in snapshot.tasks:
        if task.interrupts:
            return task.interrupts[0].value
    return None


class Runtime:
    def __init__(self, settings, store, gateway=None):
        self.settings, self.store = settings, store
        self.requires_model_configuration = gateway is None
        self.gateway = gateway or ModelGateway(settings, store, streaming=True)
        self.stop = threading.Event()
        self.stack = ExitStack()

    def __enter__(self):
        try:
            self.stack.enter_context(
                FileLock(str(self.settings.data_dir / "worker.lock"), timeout=0)
            )
            if self.store.engine.dialect.name == "postgresql":
                connection = self.stack.enter_context(
                    self.store.engine.connect().execution_options(isolation_level="AUTOCOMMIT")
                )
                if not connection.scalar(text("SELECT pg_try_advisory_lock(728194602)")):
                    raise PrerequisiteError("该数据库已有 Worker，不能同时启动第二个")
                self.stack.callback(
                    lambda: connection.execute(text("SELECT pg_advisory_unlock(728194602)"))
                )
                from langgraph.checkpoint.postgres import PostgresSaver

                url = make_url(
                    local_database_url(self.settings.checkpoint_url) or self.settings.db_url
                ).set(drivername="postgresql")
                saver = self.stack.enter_context(
                    PostgresSaver.from_conn_string(url.render_as_string(hide_password=False))
                )
            else:
                saver = self.stack.enter_context(
                    SqliteSaver.from_conn_string(str(self.settings.data_dir / "checkpoints.db"))
                )
            saver.serde = JsonPlusSerializer(pickle_fallback=False, allowed_msgpack_modules=None)
            saver.setup()
            self.graph = Workflow(self.settings, self.store, self.gateway).compile(saver)
            self.store.recover()
            return self
        except BaseException:
            self.stack.close()
            raise

    def __exit__(self, *args):
        self.stack.close()

    def tick(self):
        # First-run settings must not execute model work. Existing gate rejection
        # remains available even after credentials are removed or become invalid.
        if self.requires_model_configuration and not self.settings.models_ready():
            job = self.store.claim(only_rejections=True)
        else:
            job = self.store.claim()
        if job is None:
            return False
        run_id, payload = job["run_id"], job["payload"]
        config = {"configurable": {"thread_id": run_id}, "recursion_limit": 150}
        pending = None
        try:
            snapshot = self.graph.get_state(config)
            waiting = pending_interrupt(snapshot)
            if not snapshot.values:
                run = self.store.get_run(run_id)
                self.graph.invoke(
                    {
                        "run_id": run_id,
                        "template": run["template"],
                        "round": 1,
                        "last_job_id": job["id"],
                        "attempt": 0,
                    },
                    config,
                )
            elif (
                payload["action"] in {"start", "retry"}
                or snapshot.values.get("last_job_id") == job["id"]
            ):
                # Graph progress may already be committed even though Store.finish was interrupted.
                if snapshot.next and not waiting:
                    self.graph.invoke(None, config)
            elif waiting:
                if waiting["gate_id"] != payload.get("gate_id"):
                    raise Conflict("恢复任务与当前等待版本不同，拒绝重复消费回答")
                self.graph.invoke(Command(resume={**payload, "job_id": job["id"]}), config)
            else:
                # Resume may have been persisted just before the process died.
                self.graph.invoke(None, config)
            # Explicit delegation may be enabled before starting or at any human gate.
            # Each stage gets a bounded repair allowance. Clarification repairs
            # must not consume design repairs; the global model budget still applies.
            resolutions = {}
            while True:
                snapshot = self.graph.get_state(config)
                pending = pending_interrupt(snapshot)
                if not pending or not self.store.get_run(run_id)["auto_mode"]:
                    break
                if pending["can_approve"]:
                    self.store.auto_approve(run_id, pending)
                    action = {"action": "approve", "approved": True}
                else:
                    attempts = resolutions.get(pending["stage"], 0)
                    if attempts >= 2:
                        report = blocked_report(pending, attempts)
                        report = json.loads(
                            self.settings.redact(json.dumps(report, ensure_ascii=False))
                        )
                        report_path = (
                            self.settings.data_dir / "runs" / run_id / "recommendation-blocked.json"
                        )
                        try:
                            write_json(report_path, report)
                        except OSError:
                            logger.warning(
                                "Could not write recommendation diagnostic for %s", run_id
                            )
                        raise UnsupportedScope(
                            "智能推荐已暂停（"
                            + report["stage"]
                            + "）："
                            + "；".join(report["reasons"])[:500]
                            + "。本阶段两轮自动修正仍未通过，未跳过验收。"
                            + "使用 uv run rnd chat --run "
                            + run_id
                            + " 查看阻塞详情，可继续推荐、补充要求或切换手动；无需新建运行。"
                        )
                    resolutions[pending["stage"]] = attempts + 1
                    action = {"action": "recommend", "approved": True}
                self.graph.invoke(
                    Command(resume={**action, "gate_id": pending["gate_id"], "job_id": job["id"]}),
                    config,
                )
            if pending:
                self.store.finish(job, "WAITING_" + pending["stage"].upper(), pending=pending)
            else:
                self.store.finish(
                    job,
                    snapshot.values.get("status", "FAILED"),
                    result=snapshot.values.get("delivery", {}),
                )
        except Exception as exc:
            if isinstance(exc, UnsupportedScope):
                # An exception between gates (for example review clearance) must not
                # recycle the already-consumed design gate from the automatic loop.
                pending = pending_interrupt(self.graph.get_state(config))
            # Preserve bounded, redacted tool output even when an adapter wraps the error.
            tool_error = exc
            seen = set()
            while not isinstance(tool_error, ToolFailure) and id(tool_error) not in seen:
                seen.add(id(tool_error))
                tool_error = tool_error.__cause__
                if tool_error is None:
                    break
            if isinstance(tool_error, ToolFailure):
                report = {
                    "passed": False,
                    "run_id": run_id,
                    "job_id": job["id"],
                    "error": self.settings.redact(str(tool_error))[:1000],
                    "log": self.settings.redact(getattr(tool_error, "log", ""))[:65536],
                    "returncode": getattr(tool_error, "returncode", None),
                    "timed_out": getattr(tool_error, "timed_out", False),
                }
                try:
                    write_json(
                        self.settings.data_dir / "runs" / run_id / "tool-failure.json", report
                    )
                    error = "工具执行失败；查看运行报告 tool-failure.json：" + report["error"]
                except OSError:
                    error = "工具执行失败且无法写入报告；请检查数据目录的空间及权限"
            elif isinstance(
                exc, (Conflict, ModelFailure, PrerequisiteError, PausedLimit, UnsupportedScope)
            ):
                error = str(exc)[:1000]
            else:
                frame = traceback.extract_tb(exc.__traceback__)[-1]
                error = f"{type(exc).__name__}：{Path(frame.filename).name}:{frame.lineno}（{frame.name}），请检查本次运行报告"
            error = self.settings.redact(error)
            logger.error("Run %s failed (%s)", run_id, type(exc).__name__)
            self.store.finish(
                job,
                "PAUSED_LIMIT"
                if isinstance(exc, PausedLimit)
                else "BLOCKED"
                if isinstance(exc, UnsupportedScope)
                else "FAILED",
                error=error,
                pending=pending if isinstance(exc, UnsupportedScope) else None,
            )
        return True

    def loop(self):
        while not self.stop.is_set():
            if not self.tick():
                self.stop.wait(0.25)
````
