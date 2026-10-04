# scripts/build_learning_docs.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.build_learning_docs；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_handbook`、`scripts.handbook_notes`、`scripts.rebuild_learning_docs`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `stage_for`（L138–L192）：接收`name`。 控制顺序：L140按`name.startswith(("workbench/web/", "ui/"))`分支；L142按`name.startswith("scripts/extension_oracles/")`分支；L144按`name.startswith("workbench/")`分支；L146按`name.startswith("migrations/") or name == "alembic.ini"`分支；L148按`name.startswith("templates/product/") or name.startswith("templates/frontends/")`分支；L150按`name.startswith("templates/business/common/")`分支；L152按`name.startswith(("templates/vendor/", "templates/business/", "templates/deployment/")…`分支；L154按`name.startswith("examples/")`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`name.startswith`、`test_stage`。 返回路径：L141的`8`；L143的`4`；L145的`MODULE_STAGE[path.stem]`。
- `test_stage`（L195–L246）：接收`name`。 控制顺序：L196按`name == "tests/conftest.py"`分支；L198按`name == "tests/news_case.py"`分支；L200按`name.startswith("tests/fixtures/")`分支；L216按`stem in early`分支；L218按`stem == "store"`分支；L220按`stem in {"contracts", "business_contracts"}`分支；L222按`stem in {"llm", "guided_models", "provider_structured_outputs"}`分支；L224按`stem.startswith("daytona") or stem == "local_only"`分支。后续分支沿下方源码相同行号继续阅读。 调用`name.startswith`、`Path(name).stem.removeprefix`、`Path`、`stem.startswith`。 返回路径：L197的`2`；L199的`7`；L201的`10`。
- `language_for`（L249–L274）：接收`name`、`binary`。 控制顺序：L250按`binary`分支；L252按`name.endswith("uv.lock")`分支；L254按`Path(name).name.startswith("Dockerfile") or name.endswith(".Dockerfile")`分支。 调用`name.endswith`、`Path(name).name.startswith`、`Path`、`{ ".py": "python", ".md": "markdown", ".toml": "toml", ".yml": "y…`。 返回路径：L251的`"base64"`；L253的`"toml"`；L255的`"dockerfile"`。
- `chunks`（L277–L316）：接收`data`、`binary`、`name`。 源码说明：Keep ordinary modules together; split only long implementations at real boundaries.。 控制顺序：L279按`binary or name.endswith(("uv.lock", "package-lock.json"))`分支；L283按`len(lines) <= 1000`分支；L286按`name.endswith(".py")`分支；L294按`name.endswith(".md")`分支；L304在`len(lines) - first > 1000`成立时循环；L306按`not options`分支；L314按`first < len(lines)`分支。 调用`name.endswith`、`data.decode`、`content.splitlines`、`len`、`ast.parse`、`min`、`ast.walk`、`isinstance`、`enumerate`等。 返回路径：L280的`[data]`；L284的`[data]`；L316的`result or [b""]`。
- `source_note`（L349–L380）：接收`name`、`content`、`first`、`last`。 控制顺序：L350按`isinstance(content, bytes)`分支；L351按`generated_frontend_asset(name)`分支；L365按`name in TEACHING_CASES`分支；L367按`not separator`分支；L370遍历`entries.splitlines()`；L372按`match and first <= int(match[1]) <= last`分支；L374按`selected`分支。 调用`isinstance`、`generated_frontend_asset`、`notes`、`detail.replace`、`detail.partition`、`entries.splitlines`、`re.search`、`int`、`selected.append`等。 返回路径：L352的`"这是Vue操作台的构建快照，不是需要手写或阅读的压缩实现。" "请读第08站的ui/src、package-lock.json和vite.config.ts，执行npm ci/b…`；L358的`"该资源是真实操作截图的原始字节。Base64按顺序解码后拼接，不把它当代码执行；文件总SHA-256校验后才能用作图片。\n\n"`；L368的`head`。
- `source_pages`（L383–L454）：接收`name`、`content`、`stage`。 控制顺序：L389按`binary`分支；L391按`name.endswith(("uv.lock", "package-lock.json"))`分支；L396遍历`enumerate(pieces)`；L417按`index`分支；L419按`index + 1 < len(pieces)`分支；L428按`not piece`分支；L430按`not binary`分支；L438按`generated_frontend_asset(name)`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`content.encode`、`chunks`、`name.replace("/", "__").replace`、`name.replace`、`name.endswith`、`range`、`len`、`language_for`等。 返回路径：L448的`result, { "path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "s…`。
- `read_content`（L457–L458）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`json.loads`、`CONTENT.read_text`。 返回路径：L458的`json.loads(CONTENT.read_text(encoding="utf-8"))`。
- `render`（L461–L508）：不接收显式业务参数，从已配置对象/模块读取依赖。生成物完全由正文源文件和实际源码计算；检查模式比较整份结果，不允许手动修改生成手册来掩盖源码不同步。 控制顺序：L463按`[stage["id"] for stage in curriculum] != STAGES`分支；L464抛异常，停止当前正常路径；L466遍历`sources()`；L467遍历`files`；L469按`set(output).intersection(pages)`分支；L470抛异常，停止当前正常路径；L479遍历`curriculum`；L484按`pos`分支。后续分支沿下方源码相同行号继续阅读。 调用`read_content`、`ValueError`、`sources`、`source_pages`、`stage_for`、`set(output).intersection`、`set`、`output.update`、`records.append`等。 返回路径：L508的`output`。
- `readme`（L511–L594）：接收`curriculum`、`records`。 控制顺序：L525遍历`curriculum`。 调用`len`。 返回路径：L594的`text`。
- `main`（L597–L625）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L607按`args.check`分支；L614按`wrong`分支；L615抛异常，停止当前正常路径；L619遍历`actual.difference(expected)`；L621遍历`expected.items()`。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`render`、`OUTPUT.exists`、`path.relative_to(OUTPUT).as_posix`、`path.relative_to`、`OUTPUT.rglob`、`path.is_file`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/build_learning_docs.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L629。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`36050`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/build_learning_docs.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b3bda9e54cba60144fc6db8c596d8b9c58c091d26984b62dbc98a5a0009280a1"} -->
````python
# scripts/build_learning_docs.py
"""Build small, staged lessons and lossless source pages from the actual platform."""

