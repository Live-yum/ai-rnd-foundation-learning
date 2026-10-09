# 02 · 持久化与迁移

[总目录](../README.md) · [上一阶段](../01-contracts/README.md) · [下一阶段](../03-requirements/README.md)

## 从内存对象跨进数据库

合同只能保证“这一份输入长得正确”，不能保证进程重启后记得它。`Store` 使用 SQLAlchemy，保存项目、运行、消息、排队任务、请求回执、审批修订和步骤证据。先画出 Project → Run → Message/Job 的归属，再看 Revision 与 Approval 为什么共用 gate_id：一次批准对应某个确定版本的内容，不能漂移到后来改过的设计。

`Store.tx` 是短事务边界；`request → _request` 把请求指纹和响应与实际变化一起提交。第一次创建成功后，网络重试带同一个幂等键应得到原响应；同键换了内容则冲突。幂等不是“忽略所有重复动作”，更不是允许把一个人的批准挪到下一道关卡。`step` 记录已完成步骤的回执，用于避免安全可重放步骤无意义地重做；后续仍要核对输入身份和源码指纹。

平台使用 Alembic 升级控制库，而不是每次启动调用删除重建。`migrations/env.py` 接收已有连接时复用它，否则自行建立 Store；它只能依赖本阶段基础层，不应导入还没实现的 API 和 Runtime。初始迁移建立控制表，第二份迁移加入运行选择与持续委托数据。数据库的版本号应是 `0002`，不会因为你少抄一份迁移而自动补齐。

## 用临时目录验证四件事

保存为 `.learning/checks/02_storage.py`：

```python
# .learning/checks/02_storage.py
from pathlib import Path
from tempfile import TemporaryDirectory
from sqlalchemy import text
from workbench.settings import Settings
from workbench.store import Conflict, Project, Store

with TemporaryDirectory(prefix="rnd-learning-store-") as directory:
    store = Store(
        Settings(data_dir=Path(directory), database_url="", install_products=False, _env_file=None)
    )
    try:
        store.migrate()
        with store.engine.connect() as connection:
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0002"
        first = store.create_project("客服学习", "same-request")
        assert store.create_project("客服学习", "same-request") == first
        try:
            store.create_project("另一个项目", "same-request")
        except Conflict:
            pass
        else:
            raise AssertionError("idempotency conflict was ignored")
        try:
            with store.tx() as session:
                session.add(Project(title="must roll back"))
                raise RuntimeError("exercise rollback")
        except RuntimeError:
            pass
        assert len(store.list_projects()) == 1
    finally:
        store.engine.dispose()
print("02 PASS: migration, idempotency, conflict and rollback")
```

```bash
# .learning/commands/02-check.sh
uv run python .learning/checks/02_storage.py
uv run pytest tests/test_contracts.py tests/test_store.py -q
```

第一条应打印 `02 PASS`，第二条应正常退出且没有 failed/error。测试会用临时库；确认没有把 `DATABASE_URL` 环境变量指向你已有的真实数据库。`finally` 在清理临时目录前关闭连接池，特别避免 Windows 文件句柄未释放。

这一站的成功意味着控制面的持久化规则成立。它还不意味着 LangGraph 的暂停点被保存，也不意味着 Worker 已启动。稍后 `checkpoints.db` 管“图停在哪”，`workbench.db` 管“用户看见什么任务和批准”；产品库则管客户、请求和任务，三者不能混用。

## 将单次运行推广成批量提交

`BatchInput` 是 1–10 个带标题的普通 `RunInput`。`Store.create_batch` 先校验整批，再通过同一个 `request` 事务创建 Project、Run、原始 Message 和 Job；单项与批量共享 `_enqueue_run`。任何一次写入失败都整批回滚，使用相同幂等键与正文重试只返回原来的结果。每项保留自己的手动或智能委托策略，批量没有额外的审批捷径。

验证入口是 `tests/test_batches.py`：检查整批回滚、重试、不重复入队、模板兼容和认证。当前 Worker 仍串行消费队列；高吞吐并行调度需要另一套明确的资源与数据库隔离设计，本阶段不声称已实现。

## 本阶段源码和后续依赖

本阶段首次创建 11 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
