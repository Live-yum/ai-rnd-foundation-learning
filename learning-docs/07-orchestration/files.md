# 审批状态机与恢复：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件在 sources/locks，截图及Vue构建快照编码在 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [scripts/news_fixture.py](sources/scripts__news_fixture_py--001.md)：资讯需求与智能推荐的显式测试响应；1 段
- [tests/news_case.py](sources/tests__news_case_py--001.md)：可重复的验收用例；1 段
- [tests/test_guided_workflow.py](sources/tests__test_guided_workflow_py--001.md)：可重复的验收用例；1 段
- [tests/test_recommendation_stage_budget.py](sources/tests__test_recommendation_stage_budget_py--001.md)：可重复的验收用例；1 段
- [tests/test_workflow.py](sources/tests__test_workflow_py--001.md)：可重复的验收用例；1 段
- [workbench/aider_tool.py](sources/workbench__aider_tool_py--001.md)：隔离的Aider命令行适配；1 段
- [workbench/capability_sandbox.py](sources/workbench__capability_sandbox_py--001.md)：项目根配置或说明；1 段
- [workbench/coding.py](sources/workbench__coding_py--001.md)：不依赖Aider的受限规则编辑；1 段
- [workbench/continue_index.py](sources/workbench__continue_index_py--001.md)：固定Continue全文索引组件的本机适配器；1 段
- [workbench/daytona_profiles.py](sources/workbench__daytona_profiles_py--001.md)：按技术栈登记离线快照和验收合同；1 段
- [workbench/flow.py](sources/workbench__flow_py--001.md)：需求到交付的LangGraph状态机；1 段
- [workbench/recommendation.py](sources/workbench__recommendation_py--001.md)：解释智能推荐为何暂停；1 段
- [workbench/runtime.py](sources/workbench__runtime_py--001.md)：持久化Worker和断点恢复；1 段
- [workbench/sandbox.py](sources/workbench__sandbox_py--001.md)：本机Daytona附加验收与生命周期；1 段
- [workbench/toolchain.py](sources/workbench__toolchain_py--001.md)：把源码上下文接到实际主流程；1 段