import argparse
import ast
import base64
import hashlib
import json
import re
import textwrap
from pathlib import Path

from scripts.build_handbook import ROOT, generated_frontend_asset, sources
from scripts.handbook_notes import notes, purpose
from scripts.rebuild_learning_docs import check_fences, comment_line

OUTPUT = ROOT / "learning-docs"
CONTENT = ROOT / "scripts/learning_docs_content.json"
STAGES = [
    "00-environment",
    "01-contracts",
    "02-storage",
    "03-requirements",
    "04-local-foundation",
    "05-product",
    "06-generation",
    "07-orchestration",
    "08-control-plane",
    "09-native",
    "10-business",
    "11-local-tools",
    "12-daytona",
    "13-delivery",
    "14-acceptance",
]
# Installation order follows imports. Later lessons deepen modules that must exist
# earlier; optional services are never implicitly started by source restoration.
MODULE_STAGE = {
    "__init__": 0,
    "local_only": 0,
    "settings": 1,
    "model_settings": 1,
    "domain": 1,
    "business_contracts": 1,
    "catalog": 1,
    "errors": 1,
    "store": 2,
    "clarification": 2,
    "conversation": 3,
    "llm": 3,
    "model_protocol": 3,
    "model_connection": 3,
    "model_diagnostics": 3,
    "streaming": 3,
    "entity_requirements": 3,
    "requirement_coverage": 3,
    "requirement_sources": 3,
    "requirement_canonical": 3,
    "requirement_intent": 3,
    "business_capabilities": 3,
    "filesystem": 4,
    "tools": 4,
    "capability_contracts": 4,
    "capability_policy": 4,
    "capability_execution": 4,
    "capability_editing": 7,
    "capability_services": 4,
    "capability_browser_isolation": 4,
    "capability_browser_policy": 4,
    "capability_contest_oracle": 4,
    "capability_native_runtime": 4,
    "orchestration": 7,
    "native_plan_normalization": 9,
    "capability_verification": 4,
    "capability_isolation": 4,
    "capability_stack": 4,
    "module_imports": 4,
    "template_adapters": 1,
    "feature_planning": 4,
    "capability_sandbox": 7,
    "owned_lifecycle": 4,
    "symbols": 4,
    "knowledge": 4,
    "retrieval": 4,
    "rules": 4,
    "context_mcp": 4,
    "business_python": 5,
    "generator": 6,
    "verification": 6,
    "product_sql": 6,
    "postgres_lab": 6,
    "coding": 7,
    "flow": 7,
    "runtime": 7,
    "recommendation": 7,
    "toolchain": 7,
    "aider_tool": 7,
    "continue_index": 7,
    "sandbox": 7,
    "daytona_profiles": 7,
    "api": 8,
    "cli": 8,
    "vendor": 9,
    "native": 8,
    "native_acceptance": 9,
    "native_checks": 9,
    "native_coding": 9,
    "native_compatibility": 9,
    "native_delivery": 9,
    "native_environment": 9,
    "native_evidence": 9,
    "native_frontend": 9,
    "native_lab": 9,
    "native_modules": 9,
    "native_ports": 9,
    "native_recovery": 9,
    "native_resources": 9,
    "native_style": 9,
    "native_vben": 9,
    "native_business_checks": 9,
    "native_business_probe": 9,
    "scaffolding": 9,
    "yudao_navigation": 9,
    "yudao_navigation_checks": 9,
    "portable": 9,
    "portable_checks": 9,
    "business_browser": 9,
    "business_probe": 9,
    "business_schema_receipt": 9,
    "business_native": 9,
    "business_fastapi": 9,
    "business_yudao": 9,
    "daytona_sessions": 12,
    "daytona_diagnostics": 12,
    "daytona_worker": 12,
}


