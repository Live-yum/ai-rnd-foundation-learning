# 第 20 章：把代码上下文、精确编辑和沙箱接入实际流水线

这一章从已经完成第 0 至 19 章的平台继续，不新建另一套平台。全部文件的完整内容在本手册后面的“完整源码附录”；包括本章新文件、已有文件修改后的全文、两套 uv.lock、测试和 Actions，不需要从片段猜出剩余内容。创建文件时始终以仓库根目录为当前目录，按附录标题所示的相对路径新建父目录、粘贴完整文件，保存为 UTF-8。不要把 tools/aider 的依赖装进平台环境。

## 20.1 先理解新增的关卡

现在实际连接是：选择技术栈和数据库 → 累积澄清 → 需求确认 → source_context（校验模板、解析、检索、仓库地图）→ 规划 → 设计确认 → 原生/确定性生成器 → 受限业务规则编辑 → 本机真实验收 → sandbox（可选 Daytona 附加关卡）→ 可选语义审阅 → 干净解压复验 → 交付确认。已有 checkpoint、人工批准、智能推荐、多模型隔离和失败恢复继续工作。

AI 不负责重复写 CRUD。Yudao 仍调用已集成的 yudao-module-infra 原生生成器，FastapiAdmin 仍调用其原生生成器；数据库初始化、迁移、业务表、菜单和权限仍走原有确定性流程。增加工具不是放开任意 shell 或允许模型改变验收测试。

| 文件 | 在哪里创建、为什么需要 | 连接到哪里、下一步 |
| --- | --- | --- |
| `workbench/symbols.py` | workbench 目录；解析 Java、TS、JS、Vue 的声明、注解、继承和组件标签 | knowledge.build_index 调用；先通过解析测试再接检索 |
| `workbench/retrieval.py` | 同目录；把带 SHA 的语法片段写入 SQLite FTS5，按预算返回真实行号 | source_context 和 MCP 共用；源码变化必须先重建 |
| `workbench/knowledge.py` | 用附录全文更新原文件；保留 Python AST，增加语法版本及增量缓存 | rnd init、rnd index、编辑前后都会调用 |
| `workbench/context_mcp.py` | 同目录；只公开查询和仓库地图两个工具 | Continue Agent 通过 stdio 调用；不提供 shell 或写文件接口 |
| `tools/aider/pyproject.toml`、`.python-version`、`uv.lock` | 新建 tools/aider；把 Aider 冻结在独立 Python 3.12 环境 | 平台调用可执行文件，不 import Aider 私有 Python 实现 |
| `workbench/aider_tool.py` | workbench 目录；调用真实 Aider CLI 的 Repo Map 和 apply | 模型输出经预验证后进入临时 Git 工作区；最后受控写回 |
| `workbench/sandbox.py` | 同目录；明确同意上传后创建、上传、固定检查、收集结果、删除 Daytona | 本机通过后才执行；任何失败都不能自动变成 READY |
| `workbench/toolchain.py` | 同目录；封装流水线 context 阶段与 rnd tools 命令 | CLI 与 flow 使用同一套实现，不另写演示程序 |
| `workbench/settings.py`、`cli.py`、`flow.py`、`runtime.py`、`api.py` | 更新附录全文；接线、设置默认关闭外部服务、记录状态 | 与现有 API/GUI 共用工作流，不改变用户的批准语义 |
| `tests/test_toolchain.py`、`scripts/ci_toolchain.py` | 分别在 tests、scripts 新建 | 前者测试边界与 SDK 契约；后者调用真实 Aider、MCP、原生源码 |

Tree-sitter 是语法解析器，不是 Java/TS 的完整类型系统。这里能够提取语法结构和 Vue 内嵌 script 的真实行号，不声称做了跨模块完整类型推导；编译器、vue-tsc 和运行验收仍然不可省略。解析失败或超限会有诊断，检索返回的是不可信源码数据，不是对 Agent 的高优先级指令。

## 20.2 默认安装与第一条查询：不需要新的模型账户

在根目录执行：

```bash
uv sync --locked
uv run rnd init
uv run rnd index templates/product .data/examples/product-index
uv run rnd tools search templates/product .data/examples/product-index "validate"
uv run rnd tools repo-map templates/product .data/examples/product-index
```

正常结果：第一条查询打印 JSON，包含 source_digest、mode=ast+fts5、matches；每条命中都有 path、start、end、sha256、content。仓库地图的 provider 默认是 local-symbol-map，并明确报告 omitted_symbols。这两条命令不会调用模型。索引目录必须放在被索引源码目录之外，不能把索引放入 templates/product 内。

