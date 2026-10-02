# 08 · API、CLI与Vue流式操作台

[总目录](../README.md) · [上一阶段](../07-orchestration/README.md) · [下一阶段](../09-native/README.md)

## 一套内核，三个入口

`api.create_app` 把Store和Runtime接到FastAPI生命周期，启动时迁移控制数据库并取得本机访问令牌，可选启动内置Worker；关闭时通知Worker停止、等待线程退出并释放数据库。`/health` 说明进程能回答，`/ready` 进一步检查数据库与要求中的Worker，它们不能互相替代。

CLI和Vue操作台都是HTTP客户端，不各自复制一套编排。全部数据接口、模型设置、SSE和下载都要求本机Bearer令牌；TrustedHost限制可信主机名，页面还设置同源脚本/连接等CSP边界。创建项目、运行、回答关卡等状态变更继续使用幂等键，审批继续绑定当前gate_id。漂亮的按钮不能让一个过期批准重新有效。

## 先按依赖顺序写界面，再构建

`ui/` 是平台本身的控制面，`templates/frontends/` 是以后生成给业务产品的页面，两者不能互换。先读 `ui/src/types.ts` 与 `api.ts` 的数据和传输约定，再写 `presentation.ts`、`state.ts` 的状态变化，最后组装App和components。每一层都有独立责任：api只处理认证请求和流帧；state管理当前任务、游标和订阅寿命；展示函数把事件映射为消息；组件渲染表单、进度与操作。

在学生项目根目录执行以下命令，不进入tools/node，也不在learning-docs目录安装依赖：

```bash
# .learning/commands/08-build-vue.sh
npm ci --prefix ui --no-audit --no-fund
npm test --prefix ui
npm run build --prefix ui
```

`npm ci` 根据lock安装，`npm test` 执行实际Vitest测试，build先做vue-tsc类型检查再由Vite输出 `workbench/web`。构建失败就停在这里，不使用工作区里原有app.js假装新源码已经成功。`npm run dev --prefix ui` 只适合开发热更新，代理目标见vite配置；正式 `rnd start` 使用本机后端提供的构建资源，不要求另开Vite服务器。

生成的app.js、style.css和index.html在源码附页中按Base64资产快照折叠保存。它们无需手写；可读实现位于ui/src。这样只带教材既能逐字节还原已有运行资产，也能用完整源与锁重新构建。最后一站的独立验收会比较重新构建后的全部资产路径和字节，不允许漏文件或用旧bundle掩盖源码缺失。

## 无账号的检查先走通

```bash
# .learning/commands/08-api.sh
uv run pytest tests/test_api.py tests/test_guided_selection.py tests/test_cli_connection.py tests/test_streaming_backend.py tests/test_model_settings.py tests/test_clarification_choices.py -q
uv run rnd --help
uv run rnd doctor
```

API测试使用临时Store和明确测试网关，协议测试使用受控的增量HTTP传输；它们不接触自己的供应商账号。检查包括错误令牌401、恶意Host400、过期配置409、错误关卡冲突、幂等重复请求、真实协议增量先于最终结果、失败草稿清除和跨分块密钥脱敏。这是本机协议与交互逻辑的证据，不是已向真实付费模型成功请求的证据。未配置模型时doctor明确显示缺失，不能把它叫模型通过。

## 第一次启动，先打开设置壳

本阶段可以在没有供应商Key时启动操作台，页面会引导配置；创建运行及需要模型的后续操作仍拒绝无效配置，不会偷偷换成测试答案。`rnd init` 还会解压原生模板归档，分阶段读到这里先不运行它；归档要在第09站按固定上游来源准备。基础页面和模型设置不等于原生环境已经就绪。

终端A在项目根目录保持服务运行：

```bash
# .learning/commands/08-live-start.sh
uv run rnd start
```

终端B在同一项目目录取得本机令牌，输入终端A打印的页面地址：

```bash
# .learning/commands/08-local-token.sh
uv run rnd token
```

令牌只输入自己的本机页面，不分享、不写入截图或教程。页面把它保存在当前内存，刷新后需要重新连接；它不是模型API Key。默认地址为 `http://127.0.0.1:8000/`，设置PORT后用实际打印地址。端口冲突先检查启动日志，不能看到旧页面就判断新服务已启动。平台仍只监听本机，没有公网多用户身份体系。

## 一个需求怎样逐段出现

连接后可先在首页或项目内写下需求，提交前再确认真实目录中的模板、前端、数据库和标题。HomeView负责创建项目（需要时）与运行，ProjectsView只负责已有项目列表和导航。页面创建运行只是提交受认证的HTTP请求，模型由Worker执行。`Runtime → ModelGateway → AuditedEventStream → AssistantStream → Store事件` 是文字产生链；`/runs/{id}/stream → ui/src/api.ts → state.ts → RunView` 是显示链。