def stage_for(name):
    path = Path(name)
    if name.startswith(("workbench/web/", "ui/")):
        return 8
    if name.startswith("scripts/extension_oracles/"):
        return 4
    if name.startswith("workbench/"):
        return MODULE_STAGE[path.stem]
    if name.startswith("migrations/") or name == "alembic.ini":
        return 2
    if name.startswith("templates/product/") or name.startswith("templates/frontends/"):
        return 5
    if name.startswith("templates/business/common/"):
        return 5
    if name.startswith(("templates/vendor/", "templates/business/", "templates/deployment/")):
        return 9
    if name.startswith("examples/"):
        return 3
    if (
        name.startswith("tools/daytona/")
        or name.startswith("scripts/daytona")
        or name.startswith("scripts/ci_daytona")
    ):
        return 12
    if name.startswith("tools/"):
        return 11
    if name == "scripts/news_fixture.py":
        return 7
    if name in {
        "scripts/vendor_templates.py",
        "scripts/ci_native_generated.py",
        "scripts/ci_native_bundled.py",
        "scripts/native_coding_fixture.py",
    }:
        return 9
    if name in {
        "scripts/ci_toolchain.py",
        "scripts/ci_aider_workflow.py",
        "scripts/ci_native_tools.py",
        "scripts/ci_local_embeddings.py",
    }:
        return 11
    if name == "scripts/ci_clean_install.py":
        return 13
    if name.startswith("scripts/business_") or name == "scripts/native_browser.cjs":
        return 9
    if name == "scripts/guided_browser.cjs":
        return 8
    if name.startswith("tests/"):
        return test_stage(name)
    if name.startswith("docs/") or name.startswith(".github/") or name.startswith("scripts/"):
        return 14
    if name in {"README.md", "SECURITY.md"}:
        return 14
    return 0


def test_stage(name):
    if name == "tests/conftest.py":
        return 2
    if name == "tests/news_case.py":
        return 7
    if name.startswith("tests/fixtures/"):
        return 10
    stem = Path(name).stem.removeprefix("test_")
    early = {
        "field_predicate_semantics": 3,
        "generation_preservation": 6,
        "product_browser_gate": 6,
        "workflow": 7,
        "guided_workflow": 7,
        "recommendation_stage_budget": 7,
        "vendor": 9,
        "native_archive_limits": 9,
        "native_delivery_boundaries": 9,
        "native_tools": 11,
        "delivery_clearance": 13,
    }
    if stem in early:
        return early[stem]
    if stem == "store":
        return 2
    if stem in {"contracts", "business_contracts"}:
        return 2  # pytest's conftest imports Store.
    if stem in {"llm", "guided_models", "provider_structured_outputs"}:
        return 3
    if stem.startswith("daytona") or stem == "local_only":
        return 12
    if stem in {"aider_offline", "continue_index", "local_embeddings", "toolchain"}:
        return 11
    if stem.startswith(("native", "vendor", "yudao")):
        return 13
    if stem.startswith(("business", "customer")):
        return 10
    if stem in {
        "api",
        "tools_cli",
        "guided_selection",
        "cli_connection",
        "streaming_backend",
        "model_settings",
        "clarification_choices",
    }:
        return 8
    if stem.startswith(("handbook", "learning", "real_model")):
        return 14
    # Complex historical regression cases import several later layers. Keep them
    # in the final complete suite rather than advertising an un-runnable early test.
    return 14


