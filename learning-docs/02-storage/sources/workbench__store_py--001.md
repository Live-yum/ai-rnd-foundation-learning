# workbench/store.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](workbench__store_py--002.md)

**作用：持久化项目、会话、任务、版本、审批和证据。** SQLAlchemy类说明表的列，Store的方法说明事务操作。create_run和create_batch共享入队逻辑；批量先整批校验再在同一幂等事务建立项目、运行和消息，失败全部回滚。任务认领与完成有状态约束，修订和审批保留指纹。页面状态与Worker进度不能只保存在内存变量里。

**对应关系：** api写入Store → Runtime认领Job → Workflow记录Revision/Approval/Step/Event；test_store。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.errors`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** create_project第一次使用请求键K时创建项目并保存回执；同键同内容返回原结果，同键不同标题抛Conflict。关键是状态变化与回执在同一短事务里完成；若事务中抛异常，新增记录整体回滚。审批还把gate_id绑定到确定版本，而不是只保存一个永远有效的approved标志。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `action_needs_model`（L35–L36）：接收`stage`、`action`。 返回路径：L36的`action != "reject" and not (action == "approve" and stage in MODEL_FREE_APPROVAL_STAGES)`。
- `now`（L39–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`datetime.now(timezone.utc).isoformat`、`datetime.now`。 返回路径：L40的`datetime.now(timezone.utc).isoformat(timespec="microseconds")`。
- `uid`（L43–L44）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`str`、`uuid.uuid4`。 返回路径：L44的`str(uuid.uuid4())`。
- `Conflict`（L47–L48）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Missing`（L51–L52）：继承`LookupError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Base`（L55–L56）：继承`DeclarativeBase`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Project`（L59–L63）：继承`Base`。声明的数据项为`id`、`title`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Run`（L66–L79）：继承`Base`。声明的数据项为`id`、`project_id`、`template`、`status`、`pending`、`result`、`error`、`model_calls`、`options`、`auto_mode`、`created_at`、`updated_at`；类型约束/数据库列参数以完整定义为准。
- `Message`（L82–L88）：继承`Base`。声明的数据项为`id`、`run_id`、`role`、`content`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Job`（L91–L97）：继承`Base`。声明的数据项为`id`、`run_id`、`payload`、`status`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Request`（L100–L104）：继承`Base`。声明的数据项为`key`、`fingerprint`、`response`；类型约束/数据库列参数以完整定义为准。
- `Revision`（L107–L114）：继承`Base`。声明的数据项为`gate_id`、`run_id`、`stage`、`digest`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Approval`（L117–L122）：继承`Base`。声明的数据项为`gate_id`、`decision`、`actor`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Step`（L125–L132）：继承`Base`。声明的数据项为`id`、`run_id`、`name`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Event`（L135–L141）：继承`Base`。声明的数据项为`id`、`run_id`、`kind`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Store`（L144–L1052）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Store.__init__`（L145–L168）：接收`settings`。 控制顺序：L154按`self.engine.dialect.name == "sqlite"`分支。 调用`settings.prepare`、`settings.db_url.startswith`、`create_engine`、`sessionmaker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.__init__.configure`（L157–L166）：接收`connection`、`_`。 调用`_cursor`、`cursor.execute`、`event.listens_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.migrate`（L170–L175）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Config`、`str`、`config.set_main_option`、`self.engine.begin`、`command.upgrade`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.token`（L177–L186）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L179按`not path.exists()`分支。 调用`path.exists`、`path.open`、`f.write`、`secrets.token_urlsafe`、`path.chmod`、`path.read_text(encoding="utf-8").strip`、`path.read_text`。 返回路径：L186的`path.read_text(encoding="utf-8").strip()`。
- `Store.tx`（L189–L191）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.sessions.begin`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `Store.request`（L193–L196）：接收`key`、`payload`、`operation`。 调用`FileLock`、`str`、`self._request`。 返回路径：L196的`self._request(key, payload, operation)`。
- `Store._request`（L198–L212）：接收`key`、`payload`、`operation`。 控制顺序：L199按`not key or len(key) > 100`分支；L200抛异常，停止当前正常路径；L203按`self.engine.dialect.name == "postgresql"`分支；L206按`previous`分支；L207按`previous.fingerprint != fingerprint`分支；L208抛异常，停止当前正常路径。 调用`len`、`Conflict`、`digest`、`self.tx`、`session.execute`、`text`、`session.get`、`operation`、`session.add`等。 返回路径：L209的`previous.response`；L212的`response`。
- `Store.create_project`（L214–L221）：接收`title`、`key`。 调用`self.request`。 返回路径：L221的`self.request(key, {"operation": "create-project", "title": title}, operation)`。
- `Store.create_project.operation`（L215–L219）：接收`session`。 调用`Project`、`session.add`、`session.flush`。 返回路径：L219的`{"id": project.id, "title": project.title}`。
- `Store.create_run`（L223–L233）：接收`project_id`、`data`、`key`。 调用`RunInput.model_validate(data).model_dump`、`RunInput.model_validate`、`self.request`。 返回路径：L231的`self.request( key, {"operation": "create-run", "project": project_id, **data}, operation )`。
- `Store.create_run.operation`（L226–L229）：接收`session`。 控制顺序：L227按`not session.get(Project, project_id)`分支；L228抛异常，停止当前正常路径。 调用`session.get`、`Missing`、`self._enqueue_run`。 返回路径：L229的`self._enqueue_run(session, project_id, data)`。
- `Store.create_batch`（L235–L249）：接收`data`、`key`。 源码说明：Validate then create all projects and jobs in one idempotent transaction.。 调用`BatchInput.model_validate(data).model_dump`、`BatchInput.model_validate`、`self.request`。 返回路径：L249的`self.request(key, {"operation": "create-batch", **data}, operation)`。
- `Store.create_batch.operation`（L239–L247）：接收`session`。 控制顺序：L241遍历`data["items"]`。 调用`Project`、`session.add`、`session.flush`、`self._enqueue_run`、`items.append`。 返回路径：L247的`{"items": items}`。
- `Store._enqueue_run`（L251–L278）：接收`session`、`project_id`、`data`。 源码说明：Single and batch creation share the same durable worker and delegation.。 控制顺序：L266按`run.auto_mode`分支。 调用`Run`、`session.add`、`session.flush`、`Message`、`Job`、`Event`。 返回路径：L278的`{"run_id": run.id, "status": "QUEUED"}`。
- `Store.submit`（L280–L338）：接收`run_id`、`data`、`key`。 控制顺序：L284遍历`("version", "digest", "answers")`；L285按`data[field] is None or data[field] == []`分支。 调用`ResumeInput.model_validate(data).model_dump`、`ResumeInput.model_validate`、`data.pop`、`self.request`。 返回路径：L338的`self.request(key, {"operation": "submit", "run_id": run_id, **data}, operation)`。
- `Store.submit.operation`（L288–L336）：接收`session`。 控制顺序：L290按`not run`分支；L291抛异常，停止当前正常路径；L293按`not pending or pending["gate_id"] != data["gate_id"]`分支；L294抛异常，停止当前正常路径；L295按`data.get("version") is not None and data["version"] != pending["version"]`分支；L296抛异常，停止当前正常路径；L297按`data.get("digest") is not None and data["digest"] != pending["digest"]`分支；L298抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`session.get`、`Missing`、`Conflict`、`data.get`、`pending.get`、`pending.get("data", {}).get`、`session.add`、`Event`、`render_answer`等。 返回路径：L336的`{"run_id": run_id, "job_id": job.id, "status": "QUEUED"}`。
- `Store._model_free_retry`（L340–L378）：接收`session`、`run`。 控制顺序：L341按`not run or run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}`分支；L349按`not stage or stage.data.get("name") != "extension_package" or stage.data.get("phase")…`分支；L358按`not previous or previous.status != "FAILED" or previous.payload.get("approved") is no…`分支；L366按`not ( revision and revision.run_id == run.id and revision.stage == "extension_scope" …`分支。 调用`session.scalar`、`select(Event) .where(Event.run_id == run.id, Event.kind == "stage…`、`select(Event) .where`、`select`、`Event.id.desc`、`stage.data.get`、`select(Job).where(Job.run_id == run.id).order_by(Job.created_at.d…`、`select(Job).where(Job.run_id == run.id).order_by`、`select(Job).where`等。 返回路径：L342的`None`；L354的`None`；L363的`None`。
- `Store.is_model_free_retry`（L380–L385）：接收`run_id`、`key`。 控制顺序：L383按`old and old.fingerprint == digest({"operation": "retry", "run_id": run_id})`分支。 调用`self.tx`、`session.get`、`digest`、`self._model_free_retry`。 返回路径：L384的`True`；L385的`self._model_free_retry(session, session.get(Run, run_id)) is not None`。
- `Store.retry`（L387–L406）：接收`run_id`、`key`、`require_model_free`。 调用`self.request`。 返回路径：L406的`self.request(key, {"operation": "retry", "run_id": run_id}, operation)`。
- `Store.retry.operation`（L388–L404）：接收`session`。 控制顺序：L390按`not run`分支；L391抛异常，停止当前正常路径；L392按`run.status not in {"FAILED", "BLOCKED", "PAUSED_LIMIT"}`分支；L393抛异常，停止当前正常路径；L394按`run.pending and run.pending.get("data", {}).get("capability_conflicts")`分支；L395抛异常，停止当前正常路径；L397按`require_model_free and not bound_retry`分支；L398抛异常，停止当前正常路径。 调用`session.get`、`Missing`、`Conflict`、`run.pending.get("data", {}).get`、`run.pending.get`、`self._model_free_retry`、`session.add`、`Job`。 返回路径：L404的`{"run_id": run_id, "status": run.status}`。
- `Store.get_run`（L408–L425）：接收`run_id`。 控制顺序：L411按`not run`分支；L412抛异常，停止当前正常路径。 调用`self.tx`、`session.get`、`Missing`、`getattr`、`action_needs_model`、`self._model_free_retry`。 返回路径：L413的`{ **{c.name: getattr(run, c.name) for c in Run.__table__.columns}, "pending": { **run.pend…`。
- `Store.messages`（L427–L432）：接收`run_id`。 调用`self.tx`、`session.scalars`、`select(Message).where(Message.run_id == run_id).order_by`、`select(Message).where`、`select`。 返回路径：L432的`[{"role": row.role, "content": row.content} for row in rows]`。
- `Store.assistant_event`（L434–L506）：接收`run_id`、`kind`、`data`。 源码说明：Append UI-only assistant events; terminal replay is idempotent. The existing Message table remains the authoritative human-input history. Assistant drafts cannot accidentally become requirements on a 。 控制顺序：L447按`kind not in allowed`分支；L448抛异常，停止当前正常路径；L451按`not session.get(Run, run_id)`分支；L452抛异常，停止当前正常路径；L469按`any(r.kind == kind for r in matching) and kind in { "assistant_start", "assistant_com…`分支；L475按`any(r.kind in {"assistant_completed", "assistant_failed"} for r in matching)`分支；L477按`kind == "assistant_start"`分支；L480遍历`rows`。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`FileLock`、`str`、`self.tx`、`session.get`、`Missing`、`list`、`session.scalars`、`select(Event) .where( Event.run_id == run_id, Event.kind.in_( {"a…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.transcript`（L508–L615）：接收`run_id`。 源码说明：One read snapshot plus cursor, suitable for replay without duplicated text.。 控制顺序：L511按`self.engine.dialect.name == "postgresql"`分支；L513按`not session.get(Run, run_id)`分支；L514抛异常，停止当前正常路径；L530遍历`session.scalars( select(Event).where(Event.run_id == run_id).orde…`；L534按`not row.kind.startswith("assistant_")`分支；L563按`row.kind == "assistant_delta"`分支；L565按`row.kind in {"assistant_completed", "assistant_failed"}`分支；L571遍历`session.scalars( select(Revision).where(Revision.run_id == run_id…`。后续分支沿下方源码相同行号继续阅读。 调用`self.tx`、`session.execute`、`text`、`session.get`、`Missing`、`str`、`session.scalars`、`select(Message).where(Message.run_id == run_id).order_by`、`select(Message).where`等。 返回路径：L615的`{"messages": messages, "cursor": cursor}`。
- `Store.step`（L617–L627）：接收`run_id`、`name`、`fn`。 控制顺序：L620按`old`分支。 调用`self.tx`、`session.scalar`、`select(Step).where`、`select`、`fn`、`json.loads`、`json.dumps`、`session.add`、`Step`等。 返回路径：L621的`old.data`；L627的`result`。
- `Store.reserve_model_call`（L629–L638）：接收`run_id`。 控制顺序：L632按`self.settings.max_model_calls`分支；L635按`changed != 1`分支；L636抛异常，停止当前正常路径。 调用`self.tx`、`update(Run).where`、`update`、`statement.where`、`session.execute`、`statement.values`、`PausedLimit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.set_automation`（L640–L702）：接收`run_id`、`enabled`、`key`。 调用`self.request`。 返回路径：L700的`self.request( key, {"operation": "automation", "run_id": run_id, "enabled": enabled}, oper…`。
- `Store.set_automation.operation`（L641–L698）：接收`session`。 控制顺序：L643按`run is None`分支；L644抛异常，停止当前正常路径；L645按`run.status in {"READY", "SOURCE_READY", "REJECTED"}`分支；L646抛异常，停止当前正常路径；L659按`enabled and run.pending and run.pending.get("data", {}).get("requires_explicit_review…`分支；L670按`enabled and run.pending and run.pending.get("data", {}).get("capability_conflicts")`分支；L679按`enabled and run.pending`分支；L692按`not enabled and run.status == "BLOCKED" and run.pending`分支。后续分支沿下方源码相同行号继续阅读。 调用`session.get`、`Missing`、`Conflict`、`session.add`、`Event`、`run.pending.get("data", {}).get`、`run.pending.get`、`Job`、`run.pending["stage"].upper`。 返回路径：L664的`{ "run_id": run_id, "auto_mode": enabled, "status": run.status, "message": "本次模块权限变更仍需明确人工…`；L673的`{ "run_id": run_id, "auto_mode": enabled, "status": run.status, "message": "当前报名入口仍需明确选择；已…`；L698的`{"run_id": run_id, "auto_mode": enabled, "status": run.status}`。
- `Store.auto_approve`（L704–L729）：接收`run_id`、`gate`。 控制顺序：L707按`not run or not run.auto_mode or not gate["can_approve"] or gate.get("data", {}).get("…`分支；L713抛异常，停止当前正常路径；L715按`current and not current.decision`分支；L716抛异常，停止当前正常路径；L717按`not current`分支。 调用`self.tx`、`session.get`、`gate.get("data", {}).get`、`gate.get`、`Conflict`、`session.add`、`Approval`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.record_event`（L731–L733）：接收`run_id`、`kind`、`data`。 调用`self.tx`、`session.add`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.model_records`（L735–L767）：接收`run_id`。 调用`self.get_run`、`self.tx`、`session.scalars`、`select(Step) .where(Step.run_id == run_id, Step.name.like("model:…`、`select(Step) .where`、`select`、`Step.name.like`、`r.data.get`、`select(Event) .where(Event.run_id == run_id, Event.kind == "model…`等。 返回路径：L767的`sorted(records, key=lambda item: item["created_at"])`。
- `Store.gate`（L769–L792）：接收`run_id`、`stage`、`version`、`data`、`actions`、`can_approve`。 控制顺序：L773按`not session.get(Revision, gate_id)`分支。 调用`digest`、`self.tx`、`session.get`、`session.add`、`Revision`、`action_needs_model`。 返回路径：L783的`{ "gate_id": gate_id, "stage": stage, "version": version, "digest": content_digest, "data"…`。
- `Store.check_decision`（L794–L817）：接收`run_id`、`gate`、`value`。 控制顺序：L795按`not isinstance(value, dict)`分支；L796抛异常，停止当前正常路径；L797按`value.get("gate_id") != gate["gate_id"] or ( value.get("action") not in gate["actions…`分支；L800抛异常，停止当前正常路径；L801按`value["action"] == "recommend"`分支；L802按`gate.get("data", {}).get("requires_explicit_review")`分支；L803抛异常，停止当前正常路径；L804按`value.get("approved") is not True or not self.get_run(run_id)["auto_mode"]`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`Conflict`、`value.get`、`gate.get("data", {}).get`、`gate.get`、`self.get_run`、`self.tx`、`session.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.explicit_approval`（L819–L842）：接收`run_id`、`stage`、`data`、`version`。 源码说明：Read the durable operator decision, never a model/candidate receipt.。 控制顺序：L835遍历`rows`；L836按`approval.decision is True and approval.actor == "local-operator"`分支；L842抛异常，停止当前正常路径。 调用`digest`、`self.tx`、`session.execute`、`select(Revision, Approval) .join(Approval, Approval.gate_id == Re…`、`select(Revision, Approval) .join`、`select`、`Revision.created_at.desc`、`Conflict`。 返回路径：L837的`{ "gate_id": revision.gate_id, "data_digest": content_digest, "actor": approval.actor, }`。
- `Store.is_model_free_approval`（L844–L859）：接收`run_id`、`data`。 源码说明：Use the controller's immutable gate, never a client-supplied stage. submit still validates the current pending gate, approval and idempotency. Reading the revision also permits an exact idempotent rep。 控制顺序：L851按`data.get("action") != "approve" or data.get("approved") is not True`分支。 调用`data.get`、`self.tx`、`session.get`、`bool`、`action_needs_model`。 返回路径：L852的`False`；L855的`bool( revision and revision.run_id == run_id and not action_needs_model(revision.stage, da…`。
- `Store.claim`（L861–L890）：接收`only_rejections`、`include_model_free`。 控制顺序：L864按`only_rejections`分支；L866按`include_model_free`分支；L881按`job is None`分支；L886按`changed != 1`分支。 调用`self.tx`、`select(Job).where`、`select`、`Job.payload["action"].as_string`、`select(Revision.gate_id).where`、`Revision.stage.in_`、`or_`、`and_`、`Job.payload["action"].as_string().in_`等。 返回路径：L882的`None`；L887的`None`；L890的`{"id": job.id, "run_id": job.run_id, "payload": job.payload}`。

