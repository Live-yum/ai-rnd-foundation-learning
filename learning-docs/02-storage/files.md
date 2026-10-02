# 持久化与迁移：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件在 sources/locks，截图及Vue构建快照编码在 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [alembic.ini](sources/alembic_ini--001.md)：项目根配置或说明；1 段
- [migrations/env.py](sources/migrations__env_py--001.md)：工作台数据库迁移；1 段
- [migrations/script.py.mako](sources/migrations__script_py_mako--001.md)：工作台数据库迁移；1 段
- [migrations/versions/0001_initial_control_plane_schema.py](sources/migrations__versions__0001_initial_control_plane_schema_py--001.md)：工作台数据库迁移；1 段
- [migrations/versions/0002_run_selection_and_delegation.py](sources/migrations__versions__0002_run_selection_and_delegation_py--001.md)：工作台数据库迁移；1 段
- [tests/conftest.py](sources/tests__conftest_py--001.md)：可重复的验收用例；1 段
- [tests/test_business_contracts.py](sources/tests__test_business_contracts_py--001.md)：可重复的验收用例；1 段
- [tests/test_contracts.py](sources/tests__test_contracts_py--001.md)：可重复的验收用例；1 段
- [tests/test_store.py](sources/tests__test_store_py--001.md)：可重复的验收用例；1 段
- [workbench/clarification.py](sources/workbench__clarification_py--001.md)：把当前澄清关卡的选择可靠还原为用户回答；1 段
- [workbench/store.py](sources/workbench__store_py--001.md)：持久化项目、会话、任务、版本、审批和证据；1 段