def language_for(name, binary=False):
    if binary:
        return "base64"
    if name.endswith("uv.lock"):
        return "toml"
    if Path(name).name.startswith("Dockerfile") or name.endswith(".Dockerfile"):
        return "dockerfile"
    return {
        ".py": "python",
        ".md": "markdown",
        ".toml": "toml",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
        ".cjs": "javascript",
        ".mjs": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".vue": "vue",
        ".js": "javascript",
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".ini": "ini",
        ".sh": "bash",
    }.get(Path(name).suffix, "text")


def chunks(data, binary, name):
    """Keep ordinary modules together; split only long implementations at real boundaries."""
    if binary or name.endswith(("uv.lock", "package-lock.json")):
        return [data]
    content = data.decode("utf-8")
    lines = content.splitlines(keepends=True)
    if len(lines) <= 1000:
        return [data]
    anchors = []
    if name.endswith(".py"):
        tree = ast.parse(content)
        anchors = [
            min([node.lineno, *(d.lineno for d in node.decorator_list)]) - 1
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.col_offset <= 4
        ]
    elif name.endswith(".md"):
        anchors = [n for n, line in enumerate(lines) if re.match(r"#{1,3} ", line)]
    else:
        anchors = [
            n
            for n, line in enumerate(lines)
            if re.match(r"(?:export )?(?:async )?(?:function|class) ", line)
        ]
    anchors = sorted(set([0, *anchors, len(lines)]))
    result, first = [], 0
    while len(lines) - first > 1000:
        options = [line for line in anchors if first + 350 <= line <= first + 900]
        if not options:
            # A large declaration stays intact through its next natural boundary.
            options = [line for line in anchors if line > first + 350]
            last = options[0] if options else len(lines)
        else:
            last = options[-1]
        result.append("".join(lines[first:last]).encode("utf-8"))
        first = last
    if first < len(lines):
        result.append("".join(lines[first:]).encode("utf-8"))
    return result or [b""]


