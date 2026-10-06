# workbench/store.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](workbench__store_py--002.md)

**作用：持久化项目、会话、任务、版本、审批和证据。** SQLAlchemy类说明表的列，Store的方法说明事务操作。create_run建立运行和首条消息；任务认领与完成有状态约束，修订和审批保留指纹。页面状态与Worker进度不能只保存在内存变量里。

**对应关系：** api写入Store → Runtime认领Job → Workflow记录Revision/Approval/Step/Event；test_store。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.errors`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** create_project第一次使用请求键K时创建项目并保存回执；同键同内容返回原结果，同键不同标题抛Conflict。关键是状态变化与回执在同一短事务里完成；若事务中抛异常，新增记录整体回滚。审批还把gate_id绑定到确定版本，而不是只保存一个永远有效的approved标志。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `now`（L35–L36）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`datetime.now(timezone.utc).isoformat`、`datetime.now`。 返回路径：L36的`datetime.now(timezone.utc).isoformat(timespec="microseconds")`。
- `uid`（L39–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`str`、`uuid.uuid4`。 返回路径：L40的`str(uuid.uuid4())`。
- `Conflict`（L43–L44）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Missing`（L47–L48）：继承`LookupError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Base`（L51–L52）：继承`DeclarativeBase`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Project`（L55–L59）：继承`Base`。声明的数据项为`id`、`title`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Run`（L62–L75）：继承`Base`。声明的数据项为`id`、`project_id`、`template`、`status`、`pending`、`result`、`error`、`model_calls`、`options`、`auto_mode`、`created_at`、`updated_at`；类型约束/数据库列参数以完整定义为准。
- `Message`（L78–L84）：继承`Base`。声明的数据项为`id`、`run_id`、`role`、`content`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Job`（L87–L93）：继承`Base`。声明的数据项为`id`、`run_id`、`payload`、`status`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Request`（L96–L100）：继承`Base`。声明的数据项为`key`、`fingerprint`、`response`；类型约束/数据库列参数以完整定义为准。
- `Revision`（L103–L110）：继承`Base`。声明的数据项为`gate_id`、`run_id`、`stage`、`digest`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Approval`（L113–L118）：继承`Base`。声明的数据项为`gate_id`、`decision`、`actor`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Step`（L121–L128）：继承`Base`。声明的数据项为`id`、`run_id`、`name`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Event`（L131–L137）：继承`Base`。声明的数据项为`id`、`run_id`、`kind`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Store`（L140–L1012）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Store.__init__`（L141–L164）：接收`settings`。 控制顺序：L150按`self.engine.dialect.name == "sqlite"`分支。 调用`settings.prepare`、`settings.db_url.startswith`、`create_engine`、`sessionmaker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.__init__.configure`（L153–L162）：接收`connection`、`_`。 调用`_cursor`、`cursor.execute`、`event.listens_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.migrate`（L166–L171）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Config`、`str`、`config.set_main_option`、`self.engine.begin`、`command.upgrade`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.token`（L173–L182）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L175按`not path.exists()`分支。 调用`path.exists`、`path.open`、`f.write`、`secrets.token_urlsafe`、`path.chmod`、`path.read_text(encoding="utf-8").strip`、`path.read_text`。 返回路径：L182的`path.read_text(encoding="utf-8").strip()`。
- `Store.tx`（L185–L187）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.sessions.begin`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `Store.request`（L189–L192）：接收`key`、`payload`、`operation`。 调用`FileLock`、`str`、`self._request`。 返回路径：L192的`self._request(key, payload, operation)`。
- `Store._request`（L194–L208）：接收`key`、`payload`、`operation`。 控制顺序：L195按`not key or len(key) > 100`分支；L196抛异常，停止当前正常路径；L199按`self.engine.dialect.name == "postgresql"`分支；L202按`previous`分支；L203按`previous.fingerprint != fingerprint`分支；L204抛异常，停止当前正常路径。 调用`len`、`Conflict`、`digest`、`self.tx`、`session.execute`、`text`、`session.get`、`operation`、`session.add`等。 返回路径：L205的`previous.response`；L208的`response`。
- `Store.create_project`（L210–L217）：接收`title`、`key`。 调用`self.request`。 返回路径：L217的`self.request(key, {"operation": "create-project", "title": title}, operation)`。
- `Store.create_project.operation`（L211–L215）：接收`session`。 调用`Project`、`session.add`、`session.flush`。 返回路径：L215的`{"id": project.id, "title": project.title}`。
- `Store.create_run`（L219–L251）：接收`project_id`、`data`、`key`。 调用`RunInput.model_validate(data).model_dump`、`RunInput.model_validate`、`self.request`。 返回路径：L249的`self.request( key, {"operation": "create-run", "project": project_id, **data}, operation )`。
- `Store.create_run.operation`（L222–L247）：接收`session`。 控制顺序：L223按`not session.get(Project, project_id)`分支；L224抛异常，停止当前正常路径；L235按`run.auto_mode`分支。 调用`session.get`、`Missing`、`Run`、`session.add`、`session.flush`、`Message`、`Job`、`Event`。 返回路径：L247的`{"run_id": run.id, "status": "QUEUED"}`。
- `Store.submit`（L253–L311）：接收`run_id`、`data`、`key`。 控制顺序：L257遍历`("version", "digest", "answers")`；L258按`data[field] is None or data[field] == []`分支。 调用`ResumeInput.model_validate(data).model_dump`、`ResumeInput.model_validate`、`data.pop`、`self.request`。 返回路径：L311的`self.request(key, {"operation": "submit", "run_id": run_id, **data}, operation)`。
- `Store.submit.operation`（L261–L309）：接收`session`。 控制顺序：L263按`not run`分支；L264抛异常，停止当前正常路径；L266按`not pending or pending["gate_id"] != data["gate_id"]`分支；L267抛异常，停止当前正常路径；L268按`data.get("version") is not None and data["version"] != pending["version"]`分支；L269抛异常，停止当前正常路径；L270按`data.get("digest") is not None and data["digest"] != pending["digest"]`分支；L271抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`session.get`、`Missing`、`Conflict`、`data.get`、`pending.get`、`pending.get("data", {}).get`、`session.add`、`Event`、`render_answer`等。 返回路径：L309的`{"run_id": run_id, "job_id": job.id, "status": "QUEUED"}`。
- `Store._model_free_retry`（L313–L351）：接收`session`、`run`。 控制顺序：L314按`not run or run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}`分支；L322按`not stage or stage.data.get("name") != "extension_package" or stage.data.get("phase")…`分支；L331按`not previous or previous.status != "FAILED" or previous.payload.get("approved") is no…`分支；L339按`not ( revision and revision.run_id == run.id and revision.stage == "extension_scope" …`分支。 调用`session.scalar`、`select(Event) .where(Event.run_id == run.id, Event.kind == "stage…`、`select(Event) .where`、`select`、`Event.id.desc`、`stage.data.get`、`select(Job).where(Job.run_id == run.id).order_by(Job.created_at.d…`、`select(Job).where(Job.run_id == run.id).order_by`、`select(Job).where`等。 返回路径：L315的`None`；L327的`None`；L336的`None`。
- `Store.is_model_free_retry`（L353–L358）：接收`run_id`、`key`。 控制顺序：L356按`old and old.fingerprint == digest({"operation": "retry", "run_id": run_id})`分支。 调用`self.tx`、`session.get`、`digest`、`self._model_free_retry`。 返回路径：L357的`True`；L358的`self._model_free_retry(session, session.get(Run, run_id)) is not None`。
- `Store.retry`（L360–L379）：接收`run_id`、`key`、`require_model_free`。 调用`self.request`。 返回路径：L379的`self.request(key, {"operation": "retry", "run_id": run_id}, operation)`。
- `Store.retry.operation`（L361–L377）：接收`session`。 控制顺序：L363按`not run`分支；L364抛异常，停止当前正常路径；L365按`run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}`分支；L366抛异常，停止当前正常路径；L367按`run.pending and run.pending.get("data", {}).get("capability_conflicts")`分支；L368抛异常，停止当前正常路径；L370按`require_model_free and not bound_retry`分支；L371抛异常，停止当前正常路径。 调用`session.get`、`Missing`、`Conflict`、`run.pending.get("data", {}).get`、`run.pending.get`、`self._model_free_retry`、`session.add`、`Job`。 返回路径：L377的`{"run_id": run_id, "status": run.status}`。
- `Store.get_run`（L381–L389）：接收`run_id`。 控制顺序：L384按`not run`分支；L385抛异常，停止当前正常路径。 调用`self.tx`、`session.get`、`Missing`、`getattr`、`self._model_free_retry`。 返回路径：L386的`{ **{c.name: getattr(run, c.name) for c in Run.__table__.columns}, "model_free_retry": sel…`。
- `Store.messages`（L391–L396）：接收`run_id`。 调用`self.tx`、`session.scalars`、`select(Message).where(Message.run_id == run_id).order_by`、`select(Message).where`、`select`。 返回路径：L396的`[{"role": row.role, "content": row.content} for row in rows]`。
- `Store.assistant_event`（L398–L470）：接收`run_id`、`kind`、`data`。 源码说明：Append UI-only assistant events; terminal replay is idempotent. The existing Message table remains the authoritative human-input history. Assistant drafts cannot accidentally become requirements on a 。 控制顺序：L411按`kind not in allowed`分支；L412抛异常，停止当前正常路径；L415按`not session.get(Run, run_id)`分支；L416抛异常，停止当前正常路径；L433按`any(r.kind == kind for r in matching) and kind in { "assistant_start", "assistant_com…`分支；L439按`any(r.kind in {"assistant_completed", "assistant_failed"} for r in matching)`分支；L441按`kind == "assistant_start"`分支；L444遍历`rows`。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`FileLock`、`str`、`self.tx`、`session.get`、`Missing`、`list`、`session.scalars`、`select(Event) .where( Event.run_id == run_id, Event.kind.in_( {"a…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.transcript`（L472–L579）：接收`run_id`。 源码说明：One read snapshot plus cursor, suitable for replay without duplicated text.。 控制顺序：L475按`self.engine.dialect.name == "postgresql"`分支；L477按`not session.get(Run, run_id)`分支；L478抛异常，停止当前正常路径；L494遍历`session.scalars( select(Event).where(Event.run_id == run_id).orde…`；L498按`not row.kind.startswith("assistant_")`分支；L527按`row.kind == "assistant_delta"`分支；L529按`row.kind in {"assistant_completed", "assistant_failed"}`分支；L535遍历`session.scalars( select(Revision).where(Revision.run_id == run_id…`。后续分支沿下方源码相同行号继续阅读。 调用`self.tx`、`session.execute`、`text`、`session.get`、`Missing`、`str`、`session.scalars`、`select(Message).where(Message.run_id == run_id).order_by`、`select(Message).where`等。 返回路径：L579的`{"messages": messages, "cursor": cursor}`。
- `Store.step`（L581–L591）：接收`run_id`、`name`、`fn`。 控制顺序：L584按`old`分支。 调用`self.tx`、`session.scalar`、`select(Step).where`、`select`、`fn`、`json.loads`、`json.dumps`、`session.add`、`Step`等。 返回路径：L585的`old.data`；L591的`result`。
- `Store.reserve_model_call`（L593–L602）：接收`run_id`。 控制顺序：L596按`self.settings.max_model_calls`分支；L599按`changed != 1`分支；L600抛异常，停止当前正常路径。 调用`self.tx`、`update(Run).where`、`update`、`statement.where`、`session.execute`、`statement.values`、`PausedLimit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.set_automation`（L604–L666）：接收`run_id`、`enabled`、`key`。 调用`self.request`。 返回路径：L664的`self.request( key, {"operation": "automation", "run_id": run_id, "enabled": enabled}, oper…`。
- `Store.set_automation.operation`（L605–L662）：接收`session`。 控制顺序：L607按`run is None`分支；L608抛异常，停止当前正常路径；L609按`run.status in {"READY", "SOURCE_READY", "REJECTED"}`分支；L610抛异常，停止当前正常路径；L623按`enabled and run.pending and run.pending.get("data", {}).get("requires_explicit_review…`分支；L634按`enabled and run.pending and run.pending.get("data", {}).get("capability_conflicts")`分支；L643按`enabled and run.pending`分支；L656按`not enabled and run.status == "BLOCKED" and run.pending`分支。后续分支沿下方源码相同行号继续阅读。 调用`session.get`、`Missing`、`Conflict`、`session.add`、`Event`、`run.pending.get("data", {}).get`、`run.pending.get`、`Job`、`run.pending["stage"].upper`。 返回路径：L628的`{ "run_id": run_id, "auto_mode": enabled, "status": run.status, "message": "本次模块权限变更仍需明确人工…`；L637的`{ "run_id": run_id, "auto_mode": enabled, "status": run.status, "message": "当前报名入口仍需明确选择；已…`；L662的`{"run_id": run_id, "auto_mode": enabled, "status": run.status}`。
- `Store.auto_approve`（L668–L693）：接收`run_id`、`gate`。 控制顺序：L671按`not run or not run.auto_mode or not gate["can_approve"] or gate.get("data", {}).get("…`分支；L677抛异常，停止当前正常路径；L679按`current and not current.decision`分支；L680抛异常，停止当前正常路径；L681按`not current`分支。 调用`self.tx`、`session.get`、`gate.get("data", {}).get`、`gate.get`、`Conflict`、`session.add`、`Approval`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.record_event`（L695–L697）：接收`run_id`、`kind`、`data`。 调用`self.tx`、`session.add`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.model_records`（L699–L731）：接收`run_id`。 调用`self.get_run`、`self.tx`、`session.scalars`、`select(Step) .where(Step.run_id == run_id, Step.name.like("model:…`、`select(Step) .where`、`select`、`Step.name.like`、`r.data.get`、`select(Event) .where(Event.run_id == run_id, Event.kind == "model…`等。 返回路径：L731的`sorted(records, key=lambda item: item["created_at"])`。
- `Store.gate`（L733–L755）：接收`run_id`、`stage`、`version`、`data`、`actions`、`can_approve`。 控制顺序：L737按`not session.get(Revision, gate_id)`分支。 调用`digest`、`self.tx`、`session.get`、`session.add`、`Revision`。 返回路径：L747的`{ "gate_id": gate_id, "stage": stage, "version": version, "digest": content_digest, "data"…`。
- `Store.check_decision`（L757–L780）：接收`run_id`、`gate`、`value`。 控制顺序：L758按`not isinstance(value, dict)`分支；L759抛异常，停止当前正常路径；L760按`value.get("gate_id") != gate["gate_id"] or ( value.get("action") not in gate["actions…`分支；L763抛异常，停止当前正常路径；L764按`value["action"] == "recommend"`分支；L765按`gate.get("data", {}).get("requires_explicit_review")`分支；L766抛异常，停止当前正常路径；L767按`value.get("approved") is not True or not self.get_run(run_id)["auto_mode"]`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`Conflict`、`value.get`、`gate.get("data", {}).get`、`gate.get`、`self.get_run`、`self.tx`、`session.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.explicit_approval`（L782–L805）：接收`run_id`、`stage`、`data`、`version`。 源码说明：Read the durable operator decision, never a model/candidate receipt.。 控制顺序：L798遍历`rows`；L799按`approval.decision is True and approval.actor == "local-operator"`分支；L805抛异常，停止当前正常路径。 调用`digest`、`self.tx`、`session.execute`、`select(Revision, Approval) .join(Approval, Approval.gate_id == Re…`、`select(Revision, Approval) .join`、`select`、`Revision.created_at.desc`、`Conflict`。 返回路径：L800的`{ "gate_id": revision.gate_id, "data_digest": content_digest, "actor": approval.actor, }`。
- `Store.is_model_free_approval`（L807–L822）：接收`run_id`、`data`。 源码说明：Use the controller's immutable gate, never a client-supplied stage. submit still validates the current pending gate, approval and idempotency. Reading the revision also permits an exact idempotent rep。 控制顺序：L814按`data.get("action") != "approve" or data.get("approved") is not True`分支。 调用`data.get`、`self.tx`、`session.get`、`bool`。 返回路径：L815的`False`；L818的`bool( revision and revision.run_id == run_id and revision.stage in MODEL_FREE_APPROVAL_STA…`。
- `Store.claim`（L824–L853）：接收`only_rejections`、`include_model_free`。 控制顺序：L827按`only_rejections`分支；L829按`include_model_free`分支；L844按`job is None`分支；L849按`changed != 1`分支。 调用`self.tx`、`select(Job).where`、`select`、`Job.payload["action"].as_string`、`select(Revision.gate_id).where`、`Revision.stage.in_`、`or_`、`and_`、`Job.payload["action"].as_string().in_`等。 返回路径：L845的`None`；L850的`None`；L853的`{"id": job.id, "run_id": job.run_id, "payload": job.payload}`。
- `Store.recover`（L855–L865）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L863遍历`runs`。 调用`FileLock`、`str`、`self.tx`、`list`、`session.scalars`、`select(Job.run_id).where(Job.status == "RUNNING").distinct`、`select(Job.run_id).where`、`select`、`self._recover_assistants`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/store.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L866。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`38393`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/store.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "f84474cb685dd75f325c3cf5b75f19b1c76f67265d3f3890913d437c95271514"} -->
````python
# workbench/store.py
"""Short SQLAlchemy transactions; no model/tool calls inside a database transaction."""

