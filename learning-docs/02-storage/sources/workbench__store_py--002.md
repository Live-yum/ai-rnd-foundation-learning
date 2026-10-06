# workbench/store.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__store_py--001.md)

**作用：持久化项目、会话、任务、版本、审批和证据。** SQLAlchemy类说明表的列，Store的方法说明事务操作。create_run建立运行和首条消息；任务认领与完成有状态约束，修订和审批保留指纹。页面状态与Worker进度不能只保存在内存变量里。

**对应关系：** api写入Store → Runtime认领Job → Workflow记录Revision/Approval/Step/Event；test_store。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.errors`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** create_project第一次使用请求键K时创建项目并保存回执；同键同内容返回原结果，同键不同标题抛Conflict。关键是状态变化与回执在同一短事务里完成；若事务中抛异常，新增记录整体回滚。审批还把gate_id绑定到确定版本，而不是只保存一个永远有效的approved标志。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Store._recover_assistants`（L867–L948）：接收`session`、`run_id`。 源码说明：Resolve every abandoned attempt, even after a model/profile change.。 控制顺序：L870遍历`session.scalars( select(Event) .where( Event.run_id == run_id, Ev…`；L891按`not unfinished`分支；L896遍历`session.scalars( select(Step.data["assistant"]).where( Step.run_i…`；L903按`isinstance(data, dict) and data.get("validation") == "validated" and data.get("status…`分支；L910遍历`unfinished.items()`；L911按`message_id in committed`分支。 调用`session.scalars`、`select(Event) .where( Event.run_id == run_id, Event.kind.in_( { "…`、`select(Event) .where`、`select`、`Event.kind.in_`、`latest.items`、`select(Step.data["assistant"]).where`、`Step.name.like`、`Step.data["contract_version"].as_integer`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.finish`（L950–L959）：接收`job`、`status`、`pending`、`result`、`error`。 控制顺序：L955按`result is not None`分支。 调用`self.tx`、`session.get`、`session.add`、`Event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Store.events`（L961–L973）：接收`run_id`、`after`。 调用`self.get_run`、`self.tx`、`session.scalars`、`select(Event) .where(Event.run_id == run_id, Event.id > after) .o…`、`select(Event) .where`、`select`。 返回路径：L970的`[ {"id": r.id, "kind": r.kind, "data": r.data, "created_at": r.created_at} for r in rows ]`。
- `Store.list_projects`（L975–L982）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.tx`、`session.scalars`、`select(Project).order_by(Project.created_at.desc()).limit`、`select(Project).order_by`、`select`、`Project.created_at.desc`。 返回路径：L977的`[ {"id": p.id, "title": p.title, "created_at": p.created_at} for p in session.scalars( sel…`。
- `Store.list_runs`（L984–L1002）：接收`project_id`。 控制顺序：L987按`project_id is not None`分支；L988按`not session.get(Project, project_id)`分支；L989抛异常，停止当前正常路径。 调用`self.tx`、`select(Run).order_by(Run.created_at.desc()).limit`、`select(Run).order_by`、`select`、`Run.created_at.desc`、`session.get`、`Missing`、`statement.where`、`session.scalars`。 返回路径：L991的`[ { "id": r.id, "project_id": r.project_id, "status": r.status, "template": r.template, "o…`。
- `Store.latest_revision`（L1004–L1012）：接收`run_id`、`stage`。 调用`self.tx`、`session.scalar`、`select(Revision) .where(Revision.run_id == run_id, Revision.stage…`、`select(Revision) .where`、`select`、`Revision.created_at.desc`。 返回路径：L1012的`row.data if row else None`。
- `_cursor`（L1016–L1021）：接收`connection`。 调用`connection.cursor`、`cursor.close`。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `workbench/store.py`；**本文件共有 2 段**。本段覆盖源文件 L867–L1021。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5735`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/store.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "aba421cc163907f9125e63e26e0a8a509e333a242f1d1de8a2ce8f3dcba077d3"} -->
````python
# workbench/store.py
    def _recover_assistants(self, session, run_id):
        """Resolve every abandoned attempt, even after a model/profile change."""
        latest = {}
        for row in session.scalars(
            select(Event)
            .where(
                Event.run_id == run_id,
                Event.kind.in_(
                    {
                        "assistant_start",
                        "assistant_status",
                        "assistant_completed",
                        "assistant_failed",
                    }
                ),
            )
            .order_by(Event.id)
        ):
            latest[row.data["message_id"]] = row
        unfinished = {
            key: row
            for key, row in latest.items()
            if row.kind not in {"assistant_completed", "assistant_failed"}
        }
        if not unfinished:
            return
        # Select only already-sanitized assistant metadata. The full model JSON,
        # prompts and executable patches never enter recovery UI events.
        committed = {}
        for data in session.scalars(
            select(Step.data["assistant"]).where(
                Step.run_id == run_id,
                Step.name.like("model:%"),
                Step.data["contract_version"].as_integer() >= 2,
            )
        ):
            if (
                isinstance(data, dict)
                and data.get("validation") == "validated"
                and data.get("status") == "completed"
                and isinstance(data.get("content"), str)
            ):
                committed[data.get("message_id")] = data
        for message_id, row in unfinished.items():
            if message_id in committed:
                data = committed[message_id]
                session.add(
                    Event(
                        run_id=run_id,
                        kind="assistant_completed",
                        data={
                            key: data[key]
                            for key in (
                                "message_id",
                                "response_id",
                                "stage",
                                "transport",
                                "validation",
                                "status",
                                "content",
                            )
                            if key in data
                        },
                    )
                )
            else:
                session.add(
                    Event(
                        run_id=run_id,
                        kind="assistant_failed",
                        data={
                            **{
                                key: row.data.get(key)
                                for key in ("message_id", "response_id", "stage", "transport")
                            },
                            "validation": "failed",
                            "status": "failed",
                            "code": "worker_interrupted",
                            "content": "",
                        },
                    )
                )

    def finish(self, job, status, pending=None, result=None, error=None):
        with self.tx() as session:
            session.get(Job, job["id"]).status = "FAILED" if error else "DONE"
            run = session.get(Run, job["run_id"])
            run.status, run.pending, run.error = status, pending, error
            if result is not None:
                run.result = result
            session.add(
                Event(run_id=run.id, kind="status", data={"status": status, "error": error})
            )

    def events(self, run_id, after=0):
        self.get_run(run_id)
        with self.tx() as session:
            rows = session.scalars(
                select(Event)
                .where(Event.run_id == run_id, Event.id > after)
                .order_by(Event.id)
                .limit(200)
            )
            return [
                {"id": r.id, "kind": r.kind, "data": r.data, "created_at": r.created_at}
                for r in rows
            ]

    def list_projects(self):
        with self.tx() as session:
            return [
                {"id": p.id, "title": p.title, "created_at": p.created_at}
                for p in session.scalars(
                    select(Project).order_by(Project.created_at.desc()).limit(100)
                )
            ]

    def list_runs(self, project_id=None):
        with self.tx() as session:
            statement = select(Run).order_by(Run.created_at.desc()).limit(100)
            if project_id is not None:
                if not session.get(Project, project_id):
                    raise Missing("项目不存在")
                statement = statement.where(Run.project_id == project_id)
            return [
                {
                    "id": r.id,
                    "project_id": r.project_id,
                    "status": r.status,
                    "template": r.template,
                    "options": r.options,
                    "auto_mode": r.auto_mode,
                    "updated_at": r.updated_at,
                }
                for r in session.scalars(statement)
            ]

    def latest_revision(self, run_id, stage):
        with self.tx() as session:
            row = session.scalar(
                select(Revision)
                .where(Revision.run_id == run_id, Revision.stage == stage)
                .order_by(Revision.created_at.desc())
                .limit(1)
            )
            return row.data if row else None


@contextmanager
def _cursor(connection):
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
````