# Short hand-written cases explain decisions; mechanical symbol inventories stay folded.
TEACHING_CASES = {
    "workbench/model_settings.py": "两个窗口都读到版本R。窗口A保存得到R2后，窗口B仍带expected_revision=R时必须收到409，不能覆盖A。只改模型名称可以保留原地址Key；把地址A改成B必须为B输入新的独立Key。public响应只说是否已配置，真正密钥既不回填输入框，也不随错误返回。",
    "workbench/streaming.py": "服务商把summary分成两段发来时，AssistantStream先提取已完整解码的公开前缀，保存assistant_delta；此刻页面显示草稿。最后整个对象通过schema校验，才写assistant_completed。若后半段不合法，assistant_failed清掉草稿，不能因为用户已经看到一些文字就标成成功。刷新用transcript.cursor续读，而不是再次调用模型。",
    "workbench/clarification.py": "当前问题Q的选项O1标签是‘内部团队’，浏览器提交的是Q/O1。render_answer从当前pending取标签，不以客户端伪造标签为准；Q已被下一版替换或单选提交两个选项时，在同一事务里拒绝且不排队。合法回答成为用户原文，仍不等于需求/计划批准。",
    "ui/src/api.ts": "中文字符和一个SSE帧都可能跨网络块。TextDecoder保留半个UTF-8字符，SSEParser保留未遇到空行的帧；直到data完整才解析JSON。令牌放Authorization而非URL，订阅中断只取消reader，不调用任务重试端点。",
    "ui/src/state.ts": "快速打开运行A再打开B时，即使A的请求最后才返回，也不能把A消息写到B。openRun先关闭旧订阅并递增runGeneration；回调核对代次后才更新。重连只接受id大于当前cursor的事件，因此同一已提交delta不会再追加一次。",
    "ui/src/components/SettingsView.vue": "页面显示‘Key已配置’不代表拿到了Key原文；留空表示不修改，明确清除才删除覆盖。保存只验证并落盘，不能显示‘模型连接成功’。如果另一窗口先保存导致409，应读取新版本让用户复核，而不是自动拿新revision重发旧表单。",
    "workbench/requirement_coverage.py": "例如用户已明确请求标题可搜索，候选Plan却把 searchable 设为 false：coverage_gaps 返回可定位的缺项，流程不能因为JSON合法就批准。reconcile 接收上一版Requirement和新候选；新一轮只是没再提到字段时保留原事实，只有带本轮原话证据的明确更正才能修改。读这一层时用第03阶段的正确计划、缺搜索计划和省略事实三份输入对照，不先背辅助正则。",
    "workbench/requirement_sources.py": "先把用户原文、已确认合同和模型候选放在各自来源中比较。若同一字段被明确要求为必填，而候选却明确写成可选，应返回冲突诊断交回分析纠错；函数不替用户选择哪项约束获胜。无法可靠定位的旧文本继续保守校验，不能把猜测写成已批准事实。",
    "workbench/domain.py": "以批准为例：网页传入的是ResumeInput，不是任意字典。action=approve必须携带严格布尔true，字符串true不能当批准；gate_id随后还要与数据库当前关口相符。Plan的字段、关系和业务合同先完成交叉校验，再允许生成器接收，所以模型写出一段JSON并不是绕过边界的办法。",
    "workbench/business_contracts.py": "例如一条requests到customers的关系需要指向实际存在的实体与字段，某个角色的权限也必须引用已登记角色。BusinessSpec先拒绝这些悬空引用，再检查工作流和受保护系统字段；它输出的是受约束声明，不能包含任意SQL来替代业务合同。执行这些声明的事务和权限判断在第10阶段实现。",
    "workbench/settings.py": "默认地址A、默认Key A可以被同服务商的planning阶段继承。若planning只改成地址B而未提供Key B，model_for必须在HTTP之前拒绝；否则会把A的密钥发送给B。public和redact只允许显示模型身份与脱敏诊断，练习时不把秘密打印出来证明它存在。",
    "workbench/store.py": "create_project第一次使用请求键K时创建项目并保存回执；同键同内容返回原结果，同键不同标题抛Conflict。关键是状态变化与回执在同一短事务里完成；若事务中抛异常，新增记录整体回滚。审批还把gate_id绑定到确定版本，而不是只保存一个永远有效的approved标志。",
    "workbench/llm.py": "complete先选阶段模型并检查预算，构造受约束请求，再通过协议层解析、验证响应并保存使用回执。HTTP成功却返回不符合schema的JSON仍应失败；传输错误的有限重试也不能变成无上限重复收费。测试显式注入MockTransport，生产缺少模型配置时不会静默换成样例答案。",
    "workbench/model_protocol.py": "服务商原生结构化输出只是传输能力：协议层必须仍检查返回内容大小、JSON结构和本地schema。一个供应商声称strict并不能代替本地验证；不支持的响应形状应给出可脱敏诊断，而不是扫描任意文本直到拼出看似合格的对象。",
    "workbench/generator.py": "generate_basic把批准Plan和已校验选择写成不可含糊的产物身份，再复制模板、生成迁移并登记每个文件SHA。第一次创建目标目录应得到完整产品；同一路径已经有文件却无相符回执时应停止并保留现场。这里不能用删除重建来伪装幂等，因为目录可能已包含用户修改或数据。",
    "workbench/verification.py": "verify_basic先核对生成回执与当前源码，再让产品自己的环境真实运行；页面、HTTP和重启失败会保留失败，不能靠模型审阅改成passed。package_basic随后还要在新目录解压复验，检测遗漏文件或借用平台环境的问题。测试后改一个受保护文件，原有报告即失效。",
    "workbench/flow.py": "Workflow把需求确认、设计、生成、验证和交付排成有条件的图。gate先保存本版审批内容，再interrupt等待；恢复必须提交当前gate_id。智能推荐可以替用户补普通未知项并留下委托记录，但代码验证失败时仍不得进入READY。请沿第07阶段的三次等待状态走一次，而非假设所有节点每次都会执行。",
    "workbench/cli.py": "先在终端A保持rnd start运行，终端B的chat/show等才是HTTP客户端。client用contextmanager管理连接，按Settings.port取得地址，在进入模板或项目问题前先请求/health；初次或后续ConnectError都转成中文启动/PORT提示并以退出码1结束，连接仍会关闭。健康请求只能证明服务可连，不能代替/ready、批准关卡或产品验收。",
    "workbench/runtime.py": "队列任务只是唤醒同一run_id的理由，LangGraph检查点才说明流程停在哪。Runtime认领任务并恢复原图，遇到interrupt保存等待状态；崩溃后不能把上个任务误当下一关的新批准。一个控制库只允许一个Worker，退出时关闭锁与检查点连接，才能在Windows等平台安全恢复。",
    "workbench/native_modules.py": "批准的实体不是直接拷贝成通用Python CRUD。这里把表和字段翻译成所选框架的真实代码生成输入，再安装实际导出文件与菜单；表名、序列、逻辑删除字段和原生权限均需匹配。源码导出仅证明SOURCE_READY，之后还要编译、启动、HTTP和原生浏览器检查。",
    "workbench/native_lab.py": "把原生流程看成一串证据：固定来源→专用库→真实生成→SQL/菜单→编译/类型检查→HTTP→原生页面。run_acceptance只能在每一步实际完成后汇总报告。某个模板跑通不能替另一个模板写passed，恢复也必须先核对原始Plan、源码与数据库身份。",
    "workbench/business_native.py": "业务扩展SQL属于已验证适配器的输出，安装前先验证专用本机库与模板身份。按既定顺序在事务中执行；中途失败整体回滚，记录的是实际执行SQL的哈希。不能接收模型随口生成的任意SQL，也不能为修复冲突自动清空既有业务库。",
    "workbench/native_evidence.py": "一个passed=true不能证明三角色、逐字段查询和关联权限都被观察。这里检查报告中预期与实际集合、身份、计数、源码哈希等细项，只有覆盖当前批准合同的证据才送审。审阅材料排除原始账号和业务记录，模型看到的也是受限证据而非秘密日志。",
    "workbench/portable.py": "交付包不能在新电脑上偷偷import旧工作台路径。build_native_delivery只复制明确HELPERS清单、固定原生源码、SQL/菜单与独立启动器；新目录必须从自己的依赖和新数据库启动。源码包不携带真实业务数据，结构不匹配时拒绝恢复，不删除数据强行对齐。",
    "workbench/sandbox.py": "本机可信验证先通过，Daytona才增加独立执行证据。所选模板/数据库决定profile，镜像、源码和报告身份必须匹配；请求超时不能当作操作未执行而无限重放。运行结果和本次沙箱清理都成立才允许交付，不能用一个API健康响应替代产品验收。",
}


