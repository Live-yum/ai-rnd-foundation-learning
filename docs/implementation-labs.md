# 动手写与跑：从第一行Python到完整调用链

这一部分不是让你先拿一个骨架运行。先按“逐文件实现讲解”的组0—10，在空文件夹把附录中对应文件完整写出；每一课明确说明最少需要哪组代码。这里再写小实验，把你刚写的模块亲手调用起来，观察输入、结果和错误。这样能知道某一段代码为什么存在，而不只是抄完数千行。

每个实验都是一个完整`.py`文件，第一行的`# lesson:`是普通注释，可以保留。将实验文件放在项目根目录的`learning/`文件夹。先新建文件、粘贴该课完整代码、保存，再在项目根目录运行，例如`uv run python learning/lesson_01.py`。不要在Python的`>>>`提示符内粘贴终端命令；若误入交互器，输入`exit()`返回终端。代码块没有行号，不要加行号。

实验使用临时目录，结束时清理自己创建的测试数据，不读你的业务库、不调用真实聊天模型、不打印密钥。实验是教学材料，不是替代正文完整模块的小型产品。每课完成后回到附录同名函数，看实验刚走过的分支。

## 第0课：确认自己能创建并运行一个文件

先只需Python和uv。新建`learning/lesson_00.py`，逐行输入：

```python
# lesson: 00
name = "我的研发工作台"
steps = ["需求", "设计", "生成", "验证", "交付"]
for number, step in enumerate(steps, start=1):
    print(number, step)
assert len(steps) == 5
print(name, "：能运行第一份代码")
```

`name`保存一段文字；`steps`保存有序列表；`for`每次取出一项；缩进的`print`属于循环；最后两行不缩进，所以只执行一次。`assert`是不成立就报错的断言，不是界面提示。应看到1到5及最后一句文字。你可以临时把断言的5改成6，确认会出现AssertionError，再改回5。

如果还没有创建pyproject，运行`uv run --no-project --python 3.14 python learning/lesson_00.py`；组0完成且`uv sync --locked`成功后，其余课统一用`uv run python`。报找不到文件先检查当前目录和文件是否误存为`.py.txt`，不要重装全部软件。

## 第1课：写合同，先拒绝错误输入

**先完成**组0—1：项目配置、local_only、settings、catalog、domain与errors。完整写出`catalog.py`中的PAIRS、Selection及校验器；再写`domain.py`的字段、实体和Plan模型。新建`learning/lesson_01.py`：

```python
# lesson: 01
from pydantic import ValidationError
from workbench.catalog import Selection
from workbench.domain import FieldSpec

selection = Selection(template="python-basic")
assert selection.frontend == "simple-admin"
assert selection.database == "sqlite"
title = FieldSpec(
    name="title",
    kind="text",
    required=True,
    min_length=1,
    max_length=80,
    searchable=True,
)
assert title.model_dump()["max_length"] == 80
try:
    Selection(template="yudao-vben", database="sqlite")
except ValidationError:
    print("未适配的模板/数据库组合被拒绝")
else:
    raise AssertionError("错误组合不应通过")
try:
    FieldSpec(name="title", kind="text", min_length=100, max_length=80)
except ValidationError:
    print("最小长度超过最大长度被拒绝")
else:
    raise AssertionError("矛盾长度不应通过")
print("合同实验通过")
```

这里有两层含义：Selection从程序目录给出默认组合；FieldSpec约束业务字段。`try`内故意写错，只有捕获指定ValidationError才算实验通过；`else`在没有抛异常时执行，因此能发现“校验根本没运行”。不要用`except Exception: pass`吞掉任何错误。

**回读代码**：先找到Selection的`model_validator`，再找到FieldSpec的`field_options`。指出数据库选项来自哪个字典，长度大小关系在哪里检查。此时尚未调用模型，证明能力范围不是模型随口决定。

## 第2课：把需求变成计划，也要保住原条件

**先完成**domain、requirement_coverage及其直接依赖。该模块是实际需求流程的一部分，不是这个实验的临时假实现。新建`learning/lesson_02.py`：

```python
# lesson: 02
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps, reconcile

requirement = Requirement(
    summary="个人资讯",
    users=["我"],
    data_scope="per_user",
    features=["管理资讯"],
    acceptance=["标题规则正确"],
    facts={"标题说明": "保留原始标题"},
    field_requirements=[
        {
            "entity": "article",
            "field": "title",
            "kind": "text",
            "required": True,
            "max_length": 80,
            "searchable": True,
        }
    ],
)
plan = Plan(
    title="资讯",
    data_scope="per_user",
    acceptance=["标题规则正确"],
    entities=[
        {
            "name": "article",
            "description": "文章",
            "fields": [
                {
                    "name": "title",
                    "kind": "text",
                    "max_length": 80,
                    "required": True,
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
kept = reconcile(requirement.model_dump(), omitted, corrections=[])
assert kept.facts == requirement.facts
assert kept.field_requirements == requirement.field_requirements
print("正确计划通过；漏搜索的计划拒绝；下一轮省略不删除事实")
```

