# workbench/capability_contracts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.catalog`、`workbench.domain`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `custom_requested`（L17–L28）：接收`messages`。 源码说明：Only explicit human authorization selects this path, never model claims.。 控制顺序：L20遍历`messages`；L21按`re.search(r"(?:禁止\|不允许\|不要)自定义实现\|仅(?:使用\|用)模板", text)`分支；L23按`CUSTOM_CHOICE in text or ( re.search(r"(?:自己\|自定义)(?:开发\|实现)\|自行(?:开发\|实现)", text) an…`分支。 调用`re.search`。 返回路径：L28的`enabled`。
- `scope_sources`（L31–L57）：接收`messages`。 源码说明：Keep every exact human source; source units are coverage references, not summaries.。 控制顺序：L34遍历`enumerate(messages)`；L35按`text.strip() in {"继续", "请继续", "好的", "好", "确认", "确认继续"}`分支；L38遍历`re.finditer(r"[^。；;\n]+[。；;\n]*", text)`；L40遍历`range(0, len(value), 1000)`；L42按`not quote.strip()`分支；L55按`len(rows) > 256`分支；L56抛异常，停止当前正常路径。 调用`enumerate`、`text.strip`、`re.finditer`、`match.group`、`range`、`len`、`quote.strip`、`rows.append`、`match.start`等。 返回路径：L57的`rows`。
- `source_path`（L60–L76）：接收`value`。 控制顺序：L62按`not value or len(value) > 300 or p.is_absolute() or any(part in {"", ".", ".."} for p…`分支；L75抛异常，停止当前正常路径。 调用`PurePosixPath`、`len`、`p.is_absolute`、`any`、`value.split`、`ord`、`set`、`secret_name`、`ValueError`。 返回路径：L76的`value`。
- `TaskCommand`（L79–L95）：继承`Contract`。声明的数据项为`argv`、`cwd`；类型约束/数据库列参数以完整定义为准。
- `TaskCommand.relative_directory`（L87–L88）：接收`value`。 调用`source_path`、`field_validator`。 返回路径：L88的`value if value == "." else source_path(value)`。
- `TaskCommand.no_control_characters`（L92–L95）：接收`value`。 控制顺序：L93按`any(any(ord(c) < 32 for c in item) for item in value)`分支；L94抛异常，停止当前正常路径。 调用`any`、`ord`、`ValueError`、`field_validator`。 返回路径：L95的`value`。
- `RuntimeContract`（L98–L135）：继承`Contract`。声明的数据项为`prepare`、`start`、`port`、`health_path`、`startup_seconds`、`database_path`、`database_tables`；类型约束/数据库列参数以完整定义为准。
- `RuntimeContract.product_port`（L111–L114）：接收`value`。 控制顺序：L112按`value in {2280, 55432}`分支；L113抛异常，停止当前正常路径。 调用`ValueError`、`field_validator`。 返回路径：L114的`value`。
- `RuntimeContract.health_is_relative`（L118–L121）：接收`value`。 控制顺序：L119按`not value.startswith("/") or value.startswith("//") or "\\" in value`分支；L120抛异常，停止当前正常路径。 调用`value.startswith`、`ValueError`、`field_validator`。 返回路径：L121的`value`。
- `RuntimeContract.storage_is_relative`（L125–L135）：接收`value`。 控制顺序：L127按`p.is_absolute() or ".." in p.parts or "\\" in value or ":" in value or value.startswi…`分支；L134抛异常，停止当前正常路径。 调用`PurePosixPath`、`p.is_absolute`、`value.startswith`、`ValueError`、`field_validator`。 返回路径：L135的`value`。
- `HttpStep`（L138–L171）：继承`Contract`。声明的数据项为`method`、`path`、`headers`、`body`、`status`、`equals`、`absent`、`captures`；类型约束/数据库列参数以完整定义为准。
- `HttpStep.loopback_path`（L150–L158）：接收`value`。 控制顺序：L151按`not value.startswith("/") or value.startswith("//") or "\\" in value or any(ord(c) < …`分支；L157抛异常，停止当前正常路径。 调用`value.startswith`、`any`、`ord`、`ValueError`、`field_validator`。 返回路径：L158的`value`。
- `HttpStep.bounded_headers`（L162–L171）：接收`value`。 控制顺序：L163按`any( k.lower() in {"host", "proxy-authorization", "connection", "content-length"} or …`分支；L170抛异常，停止当前正常路径。 调用`any`、`k.lower`、`k.lower().startswith`、`re.fullmatch`、`ord`、`value.items`、`ValueError`、`field_validator`。 返回路径：L171的`value`。
- `AcceptanceScenario`（L174–L189）：继承`Contract`。声明的数据项为`id`、`title`、`requirements`、`steps`、`after_restart`、`browser`、`evidence`、`external_service`；类型约束/数据库列参数以完整定义为准。
- `AcceptanceScenario.fixture_identity`（L186–L189）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L187按`(self.evidence == "external_fixture") != (self.external_service is not None)`分支；L188抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L189的`self`。
- `BrowserStep`（L192–L205）：继承`Contract`。声明的数据项为`action`、`selector`、`value`、`width`、`height`；类型约束/数据库列参数以完整定义为准。
- `BrowserStep.action_contract`（L200–L205）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L201按`self.action == "open"`分支；L203按`self.action != "viewport" and not self.selector`分支；L204抛异常，停止当前正常路径。 调用`HttpStep.loopback_path`、`ValueError`、`model_validator`。 返回路径：L205的`self`。
- `ExternalPrerequisite`（L208–L230）：继承`Contract`。声明的数据项为`id`、`kind`、`description`、`requirements`、`configuration_names`、`provider`、`probe`；类型约束/数据库列参数以完整定义为准。
- `ExternalPrerequisite.bounded_provider_probe`（L219–L230）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L220按`self.provider == "http_json" and ( self.probe is None or self.probe.method != "GET" o…`分支；L227抛异常，停止当前正常路径；L228按`self.provider != "http_json" and self.probe is not None`分支；L229抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L230的`self`。
- `CapabilityTask`（L233–L249）：继承`Contract`。声明的数据项为`id`、`title`、`depends_on`、`requirements`、`files`、`contract`、`scenarios`；类型约束/数据库列参数以完整定义为准。
- `CapabilityTask.exact_files`（L244–L249）：接收`values`。 控制顺序：L245遍历`values`；L247按`len({v.casefold() for v in values}) != len(values)`分支；L248抛异常，停止当前正常路径。 调用`source_path`、`len`、`v.casefold`、`ValueError`、`field_validator`。 返回路径：L249的`values`。
- `CapabilityPlan`（L252–L299）：继承`Contract`。声明的数据项为`title`、`summary`、`selection`、`source_digest`、`tasks`、`runtime`、`scenarios`、`prerequisites`；类型约束/数据库列参数以完整定义为准。
- `CapabilityPlan.dependency_contract`（L263–L299）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L266按`len(tasks) != len(self.tasks) or len(scenarios) != len(self.scenarios)`分支；L267抛异常，停止当前正常路径；L268按`len({p.id for p in self.prerequisites}) != len(self.prerequisites)`分支；L269抛异常，停止当前正常路径；L283遍历`self.tasks`；L285按`len(set(task.depends_on)) != len(task.depends_on) or not set(task.scenarios) <= scena…`分支；L289抛异常，停止当前正常路径；L290遍历`enumerate(self.tasks)`。后续分支沿下方源码相同行号继续阅读。 调用`len`、`ValueError`、`visit`、`set`、`scenarios.keys`、`enumerate`、`p.casefold`、`model_validator`。 返回路径：L299的`self`。
- `CapabilityPlan.dependency_contract.visit`（L272–L281）：接收`identifier`、`stack`。 控制顺序：L273按`identifier in stack`分支；L274抛异常，停止当前正常路径；L275按`identifier not in tasks`分支；L276抛异常，停止当前正常路径；L277按`identifier not in ancestors`分支；L279遍历`tasks[identifier].depends_on`。 调用`ValueError`、`set`、`visit`。 返回路径：L281的`ancestors[identifier]`。
- `CapabilityOutline`（L302–L311）：继承`Contract`。声明的数据项为`title`、`summary`、`selection`、`source_digest`、`tasks`、`runtime`、`prerequisites`；类型约束/数据库列参数以完整定义为准。
- `CapabilityScenarioBatch`（L314–L316）：继承`Contract`。声明的数据项为`summary`、`scenarios`；类型约束/数据库列参数以完整定义为准。
- `SourceEdit`（L319–L327）：继承`Contract`。声明的数据项为`path`、`before_sha256`、`content`；类型约束/数据库列参数以完整定义为准。
- `SourceEdit.path_contract`（L326–L327）：接收`value`。 调用`source_path`、`field_validator`。 返回路径：L327的`source_path(value)`。
- `CapabilityEdits`（L330–L332）：继承`Contract`。声明的数据项为`explanation`、`files`；类型约束/数据库列参数以完整定义为准。
- `coverage_errors`（L335–L361）：接收`plan`、`sources`。 控制顺序：L339遍历`plan.tasks`；L347按`not set(task.requirements) <= checked`分支；L354按`expected - covered`分支；L356按`all_refs - expected`分支；L359按`any(s.external_service and s.external_service not in services for s in plan.scenarios…`分支。 调用`set`、`covered.update`、`errors.append`、`", ".join`、`sorted`、`any`。 返回路径：L361的`errors`。

