# LangGraph 工作流的统一结构化输出

平台优先采用 LangGraph 文档推荐的 LangChain 模型增强方法：`with_structured_output`。需求、规划、编码补丁、模型审阅四个节点继续经过同一个 `ModelGateway`，不分别维护按模型 ID 判断能力的适配表，也不自行重写供应商 strict Schema。

本次 **OpenAI 未调用真实 API 验证**。离线测试验证真实官方集成类构造出的 HTTP 请求及响应处理，不代表账户权限、模型可用性或线上质量。DeepSeek 客服真实验收另按同一提交的 `docs/real-model-acceptance.md` 中的验收说明 执行。

## 框架接线

`workbench/model_protocol.py` 使用官方 `ChatDeepSeek` 或 `ChatOpenAI`，共同调用：

```python
structured = model.with_structured_output(
    schema,
    method="json_mode",
    include_raw=True,
)
result = structured.invoke(messages, config={"callbacks": []})
```

`schema` 是现有 Pydantic `Requirement`、`Plan`、`Patches`、`ModelReview` 之一。系统消息仍明确要求一个 JSON 对象并包含完整 Schema，因为 JSON mode 不自动把完整业务约束传给供应商。官方集成负责格式参数、消息协议和结构化解析；平台随后针对原始内容执行严格校验。