这里用带Authorization的fetch读取SSE，而不是把令牌放URL。TextDecoder保留不完整UTF-8字符，SSEParser等到空行才结束一帧；一帧可能跨多个网络块，也可能含多行data，注释心跳不应变成聊天消息。公开增量显示为待验证草稿，完成事件用严格校验后的完整公开内容收口，失败则清除草稿并显示安全错误。模型的隐藏推理、原始提示和补丁源码不会因此成为聊天内容。

刷新不是“重新问一次模型”。页面先获取同一个快照的transcript与cursor，再订阅cursor之后的事件。断线按有界退避重连，每个事件id只应用一次。快速从运行A切到B时，`runGeneration` 和AbortController让A迟到的响应失效，不会把A的字填进B。关闭页面或断开订阅不等于取消后台任务，本版本不能把它说明为已经停止模型；真正运行状态始终以后台为准。

服务商没有提供增量时，页面明确显示非流式结果，不以逐字动画伪装。任务阶段进度来自run状态、pending和事件；“等待确认”“预算暂停”“生成失败”“可交付”各有不同的后台含义。阅读进度抽屉时，应能在事件或报告中找到对应事实，而不是只看到一个装饰百分比。

## 澄清选项与审批不是一回事

单选、多选和文字问题来自当前Requirement.question_items。Questionnaire提交question_id、option_ids及用户补充，后端从当前pending取选项标签。比如“谁用第一版”已经从旧问题Q变为Q2，旧页即使仍能点击也不能排队；要刷新当前关卡、重新确认。必答项没完成，页面应解释缺项，服务器仍要再校验。

补充回答只让需求继续分析。看到需求或计划卡片后再执行批准/拒绝；gate_id保护内容版本。智能推荐修改的是持续委托状态，不是一次普通提示，恢复人工确认影响后续关口。连续点击同一操作或网络重试必须保留相同幂等请求身份；旧版本冲突不能靠自动重发批准消除。

## 模型设置：保存成功不等于连接测试成功

设置页区分默认连接、需求、计划、代码和可选复核覆盖。GET `/settings/models` 只返回安全摘要与revision，不回填已保存密钥。保存使用PATCH/PUT及expected_revision，另一窗口已经写入时返回409；用户应读取最新版本重新核对，而不是让页面暗中覆盖。输入仍未保存时离开有提示，放弃修改也清除尚未保存的Key。

Key操作明确区分保留、更换和清除；更换BaseURL必须为新服务输入独立Key，不能把旧服务Key自动带到新地址。同源认证、请求大小限制、文件锁与原子替换共同保护写入。本机配置文件包含秘密，POSIX要求600权限，路径不能是符号链接；不要将它加入Git或当成学习示例。正在执行的一次模型调用和它的重试使用固定配置快照，下一次调用才看到新配置。

当前保存接口只做格式、继承、安全约束与持久化校验，不发起模型请求；界面的连接测试尚未开放，不能显示“保存即连接成功”。需要真实调用时由操作者明确配置自己的供应商并发起需求，费用与外部服务证据单独记录。

## CLI连接语义保留

`rnd chat` 不是独立服务启动器。终端A保持 `uv run rnd start`，终端B才运行chat、show、retry、recommend、manual或download。`client()` 用contextmanager管理HTTP连接，按同一份Settings.port构造地址，在初次交互之前先请求 `/health`。

初次或后续 `httpx.ConnectError` 都转换为“无法连接本机平台”和另终端启动、检查PORT/日志的中文提示，退出码为1并关闭客户端。初次健康检查失败不会先询问项目；后续断连可能发生在交互开始后。服务端业务错误、模型配置缺失或审批拒绝，不属于这条连接错误。`tests/test_cli_connection.py` 的7类离线命令与2种成功/后续断连实例继续保护用户修复。

## 本阶段练习与排错

用受控测试先验证：两个增量在最终响应前可见；失败不留下已批准结果；刷新无重复文本；切到另一运行无串线；过期问题/配置保存被拒绝。真实页面测试见第14站的浏览器验收，它会实际启动服务并操作组件，不能用截一张静态原型图代替。

白屏先看构建是否完成以及index引用的 `/ui/` 资产是否可达；401先重新输入本机令牌；模型配置503去设置页核对有效字段；SSE无文字先区分“没有公开字段增量”“兼容服务非流式”和“网络断开”。不要用允许跨源、移除认证或伪造完成事件来解决页面问题。下载仍要检查实际交付状态、批准与包哈希：READY表示运行验收后的交付；SOURCE_READY只允许拿到来源已核对的源码包，不等于原生平台已经编译、启动或浏览器验收。不能仅凭下载按钮说明项目已完成。

## 本阶段源码和后续依赖

本阶段首次创建 40 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
