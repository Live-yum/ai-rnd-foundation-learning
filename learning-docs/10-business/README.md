# 10 · 角色权限与客服业务

[总目录](../README.md) · [上一阶段](../09-native/README.md) · [下一阶段](../11-local-tools/README.md)

## 从个人CRUD走向团队业务

现在回到标准案例：维护客户、创建服务请求、分配负责人、按批准动作推进状态、追加处理记录、协作任务、站内提醒和统计。三份输入有不同职责：原始需求保存业务目标，默认决策明确可执行选择，字段合同固定名称、枚举和类型。必须一起保留，不能把原需求改写成更小的任务后说完成。`examples/plans/customer-service.json` 是确定性验收输入，不是模型失败时的隐藏答案。

`BusinessSpec` 把行为限制成可验证的结构。资源声明负责人字段、归档与历史；关系声明引用目标及restrict删除语义；permissions逐角色逐实体声明完整动作和范围；workflows给出命名转换、合法起始状态和时间戳写入；notifications明确事件与接收者；metrics明确计数、平均时长、分组和每日趋势。shared表示团队业务模型，不表示所有员工都能读全部记录。

`templates/business/common/policy.py` 负责共同语义。默认没有动作就拒绝；own依据不可改的created_by，assigned依据批准的负责人字段，all才是全部可见范围。`read_history`、`read_audit`、`read_metrics` 是独立动作，不能由“能读记录”推导出“能读审计与统计”。角色从服务端实时读取；前端隐藏按钮只是辅助体验，HTTP直接请求仍必须被服务端拒绝。

## 沿一笔“解决请求”追踪事务

从页面点击命名动作resolve开始，先识别当前用户，再核对该角色对requests的transition权限和当前行范围；读取并锁定记录，检查原状态是否属于允许来源，然后修改状态并填写批准的完成时间。同一个事务还要追加服务端作者的审计/历史、生成要求的站内提醒。失败要整体回滚，不能出现“状态已解决却没有审计”，也不能允许普通update绕过命名转换。

Python产品的 `business_schema.py`、`business_runtime.py` 生成表并实现事务；FastapiAdmin适配器与模板延续其原生控制器/ORM/事务；Yudao适配器生成Java服务、Mapper、控制器和原生表单面板。共同合同不意味着强行共用同一套前端或伪造框架事务。`business_schema_receipt.py` 与业务探针把实际SQL结构及行为证据绑定到设计。

提醒要按源事件和接收者去重，读收件箱不能再产生一批提醒；标记已读只影响当前接收者。统计同样先授权再选行：总数与已解决数不能混用，创建到解决平均时长排除缺失端点的记录，零样本返回null，UTC日桶必须一致。增加未解决对照请求和第二类客户，是为了让错误的全量计数、分组或时长计算暴露出来。

## 按层验收，不只看一个总passed

```bash
# .learning/commands/10-business-contracts.sh
uv run pytest tests/test_business_contracts.py tests/test_business_capabilities.py tests/test_business_python.py tests/test_business_fastapi.py tests/test_business_yudao.py -q
uv run pytest tests/test_business_audit_permissions.py tests/test_business_note_notifications.py tests/test_customer_employee_task_scopes.py tests/test_business_query_api.py -q
```

这些文件中一部分是真实生成产品HTTP/SQL，另一部分是适配器与证据合同；阅读文件说明，不能把全部统称原生运行。相关测试辅助文件和fixtures必须按源码索引齐全。浏览器工具准备好后：

```bash
# .learning/commands/10-business-browser.sh
uv run pytest tests/test_business_python_browser.py -q
```

再回到第09节执行两种原生客服命令，分别保留真实报告。预期包括三角色授权正反例、客户关联选择、分配、start/resolve、备注、归档、提醒和统计，不只是“页面有几张卡片”。原生浏览器必须从登录与菜单进入实际业务路由，不能注入Token或截一张静态首页替代流程。

如果一个计划缺动作或范围，先回需求与设计层判定批准内容；不要临时给员工管理员角色以让测试通过。失败的诊断候选Plan只是分析材料，只有确实已批准且通过合同检查的Plan才能进入生成。

## 本阶段源码和后续依赖

本阶段首次创建 72 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