</details>

**创建路径：** `workbench/capability_contracts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L361。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14386`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_contracts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "af77b993ab002d589f6f51c848ac9bb236d6a7c47763013cf87d2e697e2a0e73"} -->
````python
# workbench/capability_contracts.py
"""Reviewed source tasks and executable checks, separate from template CRUD schemas."""

import re
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import Field, JsonValue, field_validator, model_validator

from workbench.catalog import Selection
from workbench.domain import Contract, UserText, digest
from workbench.filesystem import EXCLUDED_DIRS, secret_name

Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")]
CUSTOM_CHOICE = "保留全部已提出功能，规划并自定义实现模板未覆盖的能力"


def custom_requested(messages):
    """Only explicit human authorization selects this path, never model claims."""
    enabled = False
    for text in messages:
        if re.search(r"(?:禁止|不允许|不要)自定义实现|仅(?:使用|用)模板", text):
            enabled = False
        elif CUSTOM_CHOICE in text or (
            re.search(r"(?:自己|自定义)(?:开发|实现)|自行(?:开发|实现)", text)
            and re.search(r"不用模板|不依赖模板|模板(?:未|不|无法|不能)|超出模板", text)
        ):
            enabled = True
    return enabled


def scope_sources(messages):
    """Keep every exact human source; source units are coverage references, not summaries."""
    rows = []
    for index, text in enumerate(messages):
        if text.strip() in {"继续", "请继续", "好的", "好", "确认", "确认继续"}:
            continue
        position = 0
        for match in re.finditer(r"[^。；;\n]+[。；;\n]*", text):
            value = match.group()
            for offset in range(0, len(value), 1000):
                quote = value[offset : offset + 1000]
                if not quote.strip():
                    continue
                rows.append(
                    {
                        "id": f"source-{index}-{position}",
                        "message_index": index,
                        "start": match.start() + offset,
                        "end": match.start() + offset + len(quote),
                        "text": quote,
                        "sha256": digest(quote),
                    }
                )
                position += 1
    if len(rows) > 256:
        raise ValueError("自定义范围超过单次计划的256个来源单元；原始内容仍保留，请分项目规划")
    return rows