打开 `.data/examples/product-index/index.json` 可以看文件哈希、符号和解析器版本；`search.sqlite3` 是生成的搜索数据库，不是用户的业务数据库，不应加入 Git 或交付包。第二次索引会复用未变化文件。文件删除会移除旧片段，文件变化会使旧查询直接报错，重新执行 rnd index 即可。解析器版本或分块规则变化也会触发搜索库重建；内容未改变的分块可以保留已有向量。

原生模板在 rnd init/源上下文关卡从仓库内的固定 SHA 归档展开并索引，不需要运行任务时克隆上游。模板归档及许可证仍按 manifest 校验。依赖安装仍需要网络。

## 20.3 真实 Aider Repo Map 与 SEARCH/REPLACE

先单独安装工具，明确指定 Python，避免 CI 或终端中已有 UV_PYTHON=3.14 覆盖工具环境：

```bash
uv sync --locked --project tools/aider --python 3.12
```

在平台根目录 `.env` 中按需要设置：

```dotenv
REPO_MAP_PROVIDER=aider
CODING_ENGINE=aider
```

重启工作台后，新任务的规划上下文使用 Aider 实际 `--show-repo-map`；选择 `symbols` 可以恢复默认确定性语法地图。`rnd tools repo-map` 也使用同一个开关。Aider 版本不匹配或未安装时会报错，不会在你明确选择 Aider 后悄悄用另一个工具冒充。

只有计划中存在已批准、平台支持的业务规则时才调用编码模型。编码模型仍由现有 ModelGateway 调用，因此一个默认 BASE_URL/API_KEY/MODE 就能使用，也保留 CODING_* 分阶段覆盖和总量预算。Aider 不接收真实模型密钥；它只应用已经结构化返回的块，不自主运行模型、lint、测试、网页访问、shell 或 Git hooks。

精确编辑顺序是：读取 custom_rules.py 当前文本及 SHA → 模型返回 SEARCH/REPLACE 块 → 检查允许路径及唯一原文匹配 → Rules 语法白名单校验 → 临时 Git 仓库记录修改前 commit → 真实 Aider `--apply` → 比对实际结果与预期结果 → 再次校验 → 记录修改后 commit → 受控原子写回 → 重建索引 → 原有正反例、HTTP、重启、干净解压验收。失败重试仍有界，不能删除规则来让测试变绿。

当前自动编辑白名单仍是 python-basic 产品的 `custom_rules.py`，不是放开任意 Java/Vue 文件修改。Yudao/Vben 已接入解析、地图、检索及原生生成器，但不能把此 PR 理解为已经支持所有复杂 Java/Vue 定制。要扩大白名单，需要独立批准任务类型、实现对应结构校验和真实运行验收；现有不支持项会继续 BLOCKED，不把源码生成当成成品验收。

回执在 `.data/runs/<run-id>/coding-<attempt>.json`；记录前后 SHA、diff、Aider 版本和前后 Git commit。工具配置、缓存、Git 历史不进入产品 ZIP。修改历史保存在该 run 的 edits 子目录；交付前发现错误应恢复同一 run 修复并重新验收，不要手工更改已验收 ZIP 后沿用旧回执。

## 20.4 Continue：公开 MCP 接口，共用本地索引

维护状态核查：Continue 上游 README 已宣布不再主动维护，保留最终 2.0.0 版本。参考 https://github.com/continuedev/continue 。本平台因此只使用其公开 MCP 配置边界，不 import 上游私有索引内部实现，也不会自动替用户切换到其他编辑器。平台自有检索与交付流程不依赖 Continue 进程存活；CI 验证的是 MCP 协议和导出配置，不把协议通过写成已经验证你的 IDE、模型账号或所有扩展版本。安装/升级客户端后应检查实际加载的两项工具。

这里没有伪造一个“Continue 独立索引 HTTP API”，也没有复制 Continue 私有向量数据库。平台实现自己的 AST + SQLite FTS5 + 可选向量检索，并通过 Continue 官方支持的 MCP 接口提供上下文。Continue 扩展是可选开发者界面；不懂编程的用户仍只用平台网页。

假设把根目录作为 Continue 工作区，继续使用上面的示例索引：

```bash
uv run rnd tools continue-config . templates/product .data/examples/product-index
```

正常创建 `.continue/mcpServers/rnd.json`，里面只有 uv 命令和明确的本机路径，没有 API_KEY。在 Continue 的 Agent 模式加载该工作区 MCP 配置，可看到 `search_code` 和 `repository_map`。客户端的模型仍可能把返回的上下文发送到其已配置的供应商，使用前必须确认 Continue 自己的模型配置和数据策略。平台不替第三方 IDE 作保密保证。

