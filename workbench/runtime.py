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
        self.gateway = gateway or ModelGateway(settings, store)
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
