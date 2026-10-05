# 从零实现 AI 研发平台 · 分阶段实操教材

只保存本目录，就能在另一个空目录重建本项目的自有代码、前端、测试、迁移、配置、锁文件及教材维护工具。不需要本项目仓库、代码骨架或旧版大手册。第三方原生框架按第09阶段的固定提交从公开上游下载并处理；语言解释器、包管理器、依赖和浏览器按第00阶段安装。

## 如何学，而不只是如何复制

从00按顺序走到14。每站先看“为什么”，按落盘清单创建文件，运行该站指定的小实验，核对观察结果，再继续。每个模块页说明职责、上下游和当前段函数的控制逻辑；完整代码按文件职责归类，普通模块一页完整展示；只有超过千行的实现按函数、类或章节的自然边界拆段。锁文件、截图和Vue构建资产编码单独放在资源层，日常学习无需打开这些大块数据。后续阶段会深化前站因导入依赖而必须先创建的模块，不把它们偷偷留空。

模型只处理需求/规划/必要规则/可选审阅。数据库、模板、代码检查、浏览器和打包由真实工具执行。教材把“可复现确定性平台”“真实模型调用”“三套原生产品”“本机Daytona”分别列出验收证据，不能以一个PASS代替其余路径。

## 目录

- [00 · 项目与安装边界](00-environment/README.md)
- [01 · 配置与数据合同](01-contracts/README.md)
- [02 · 持久化与迁移](02-storage/README.md)
- [03 · 需求保真与模型协议](03-requirements/README.md)
- [04 · 文件安全与源码检索](04-local-foundation/README.md)
- [05 · 产品模板与认证](05-product/README.md)
- [06 · 确定性生成与独立验证](06-generation/README.md)
- [07 · 审批状态机与恢复](07-orchestration/README.md)
- [08 · API、CLI与Vue流式操作台](08-control-plane/README.md)
- [09 · 原生快照与框架接入](09-native/README.md)
- [10 · 角色权限与客服业务](10-business/README.md)
- [11 · Continue、Plop与Aider](11-local-tools/README.md)
- [12 · 本机沙箱与镜像](12-daytona/README.md)
- [13 · 独立交付与重启](13-delivery/README.md)
- [14 · 全平台验收与证据阅读](14-acceptance/README.md)

本版完整收录 **587 个源文件**；[源文件总索引](source-index.md)供查找，`manifest.json`记录每个文件的完整SHA-256、字节数、阶段和全部分段。它不是另一个代码下载地址。

## 每个代码块第一行是什么

第一行始终是对应文件的项目相对路径注释，例如 Python 的 `# workbench/business_contracts.py`、JS/JSON 的 `// tools/node/package.json`、HTML/Vue/Markdown 的HTML注释、SQL 的 `--`、CSS 的 `/* */`、INI 的 `;`。JSON、`.python-version`、Base64等本身不支持该注释；它是统一的教材定位行，不属于原文件。

手抄时只删除每块的第一行定位注释，然后按序拼接同一文件全部分段。原文件已有注释、shebang、空行和缩进都保留。不把Markdown围栏复制进去，不把JSON另存为JSONC，不给锁文件加说明文字。源码页的行号不计定位行。自动还原器删除的也是恰好这一行，先检查分段和整文件哈希，正确恢复空文件、无结尾换行、二进制图片及构建资产后才写盘。

命令示例的路径以`.learning/commands/`开头，表示可选练习脚本；在文字指定的工作目录执行它的内容，不属于平台源文件。`.learning/checks/`是需要手动新建的练习文件；`.learning/output/`是预期输出示意，不保存成程序。源文件页中的大围栏若包含Markdown示例，内部反引号只是原文件的文字，先去外层路径定位行即可。

## 三种实际使用方法

### A. 逐文件手写