查询具体 Vben Ant Design 页面用法时，在 search_code 参数中设置 `file_suffix=".vue"` 和 `path_prefix="apps/web-antd/"`；CLI 对应 `--file-suffix .vue --path-prefix apps/web-antd/`。筛选在数据库排名之前执行，避免其他前端适配器的同名 Hook 定义占满结果。

已经存在 rnd.json 会报错，而不是覆盖你的配置。换机器后路径可能不同，应人工比较后重新生成。MCP 进程的 stdout 专用于 JSON-RPC，不要在 context-server 里添加 print 调试输出。源码根目录在启动时固定，调用者不能指定任意路径或执行命令。`.continue` 配置不进入源码索引和最终产品。

## 20.5 可选向量检索：独立地址、独立密钥、明确上传同意

默认 FTS5 + 符号查询已经可用。语义检索需要额外的 embedding 模型，不是把聊天模型名字塞入 /embeddings 就一定能工作。只有明确配置下面全部条件后才上传源码片段：

```dotenv
EMBEDDING_BASE_URL=https://your-approved-provider.example/v1
EMBEDDING_API_KEY=replace-with-that-providers-own-key
EMBEDDING_MODE=replace-with-your-embedding-model
EMBEDDING_ALLOW_UPLOAD=true
EMBEDDING_MAX_CHUNKS=500
```

然后执行：

```bash
uv run rnd tools embed templates/product .data/examples/product-index
uv run rnd tools search templates/product .data/examples/product-index "where are input values validated"
```

向量建立成功后，CLI/MCP 查询的 mode 包含 vector-rrf。检索组合关键词和向量的排名，而不是把两个不兼容分数随意相加。默认规划关卡仍使用不收费的 AST/关键词/仓库地图；可选向量当前供显式 CLI/MCP 查询使用，不声称每次规划都调用向量模型。待嵌入块数超过预算时在调用前停止；重复执行会复用未变化的分块。

默认 API_KEY、CODING_API_KEY 不会隐式传给 embedding 地址。客户端不跟随重定向，不读取 HTTP 代理环境，检查响应尺寸、向量维度、有限数值和分块序号。改变 embedding 模型应重新建立对应向量；同名模型维度突然变化会拒绝混用。响应无效或网络错误应修复配置，不要改测试为跳过。

## 20.6 Daytona：先明示同意，再执行额外验证

默认 `SANDBOX_PROVIDER=local`，不创建任何云资源、不要求 Daytona 账户。启用前先安装 SDK：

```bash
uv sync --locked --extra daytona
```

创建并审核你自己账户中的沙箱快照。python-basic 快照需要 Linux、Python 3、uv、可安装 Python 3.14、允许访问依赖源；原生构建还需要对应 JDK/Maven、Node/pnpm。快照名和目标区域由你决定，平台不会替你选择付费镜像或给出账户可用性保证。

```dotenv
SANDBOX_PROVIDER=daytona
DAYTONA_API_URL=https://app.daytona.io/api
DAYTONA_API_KEY=replace-with-your-daytona-key
DAYTONA_TARGET=us
DAYTONA_SNAPSHOT=replace-with-your-reviewed-snapshot
DAYTONA_ALLOW_UPLOAD=true
```

这些配置表示允许把经过筛选的产品源码上传到所选 Daytona 服务，可能产生该账户费用。请先了解自己的费用和配额；不需要这一步的学习用户保持 local 即可。生产数据库、平台 `.env`、模型密钥和本机业务数据库不上传；`.npmrc` 出现认证字段会拒绝上传，而不是泄漏账户令牌。

python-basic + SQLite 的远程关卡执行锁定依赖安装、可信迁移/HTTP/CRUD/重启验证，并读取实际 JSON 报告。可信 verify.py 从平台原始模板上传到产品之外，不接受模型改写的“总是成功”验收脚本。python-basic + PostgreSQL 的远程关卡当前明确阻止，因为没有获授权的远程测试数据库，不能把本机凭据发送到云端。

Yudao 和 FastapiAdmin 的远程关卡是额外构建/类型/语法检查，不冒充远程完整原生数据库、浏览器验收；原有本机托管模式的真实数据库、权限、浏览器、独立新数据库恢复等门槛仍必须通过。本 PR 没有配置 E2B，也没有把它标为已接入。

成功、命令失败、上传失败均进入 finally 删除沙箱。配置自动停止/删除兜底；删除失败会保留 sandbox_id 并阻止交付，请在你自己的 Daytona 控制台清理。`.data/runs/<run-id>/daytona-verification.json` 包含源码摘要、检查名称/退出码、脱敏日志、SDK 版本和 cleanup。不要把 SDK 契约测试当成已经在你的云账户执行：没有真实凭据时，CI 只验证真实 SDK 的接口和明确标注的模拟生命周期。