`deep=True`让错误样本拥有独立的嵌套字段对象，不把原正确计划也改坏；`coverage_gaps`返回空列表表示无已登记缺口。这里直接构造响应是教学输入，不是假装模型实际运行。真实流程在analyse保留事实、plan提出实现、design执行同一检查。

**回读代码**：在reconcile里找旧facts覆盖省略值的位置；在coverage_gaps里找字段匹配和searchable比较。必须能解释为什么“模型没再提到”不是“用户同意删除”。本实验不证明程序能自动理解任意自由文字约束。

## 第3课：数据库为什么要有事务与幂等键

**先完成**组0—2的全部文件和迁移；`uv sync --locked`成功后运行。新建`learning/lesson_03.py`：

```python
# lesson: 03
from pathlib import Path
from tempfile import TemporaryDirectory
from workbench.settings import Settings
from workbench.store import Conflict, Store

with TemporaryDirectory(prefix="rnd-lesson-") as temporary:
    settings = Settings(
        data_dir=Path(temporary),
        database_url="",
        checkpoint_url="",
        _env_file=None,
    )
    store = Store(settings)
    try:
        store.migrate()
        first = store.create_project("资讯练习", "same-request")
        repeated = store.create_project("资讯练习", "same-request")
        assert first["id"] == repeated["id"]
        try:
            store.create_project("不同内容", "same-request")
        except Conflict:
            print("同键异内容被拒绝")
        else:
            raise AssertionError("相同键不允许代表另一个请求")
    finally:
        store.engine.dispose()
print("相同请求只创建一个项目；临时数据库已关闭")
```

TemporaryDirectory把实验数据与正式`.data`分开；显式空数据库配置选择临时SQLite；`_env_file=None`不读取个人.env。create_project内部的operation在事务里创建Project并flush取得ID，request保存请求指纹和响应。同请求返回原结果；同键不同输入拒绝，防止网络重试重复创建任务。

`finally`先关闭连接池，离开with才删除临时目录；Windows尤其不能依赖进程退出碰巧释放文件句柄。**回读代码**：把`create_project → request → _request → tx`四个函数按调用顺序找出，指出“写项目”和“写请求回执”为何应在同一事务内。

## 第4课：亲手建立索引，再制造一次过期

**先完成**组4—5：filesystem、tools、symbols、knowledge、retrieval等全部文件；默认本机AST/FTS不需要Continue或embedding。新建`learning/lesson_04.py`：

```python
# lesson: 04
from pathlib import Path
from tempfile import TemporaryDirectory
from workbench.knowledge import build_index
from workbench.retrieval import query

with TemporaryDirectory(prefix="rnd-index-lesson-") as temporary:
    base = Path(temporary)
    source, index = base / "source", base / "index"
    source.mkdir()
    file = source / "demo.py"
    file.write_text("def model_for(stage):\n    return stage\n", encoding="utf-8")
    first = build_index(source, index)
    second = build_index(source, index)
    assert first["files"] == 1
    assert second["reused"] == 1
    found = query(source, index, "model_for")
    assert any(item["path"] == "demo.py" for item in found["matches"])
    file.write_text("def model_for(stage):\n    return 'new'\n", encoding="utf-8")
    try:
        query(source, index, "model_for")
    except ValueError as error:
        assert "源码已改变" in str(error)
    else:
        raise AssertionError("旧索引不应继续回答新源码")
print("真实符号检索、缓存复用和过期拒绝通过")
```

source和index是并列目录。如果把index放进source，下一次扫描会把自己的输出也算作源码变化。build_index第一次计算SHA和符号，第二次复用；query不是盲信旧库，会先核对当前源码。该例中的`demo.py`只被当文字解析，没有执行它的函数。

**回读代码**：knowledge如何保存`line`与`end_line`；retrieval.current_index如何发现SHA改变；parse_file如何把Vue脚本行号转换回SFC。再按第20章换成真实原生源码，并显式准备Continue或本机向量，不把这个一文件练习当全仓库语义验证。

## 第5课：业务表达式为何不能变成任意Python

**先完成**`workbench/rules.py`。新建`learning/lesson_05.py`：

```python
# lesson: 05
from workbench.rules import Rules, UnsafeRule

source = """def validate(entity, data):
    if entity == "device" and data["quantity"] < 0:
        raise ValueError("数量不能为负")
    return None
"""
rules = Rules(source)
rules.validate("device", {"quantity": 0})
try:
    rules.validate("device", {"quantity": -1})
except ValueError as error:
    assert str(error) == "数量不能为负"
else:
    raise AssertionError("负例应被业务规则拒绝")
try:
    Rules("import os\n")
except UnsafeRule:
    print("导入系统模块的规则被拒绝")
else:
    raise AssertionError("规则不能成为任意程序")
print("正例、反例、安全拒绝三条路径通过")
```

这里把源码作为字符串交给Rules，Rules只解析并解释允许的AST节点，没有`exec(source)`。正例证明合法值能用；反例证明规则真正生效；非法程序证明权限边界没有被突破。三者缺一不可。

