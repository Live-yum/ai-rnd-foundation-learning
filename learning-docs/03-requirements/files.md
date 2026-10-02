# 需求保真与模型协议：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件与截图编码在 sources/locks 和 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [examples/plans/customer-service.json](sources/examples__plans__customer-service_json--001.md)：可审查的需求与完整合同验收样例；1 段
- [examples/requirements/customer-service-contract.md](sources/examples__requirements__customer-service-contract_md--001.md)：客服黑盒验收的字段与命名约定；1 段
- [examples/requirements/customer-service-decisions.md](sources/examples__requirements__customer-service-decisions_md--001.md)：客服演示的明确默认决策；1 段
- [examples/requirements/customer-service.md](sources/examples__requirements__customer-service_md--001.md)：用户原始客服需求；1 段
- [tests/test_field_predicate_semantics.py](sources/tests__test_field_predicate_semantics_py--001.md)：可重复的验收用例；1 段
- [tests/test_guided_models.py](sources/tests__test_guided_models_py--001.md)：可重复的验收用例；1 段
- [tests/test_llm.py](sources/tests__test_llm_py--001.md)：可重复的验收用例；1 段
- [tests/test_provider_structured_outputs.py](sources/tests__test_provider_structured_outputs_py--001.md)：可重复的验收用例；1 段
- [workbench/business_capabilities.py](sources/workbench__business_capabilities_py--001.md)：业务合同的可执行能力边界；2 段
- [workbench/conversation.py](sources/workbench__conversation_py--001.md)：从持久化记录组织对话上下文；1 段
- [workbench/entity_requirements.py](sources/workbench__entity_requirements_py--001.md)：用户明确封闭的实体与字段清单；1 段
- [workbench/llm.py](sources/workbench__llm_py--001.md)：唯一的对话模型调用网关；1 段
- [workbench/model_protocol.py](sources/workbench__model_protocol_py--001.md)：项目根配置或说明；1 段
- [workbench/requirement_coverage.py](sources/workbench__requirement_coverage_py--001.md)：保留用户事实并检查可执行需求覆盖；3 段
- [workbench/requirement_sources.py](sources/workbench__requirement_sources_py--001.md)：在规划前拒绝明确来源互相冲突的分析候选；1 段
