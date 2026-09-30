# Exact, reviewable UTF-8 source operations against verified commit c3d3c612.
PATCHES = {
    '.env.example': ('c903ca76073590f1aa267891c06fe10cd43930ec6d6246868eb382f2445ff5d1', [
        (64, 64, r'''
# Optional actual Continue FTS component (local by default: no Node required).
# Install/build tools/node first, then select continue to combine its FTS with AST/vector retrieval.
RETRIEVAL_ENGINE=local
'''),
    ]),
    '.gitignore': ('4f57aa9642b7d8685db28539a2715e3e66f59caf9e37737cdf1e74e29535fa40', [
        (18, 18, r'''
# Optional local Node tools; never ship installed dependencies or generated bundles.
node_modules/
tools/node/.built/
'''),
    ]),
    'README.md': ('0fac0c7f99eec9a2cb4a17e1f5d0fc45d56a5f433bc9fd5e459eafb9d0ca031b', [
        (185, 186, r'''设置`CODING_ENGINE=aider`和`REPO_MAP_PROVIDER=aider`可启用实际本机编辑/Repo Map。真实模型Key只交给平台网关，Aider不取得它；登记的CLI入口禁用网络，Token编码和模型元数据来自经过SHA校验的锁定依赖，不在生成任务中下载。

实际Continue全文索引组件已随仓库包含源码和Apache-2.0许可证，固定提交为`5522c6f44ca0ac3528b37244818fbfa39b5af470`。使用Node22（至少22.13）在本机准备：

```powershell
node --version
npm ci --prefix tools/node --no-audit --no-fund
npm run build --prefix tools/node
```

在项目`.env`设置`RETRIEVAL_ENGINE=continue`并重启平台。规划、CLI和只读MCP都会实际执行上游`FullTextSearchCodebaseIndex.update/retrieve`，与本机AST、FTS5和可选向量融合；不是把自写索引重命名为Continue。查询进程禁用网络，不读取IDE私有缓存。`RETRIEVAL_ENGINE=local`仍是无需Node的默认基础方案。Continue IDE可以通过本机stdio MCP访问同一套只读search_code/repository_map，不要求云账号。
'''),
        (202, 202, r'''最后一条是完整资讯测试：复现“模板说明被误作需求阻塞”的初始问答，授权一次智能推荐，经真实Continue/Aider上下文、本机HTTP/数据库验收、真实Daytona与删除沙箱、独立ZIP重新解压验收到READY。模型响应是明确测试夹具，不代表实际供应商账号联调已通过。需先按上方准备Node组件与Aider环境。

'''),
    ]),
    'docs/implementation.md': ('f9b49dc5ff4ec5cd894ec5045618e2cbaa03844a999c1832db660bc2641b2d77', [
        (51, 52, r'''| 5 上下文 | `symbols.py`、`knowledge.py`、`retrieval.py`、`continue_index.py`、`context_mcp.py`、`toolchain.py`、`tools/node/`全部文本文件 | Java/TS/Vue/Python符号和源码行号可检索；只读MCP共享同一索引 |
'''),
        (143, 144, r'''这是本机模型推理，不能配置托管向量数据库或云端embedding API，也不继承聊天模型Key。prepare_context把同一检索结果接到规划阶段；CLI和Continue的MCP读取的也是这套索引。RETRIEVAL_ENGINE=continue时，continue_index桥接固定的上游FullTextSearchCodebaseIndex组件，seed_cache创建它的本机片段输入，Node适配器实际调用update/retrieve，返回结果交给融合器。未选择时保留无需Node的默认实现；不要把MCP桥接误称为索引算法，也不要把组件测试称为IDE界面测试。
'''),
        (161, 162, r'''Aider安装在tools/aider独立Python3.12环境，平台保持Python3.14，避免依赖相互覆盖。平台网关取得经过验证的SEARCH/REPLACE块；Aider CLI在临时独立Git目录执行本机应用操作，不接收真实模型Key。它由tools/aider/offline_runner.py启动，先验证锁定依赖携带的编码和元数据，再禁用联网入口；运行中的版本查询、Repo Map和编辑均不临时下载数据。依赖安装仍是明确单独的uv步骤。
'''),
    ]),
    'docs/recommendation-recovery.md': ('4aaf51f0249e201f83c0b19d572381378c1d41373e91b0bda6646d0e32916ebe', [
        (60, 60, r'''

## 同一资讯任务的跨工具证据

`scripts/news_fixture.py`只是CI注入的模型夹具，不是生产模型失败后的兜底。第一条响应故意把未要求的爬虫和公众网站写进unsupported，模拟报告中的错误。授权一次后，夹具必须收到原始请求、原facts和具体resolution_feedback，第二条响应才把未要求的边界放回limitations。设计响应还核对已批准facts未丢失；真正的生成、数据库、HTTP、浏览器和沙箱程序并不被替换。

浏览器验收从只填写“泰拉瑞瑞亚游戏资讯”开始，真实点击一次智能推荐到下载，再在新产品中验证标题/正文搜索、分类、单日、含两端日期区间以及组合过滤。Daytona验收则在同一真实Runtime中同时启用Aider Repo Map和Continue原生索引，确认本机产品验收、真实Daytona运行及删除、独立ZIP解压复验全部通过后才允许READY。额外业务规则的实际Aider编辑由ci_aider_workflow单独覆盖，普通资讯CRUD不为展示工具而调用编码模型。

以上能证明状态恢复、工具接线与交付验证正常，不能证明所有模型供应商都能理解同一句自然语言。真实供应商的结构化输出、余额和权限仍需用用户自己的配置联调；测试不得偷偷使用用户Key。
'''),
    ]),
    'docs/toolchain.md': ('719b78ee9278e8cb30090ee6084fa00f869a09c75e1d35bcaa0fd21f9f410748', [
        (107, 108, r'''uv run --locked --project tools/aider --python 3.12 python tools/aider/offline_runner.py --check-local-deps
'''),
        (110, 111, r'''预期JSON中aider为0.86.2，packaged_encodings_verified为true，network为disabled。平台依然用Python3.14；不要把Aider的依赖装进平台环境。工具路径可以由程序发现，或在AIDER_EXECUTABLE中明确指定本机安装位置。
'''),
        (116, 116, r'''
先按附录写出tools/aider/offline_runner.py。它由独立3.12解释器运行，验证Aider版本和LiteLLM安装包内的两份Token数据；通过Python审计钩子拒绝DNS、TCP/UDP连接和网络监听，再导入真实Aider。运行时还向Aider提供本地模型元数据文件，避免隐式查询远程价格表。校验失败应按锁文件重新安装，不能删除校验；登记入口不是任意Python的强安全沙箱。
'''),
        (125, 126, r'''运行该脚本前先完成20.5.1的Node准备。它真实调用Aider，真实执行Continue组件与MCP并索引固定Java/Vue源码；模型响应是显式本机测试夹具，不消耗付费模型。报告中的SDK契约测试和本机Daytona服务测试分开标记，不能把前者冒充后者。
'''),
        (127, 128, r'''### 20.5 Continue原生索引与本机stdio连接

#### 20.5.1 先建立能独立运行的真实索引组件

先按附录写出`tools/node/package.json`、`package-lock.json`、`build.mjs`、`continue-host.mjs`、`continue-runner.mjs`、`no-network.cjs`和`upstream/`中的三个文件，再写`workbench/continue_index.py`。全部内容均在书内，不需要先下载本项目骨架。`upstream/FullTextSearchCodebaseIndex.ts`是固定提交`5522c6f44ca0ac3528b37244818fbfa39b5af470`的完整原文件，不能自己删改；LICENSE随它保留，manifest同时记录Git对象指纹及SHA-256。这里使用该公开组件，不声称复制了Continue整个IDE索引生命周期。

本模块需要Node22，至少22.13。没有Node时从Node.js官方历史发布页选择22.x的本机安装包；Windows安装器完成后重新打开终端，WSL使用Linux版本而非Windows可执行文件。先用`node --version`确认版本，再按顺序执行：

```powershell
node --version
npm --version
npm ci --prefix tools/node --no-audit --no-fund
npm run build --prefix tools/node
```

npm ci是安装步骤，只安装package-lock中校验过的依赖；不是索引步骤。build.mjs先检查原组件和许可证指纹，再用固定esbuild将原组件与本机适配器编译到`.built/continue.cjs`，最后记录每份输入及输出的SHA。预期出现`Verified Continue source compiled locally`。生成目录和node_modules不入Git；如果原文件被修改，构建失败而不是从网络取另一版。修改自有适配器后需要重新build；对上游组件的变更必须重新审查来源，不能随手改清单绕过校验。

项目.env写入：

```dotenv
RETRIEVAL_ENGINE=continue
```

然后重启平台，运行：

```powershell
uv run rnd index workbench .data/platform-index
uv run rnd tools search workbench .data/platform-index "model_for"
uv run pytest tests/test_continue_index.py -q
```

检索报告的mode应为`ast+continue-fts5+fts5`；启用本机向量则还带`+vector-rrf`。索引目录产生`continue.sqlite3`和`continue-index.json`，后者包含真实组件名称、文件/片段数量、固定revision、源码摘要和禁网标记。测试中Node未安装会明确跳过可选工具测试；正式Actions设置`RND_REQUIRE_NODE_TESTS=1`，缺少工具会失败而非通过。缺少`.built`时应执行上述安装/构建，索引过期则重建源码索引；不能把配置改成远程URL绕过。

接下来理解每个文件如何连接：retrieval.query先完成模板源码和行号校验，continue_index.rank用源指纹加工具指纹判断缓存是否有效。seed_cache将原有AST片段转换成组件所需的chunks/chunk_tags表；只有缓存库涉及此转换，不修改产品数据库。invoke通过固定Node命令传递临时JSON请求，子进程只读这些请求和缓存。continue-runner调用上游update写真实FTS表，随后调用上游retrieve做BM25查询。continue-host只提供SQLite、标签和文件名接口，不重新实现上游索引算法。返回值只有已知片段ID，Python再从已校验的本机片段库取内容。

限定路径时先筛选候选，空路径集不会变成“全仓库”；短于三字符的符号仍可由平台原有FTS/符号检索贡献结果。融合器合并Continue排名、平台词法排名和可选本机向量排名，并再次执行输出预算。源码改变或文件删除后，旧Continue库整体按新片段身份原子重建，不保留失效行号。上游读取结果用IN查询不保证排名顺序，本机适配器恢复它自己的BM25顺序，不用另一个模型重排。

`no-network.cjs`在登记的Node程序载入前禁用DNS、TCP、UDP、HTTP、HTTPS、HTTP2和fetch入口；请求环境不传模型Key、代理或遥测变量。被索引源码只是文本，不执行其import或脚本。此钩子保护已审阅的索引程序，不是对恶意原生程序的操作系统沙箱。无需这些能力时保持`RETRIEVAL_ENGINE=local`，平台仍可用默认AST/FTS完成生成。

#### 20.5.2 再连接可选的本机IDE

'''),
        (174, 175, r'''MCP是IDE接入方式，原生FTS是上一节独立运行的索引组件，两者不是同一个概念。CI既测试真实上游组件，也测试真实stdio初始化/工具查询；这些不是自动操作IDE界面的测试。IDE聊天模型可按你的服务填写；不启用云端检索、远程配置和额外遥测。
'''),
        (267, 268, r'''| 混合检索 | retrieval.query、continue_index.rank、Continue原生update/retrieve、add_embeddings | 实际组件SQLite表与BM25、可选本机向量、预算、过滤、过期拒绝 |
'''),
        (270, 271, r'''| 本机沙箱 | sandbox、daytona_worker、daytona_local、daytona_bootstrap、ci_daytona_local | 从一次智能推荐经真实上下文/验收/沙箱/清理/独立解压到READY的同一运行；LLM仅显式测试夹具 |
'''),
        (312, 312, r'''
Continue固定全文组件：https://github.com/continuedev/continue/blob/5522c6f44ca0ac3528b37244818fbfa39b5af470/core/indexing/FullTextSearchCodebaseIndex.ts
Node本机SQLite接口：https://nodejs.org/download/release/v22.16.0/docs/api/sqlite.html
'''),
    ]),
    'scripts/build_handbook.py': ('2bdc1afec9c93aa13aad144a2a0794e45146ff5866384e6b7a0869bd077178a3', [
        (51, 51, r'''            "tools/aider/offline_runner.py",
'''),
        (56, 56, r'''    ("本机Continue组件、适配器及Node依赖锁", [
        "tools/node/package.json", "tools/node/package-lock.json", "tools/node/build.mjs",
        "tools/node/continue-host.mjs", "tools/node/continue-runner.mjs", "tools/node/no-network.cjs",
        "tools/node/upstream/manifest.json", "tools/node/upstream/FullTextSearchCodebaseIndex.ts", "tools/node/upstream/LICENSE",
    ]),
'''),
        (78, 79, r'''                if name in {".github/workflows/prepare-local-tools.yml", ".github/workflows/runtime-contract.yml"}:
'''),
        (108, 108, r'''                ".mjs": "javascript",
                ".ts": "typescript",
'''),
    ]),
    'scripts/handbook_notes.py': ('e14369b5f99018af33295aad690e6194ca726eb7822984207a887ca57469883f', [
        (84, 84, r'''    "continue_index": (
        "固定Continue全文索引组件的本机适配器",
        "bridge_identity校验源码与已编译工具；seed_cache把Tree-sitter分块转换为上游组件需要的表列。rank按索引身份原子重建并运行实际update/retrieve，再把结果限制在平台已验证的分块范围。缺少工具时报出安装命令，绝不连接云端替代。",
        "retrieval.query → continue_index → 固定Continue组件 → 独立本机SQLite缓存；test_continue_index。",
    ),
'''),
        (96, 97, r'''        "make_server将search_code和repository_map包装成MCP工具，结果仍来自本平台索引。export_continue只写明确的stdio启动配置，已有配置拒绝覆盖；服务不开放HTTP云入口；启用Continue引擎时，查询会交给固定上游全文组件及本机适配器，而非IDE全局缓存。",
'''),
        (379, 379, r'''    if name == "tools/aider/offline_runner.py":
        return ("Aider本机禁网入口", "校验独立Python版本、Aider版本、依赖中Token数据与模型元数据，再安装审计钩子并调用真实CLI；--check-local-deps只做离线自检。", "aider_tool.command → 本文件 → Aider Repo Map/apply；tests/test_aider_offline和ci_toolchain分别验证拒绝路径与实际工具。")
    if name.startswith("tools/node/upstream/"):
        return (
            "固定的Continue开源全文索引组件及许可证",
            "TypeScript源码原样保留，manifest记录上游提交、Git对象哈希与SHA256，构建前逐个验证。这里只嵌入全文索引组件，不加载Continue的IDE、账户或托管服务；LICENSE必须随源码保留。",
            "npm run build --prefix tools/node → esbuild绑定本机host → continue_index调用；独立SQLite缓存。",
        )
    if name.startswith("tools/node/"):
        return (
            "本机Node索引运行边界",
            "package-lock固定安装依赖；build校验上游源码并编译工具，host用Node内置SQLite提供数据库接口，runner只接受有界JSON文件协议，no-network在进程启动时拒绝网络接口。源码片段只写入检索库，不被执行。",
            "先npm ci再npm run build；Python continue_index校验构建回执并调用runner；test_continue_index与ci_toolchain。",
        )
'''),
    ]),
}