</details>

**创建路径：** `workbench/store.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L891。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`39260`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/store.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "5a929eccdecb38382df3d4d8990b7502f57683a542df35a6ef433baa9a880a16"} -->
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

from workbench.domain import BatchInput, ResumeInput, RunInput, digest
from workbench.errors import PausedLimit
from workbench.settings import ROOT, Settings

MODEL_FREE_APPROVAL_STAGES = frozenset({"delivery", "extension_scope", "extension_delivery"})


def action_needs_model(stage, action):
    return action != "reject" and not (action == "approve" and stage in MODEL_FREE_APPROVAL_STAGES)


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
            return self._enqueue_run(session, project_id, data)

        return self.request(
            key, {"operation": "create-run", "project": project_id, **data}, operation
        )

    def create_batch(self, data, key):
        """Validate then create all projects and jobs in one idempotent transaction."""
        data = BatchInput.model_validate(data).model_dump()

        def operation(session):
            items = []
            for item in data["items"]:
                project = Project(title=item["title"])
                session.add(project)
                session.flush()
                queued = self._enqueue_run(session, project.id, item)
                items.append({"project_id": project.id, "title": project.title, **queued})
            return {"items": items}

        return self.request(key, {"operation": "create-batch", **data}, operation)

    def _enqueue_run(self, session, project_id, data):
        """Single and batch creation share the same durable worker and delegation."""
        run = Run(
            project_id=project_id,
            template=data["template"],
            options={
                **data["selection"],
                "allow_custom_extensions": data["allow_custom_extensions"],
            },
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
                "pending": {
                    **run.pending,
                    "needs_model": {
                        action: action_needs_model(run.pending["stage"], action)
                        for action in run.pending["actions"]
                    },
                }
                if run.pending
                else None,
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
            "needs_model": {action: action_needs_model(stage, action) for action in actions},
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
                and not action_needs_model(revision.stage, data["action"])
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

````
