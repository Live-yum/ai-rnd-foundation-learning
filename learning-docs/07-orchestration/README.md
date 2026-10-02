# 07 · 审批状态机与恢复

[总目录](../README.md) · [上一阶段](../06-generation/README.md) · [下一阶段](../08-control-plane/README.md)

## 图负责顺序，工具负责真相

`flow.Workflow` 把前面写好的函数串成节点：分析需求、澄清/确认、形成设计、设计校验、生成、受限编码、独立验证、可选本机沙箱、可选模型审阅、交付批准和打包。按 `compile` 中的节点与条件边阅读，不要把某个节点函数存在误认为它一定会执行。例如纯CRUD不需要编码模型；只有已批准的额外单记录规则进入编码与有界修复。

`gate` 先由 Store 固化这一版审批内容，再调用 LangGraph 的 `interrupt`。用户回答带 gate_id，恢复时再次核对当前版本与已存批准；模型不能通过在JSON里写 `approved=true` 自己跨过关卡。`conversation.py` 将“批准”“智能推荐”等控制词与普通需求内容区分，避免把批准口令当新需求再次发给模型。

`Runtime` 负责取队列任务、载入检查点、进入图、完成任务和归类错误。SQLite使用独立 `checkpoints.db`；PostgreSQL使用对应checkpoint后端。文件锁和数据库锁限制一个Worker。`last_job_id` 与当前中断共同防止“图已推进，但任务完成记录还没写入”这种崩溃窗口重复消耗下一次回答。

## 依赖闭包为什么比章节标题更重要

此站第一次跑整条本地流程。`flow.plan` 会导入 `toolchain.prepare_context`，`flow.design` 即使是local配置也会导入 `sandbox.validate_configuration`，后者又需要 `daytona_profiles.py`。这些文件必须先完整写入；Daytona SDK和服务仍是第12站才安装启用的可选运行能力。不要为了看起来顺序漂亮把源码换成假stub，也不要因为文件提前存在就声称沙箱已经验收。

模型使用 `tests/conftest.py` 的 `FixtureGateway`，这是明确的测试替身，只为让同样输入可重现。生产 `rnd start` 不会在缺Key时偷偷选择它。夹具控制模型响应，但生成、迁移、HTTP、浏览器和干净解压仍由真实本机工具决定结果。

```bash
# .learning/commands/07-state-machine.sh
uv run pytest tests/test_workflow.py tests/test_guided_workflow.py tests/test_recommendation_stage_budget.py -q
```

前提是相关测试文件已按本阶段索引写齐。需求覆盖完整历史回归含原生适配用例，来源冲突回归还读取诊断fixtures，recommendation_recovery会导入CLI，guided_completion会读取独立部署模板，因此这些整文件统一放第14站全套运行；此处只运行当前闭包完整的三个文件。预期所有用例正常退出，没有failed/error。`test_complete_default_flow` 会实际依次检查 `WAITING_REQUIREMENTS`、`WAITING_DESIGN`、`WAITING_DELIVERY`，再看到 `READY` 和cleanroom报告；其模型调用只有 requirement 与 plan，恰好证明CRUD不靠模型自由编码。

## 主动制造一次“不能继续”

读测试里的旧gate、第二Worker和模型预算反例，先说出你预期的错误，再运行对应测试。`MAX_ROUNDS=0` 和 `MAX_MODEL_CALLS=0` 表示不设累计上限，不意味着HTTP重试或自动修复无限。智能推荐对每个阻塞阶段有独立修复预算，修复失败进入 `BLOCKED` 并保存诊断；不能把需求澄清消耗的修复次数错误借到设计阶段，也不能删掉验收条件来解除阻塞。

本阶段结束时应能跟踪同一run_id从排队到等待、从批准到恢复。真正的恢复是继续已有身份与证据，而非重新新建一个项目看起来成功。下一站只是在这条已测链路外加API、CLI和操作台，不把业务逻辑搬进网页按钮。

## 对话事件与工作流状态分别持久化

流式页面需要展示“正在收到什么”，而编排需要决定“下一步可以执行什么”。两者共用run_id，但不能混为一张已批准需求表。`Store.assistant_event` 追加 `assistant_start/status/delta/completed/failed` 事件；用户回答继续写入Message。助手草稿不会被当作下一轮用户需求，完成事件也不会自动消费审批关卡。

一次逻辑模型响应由response_id联系起来，每次真实尝试还有单独message_id。工作进程重启后，新尝试开始时旧的未完成草稿会被标为 `worker_interrupted`；终态事件重复到达不能追加第二个完成结果。这样既能说明发生过重试，又不让旧消息永远显示“生成中”。

刷新页面时，`Store.transcript` 在同一个读取快照中返回对话与cursor；后续SSE只从cursor之后继续。PostgreSQL显式使用可重复读，避免“消息包含了某个增量，cursor却没包含它”造成重复。`event_stream` 从已经提交的事件回放再跟随新事件，检查到任务不再QUEUED/RUNNING时补查一次尾部事件，再发送idle结束。浏览器关闭或切换任务只关闭这条订阅，已持久化Worker任务仍可继续；重新订阅不会再次调用模型。

需求澄清现在还可包含有ID的结构化问题与选项。先看 `domain.ClarificationQuestion` 的single/multiple/text约束，再看 `clarification.render_answer`：它在 `Store.submit` 已锁定、核对当前gate_id的事务里，从服务器当前选项恢复标签、拼接用户补充文字。旧关卡、伪造选项或漏答必填必须整体拒绝，不能先入队再提示错误。合法回答进入下一轮分析，批准需求/计划仍是另一次明确操作。

## 本阶段源码和后续依赖

本阶段首次创建 14 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
