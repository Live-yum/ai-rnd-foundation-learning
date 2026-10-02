# 00 · 项目与安装边界

[总目录](../README.md) · [下一阶段](../01-contracts/README.md)

## 真正从没有工具的电脑开始

本教程不要求克隆本项目源码。你需要的是这份完整 `learning-docs` 教材目录、一处准备写代码的空目录，以及终端和纯文本编辑器。编辑器任选你熟悉的工具，能创建目录、显示文件扩展名并按UTF-8保存即可；别把Word文档改名成 `.py`。基础平台可在Windows/Linux学习；原生框架和Daytona章节请使用其明确支持的Linux/WSL环境。

先从 [Git官方安装入口](https://git-scm.com/install/) 选择操作系统并按官方步骤安装。Git在后面的固定上游源码获取和Aider隔离副本中需要；不必先用它克隆本项目。安装后重新打开终端，运行 `git --version` 应显示版本。若提示命令不存在，先检查安装器提示与PATH，不盲目重装Python。

uv有不依赖预装Python的独立安装器。下面是 [uv官方安装文档](https://docs.astral.sh/uv/getting-started/installation/) 提供的两种入口，按自己的系统只选一条；它会下载并执行官方安装脚本，你也可以先从官方文档检查脚本内容。

```bash
# .learning/commands/00-install-uv-linux.sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# .learning/commands/00-install-uv-windows.ps1
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装后关闭并重新打开终端，运行 `uv --version` 应显示版本。PowerShell的这条命令为本次官方安装脚本使用相应执行策略，不需要为了教程永久关闭系统安全设置。若组织策略不允许安装，请使用组织批准的官方安装方式，不绕过限制。

## 先取得解释器，再选择手写或逐站还原

你还没有 `pyproject.toml` 时，也可以让uv安装Python3.14；这解决“教材还原器本身需要Python”的前置问题。在教材目录的上一级执行：

```bash
# .learning/commands/00-bootstrap-python.sh
uv python install 3.14
uv run --no-project --python 3.14 python -c "import sys; assert sys.version_info[:2] == (3, 14); print(sys.version.split()[0])"
```

应打印3.14.x。`--no-project` 表示这一条命令不寻找尚未创建的项目配置。接下来有两条都真实可行的学习路径：手写时新建 `student-project`，按本阶段源码索引创建每个文件；辅助还原时先不要创建目标目录，由教材自己的标准库脚本只还原第00站。两种方式都逐站读解释与运行检查，不需要先得到完整平台骨架。

```bash
# .learning/commands/00-restore-first-stage.sh
uv run --no-project --python 3.14 python learning-docs/rebuild.py student-project --through 00
cd student-project
```

此时应只有第00站登记的源文件与学习进度记录，没有API、CLI和Worker。下一站可以手写补齐，也可以从 `student-project` 目录运行下面的增量命令；它在已恢复源码匹配时新增到指定阶段，不覆盖你改过的代码：

```bash
# .learning/commands/00-next-stage-example.sh
uv run --no-project --python 3.14 python ../learning-docs/rebuild.py . --through 01 --advance
```

这条是“开始第01站时再执行”的示例。若你有意修改了旧源码，先理解并保存自己的变更；还原器拒绝覆盖是保护，不应通过删除检查绕开。正式安装项目依赖要在第00站文件已写齐后执行下节命令。

## 先认清你正在搭建什么

最终平台有两种程序。第一种是研发工作台，负责保存需求、审批、调用模型和运行工具；第二种是它生成的业务产品，具有自己的依赖、用户和数据库。现在只搭建第一种程序的安装外壳。`pyproject.toml` 声明 Python 范围、依赖和 `rnd` 入口，`uv.lock` 固定实际解析结果，`.python-version` 帮终端选择解释器，`workbench/__init__.py` 让工作台成为可安装包。入口声明可以先存在，入口指向的 `cli.py` 要等后面实现；安装成功不会替你补出 CLI。

按本阶段源码索引逐文件写入，不要先复制整个最终仓库。根目录是含 `pyproject.toml` 的目录；教材目录和将来的产品解压目录都不是它。保存文件使用 UTF-8，不要让编辑器暗中加 `.txt`。锁文件较长是因为依赖身份必须完整记录，它是数据，不需要当作算法逐行背诵。不要删去看起来不重要的 hash，也不要把自己重新生成的锁冒充书中同一组依赖。

下面所有 `.learning/commands/...` 标记表示终端命令示例的归属，不要求保存成脚本；后面明确写“保存为”的练习才要创建文件。

```bash
# .learning/commands/00-install.sh
uv python install 3.14
uv sync --locked
uv run python -c "import sys; assert sys.version_info[:2] == (3, 14); import fastapi, pydantic, sqlalchemy; print('00 PASS: Python 3.14 and base dependencies')"
```

最后一条应打印 `00 PASS: Python 3.14 and base dependencies`。Python3.12/3.13不是可互换环境：最终代码包含 Python3.14 的语法与运行接口，靠“我电脑有 Python”不足以判断可用。Aider 后面独立使用3.12，那是工具隔离要求，不是把平台降级到3.12。

## 学会区分安装与运行

`uv sync --locked` 会下载并安装可信来源的依赖；这不是把生成业务交给远程工具执行。平台设计要求业务工具在本机，允许聊天模型访问你明确配置的 HTTPS 推理服务。第三方源码快照、Python锁文件和Node锁文件解决的是不同层的复现问题，不能只保存其中一个。

本阶段还没有 Store、API、CLI、模型网关。不要运行 `rnd init`、`rnd doctor` 或 `rnd start` 来检验半成品；这些命令导入后续模块，`init` 还会准备原生模板；模型未配置时可在第08站启动设置页，但此时模块尚未齐全。此时运行它们报缺模块是顺序错误，不是让你提前粘贴全部源码的理由。

完成后能说清三句话：平台源码可版本管理；`.data` 是后续本机状态且不能作为源码分享；最终ZIP要去新目录和新数据库验收。此站不要放真实模型密钥，也不要建立实际业务数据。

## 后面还会建立一套平台自己的Vue操作台

第08站的 `ui/` 是平台控制面的Vue 3 / Ant Design源码，和第05站写入生成产品的 `templates/frontends/` 不是同一套界面。它使用Node 22与相邻 `package-lock.json`，不要在Python环境或 `tools/node` 目录里安装这套前端。初学到本阶段不必先构建所有界面；到第08站按顺序执行 `npm ci --prefix ui`、测试和构建。教材同时保留可重建源码与精确静态资产快照，快照不是需要手写的压缩代码。

## 本阶段源码和后续依赖

本阶段首次创建 8 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