def source_path(value):
    p = PurePosixPath(value)
    if (
        not value
        or len(value) > 300
        or p.is_absolute()
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or "\\" in value
        or ":" in value
        or any(ord(c) < 32 for c in value)
        or set(p.parts) & EXCLUDED_DIRS
        or secret_name(value)
        or p.parts[0] in {".github", ".agents", ".codex"}
        or p.name in {"RND-CANDIDATE.json", "RND-DELIVERY.json"}
    ):
        raise ValueError("只允许产品内的普通源码路径；不允许秘密、环境、工具或平台控制目录")
    return value


class TaskCommand(Contract):
    argv: list[Annotated[str, Field(min_length=1, max_length=500)]] = Field(
        min_length=1, max_length=30
    )
    cwd: str = "."

    @field_validator("cwd")
    @classmethod
    def relative_directory(cls, value):
        return value if value == "." else source_path(value)

    @field_validator("argv")
    @classmethod
    def no_control_characters(cls, value):
        if any(any(ord(c) < 32 for c in item) for item in value):
            raise ValueError("命令参数不能含控制字符")
        return value


class RuntimeContract(Contract):
    prepare: list[TaskCommand] = Field(default_factory=list, max_length=8)
    start: TaskCommand
    port: int = Field(ge=1024, le=65535)
    health_path: str = "/health"
    startup_seconds: int = Field(default=30, ge=1, le=120)
    database_path: str = "data/application.db"
    database_tables: list[Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")]] = Field(
        min_length=1, max_length=40
    )

    @field_validator("port")
    @classmethod
    def product_port(cls, value):
        if value in {2280, 55432}:
            raise ValueError("产品端口不能使用控制或独立数据库保留端口")
        return value

    @field_validator("health_path")
    @classmethod
    def health_is_relative(cls, value):
        if not value.startswith("/") or value.startswith("//") or "\\" in value:
            raise ValueError("健康检查必须是产品相对路径")
        return value

    @field_validator("database_path")
    @classmethod
    def storage_is_relative(cls, value):
        p = PurePosixPath(value)
        if (
            p.is_absolute()
            or ".." in p.parts
            or "\\" in value
            or ":" in value
            or value.startswith(".")
        ):
            raise ValueError("测试数据库只能位于隔离产品的普通相对路径")
        return value