def source_note(name, content, first, last):
    if isinstance(content, bytes):
        if generated_frontend_asset(name):
            return (
                "这是Vue操作台的构建快照，不是需要手写或阅读的压缩实现。"
                "请读第08站的ui/src、package-lock.json和vite.config.ts，执行npm ci/build生成它。"
                "保留此数据是为了仅带教材也能逐字节恢复运行资产；独立验收会从源码重新构建并比较。"
                "Base64只解码写文件，不作为脚本执行。\n\n"
            )
        return "该资源是真实操作截图的原始字节。Base64按顺序解码后拼接，不把它当代码执行；文件总SHA-256校验后才能用作图片。\n\n"
    detail = notes(name, content)
    detail = detail.replace(
        "**如何编写：** 新建与标题完全相同的相对路径，完整保存下面代码块；不要复制围栏标记。以下行号从代码块第一行起计，行号不属于文件内容。",
        "**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。",
    )
    head, separator, entries = detail.partition("**逐个入口与控制逻辑：**\n\n")
    if name in TEACHING_CASES:
        head += "**带着一个具体问题阅读：** " + TEACHING_CASES[name] + "\n\n"
    if not separator:
        return head
    selected = []
    for line in entries.splitlines():
        match = re.search(r"（L(\d+)–L(\d+)）", line)
        if match and first <= int(match[1]) <= last:
            selected.append(line)
    if selected:
        head += (
            "<details>\n<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>\n\n"
            + "\n".join(selected)
            + "\n\n</details>\n\n"
        )
    return head


