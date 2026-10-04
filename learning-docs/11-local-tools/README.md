# 11 · Continue、Plop与Aider

[总目录](../README.md) · [上一阶段](../10-business/README.md) · [下一阶段](../12-daytona/README.md)

## 给每个工具一件可以检查的事

第04站的AST/FTS已经能工作。现在接入可选增强工具：Continue使用仓库内固定提交的 `FullTextSearchCodebaseIndex.ts`，Node桥接负责本机SQLite宿主和update/retrieve调用；`continue_index.py` 核对桥接身份并执行它。这里不是安装整个IDE生命周期，也不读取IDE私有缓存。`context_mcp.py` 把同一检索与仓库地图作为只读stdio工具提供给支持MCP的客户端，不新增任意文件修改权限。

Plop与Aider不负责同一层。`scaffolding.py` 根据批准规则注册允许文件和区域，由真实node-plop从受信模板放入框架规则与表单入口。`aider_tool.py`、`native_coding.py` 再把模型网关给出的精确SEARCH/REPLACE或受限表达式交给实际Aider，在隔离Git副本里应用。命中不唯一、前像SHA过期、未知路径、越界区域、非法表达式都拒绝。Aider退出码0只说明它完成编辑，不代表业务规则通过。

原生规则需继续编译、类型检查、API正反例和真实浏览器；失败回滚候选文件，保留诊断，在有限次数内修复。客服声明式business路径无需自由编码，且不能与standalone custom_rules混用。把所有需求都推给编码模型，会破坏前面建立的确定性边界。

## 安装边界必须显式

```bash
# .learning/commands/11-tool-install.sh
node --version
npm ci --prefix tools/node --no-audit --no-fund
npm run build --prefix tools/node
uv sync --locked --project tools/aider --python 3.12
uv run --locked --project tools/aider --python 3.12 python tools/aider/offline_runner.py --check-local-deps
```

Node应为22.13或更新的22.x；Aider自检应报告锁定依赖和禁网状态。此处Python3.12环境位于tools/aider，平台仍为3.14。不要为解决一个工具的版本冲突改写平台锁文件。依赖与浏览器安装属于准备期，实际编辑/检索不应临时下载模型元数据或编码资源。

配置 `.env` 的 `RETRIEVAL_ENGINE=continue` 后重启平台，才会使用该引擎；`CODING_ENGINE=aider` 与 `REPO_MAP_PROVIDER=aider` 分别选择编辑与仓库地图。不是安装成功就已启用，也不是写了配置就已证明真实执行。

```bash
# .learning/commands/11-tool-check.sh
uv run pytest tests/test_continue_index.py tests/test_aider_offline.py tests/test_native_tools.py -q
uv run python -m scripts.ci_toolchain
```

可选Node测试可能在未准备工具时skip，必须查看摘要而不是只读退出码。`ci_toolchain` 会实际运行Aider、Continue、MCP和源码检索，并把证据写入 `reports/toolchain.json`；报告明确不声称Daytona服务已通过。此脚本包含已有产品工作流，故仍需浏览器工具。

## 向量是独立选择

`EMBEDDING_ENABLED` 默认为false。需要向量时按 `tools/embeddings` 的锁定项目和 `scripts/ci_local_embeddings.py` 准备本机权重与回环端点，然后检查真实CPU推理及融合证据。不能在本机服务连接失败时偷偷改成云地址。三份固定Vben源码的命中测试也不代表所有模板、所有中文问题都达到某个召回率；扩大范围要扩大数据和验收，而不是扩大口头承诺。


### 亲手验证可选本机向量

向量工具与Aider一样使用自己的Python3.12环境，不能安装进平台3.14里混用。准备期下载固定权重，验证期在回环HTTP服务中做真实ONNX CPU推理。下面Linux/WSL命令按顺序执行；Windows的最后一条 `--python` 改为 `tools/embeddings/.venv/Scripts/python.exe`。

```bash
# .learning/commands/11-local-embeddings.sh
uv sync --locked --project tools/embeddings --python 3.12
uv run --locked --project tools/embeddings --python 3.12 python scripts/ci_local_embeddings.py prepare
uv run python -m scripts.ci_local_embeddings verify --python tools/embeddings/.venv/bin/python
```

prepare会检查固定模型文件身份，verify自行启动并关闭本次回环服务，结合真实Continue/AST/FTS检索，报告在 `reports/local-embeddings.json`。没有成功报告不算本机向量通过。这个验收服务的随机端口只属于本次测试；要长期启用平台向量，另按同一脚本的serve接口或你自己的已准备回环服务提供稳定端点，再将实际URL和模型名写入 `.env`，不要把一次测试端口当长期服务。


若想直接用本脚本提供平台向量端点，在平台根目录的终端A运行下面命令；它持续运行，Ctrl+C只停止本次服务，不删除权重：

```bash
# .learning/commands/11-embedding-serve.sh
uv run --locked --project tools/embeddings --python 3.12 python scripts/ci_local_embeddings.py serve --ready .data/embedding-ready.json
```

终端B读取本次实际回环地址：

```bash
# .learning/commands/11-embedding-address.sh
uv run python -c "import json; from pathlib import Path; print(json.loads(Path('.data/embedding-ready.json').read_text())['url'])"
```

把打印的完整URL填入 `.env` 的 `EMBEDDING_BASE_URL`，设置 `EMBEDDING_MODE=sentence-transformers/all-MiniLM-L6-v2`、`EMBEDDING_API_KEY=local-no-auth`、`EMBEDDING_ENABLED=true`，然后重启平台。服务每次重开可能换端口，因此重启向量服务后重新读本次ready文件并核对；旧ready文件存在不证明进程还活着。这个服务只监听回环，外部请求不在本教程能力内。

## 本阶段源码和后续依赖

本阶段首次创建 41 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