LangGraph 官方的 [工作流与模型增强示例](https://docs.langchain.com/oss/python/langgraph/workflows-agents) 使用 `llm.with_structured_output(...)`。直接结构化模型调用适合本项目已存在的确定性节点，不必为了格式化再引入一个自主工具循环。LangChain 的 [模型文档](https://docs.langchain.com/oss/python/langchain/models) 介绍统一结构化接口；[ChatDeepSeek](https://docs.langchain.com/oss/python/integrations/chat/deepseek) 和 [ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai) 是使用的官方集成。

依赖通过 `pyproject.toml`/`uv.lock` 固定可重建版本，不在每次生成任务中安装或查询模型目录。当前锁定 `langchain-deepseek 1.1.1`、`langchain-openai 1.6.7`；正常 `uv sync --locked` 会安装它们。

## 为什么统一选择 JSON mode

两个集成共同使用 `method="json_mode"`，产生 `response_format={"type":"json_object"}`。这是 **供应商 JSON 格式约束 + 本地严格业务校验**，不是宣称全部响应都由供应商 `strict=true/json_schema` 保证。

当前领域契约需要动态字典，例如需求事实 `Requirement.facts`、变更值、枚举显示标签和规则示例。把所有开放对象强行改成 `additionalProperties=false` 会丢失有效需求数据。统一 JSON mode 可保留这些结构，不必建立模型 ID 白名单、私有 Schema 转换器或字段补全器。

官方 [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) 区分 JSON 模式与原生 Schema 约束；[DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/) 说明 JSON 模式、提示要求、空内容和截断边界。以后若领域契约改为适合原生 strict 的封闭传输类型，应仍使用框架的结构化方法，再补相应验证，不在这里维护逐模型协议分支。

## 配置与模型选择

原有默认三项保持不变：`BASE_URL`、`API_KEY`、`MODE`。模型 ID 按原样交给官方集成，不替换成另一模型，也不按名称前缀声称支持。模型不支持所请求格式或账户无权限时，保留明确失败，不降级成无约束文本或演示结果。

可选配置：

```dotenv
PROVIDER=auto
OUTPUT_MODE=auto
# MAX_OUTPUT_TOKENS=16384

# 阶段覆盖示例
# PLANNING_PROVIDER=deepseek
# PLANNING_OUTPUT_MODE=json_object
# PLANNING_MAX_OUTPUT_TOKENS=65536
```

- `PROVIDER=auto` 仅按准确主机选择官方集成：`api.deepseek.com` 使用 `ChatDeepSeek`，`api.openai.com` 使用 `ChatOpenAI`。其他兼容地址使用 `ChatOpenAI` 兼容接线；它同样要求 JSON mode，不能证明任意服务都支持该参数
- 私有代理可显式选择 `PROVIDER=deepseek` 或 `openai`；地址仍由用户配置，不自动改到其他域名
- `OUTPUT_MODE=auto` 和 `json_object` 都采用统一的框架 JSON mode；不提供私有逐模型模式表
- `MAX_OUTPUT_TOKENS` 是有限输出预算。默认 DeepSeek 为65536，其他为16384；参数命名由官方集成处理，捕获请求测试分别检查 DeepSeek 的 `max_tokens` 与 OpenAI 的 `max_completion_tokens`。必要时按模型官方上限调整配置；平台不会静默扩大预算。OpenAI 预算涵盖可见与推理 token，见 [Chat Completions 参数](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create)
- 四个前缀 `REQUIREMENTS_`、`PLANNING_`、`CODING_`、`REVIEW_` 都可覆盖这三项。同端点继承默认；改端点不继承原供应商协议/预算，且必须配置该阶段自己的 API_KEY

DeepSeek 真实验收仍使用已批准的 `deepseek-flash`，不改用户模型。单独的 Hello!/thinking/high smoke 保留原始请求，它只是连接测试。随后的全部业务阶段才走统一结构化链。具体供应商字段与结束原因见 [DeepSeek Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)。

## 本地验证、重试与安全边界

1. 非流式响应最多读取2,000,000字节；SSE逐Token封装与解码正文分开计量，传输上限为 min(64,000,000, 2,000,000 + MAX_OUTPUT_TOKENS × 1024) 字节，解码正文与推理文本合计仍最多2,000,000字节，单帧与未结束行也保持2,000,000字节上限。在 SDK 标准化前检查原始信封。已知供应商必须 `finish_reason=stop`。有效 JSON 若带 `length` 仍按截断失败；refusal/content_filter 立即停止，不试图绕过；不接受该阶段意外的工具调用
2. JSON 解析拒绝重复键、NaN/Infinity/数值溢出、非对象根节点和 Markdown 围栏。`Pydantic.model_validate_json(..., strict=True)` 不把 `"true"` 当布尔值，也不把 `"3"` 当整数；原有额外字段、枚举、长度、关系和跨字段业务验证继续执行
3. 必须同时得到框架的成功结构化解析和平台对原始内容的严格校验。不能只信任框架已转换的 `parsed` 对象，否则宽松类型转换或不完整 JSON 修复可能掩盖原始错误
4. SDK `max_retries=0`，平台每次操作最多两次总尝试，避免双层重试偷偷放大费用。空内容、畸形响应、中断、408/429/5xx可有界重试；类型/语义错误最多一轮带具体路径的修复。鉴权/地址/其他非暂时性4xx、拒绝和截断直接停止
5. 修复保留原要求、原 Schema、原模型/地址/JSON模式；不删除需求，不扩大预算，不声称人工批准。完整系统消息、Schema及修复反馈计入上下文字符上限。原始 reasoning_content 不保存或回填为回答
6. 使用受审计的同步 HTTP 客户端注入官方 SDK，禁止自动重定向和环境代理，保留CI的受限真实传输/离线MockTransport。异步入口为无网络的拒绝传输，不能成为绕开同步审计的另一条路径。已有遥测关闭策略和空回调配置继续生效，不新增LangSmith上传

类型/Schema正确仍不等于需求满足。`flow.py` 的已批准事实、逐字段覆盖、角色权限/关联/工作流/提醒/统计关卡与编译、API、真实浏览器验收全部保留。结构化输出不能代替用户批准或产品测试。

### 逐功能规划的字段反馈与摘要

`FeatureDesign` 的 `outline.features[].id` 是稳定技术标识，必须匹配 `^[a-z][a-z0-9_-]{0,63}$`；中文功能名写入 `title`。`capability` 最多 100 字符，原生与声明式路由必须逐字引用当前模板能力目录中的单个代码，例如 `typed-crud` 或 `role-row-permissions`，不能填入一段业务说明。规划请求从同一适配器目录生成可选代码，避免提示词与校验名单漂移。

逐功能提示独立于纯源码扩展提示：没有模块时使用 `outline + baseline`、`implementation=null`，保留普通 Plan 支持的单记录规则；确有模块时才要求完整任务、场景和受控执行契约。这样避免一段提示同时禁止和允许单记录规则，或要求无模块计划填写不存在的模块/决策字段。

无效 JSON 的重试反馈包含安全的语法行列或静态错误类别；Schema 诊断从受信任的字段定义提取正则、长度、说明和示例，不将响应原文或验证器 `input/ctx` 作为公开诊断。既有精确语义反馈仍用于同一模型的有界修复。重试保留用户需求和原候选，不自动截断、改名或删除功能；完整系统提示也纳入缓存身份。

对话摘要显式登记受控规划与源码修改契约。根级公开字段可显示待校验草稿；`FeatureDesign.outline.summary` 等嵌套摘要只在完整响应通过严格校验后展示，不递归搜索任意字段，也不展示源码内容。模型结构校验成功仍只表示候选可供后续关卡检查。

这些改动有离线协议与报名计划回归，不是用户本机供应商响应已被复现、真实报名网站已交付或模型成功率已提升的证据。

查询义务按“实体、字段、属性”分别核对：`true` 与 `false` 都是明确约束，`null` 或缺失只表示未知。
旧自然语言里的前置/后置查询动词只绑定同一局部字段列表，不能把逗号后分类精确筛选
反套到逗号前关键词字段，也不能因已有一个类型化属性就跳过同一字段的其他属性。
明确且真正矛盾的查询要求仍阻塞，不将未知值默认成 `false`。

权限列表的 Pydantic 字段说明与需求分析提示同时强调 grant-only：未列出的动作不被授权，
多角色共用一个动作的叙述必须取各角色授权的交集，不能取并集。验收说明据同一权限表生成，
不得为了满足模型自行增加的概括而扩权。这是通过现有框架 Schema/提示施加的生成约束，
不是确定性证明任意自然语言都与权限表一致，也没有新增中文 ACL 解析器。
独立审阅仍会阻塞实际语义分歧；不能用 Schema 合法、运行测试通过或关闭审阅来抹掉已记录缺口。

## 缓存与回执

缓存键加入结构化契约版本、框架模式、预算、模型、端点和原需求/Schema。旧版本输出不会被当成新协议下已验证结果。新的成功记录及失败尝试都包含 provider、output_mode、format_reason、contract_version；失败只记录有限安全错误码和尝试序号，不持久化原始拒绝、响应或密钥。运行模型回执接口返回两类记录，旧记录标为legacy。

## 离线验证

```bash
uv run pytest tests/test_provider_structured_outputs.py tests/test_llm.py tests/test_guided_models.py tests/test_permission_analysis_contract.py tests/test_query_obligation_pairing.py -q
```

测试使用真正的官方集成和 `with_structured_output`，只在最终HTTP层注入MockTransport。覆盖共同请求格式、原模型ID不替换、动态事实保真、严格类型、业务约束、拒绝/截断/过滤/空内容、畸形信封、错误回执、无隐式SDK重试、阶段隔离和缓存变更。OpenAI线上可用性保持未验证；真实DeepSeek结果必须另引用相同提交的实际验收运行。