00准备工具与空目录，之后按每阶段导读和files.md写文件。不要提前运行`rnd init`、`rnd start`或全套pytest。已有模块不完整时的ImportError是阶段顺序问题。每章仅执行本章已满足前提的检查。

### B. 分阶段落盘，逐段学习

先按00安装uv；下面让uv选取Python3.14运行标准库还原器，不要求系统预装python或Windows的py启动器。以下示例在“同时能看见learning-docs和未来student-project”的父目录执行，PowerShell和Bash都可使用同样命令及正斜线路径。还原器本身兼容Python3.10以上，但平台必须3.14。

```bash
# .learning/commands/staged-restore.sh
uv run --no-project --python 3.14 python learning-docs/rebuild.py --check
uv run --no-project --python 3.14 python learning-docs/rebuild.py student-project --through 00
uv run --no-project --python 3.14 python learning-docs/rebuild.py student-project --through 01 --advance
```

每学完一站再把`--through`改为下一站编号。`--advance`会核对已还原文件的哈希；你练习修改过源码时先把练习保存在单独目录，或创建另一个空目录继续，它不会覆盖修改。生成的`.learning-progress.json`只记录教材文件哈希，不执行任何代码，也不启动外部服务。

第09站重建第三方模板时，不同zlib版本可能只改变ZIP压缩字节，从而更新 `templates/vendor/manifest.json` 的 `archive_sha256`。`--advance` 会把它识别为已还原文件变化并停止，这是应当保留的保护。先核对固定commit、source_digest和文件数仍一致；不要删账本、改校验值或用旧manifest覆盖本机新归档。

若遇到这种情况，保留原项目和数据，在一个新的空目录采用下面C路线完整还原，再按第09站重建模板、按第06/11站准备新目录的浏览器和Node工具，继续后续学习。新完整目录不再需要 `--advance`。明确命令与恢复边界见[第09站的重打包说明](09-native/README.md)；手写后续源码也是有效路线。不删除或覆盖原项目。

### C. 一次还原，用于完整性验收

```bash
# .learning/commands/full-restore.sh
uv run --no-project --python 3.14 python learning-docs/rebuild.py student-project-complete
cd student-project-complete
uv python install 3.14
uv sync --locked --all-extras
```

这一步只证明代码落盘与依赖安装。接着按09重建三个上游模板ZIP，按11安装Node工具，按06安装浏览器，再按14执行完整检查。不要把这四行当作全平台已经运行成功。路径、哈希或段数出错时还原器在写任何源码前中止，目的目录必须为空；不要用管理员权限强行覆盖已有工程。

## 学到最后的交付标准

1. 空目录重建后的自有文件与本目录清单逐字节一致，且不是从原仓库复制代码
2. 三个原生模板来自登记的固定提交，来源摘要、文件数与许可证一致；压缩器版本不同可能改变ZIP压缩字节
3. 运行完整非PostgreSQL测试、真实浏览器以及独立产品安装；另单独运行PostgreSQL、原生三矩阵和可选本机工具验收
4. 真实模型需你自己的服务配置和费用授权；确定性夹具不会被描述为真实模型成功
5. 成品解压到另一个空目录、用新数据库启动，不再导入工作台源目录或读取模型密钥

## 手册维护与旧版兼容

本目录由`scripts/build_learning_docs.py`从当前自有源码及`scripts/learning_docs_content.json`生成。所有生成器、正文源、测试也包含在本目录中，因此还原后能自行维护。旧的大文件仍保留用于兼容，其维护命令不替代本目录的独立验收。

```bash
# .learning/commands/regenerate-docs.sh
uv run python -m scripts.build_handbook
uv run python -m scripts.build_learning_docs
uv run python -m scripts.build_learning_docs --check
```

从完整教材重建时先生成旧兼容手册，再生成本目录，最后执行14的测试。重新从上游打包会更新模板清单中的压缩摘要，之后须同步生成两套教材；不允许为了通过检查改来源提交或删除断言。
