# 03 · 需求保真与模型协议

[总目录](../README.md) · [上一阶段](../02-storage/README.md) · [下一阶段](../04-local-foundation/README.md)

## 两道不同的门：响应合同与需求覆盖

`model_protocol.py` 接管服务商结构化输出的协议边界：选择正式 LangChain 集成、检查HTTP状态和响应大小、解析JSON、执行本地严格验证。`llm.ModelGateway` 再负责阶段模型选择、调用预算、缓存/回执与安全诊断。返回合法JSON只是第一道门；例如用户要求标题可搜索，而候选计划把 `searchable` 设为 false，所有JSON字段都合法，业务仍然错误。

因此 `requirement_coverage.py` 不依赖模型自己宣布“全部覆盖”。它读取已保存的 Requirement，包括类型化字段约束、实体清单、既有 facts 及受约束的旧文本表达，再与 Plan 比较。`entity_requirements.py` 负责实体字段清单；开放清单要求“至少有这些”，封闭清单还要求“不能多出别的”。`business_capabilities.py` 专门处理角色动作、范围、关联、提醒、统计等业务义务，不能把这些义务错当作普通字段。

多轮澄清最大的陷阱是遗漏。`reconcile` 保留上一轮已确认的事实，不因下一轮模型没再写一遍就删除。真正的修改要有 `RequirementChange`，其 `source_quote` 必须能对应本轮新收到的用户更正。`requirement_sources.py` 进一步检测不同来源中的互斥约束；诊断指出冲突双方，不能自己决定哪方胜出。智能推荐是补齐普通未知项的委托，不是修改明确要求的授权。

## 一个无需真实模型的反例实验

保存为 `.learning/checks/03_requirements.py`：

```python
# .learning/checks/03_requirements.py
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps, reconcile

requirement = Requirement(
    summary="请求标题",
    users=["员工"],
    data_scope="per_user",
    features=["管理请求"],
    acceptance=["标题可搜索"],
    facts={"original": "保留原始标题"},
    field_requirements=[
        {
            "entity": "request",
            "field": "title",
            "kind": "text",
            "required": True,
            "max_length": 80,
            "searchable": True,
        }
    ],
)
plan = Plan(
    title="请求",
    data_scope="per_user",
    acceptance=["标题可搜索"],
    entities=[
        {
            "name": "request",
            "description": "请求",
            "fields": [
                {
                    "name": "title",
                    "kind": "text",
                    "required": True,
                    "max_length": 80,
                    "searchable": True,
                }
            ],
        }
    ],
)
assert coverage_gaps(requirement, plan) == []
wrong = plan.model_copy(deep=True)
wrong.entities[0].fields[0].searchable = False
assert coverage_gaps(requirement, wrong)
omitted = requirement.model_copy(update={"facts": {}, "field_requirements": []})
merged = reconcile(requirement.model_dump(), omitted, corrections=[])
assert merged.facts == requirement.facts
assert merged.field_requirements == requirement.field_requirements
print("03 PASS: coverage detects loss; omission preserves intent")
```

```bash
# .learning/commands/03-check.sh
uv run python .learning/checks/03_requirements.py
uv run pytest tests/test_llm.py tests/test_provider_structured_outputs.py tests/test_field_predicate_semantics.py -q
```

练习应打印 `03 PASS`，测试应无 failed/error。协议测试通过显式 MockTransport 检查请求响应合同，不会验证你自己的供应商账号。`deep=True` 很重要：否则错误样本可能共享嵌套对象，误把正确计划也改坏。把练习里的“正确计划”“缺搜索计划”“省略事实的下一轮”对应回三个独立变量，就能看清各函数的职责。

不要在这一站直接跑 `tests/test_requirement_coverage.py` 或 `tests/test_requirement_source_conflicts.py` 的整文件。它们混合纯函数、工作流和原生适配/诊断数据用例，既有后续Runtime导入，也读取后续fixtures。第14阶段完整源码就位后再跑它们；这并不是少测，而是把集成测试放到真实依赖成立之后。

## 本阶段源码和后续依赖

本阶段首次创建 15 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