def source_pages(name, content, stage):
    binary = isinstance(content, bytes)
    data = content if binary else content.encode("utf-8")
    pieces = chunks(data, binary, name)
    stem = name.replace("/", "__").replace(".", "_")
    directory = f"{STAGES[stage]}/sources"
    if binary:
        directory += "/assets"
    elif name.endswith(("uv.lock", "package-lock.json")):
        directory += "/locks"
    names = [f"{directory}/{stem}--{n:03d}.md" for n in range(1, len(pieces) + 1)]
    result = {}
    language = language_for(name, binary)
    for index, piece in enumerate(pieces):
        payload = (
            "\n".join(textwrap.wrap(base64.b64encode(piece).decode("ascii"), 76))
            if binary
            else piece.decode("utf-8")
        )
        width = max(4, max((len(x) for x in re.findall(r"`+", payload)), default=0) + 1)
        fence = "`" * width
        meta = {
            "path": name,
            "part": index + 1,
            "parts": len(pieces),
            "encoding": "base64" if binary else "utf-8",
            "sha256": hashlib.sha256(piece).hexdigest(),
        }
        first = sum(part.count(b"\n") for part in pieces[:index]) + 1
        last = first + len(piece.decode("utf-8").splitlines()) - 1 if not binary else 0
        body = f"# {name} · {index + 1}/{len(pieces)}\n\n"
        level = "../" * (len(Path(names[index]).parts) - 2)
        body += f"[阶段导读]({level}README.md) · [本阶段文件顺序]({level}files.md) · [全部文件索引]({level}../source-index.md)\n\n"
        neighbors = []
        if index:
            neighbors.append(f"[上一段]({Path(names[index - 1]).name})")
        if index + 1 < len(pieces):
            neighbors.append(f"[下一段]({Path(names[index + 1]).name})")
        body += " · ".join(neighbors) + "\n\n" + source_note(name, content, first, last)
        body += f"**创建路径：** `{name}`；**本文件共有 {len(pieces)} 段**。"
        body += "本段是二进制编码数据。" if binary else f"本段覆盖源文件 L{first}–L{last}。"
        body += (
            "第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。\n\n"
        )
        body += f"本段原始字节数：`{len(piece)}`。"
        if not piece:
            body += "原文件为空，不保存路径行后的围栏分隔空行。\n\n"
        elif not binary:
            body += (
                "本段原文以LF换行结束。\n\n"
                if piece.endswith(b"\n")
                else "本段原文没有结尾换行；手工保存时去掉围栏前为展示添加的最后一个换行，自动还原器会根据SHA判定。\n\n"
            )
        else:
            body += "按Base64解码后的原始字节数计算。\n\n"
        if generated_frontend_asset(name):
            body += "<details>\n<summary>展开构建资产还原数据（无需手写）</summary>\n\n"
        body += f"<!-- learning-source: {json.dumps(meta, ensure_ascii=False)} -->\n"
        body += f"{fence}{language}\n{comment_line(name, language)}\n{payload}"
        if not payload.endswith("\n"):
            body += "\n"
        body += f"{fence}\n"
        if generated_frontend_asset(name):
            body += "\n</details>\n"
        result[names[index]] = body
    return result, {
        "path": name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "stage": STAGES[stage],
        "parts": names,
    }


def read_content():
    return json.loads(CONTENT.read_text(encoding="utf-8"))