**回读代码**：在`_statements`找if/raise/return白名单，在`_expression`找可用操作符，在`validate`看如何建立entity/data环境。后续Aider只是实际应用受控编辑；它退出成功后还要重复这些业务与安全验证。

## 第6课：确定性生成器究竟写了什么

**先完成**组0—6所有自有文件及完整产品模板。这一步不需要模型Key、不启动产品服务、不安装原生Java环境。生成器只在新目标目录创建产品；已有目录只有同一计划与技术选择的有效回执才可幂等复用，回执缺失、损坏或不匹配会保留原文件并停止。本课只传新临时目录，不拿已有工作目录做实验。新建`learning/lesson_06.py`：

```python
# lesson: 06
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from workbench.domain import Plan, digest
from workbench.generator import generate_basic

plan = Plan(
    title="便签",
    data_scope="per_user",
    acceptance=["保存自己的便签"],
    entities=[
        {
            "name": "note",
            "description": "便签",
            "fields": [
                {"name": "title", "kind": "text", "required": True, "max_length": 80},
            ],
        }
    ],
)
with TemporaryDirectory(prefix="rnd-generation-lesson-") as temporary:
    product = Path(temporary) / "product"
    receipt = generate_basic(plan, product)
    assert receipt["spec_digest"] == digest(plan.model_dump())
    saved = json.loads((product / "approved-spec.json").read_text(encoding="utf-8"))
    assert saved == plan.model_dump()
    for relative in [
        "app.py",
        "start.py",
        "verify.py",
        "verify-browser.cjs",
        "uv.lock",
        "web/index.html",
        "migrations/versions/0001_initial.py",
    ]:
        assert (product / relative).is_file(), relative
    print("同一Plan生成规格、产品、前端和冻结迁移")
```

`generate_basic`先复制受信任模板，再写Plan和Selection，再生成迁移/SQL与内容清单。`receipt`是回执，含规格指纹与文件指纹；它不是运行通过证明。本课只证明文件生成关系，不能输出“产品已验收”。

**回读代码**：追踪`approved-spec.json → schema.py/fields.py → app.py → web/app.js → verify.py`。它们共享同一规格，不需要模型分别发明五套字段。真正运行要完成浏览器工具安装，再走正文的生成、独立HTTP/Chromium、干净解压复验和交付流程。

## 第7课：把上面的模块串到平台，逐项读真实证据

本课不再给一个省略真实组件的小程序。先按组7—10写齐Runtime、Workflow、API、CLI、原生模块、脚本与工作流，再按“从空目录到可信交付”准备工具。所有源文件仍在附录，没有额外下载的本项目骨架。

| 顺序 | 亲手找出并写完整的代码 | 输入到输出 | 必须亲眼核对 |
|---|---|---|---|
| 1 | Store.create_run、Runtime.tick、Workflow.compile | 页面输入 → 同事务Message/Run/Job → 持久化图 | 重试不会重复消费同一回答 |
| 2 | analyse、requirements、source_context、plan、design | 原始需求 → 保留事实 → 真实源码上下文 → 已批准Plan | 智能推荐不能丢字段、弱化数据归属或批准旧门 |
| 3 | generate、code、verify、repair | 批准计划 → 真实文件 → 有界规则编辑 → 工具报告 | 错误候选回滚；服务缺失不是改规则能解决的 |
| 4 | verification.run_probe、产品verify.py、verify-browser.cjs | 独立服务 → HTTP与逐规格Chromium → 完整checks | 当前每个实体/字段应有的检查都在，不是只看首页 |
| 5 | native_modules、scaffolding、native_coding、native_style | 原生生成 → Plop → Aider → 原生UI身份与真实表单 | 原框架布局/主题未被通用页面替换；正反例真实请求 |
| 6 | native_recovery、owned_lifecycle | 身份匹配检查点 → 同目录/库恢复 → 新进程复验 | 不可重放中断保留现场；旧进程不能冒充重启 |
| 7 | daytona_profiles、daytona_worker、sandbox | 显式本机profile → 禁外网运行 → 下载报告/删除沙箱 | 版本、依赖、数据库、当前源码身份与清理均通过 |
| 8 | model_review、package、delivery | 可选语义缺口审阅 → 干净解压复验 → 审批与哈希 | 模型审阅不能代替测试，缺口未解决不能READY |

完整应用启动前先运行不依赖外部服务的合同测试，再按工具章节逐个安装并运行真实集成。测试夹具只说明输入来自哪里，不免除真实工具执行。Actions也按这些脚本运行；查看与当前提交一致的报告，不把上一轮成功截图当这一轮证据。

## 怎样判断自己真的学会，而非仅复制完成

每完成一课，回答四个问题：输入是谁产生的？程序在哪里拒绝错误？它写了哪个文件/数据库？下一个函数从哪里读取结果？答不出时回到对应完整函数，拿本课数据跟一遍变量变化。

附录每个自有文件都有独立职责说明、调用关系及完整实现；Python函数还列参数、行号、分支和返回路径。第三方源码、锁文件和许可证是明确依赖，不要求初学者重写上游框架。先运行这些小实验再做全系统验证，能定位你刚写错的那一层，而不必在第一天同时排查模型、数据库、前端和容器。