## 20.7 从每个文件到 Actions 的验收顺序

创建完本章文件、更新源码后，在根目录执行：

```bash
uv sync --locked --all-extras
uv sync --locked --project tools/aider --python 3.12
uv run pytest tests/test_toolchain.py -q
uv run python -m scripts.ci_toolchain
uv run pytest -m "not postgres"
uv run ruff check .
uv run ruff format --check .
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
```

第一关验证 AST 注解、Vue 行号、增量失效、文件边界、预算、独立密钥、向量返回校验、MCP 工具白名单、编辑原文匹配、Daytona 同意及清理。第二关先让真实 LangGraph 调用真实 Aider，从已批准业务规则一路完成独立依赖安装、HTTP、重启和干净解压交付（仅模型返回用明确测试夹具），然后用仓库内真实 Java/Vue 模板查询，启动真实 stdio MCP 客户端/服务端，运行锁定 Aider CLI 的地图和编辑，并检查 Git commits；不消耗真实 LLM Key。第三关回归平台整个流程，不能只跑新增测试。随后必须通过 PostgreSQL、真实浏览器、原生模板和干净产品交付的既有 Actions。

`Toolchain integration acceptance` 会执行工具集成验证并上传报告；`Daytona live smoke (explicit opt-in)` 仅允许已审核合并的 main 分支手动执行、必须显式勾选上传授权并提供账户 Secrets 和快照，不能在不可信 PR 上读取密钥。真实运行没有配置或失败，不能写成通过；报告中 daytona_live=false 只说明未使用账户，不等于测试跳过所有生命周期。

新增或修改文件后必须重建两份完整手册。Actions 继续用源码哈希校验全文，并在空目录还原源文件，不能只更新章节摘要。如果缺文件、锁文件过期、解析库未安装、Aider 版本不对，停在对应关卡修复后重跑；不要删除锁、放宽规则、伪造测试或将 SOURCE_READY 改名为 READY。

## 20.8 官方接口依据与维护边界

本实现参考的公开接口：Tree-sitter Python API（https://tree-sitter.github.io/py-tree-sitter/）、Aider CLI scripting（https://aider.chat/docs/scripting.html）及选项说明（https://aider.chat/docs/config/options.html）、Continue MCP 配置（https://docs.continue.dev/customize/deep-dives/mcp）、Daytona Python SDK（https://www.daytona.io/docs/en/python-sdk/）。实际受测版本以仓库两份 uv.lock 为准，不把上游 main 分支当固定接口。

修改这些上游版本时需要同时测试 Java/Vue 真实源码、Aider CLI 行为、MCP 协议及 SDK 契约。更换实现不得改变“确定性生成优先、用户事实不丢失、不外传另一供应商密钥、测试先于 READY、产品独立启动”的原则。


## 20.9 从失败报告恢复，而不是删除项目

外部工具的退出码、超时标识和有长度上限的脱敏输出写在 `.data/runs/<run-id>/tool-failure.json`。网页的运行报告和已鉴权的 `GET /runs/<run-id>/report` 可以读取它，也能读取 `source-context/context-receipt.json` 与 `daytona-verification.json`。这些是上一次失败或检查的证据；先看 run 当前状态及报告的 job_id，不把旧失败当成重试后的最新结果。文件没有生成时不要假定该阶段通过。

例如 Aider 使用 `--config` 时需要 YAML 对象。隔离配置文件必须是 `{}\n`，不能是空文件；dotenv 和 Git 配置继续使用另一个空文件。完整实现位于 `workbench/aider_tool.py`，不要把用户 `.env` 当成 Aider 配置。配置错误会在任何产品写回前停止，并保留实际诊断；`tests/test_toolchain.py` 同时校验 YAML 类型、配置文件分离和模型密钥不继承。

修复工具安装或配置后，保留原数据目录和运行 ID，在平台根目录执行：

```bash
uv run rnd retry <run-id>
uv run rnd chat --run <run-id>
```

`<run-id>` 必须替换为网页显示的运行 UUID。重试利用原 checkpoint 和批准记录，不重新创建项目；重新验证通过后才能获得交付资格。需要向他人提供诊断时仍应先人工检查：程序屏蔽的是平台已知的密钥，不保证识别你手工写入普通源码的所有私人内容。测试中的失败夹具会验证原密钥消失、日志长度有界、退出码保留；真实 Aider 流程失败时，Actions 还会上传 `aider-workflow-failure.json` 便于定位。