def render():
    curriculum = read_content()
    if [stage["id"] for stage in curriculum] != STAGES:
        raise ValueError("The teaching stage IDs differ from the source allocation")
    output, records = {}, []
    for _, files in sources():
        for name, content in files:
            pages, record = source_pages(name, content, stage_for(name))
            if set(output).intersection(pages):
                raise ValueError("Source page filename collision: " + name)
            output.update(pages)
            records.append(record)
    records.sort(key=lambda row: (row["stage"], row["path"]))
    output["manifest.json"] = (
        json.dumps({"format": 1, "files": records}, ensure_ascii=False, indent=2) + "\n"
    )
    output["rebuild.py"] = (ROOT / "scripts/rebuild_learning_docs.py").read_text(encoding="utf-8")
    index = "# 全部源文件索引\n\n每个链接指向该文件第一段；大文件通过上一段/下一段继续，不能只复制第一段。阶段编号是首次落盘时间，之后章节会继续深入已有模块。\n\n"
    for stage in curriculum:
        sid = stage["id"]
        included = [row for row in records if row["stage"] == sid]
        pos = STAGES.index(sid)
        nav = "[总目录](../README.md)"
        if pos:
            nav += f" · [上一阶段](../{STAGES[pos - 1]}/README.md)"
        if pos + 1 < len(STAGES):
            nav += f" · [下一阶段](../{STAGES[pos + 1]}/README.md)"
        body = f"# {sid[:2]} · {stage['title']}\n\n{nav}\n\n"
        body += stage["body"].strip() + "\n\n"
        body += "## 本阶段源码和后续依赖\n\n"
        body += f"本阶段首次创建 {len(included)} 个源文件，完整位置见[文件落盘顺序](files.md)。"
        body += "已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。\n"
        output[f"{sid}/README.md"] = body
        listing = f"# {stage['title']}：本阶段文件\n\n[返回阶段导读](README.md)\n\n"
        listing += "按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件在 sources/locks，截图及Vue构建快照编码在 sources/assets 下，先读实现模块，需要校对时再打开资源。\n\n"
        index += f"## [{sid} · {stage['title']}]({sid}/README.md)\n\n"
        for row in included:
            part = row["parts"][0]
            desc = purpose(row["path"])[0]
            listing += f"- [{row['path']}]({part.removeprefix(sid + '/')})：{desc}；{len(row['parts'])} 段\n"
            index += f"- [{row['path']}]({part})（{len(row['parts'])} 段）\n"
        output[f"{sid}/files.md"] = listing
    output["source-index.md"] = index
    output["README.md"] = readme(curriculum, records)
    for name, content in output.items():
        if name.endswith(".md"):
            check_fences(content)
    return output


def readme(curriculum, records):
    text = """# 从零实现 AI 研发平台 · 分阶段实操教材

只保存本目录，就能在另一个空目录重建本项目的自有代码、前端、测试、迁移、配置、锁文件及教材维护工具。不需要本项目仓库、代码骨架或旧版大手册。第三方原生框架按第09阶段的固定提交从公开上游下载并处理；语言解释器、包管理器、依赖和浏览器按第00阶段安装。

## 如何学，而不只是如何复制

从00按顺序走到14。每站先看“为什么”，按落盘清单创建文件，运行该站指定的小实验，核对观察结果，再继续。每个模块页说明职责、上下游和当前段函数的控制逻辑；完整代码按文件职责归类，普通模块一页完整展示；只有超过千行的实现按函数、类或章节的自然边界拆段。锁文件、截图和Vue构建资产编码单独放在资源层，日常学习无需打开这些大块数据。后续阶段会深化前站因导入依赖而必须先创建的模块，不把它们偷偷留空。

模型只处理需求/规划/必要规则/可选审阅。数据库、模板、代码检查、浏览器和打包由真实工具执行。教材把“可复现确定性平台”“真实模型调用”“三套原生产品”“本机Daytona”分别列出验收证据，不能以一个PASS代替其余路径。

## 目录

"""
    for stage in curriculum:
        text += f"- [{stage['id'][:2]} · {stage['title']}]({stage['id']}/README.md)\n"
    text += f"""
本版完整收录 **{len(records)} 个源文件**；[源文件总索引](source-index.md)供查找，`manifest.json`记录每个文件的完整SHA-256、字节数、阶段和全部分段。它不是另一个代码下载地址。

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
"""
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    actual = (
        {path.relative_to(OUTPUT).as_posix() for path in OUTPUT.rglob("*") if path.is_file()}
        if OUTPUT.exists()
        else set()
    )
    if args.check:
        wrong = actual.symmetric_difference(expected)
        wrong.update(
            name
            for name in actual.intersection(expected)
            if (OUTPUT / name).read_bytes() != expected[name].encode("utf-8")
        )
        if wrong:
            raise SystemExit("learning-docs is stale: " + ", ".join(sorted(wrong)[:10]))
        print(f"Staged learning documentation PASS: {len(expected)} files")
        return
    # Only remove obsolete files in this generated directory, never source files.
    for name in actual.difference(expected):
        (OUTPUT / name).unlink()
    for name, content in expected.items():
        path = OUTPUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Staged learning documentation written: {len(expected)} files")


if __name__ == "__main__":
    main()
````