class HttpStep(Contract):
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "GET"
    path: str = Field(min_length=1, max_length=1000)
    headers: dict[str, str] = Field(default_factory=dict, max_length=12)
    body: JsonValue = None
    status: int = Field(ge=100, le=599)
    equals: dict[str, JsonValue] = Field(default_factory=dict, max_length=40)
    absent: list[str] = Field(default_factory=list, max_length=40)
    captures: dict[Identifier, str] = Field(default_factory=dict, max_length=12)

    @field_validator("path")
    @classmethod
    def loopback_path(cls, value):
        if (
            not value.startswith("/")
            or value.startswith("//")
            or "\\" in value
            or any(ord(c) < 32 for c in value)
        ):
            raise ValueError("验收请求只能使用隔离产品的相对HTTP路径")
        return value

    @field_validator("headers")
    @classmethod
    def bounded_headers(cls, value):
        if any(
            k.lower() in {"host", "proxy-authorization", "connection", "content-length"}
            or k.lower().startswith("x-daytona-")
            or not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{0,63}", k)
            or any(ord(c) < 32 for c in v)
            for k, v in value.items()
        ):
            raise ValueError("验收请求头无效")
        return value


class AcceptanceScenario(Contract):
    id: Identifier
    title: str = Field(min_length=1, max_length=500)
    requirements: list[Identifier] = Field(min_length=1, max_length=256)
    steps: list[HttpStep] = Field(min_length=1, max_length=60)
    after_restart: list[HttpStep] = Field(default_factory=list, max_length=20)
    browser: list["BrowserStep"] = Field(default_factory=list, max_length=60)
    # A declared fixture proves adapter behavior, never live service availability.
    evidence: Literal["runtime", "external_fixture"] = "runtime"
    external_service: Identifier | None = None

    @model_validator(mode="after")
    def fixture_identity(self):
        if (self.evidence == "external_fixture") != (self.external_service is not None):
            raise ValueError("外部服务替身必须声明对应服务，不能当成真实服务证据")
        return self


class BrowserStep(Contract):
    action: Literal["open", "fill", "click", "text", "visible", "hidden", "viewport"]
    selector: str = Field(default="", max_length=500)
    value: str = Field(default="", max_length=10000)
    width: int = Field(default=1280, ge=320, le=2560)
    height: int = Field(default=900, ge=480, le=2000)

    @model_validator(mode="after")
    def action_contract(self):
        if self.action == "open":
            HttpStep.loopback_path(self.value)
        elif self.action != "viewport" and not self.selector:
            raise ValueError("浏览器交互必须有明确选择器")
        return self


class ExternalPrerequisite(Contract):
    id: Identifier
    kind: Literal["service", "credential", "capacity", "human_policy"]
    description: str = Field(min_length=1, max_length=1500)
    requirements: list[Identifier] = Field(min_length=1, max_length=256)
    # Describes names/purpose only; credential values never belong in a plan.
    configuration_names: list[Identifier] = Field(default_factory=list, max_length=20)
    provider: Literal["manual", "http_json", "s3"] = "manual"
    probe: HttpStep | None = None

    @model_validator(mode="after")
    def bounded_provider_probe(self):
        if self.provider == "http_json" and (
            self.probe is None
            or self.probe.method != "GET"
            or self.probe.body is not None
            or self.probe.headers
            or self.probe.captures
        ):
            raise ValueError("HTTP服务检查只允许明确GET断言，认证由安全配置提供")
        if self.provider != "http_json" and self.probe is not None:
            raise ValueError("S3使用固定临时对象往返协议；人工条件不能伪装网络探针")
        return self