import json
import secrets
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from alembic import command
from alembic.config import Config
from filelock import FileLock
from sqlalchemy import (
    JSON,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    and_,
    create_engine,
    event,
    or_,
    select,
    text,
    update,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from workbench.domain import ResumeInput, RunInput, digest
from workbench.errors import PausedLimit
from workbench.settings import ROOT, Settings

MODEL_FREE_APPROVAL_STAGES = frozenset({"extension_scope", "extension_delivery"})


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def uid():
    return str(uuid.uuid4())


class Conflict(ValueError):
    pass


class Missing(LookupError):
    pass


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    template: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(50), default="QUEUED")
    pending: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_calls: Mapped[int] = mapped_column(default=0)
    options: Mapped[dict] = mapped_column(JSON, default=dict)
    auto_mode: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[str] = mapped_column(String(40), default=now)
    updated_at: Mapped[str] = mapped_column(String(40), default=now, onupdate=now)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED", index=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Request(Base):
    __tablename__ = "requests"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSON)


class Revision(Base):
    __tablename__ = "revisions"
    gate_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(40))
    digest: Mapped[str] = mapped_column(String(64))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Approval(Base):
    __tablename__ = "approvals"
    gate_id: Mapped[str] = mapped_column(ForeignKey("revisions.gate_id"), primary_key=True)
    decision: Mapped[bool] = mapped_column()
    actor: Mapped[str] = mapped_column(String(40), default="local-operator")
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Step(Base):
    __tablename__ = "steps"
    __table_args__ = (UniqueConstraint("run_id", "name", name="uq_steps_run_name"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    kind: Mapped[str] = mapped_column(String(50))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.prepare()
        args = (
            {"check_same_thread": False, "autocommit": False}
            if settings.db_url.startswith("sqlite:")
            else {}
        )
        self.engine = create_engine(settings.db_url, connect_args=args, pool_pre_ping=True)
        if self.engine.dialect.name == "sqlite":

            @event.listens_for(self.engine, "connect")
            def configure(connection, _):
                old = connection.autocommit
                connection.autocommit = True
                try:
                    with _cursor(connection) as cursor:
                        cursor.execute("PRAGMA foreign_keys=ON")
                        cursor.execute("PRAGMA busy_timeout=10000")
                        cursor.execute("PRAGMA journal_mode=WAL")
                finally:
                    connection.autocommit = old

        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    def migrate(self):
        config = Config(str(ROOT / "alembic.ini"))
        config.set_main_option("script_location", str(ROOT / "migrations"))
        with self.engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")

    def token(self):
        path = self.settings.data_dir / "access-token"
        if not path.exists():
            try:
                with path.open("x", encoding="utf-8") as f:
                    f.write(secrets.token_urlsafe(32))
                path.chmod(0o600)
            except FileExistsError:
                pass
        return path.read_text(encoding="utf-8").strip()

    @contextmanager
    def tx(self):
        with self.sessions.begin() as session:
            yield session

    def request(self, key, payload, operation):
        # Serialise local API mutations. PostgreSQL additionally uses a short DB lock.
        with FileLock(str(self.settings.data_dir / "requests.lock"), timeout=30):
            return self._request(key, payload, operation)

    def _request(self, key, payload, operation):
        if not key or len(key) > 100:
            raise Conflict("Idempotency-Key 必填且长度不超过 100")
        fingerprint = digest(payload)
        with self.tx() as session:
            if self.engine.dialect.name == "postgresql":
                session.execute(text("SELECT pg_advisory_xact_lock(728194601)"))
            previous = session.get(Request, key)
            if previous:
                if previous.fingerprint != fingerprint:
                    raise Conflict("相同 Idempotency-Key 不能用于不同请求")
                return previous.response
            response = operation(session)
            session.add(Request(key=key, fingerprint=fingerprint, response=response))
            return response

    def create_project(self, title, key):
        def operation(session):
            project = Project(title=title)
            session.add(project)
            session.flush()
            return {"id": project.id, "title": project.title}

        return self.request(key, {"operation": "create-project", "title": title}, operation)

    def create_run(self, project_id, data, key):
        data = RunInput.model_validate(data).model_dump()

        def operation(session):
            if not session.get(Project, project_id):
                raise Missing("项目不存在")
            run = Run(
                project_id=project_id,
                template=data["template"],
                options=data["selection"],
                auto_mode=data["intelligent"],
            )
            session.add(run)
            session.flush()
            session.add(Message(run_id=run.id, role="user", content=data["requirement"]))
            session.add(Job(run_id=run.id, payload={"action": "start"}))
            if run.auto_mode:
                session.add(
                    Event(
                        run_id=run.id,
                        kind="delegation",
                        data={
                            "enabled": True,
                            "actor": "local-operator",
                            "scope": "choose missing details and approve subsequent design/delivery; never bypass tests",
                        },
                    )
                )
            return {"run_id": run.id, "status": "QUEUED"}

        return self.request(
            key, {"operation": "create-run", "project": project_id, **data}, operation
        )

    def submit(self, run_id, data, key):
        data = ResumeInput.model_validate(data).model_dump()
        # Keep pre-upgrade idempotency fingerprints byte-equivalent when the
        # optional browser-only review metadata/choices were not supplied.
        for field in ("version", "digest", "answers"):
            if data[field] is None or data[field] == []:
                data.pop(field)

        def operation(session):
            run = session.get(Run, run_id)
            if not run:
                raise Missing("运行不存在")
            pending = run.pending
            if not pending or pending["gate_id"] != data["gate_id"]:
                raise Conflict("审批/回答版本已变化，请重新读取运行状态")
            if data.get("version") is not None and data["version"] != pending["version"]:
                raise Conflict("审批/回答版本已变化，请重新读取运行状态")
            if data.get("digest") is not None and data["digest"] != pending["digest"]:
                raise Conflict("审批/回答内容已变化，请重新审阅当前版本")
            if data["action"] not in pending["actions"] and data["action"] != "recommend":
                raise Conflict("当前阶段不接受这个动作")
            if data["action"] == "approve" and not pending.get("can_approve", False):
                raise Conflict("存在未支持项或先决条件尚未满足，不能批准")
            if data["action"] == "recommend" and pending.get("data", {}).get(
                "requires_explicit_review"
            ):
                raise Conflict("本次权限或依赖变更需要明确人工审阅，不能智能推荐批准")
            if data["action"] == "recommend" and pending.get("data", {}).get(
                "capability_conflicts"
            ):
                raise Conflict("模板能力尚未改变；智能推荐不能取消明确需求，请先答复范围选择")
            if data["action"] == "recommend":
                run.auto_mode = True
                session.add(
                    Event(
                        run_id=run_id,
                        kind="delegation",
                        data={
                            "enabled": True,
                            "actor": "local-operator",
                            "gate_id": pending["gate_id"],
                        },
                    )
                )
            if data["action"] in {"answer", "revise"}:
                from workbench.clarification import render_answer

                answer_text = render_answer(pending, data)
                session.add(Message(run_id=run_id, role="user", content=answer_text))
            if data["action"] in {"approve", "reject"}:
                session.add(Approval(gate_id=pending["gate_id"], decision=data["approved"]))
            job = Job(run_id=run_id, payload=dict(data))
            session.add(job)
            session.flush()
            run.pending = None
            run.status, run.error = "QUEUED", None
            return {"run_id": run_id, "job_id": job.id, "status": "QUEUED"}

        return self.request(key, {"operation": "submit", "run_id": run_id, **data}, operation)

    def _model_free_retry(self, session, run):
        if not run or run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}:
            return None
        stage = session.scalar(
            select(Event)
            .where(Event.run_id == run.id, Event.kind == "stage")
            .order_by(Event.id.desc())
            .limit(1)
        )
        if (
            not stage
            or stage.data.get("name") != "extension_package"
            or stage.data.get("phase") != "failed"
        ):
            return None
        previous = session.scalar(
            select(Job).where(Job.run_id == run.id).order_by(Job.created_at.desc()).limit(1)
        )
        if (
            not previous
            or previous.status != "FAILED"
            or previous.payload.get("approved") is not True
        ):
            return None
        gate_id = previous.payload.get("gate_id", "")
        revision, approval = session.get(Revision, gate_id), session.get(Approval, gate_id)
        if not (
            revision
            and revision.run_id == run.id
            and revision.stage == "extension_scope"
            and approval
            and approval.decision is True
        ):
            return None
        return {
            "gate_id": gate_id,
            "approved": True,
            "resume_from_job_id": previous.payload.get("resume_from_job_id", previous.id),
        }

    def is_model_free_retry(self, run_id, key=None):
        with self.tx() as session:
            old = session.get(Request, key) if key else None
            if old and old.fingerprint == digest({"operation": "retry", "run_id": run_id}):
                return True  # Exact replay returns its recorded response; it enqueues no work.
            return self._model_free_retry(session, session.get(Run, run_id)) is not None

    def retry(self, run_id, key, *, require_model_free=False):
        def operation(session):
            run = session.get(Run, run_id)
            if not run:
                raise Missing("运行不存在")
            if run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}:
                raise Conflict("只有 FAILED、BLOCKED 或 PAUSED_LIMIT 状态可以重试")
            if run.pending and run.pending.get("data", {}).get("capability_conflicts"):
                raise Conflict("模板能力尚未改变，重复重试不会解决；请先答复当前范围选择")
            bound_retry = self._model_free_retry(session, run)
            if require_model_free and not bound_retry:
                raise Conflict("无模型重试仅支持准确范围审批后的已保存打包阶段")
            session.add(Job(run_id=run_id, payload={"action": "retry", **(bound_retry or {})}))
            # The graph owns the saved interrupt. Hide the stale Store copy
            # while queued so a second request cannot consume it concurrently.
            run.pending = None
            run.status, run.error = "QUEUED", None
            return {"run_id": run_id, "status": run.status}

        return self.request(key, {"operation": "retry", "run_id": run_id}, operation)

    def get_run(self, run_id):
        with self.tx() as session:
            run = session.get(Run, run_id)
            if not run:
                raise Missing("运行不存在")
            return {
                **{c.name: getattr(run, c.name) for c in Run.__table__.columns},
                "model_free_retry": self._model_free_retry(session, run) is not None,
            }

    def messages(self, run_id):
        with self.tx() as session:
            rows = session.scalars(
                select(Message).where(Message.run_id == run_id).order_by(Message.id)
            )
            return [{"role": row.role, "content": row.content} for row in rows]

    def assistant_event(self, run_id, kind, data):
        """Append UI-only assistant events; terminal replay is idempotent.

        The existing Message table remains the authoritative human-input history.
        Assistant drafts cannot accidentally become requirements on a later round.
        """
        allowed = {
            "assistant_start",
            "assistant_status",
            "assistant_delta",
            "assistant_completed",
            "assistant_failed",
        }
        if kind not in allowed:
            raise ValueError("unsupported_assistant_event")
        with FileLock(str(self.settings.data_dir / "assistant-events.lock"), timeout=30):
            with self.tx() as session:
                if not session.get(Run, run_id):
                    raise Missing("运行不存在")
                rows = list(
                    session.scalars(
                        select(Event)
                        .where(
                            Event.run_id == run_id,
                            Event.kind.in_(
                                {"assistant_start", "assistant_completed", "assistant_failed"}
                            ),
                            Event.data["response_id"].as_string() == data.get("response_id")
                            if kind == "assistant_start"
                            else Event.data["message_id"].as_string() == data["message_id"],
                        )
                        .order_by(Event.id)
                    )
                )
                matching = [r for r in rows if r.data.get("message_id") == data["message_id"]]
                if any(r.kind == kind for r in matching) and kind in {
                    "assistant_start",
                    "assistant_completed",
                    "assistant_failed",
                }:
                    return
                if any(r.kind in {"assistant_completed", "assistant_failed"} for r in matching):
                    return
                if kind == "assistant_start":
                    # A restarted worker cannot leave an old attempt apparently streaming.
                    old = {}
                    for row in rows:
                        if row.data.get("response_id") == data.get("response_id"):
                            old[row.data["message_id"]] = row
                    for row in old.values():
                        if row.kind not in {"assistant_completed", "assistant_failed"}:
                            session.add(
                                Event(
                                    run_id=run_id,
                                    kind="assistant_failed",
                                    data={
                                        **{
                                            k: row.data.get(k)
                                            for k in (
                                                "message_id",
                                                "response_id",
                                                "stage",
                                                "transport",
                                            )
                                        },
                                        "validation": "failed",
                                        "status": "failed",
                                        "code": "worker_interrupted",
                                        "content": "",
                                    },
                                )
                            )
                session.add(Event(run_id=run_id, kind=kind, data=dict(data)))

    def transcript(self, run_id):
        """One read snapshot plus cursor, suitable for replay without duplicated text."""
        with self.tx() as session:
            if self.engine.dialect.name == "postgresql":
                session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
            if not session.get(Run, run_id):
                raise Missing("运行不存在")
            messages = [
                {
                    "message_id": "user-" + str(row.id),
                    "role": row.role,
                    "content": row.content,
                    "created_at": row.created_at,
                    "status": "completed",
                    "validation": "user",
                    "transport": None,
                }
                for row in session.scalars(
                    select(Message).where(Message.run_id == run_id).order_by(Message.id)
                )
            ]
            assistants, cursor = {}, 0
            for row in session.scalars(
                select(Event).where(Event.run_id == run_id).order_by(Event.id)
            ):
                cursor = row.id
                if not row.kind.startswith("assistant_"):
                    continue
                data = row.data
                message_id = data["message_id"]
                item = assistants.setdefault(
                    message_id,
                    {
                        "message_id": message_id,
                        "role": "assistant",
                        "content": "",
                        "created_at": row.created_at,
                        "status": "streaming",
                    },
                )
                item.update(
                    {
                        k: data[k]
                        for k in (
                            "stage",
                            "response_id",
                            "validation",
                            "transport",
                            "status",
                            "code",
                            "diagnostic",
                        )
                        if k in data
                    }
                )
                if row.kind == "assistant_delta":
                    item["content"] += data["text"]
                elif row.kind in {"assistant_completed", "assistant_failed"}:
                    item["content"] = data.get("content", "")
                item["event_id"] = row.id
            # Revisions are immutable, durable gate snapshots. Project the user-facing
            # clarification only, never the full plan or model internals. This also
            # recovers history created before the transcript UI existed.
            for revision in session.scalars(
                select(Revision).where(Revision.run_id == run_id).order_by(Revision.created_at)
            ):
                data = revision.data or {}
                requirement = data.get("requirement", {})
                questions = requirement.get("questions", [])
                items = requirement.get("question_items", [])
                conflicts = data.get("capability_conflicts", [])
                blocked = data.get("blocked") or requirement.get("unsupported", [])
                if not any((questions, items, conflicts, blocked)):
                    continue
                lines = ["历史澄清与模板能力提示（保留记录，不代表当前仍未解决）"]
                lines.extend(str(question) for question in questions)
                for item in items:
                    if item.get("prompt") not in questions:
                        lines.append(str(item.get("prompt", "")))
                    lines.extend(
                        "可选：" + str(option.get("label", ""))
                        for option in item.get("options", [])
                    )
                for conflict in conflicts:
                    lines.append(str(conflict.get("message", "")))
                    lines.extend(
                        "替代路径：" + str(value) for value in conflict.get("alternatives", [])
                    )
                lines.extend(
                    "能力限制：" + str(value)
                    for value in (blocked if isinstance(blocked, list) else [blocked])
                )
                messages.append(
                    {
                        "message_id": "gate-" + revision.gate_id,
                        "role": "assistant",
                        "content": self.settings.redact("\n".join(lines)),
                        "created_at": revision.created_at,
                        "stage": revision.stage,
                        "gate_id": revision.gate_id,
                        "validation": "historical_gate",
                        "status": "completed",
                        "transport": None,
                    }
                )
            messages.extend(assistants.values())
            messages.sort(key=lambda item: (item["created_at"], item["message_id"]))
            return {"messages": messages, "cursor": cursor}

    def step(self, run_id, name, fn):
        with self.tx() as session:
            old = session.scalar(select(Step).where(Step.run_id == run_id, Step.name == name))
            if old:
                return old.data
        result = fn()
        result = json.loads(json.dumps(result, ensure_ascii=False))
        with self.tx() as session:
            session.add(Step(run_id=run_id, name=name, data=result))
            session.add(Event(run_id=run_id, kind="step", data={"name": name}))
        return result

    def reserve_model_call(self, run_id):
        with self.tx() as session:
            statement = update(Run).where(Run.id == run_id)
            if self.settings.max_model_calls:
                statement = statement.where(Run.model_calls < self.settings.max_model_calls)
            changed = session.execute(statement.values(model_calls=Run.model_calls + 1)).rowcount
            if changed != 1:
                raise PausedLimit(
                    "已到达你配置的模型预算；回答已保存。调整 MAX_MODEL_CALLS 后重试同一运行，无需重建。"
                )

    def set_automation(self, run_id, enabled, key):
        def operation(session):
            run = session.get(Run, run_id)
            if run is None:
                raise Missing("运行不存在")
            if run.status in {"READY", "SOURCE_READY", "REJECTED"}:
                raise Conflict("已结束运行不能更改自动决策授权")
            run.auto_mode = enabled
            session.add(
                Event(
                    run_id=run_id,
                    kind="delegation",
                    data={
                        "enabled": enabled,
                        "actor": "local-operator",
                        "scope": "remaining decisions; cannot bypass tests",
                    },
                )
            )
            if (
                enabled
                and run.pending
                and run.pending.get("data", {}).get("requires_explicit_review")
            ):
                return {
                    "run_id": run_id,
                    "auto_mode": enabled,
                    "status": run.status,
                    "message": "本次模块权限变更仍需明确人工审批；自动模式不会消费当前关卡",
                }
            if enabled and run.pending and run.pending.get("data", {}).get("capability_conflicts"):
                # Delegation can choose missing details, not cancel a user's goal.
                # Keep this exact gate and avoid a new model job for known limits.
                return {
                    "run_id": run_id,
                    "auto_mode": enabled,
                    "status": run.status,
                    "message": "当前报名入口仍需明确选择；已保留关卡，未发起新的模型请求",
                }
            if enabled and run.pending:
                session.add(
                    Job(
                        run_id=run_id,
                        payload={
                            "action": "recommend",
                            "gate_id": run.pending["gate_id"],
                            "approved": True,
                        },
                    )
                )
                run.pending = None
                run.status, run.error = "QUEUED", None
            elif not enabled and run.status == "BLOCKED" and run.pending:
                run.status = "WAITING_" + run.pending["stage"].upper()
                run.error = None
            elif enabled and run.status in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}:
                session.add(Job(run_id=run_id, payload={"action": "retry"}))
                run.status, run.error = "QUEUED", None
            return {"run_id": run_id, "auto_mode": enabled, "status": run.status}

        return self.request(
            key, {"operation": "automation", "run_id": run_id, "enabled": enabled}, operation
        )

    def auto_approve(self, run_id, gate):
        with self.tx() as session:
            run = session.get(Run, run_id)
            if (
                not run
                or not run.auto_mode
                or not gate["can_approve"]
                or gate.get("data", {}).get("requires_explicit_review")
            ):
                raise Conflict("没有有效智能推荐授权，或存在不能自动通过的阻塞项")
            current = session.get(Approval, gate["gate_id"])
            if current and not current.decision:
                raise Conflict("已拒绝的版本不能被智能推荐重新批准")
            if not current:
                session.add(Approval(gate_id=gate["gate_id"], decision=True, actor="delegated-ai"))
                session.add(
                    Event(
                        run_id=run_id,
                        kind="auto-decision",
                        data={
                            "gate_id": gate["gate_id"],
                            "stage": gate["stage"],
                            "digest": gate["digest"],
                        },
                    )
                )

    def record_event(self, run_id, kind, data):
        with self.tx() as session:
            session.add(Event(run_id=run_id, kind=kind, data=data))

    def model_records(self, run_id):
        self.get_run(run_id)
        with self.tx() as session:
            rows = session.scalars(
                select(Step)
                .where(Step.run_id == run_id, Step.name.like("model:%"))
                .order_by(Step.id)
            )
            records = [
                {
                    "step": r.name,
                    "stage": r.data.get("stage", "legacy"),
                    "model": r.data.get("model"),
                    "endpoint": r.data.get("endpoint"),
                    "usage": r.data.get("usage"),
                    "provider": r.data.get("provider", "legacy"),
                    "output_mode": r.data.get("output_mode", "legacy"),
                    "format_reason": r.data.get("format_reason", "legacy"),
                    "contract_version": r.data.get("contract_version", 0),
                    "structured_output": r.data.get("structured_output", "legacy"),
                    "finish_reason": r.data.get("finish_reason", "unknown"),
                    "status": "validated" if r.data.get("contract_version") else "legacy",
                    "created_at": r.created_at,
                }
                for r in rows
            ]
            failures = session.scalars(
                select(Event)
                .where(Event.run_id == run_id, Event.kind == "model_failure")
                .order_by(Event.id)
            )
            records.extend({**r.data, "created_at": r.created_at} for r in failures)
            return sorted(records, key=lambda item: item["created_at"])

    def gate(self, run_id, stage, version, data, actions, can_approve=True):
        content_digest = digest(data)
        gate_id = digest([run_id, stage, version, content_digest])
        with self.tx() as session:
            if not session.get(Revision, gate_id):
                session.add(
                    Revision(
                        gate_id=gate_id,
                        run_id=run_id,
                        stage=stage,
                        digest=content_digest,
                        data=data,
                    )
                )
        return {
            "gate_id": gate_id,
            "stage": stage,
            "version": version,
            "digest": content_digest,
            "data": data,
            "actions": actions,
            "can_approve": can_approve,
        }

    def check_decision(self, run_id, gate, value):
        if not isinstance(value, dict):
            raise Conflict("工作流恢复需要结构化输入")
        if value.get("gate_id") != gate["gate_id"] or (
            value.get("action") not in gate["actions"] and value.get("action") != "recommend"
        ):
            raise Conflict("工作流恢复凭据与等待点不一致")
        if value["action"] == "recommend":
            if gate.get("data", {}).get("requires_explicit_review"):
                raise Conflict("该模块权限变更需要明确人工审批")
            if value.get("approved") is not True or not self.get_run(run_id)["auto_mode"]:
                raise Conflict("没有有效的智能推荐授权")
        if value["action"] == "approve" and not gate.get("can_approve", False):
            raise Conflict("不能批准被阻塞的版本")
        if value["action"] in {"approve", "reject"}:
            if value.get("approved") is not (value["action"] == "approve"):
                raise Conflict("审批必须使用匹配的布尔值")
            with self.tx() as session:
                revision = session.get(Revision, gate["gate_id"])
                approval = session.get(Approval, gate["gate_id"])
                if not revision or revision.run_id != run_id or not approval:
                    raise Conflict("缺少人工审批记录")
                if approval.decision is not (value["action"] == "approve"):
                    raise Conflict("审批决定不一致")

    def explicit_approval(self, run_id, stage, data, *, version):
        """Read the durable operator decision, never a model/candidate receipt."""
        content_digest = digest(data)
        gate_id = digest([run_id, stage, version, content_digest])
        with self.tx() as session:
            rows = session.execute(
                select(Revision, Approval)
                .join(Approval, Approval.gate_id == Revision.gate_id)
                .where(
                    Revision.run_id == run_id,
                    Revision.stage == stage,
                    Revision.digest == content_digest,
                    Revision.gate_id == gate_id,
                )
                .order_by(Revision.created_at.desc())
            )
            for revision, approval in rows:
                if approval.decision is True and approval.actor == "local-operator":
                    return {
                        "gate_id": revision.gate_id,
                        "data_digest": content_digest,
                        "actor": approval.actor,
                    }
        raise Conflict("当前准确来源、合同和证据缺少明确人工审批；自动或模型回执不能替代")

    def is_model_free_approval(self, run_id, data):
        """Use the controller's immutable gate, never a client-supplied stage.

        submit still validates the current pending gate, approval and idempotency.
        Reading the revision also permits an exact idempotent replay after submit
        has cleared Run.pending; it does not itself enqueue or approve anything.
        """
        if data.get("action") != "approve" or data.get("approved") is not True:
            return False
        with self.tx() as session:
            revision = session.get(Revision, data.get("gate_id", ""))
            return bool(
                revision
                and revision.run_id == run_id
                and revision.stage in MODEL_FREE_APPROVAL_STAGES
            )

    def claim(self, *, only_rejections=False, include_model_free=False):
        with self.tx() as session:
            statement = select(Job).where(Job.status == "QUEUED")
            if only_rejections:
                eligible = Job.payload["action"].as_string() == "reject"
                if include_model_free:
                    approved_gate = select(Revision.gate_id).where(
                        Revision.run_id == Job.run_id,
                        Revision.stage.in_(MODEL_FREE_APPROVAL_STAGES),
                    )
                    eligible = or_(
                        eligible,
                        and_(
                            Job.payload["action"].as_string().in_({"approve", "retry"}),
                            Job.payload["approved"].as_boolean().is_(True),
                            Job.payload["gate_id"].as_string().in_(approved_gate),
                        ),
                    )
                statement = statement.where(eligible)
            job = session.scalar(statement.order_by(Job.created_at).limit(1))
            if job is None:
                return None
            changed = session.execute(
                update(Job).where(Job.id == job.id, Job.status == "QUEUED").values(status="RUNNING")
            ).rowcount
            if changed != 1:
                return None
            run = session.get(Run, job.run_id)
            run.status = "RUNNING"
            return {"id": job.id, "run_id": job.run_id, "payload": job.payload}

    def recover(self):
        # Runtime holds the single-worker lock before recovery. Serialize with
        # assistant appenders as well, and commit transcript repair with requeue.
        with FileLock(str(self.settings.data_dir / "assistant-events.lock"), timeout=30):
            with self.tx() as session:
                runs = list(
                    session.scalars(select(Job.run_id).where(Job.status == "RUNNING").distinct())
                )
                for run_id in runs:
                    self._recover_assistants(session, run_id)
                session.execute(update(Job).where(Job.status == "RUNNING").values(status="QUEUED"))

````
