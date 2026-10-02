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

## 从真实模型增量到可见草稿，仍不能绕过最终合同

`Runtime` 创建生产 `ModelGateway(..., streaming=True)`。网关仍通过官方LangChain结构化链解析结果；`model_protocol.AuditedTransport` 在SDK规范化之前审计真实HTTP响应。服务端返回 `text/event-stream` 时，`AuditedEventStream` 逐帧消费内容、完成原因和usage，并检查大小上限、结束标记与本地严格schema。网络块不是一个JSON对象，也不保证一个中文字已经完整，协议层因此需要增量解码和帧边界处理。

`streaming.AssistantStream` 并不把服务商原始JSON全部发到网页。只有本项目指定schema的公开根字符串可以显示：需求的 `summary`、计划的 `title`、补丁的 `explanation`、复核的 `summary`。嵌套对象、补丁源码和隐藏推理字段不在投影范围。`root_string_prefix` 只返回当前已经完整解码的字符串前缀；碰到半个JSON转义或UTF-16代理对时等待后续数据，不猜一个字符。若目标字段前还有尚未完成的对象，暂时没有公开文字也是正常情况。

可以跟踪一个具体反例：服务商先返回summary前半句，页面已显示草稿，后半段却让Requirement缺了必填字段。增量不能使这次调用提前成功，完整对象仍须校验；失败事件把草稿清空并保留失败状态，重新纠错是另一次有身份的尝试。只有最终通过校验的对象才进入需求/计划与后续业务判断。

另一个难点是密钥跨块泄露。若已知Key的前半段恰好出现在当前公开字符串末尾，`AssistantStream.content` 会暂留这个可能的前缀，直到能判定或统一脱敏后才追加可见文本。修改过的本机模型配置中的旧Key也保留在脱敏集合，不能只保护当前环境变量。测试用的都是明确假Key，不需要把自己的Key写进测试证明保护有效。

并非每个兼容服务都支持流。若服务忽略 `stream=true` 而一次返回JSON，回执明确 `non_streaming`，界面一次显示真实完整结果，不在浏览器伪造逐字动画。只有协议中明确的“不支持stream”错误才允许一次非流回退；认证错误、普通超时和任意400不能被当作能力回退。增量显示、传输成功、schema通过和业务通过是四件不同的事。

## “报名网站”不能被模型悄悄改成后台代录

报名产品的核心是参赛者能否自行提交。单独出现“报名网站”并不明确等于匿名访问；先把尚未说明的入口保留为待澄清，而不是宣称所有报名都不支持。现有能力支持参赛者注册并登录后，在已生成的业务界面提交报名；设计须保留非管理员参与者角色、默认业务角色，以及create/read等本人记录权限。账号注册和业务报名是两件事，不能因为框架能注册账号就宣称独立公众报名门户已经存在。

明确要求匿名提交或独立自定义公众门户时，当前实现暂停并说明需要扩展、验证对应能力，不能换个模板名称假装已经支持。“仅管理员录入”是产品范围变更，只有用户明确取消参赛者自行报名并选择管理员代录时才成立。智能推荐、模型给出的推荐值、旧设计中的管理员角色都不能代替这个更正。

跟踪原始用户消息和本轮逐字更正的来源，再看需求账本中的before、after及变更记录。历史模型分析如果已把队长改成联系人，原始自行报名目标仍应恢复到当前摘要和范围提示；旧分析保留供审计，不能删掉历史后宣称从未出错。重复角色或等价CRUD表述可做保守规范化，但权限、否定、主体、约束和不确定改写仍须保留，不能用模糊相似度去重删除义务。

`requirement_intent.analysis_intent_conflicts` 还检查候选需求是否仍有真实参与者角色和正向自行提交行为，不能只在摘要保留“报名”两个字。`registration_plan_gaps` 再检查可执行设计：明确的报名实体、默认参与者角色、需要账号注册时启用registration，以及对应create/read的own权限。`python-basic` 的per_user、无business合同路径已有内置owner_id隔离；该窄路径无需凭空添加团队业务合同。角色、需求与Plan三层都要通过，单独选择一个范围选项不是执行证据。

## 本阶段源码和后续依赖

本阶段首次创建 18 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