class CapabilityTask(Contract):
    id: Identifier
    title: str = Field(min_length=1, max_length=300)
    depends_on: list[Identifier] = Field(default_factory=list, max_length=32)
    requirements: list[Identifier] = Field(min_length=1, max_length=256)
    files: list[str] = Field(min_length=1, max_length=64)
    contract: str = Field(min_length=1, max_length=6000)
    scenarios: list[Identifier] = Field(min_length=1, max_length=16)

    @field_validator("files")
    @classmethod
    def exact_files(cls, values):
        for value in values:
            source_path(value)
        if len({v.casefold() for v in values}) != len(values):
            raise ValueError("节点文件清单不能重复或大小写冲突")
        return values


class CapabilityPlan(Contract):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=4000)
    selection: Selection
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    tasks: list[CapabilityTask] = Field(min_length=1, max_length=32)
    runtime: RuntimeContract
    scenarios: list[AcceptanceScenario] = Field(min_length=1, max_length=128)
    prerequisites: list[ExternalPrerequisite] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def dependency_contract(self):
        tasks = {t.id: t for t in self.tasks}
        scenarios = {s.id: s for s in self.scenarios}
        if len(tasks) != len(self.tasks) or len(scenarios) != len(self.scenarios):
            raise ValueError("节点和验收场景ID必须唯一")
        if len({p.id for p in self.prerequisites}) != len(self.prerequisites):
            raise ValueError("外部前提ID必须唯一")
        ancestors = {}

        def visit(identifier, stack):
            if identifier in stack:
                raise ValueError("能力节点依赖存在循环")
            if identifier not in tasks:
                raise ValueError("能力节点引用不存在的依赖")
            if identifier not in ancestors:
                ancestors[identifier] = set()
                for dependency in tasks[identifier].depends_on:
                    ancestors[identifier] |= {dependency} | visit(dependency, {*stack, identifier})
            return ancestors[identifier]

        for task in self.tasks:
            visit(task.id, set())
            if (
                len(set(task.depends_on)) != len(task.depends_on)
                or not set(task.scenarios) <= scenarios.keys()
            ):
                raise ValueError("重复依赖或未知验收场景")
        for index, left in enumerate(self.tasks):
            for right in self.tasks[index + 1 :]:
                if {p.casefold() for p in left.files} & {
                    p.casefold() for p in right.files
                } and not (left.id in ancestors[right.id] or right.id in ancestors[left.id]):
                    raise ValueError("写同一文件的节点必须显式串行依赖")
        used = {s for task in self.tasks for s in task.scenarios}
        if used != scenarios.keys():
            raise ValueError("每个验收场景必须属于至少一个源码节点")
        return self


class CapabilityOutline(Contract):
    """Small global plan; detailed executable scenarios are generated per task."""

    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=4000)
    selection: Selection
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    tasks: list[CapabilityTask] = Field(min_length=1, max_length=32)
    runtime: RuntimeContract
    prerequisites: list[ExternalPrerequisite] = Field(default_factory=list, max_length=32)


class CapabilityScenarioBatch(Contract):
    summary: str = Field(min_length=1, max_length=2000)
    scenarios: list[AcceptanceScenario] = Field(min_length=1, max_length=16)


class SourceEdit(Contract):
    path: str
    before_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    content: UserText = Field(max_length=100000)

    @field_validator("path")
    @classmethod
    def path_contract(cls, value):
        return source_path(value)


class CapabilityEdits(Contract):
    explanation: str = Field(min_length=1, max_length=2000)
    files: list[SourceEdit] = Field(min_length=1, max_length=64)


def coverage_errors(plan, sources):
    expected = {s["id"] for s in sources}
    errors = []
    covered = set()
    for task in plan.tasks:
        covered.update(task.requirements)
        checked = {
            ref
            for scenario in plan.scenarios
            if scenario.id in task.scenarios
            for ref in scenario.requirements
        }
        if not set(task.requirements) <= checked:
            errors.append(f"节点 {task.id} 存在没有独立验收场景的来源")
    all_refs = (
        covered
        | {r for s in plan.scenarios for r in s.requirements}
        | {r for p in plan.prerequisites for r in p.requirements}
    )
    if expected - covered:
        errors.append("未覆盖原始来源：" + ", ".join(sorted(expected - covered)))
    if all_refs - expected:
        errors.append("引用不存在的来源：" + ", ".join(sorted(all_refs - expected)))
    services = {p.id for p in plan.prerequisites}
    if any(s.external_service and s.external_service not in services for s in plan.scenarios):
        errors.append("外部替身引用未声明服务")
    return errors
````
