"""Reviewed source tasks and executable checks, separate from template CRUD schemas."""

import math
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
        elif (
            CUSTOM_CHOICE in text
            or re.search(
                r"(?:这些|那些|全部|所有|不支持的|未支持的).{0,20}(?:自己|自行|自定义)(?:开发|实现)",
                text,
            )
            or (
                re.search(r"(?:自己|自定义)(?:开发|实现)|自行(?:开发|实现)", text)
                and re.search(r"不用模板|不依赖模板|模板(?:未|不|无法|不能)|超出模板", text)
            )
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
        or p.name in {"RND-CANDIDATE.json", "RND-DELIVERY.json", "RND-CONSUMER.json"}
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
    body_encoding: Literal["json", "form"] = "json"
    wait_ms: Annotated[int, Field(strict=True, ge=0, le=1000)] = 0
    status: int = Field(ge=100, le=599)
    equals: dict[str, JsonValue] = Field(default_factory=dict, max_length=40)
    absent: list[str] = Field(default_factory=list, max_length=40)
    captures: dict[Identifier, str] = Field(default_factory=dict, max_length=12)

    @field_validator("captures")
    @classmethod
    def controller_challenge_is_immutable(cls, value):
        if "nonce" in value:
            raise ValueError("nonce由控制器生成，应用响应不能替换独立随机挑战")
        return value

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
            k.lower()
            in {
                "host",
                "proxy-authorization",
                "connection",
                "content-length",
                "content-type",
                "content-encoding",
                "transfer-encoding",
            }
            or k.lower().startswith("x-daytona-")
            or not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{0,63}", k)
            or any(ord(c) < 32 for c in v)
            for k, v in value.items()
        ):
            raise ValueError("验收请求头无效")
        return value

    @model_validator(mode="after")
    def form_contract(self):
        if self.body_encoding == "form":
            if self.method not in {"POST", "PUT", "PATCH", "DELETE"} or not isinstance(
                self.body, dict
            ):
                raise ValueError("form只支持明确写请求的键值对象")
            self.bounded_form(self.body)
        return self

    @staticmethod
    def bounded_form(value):
        if not isinstance(value, dict) or not 1 <= len(value) <= 20:
            raise ValueError("form必须有1至20个明确字段")
        size = 0
        for key, item in value.items():
            if (
                not isinstance(key, str)
                or not 1 <= len(key) <= 100
                or not isinstance(item, str)
                or len(item) > 4096
                or any(ord(c) < 32 for c in key)
            ):
                raise ValueError("form只接受有界字符串字段")
            size += len(key.encode("utf-8")) + len(item.encode("utf-8"))
            if size > 8192:
                raise ValueError("form超过8KiB内容预算")
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


class PhysicalAssertion(Contract):
    """Reviewed data-only query; never candidate SQL or an application snapshot."""

    table: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")]
    key: dict[str, JsonValue] = Field(min_length=1, max_length=12)
    values: dict[str, JsonValue] = Field(min_length=1, max_length=12)

    @field_validator("key", "values")
    @classmethod
    def scalar_columns(cls, values):
        for key, value in values.items():
            if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key) or type(value) not in {
                str,
                int,
                float,
            }:
                raise ValueError("物理断言只允许明确列名与SQLite存储标量；布尔值须用0/1")
            if isinstance(value, str) and len(value) > 4096:
                raise ValueError("物理断言值超过预算")
            if type(value) is float and not math.isfinite(value):
                raise ValueError("物理断言只允许有限数值")
        return values


class BusinessObligation(Contract):
    """A proposed atomic assertion needs explicit source/decomposition review."""

    id: Identifier
    source_id: Identifier
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    assertion: str = Field(min_length=1, max_length=2000)
    scenario_id: Identifier
    physical: PhysicalAssertion


class CapabilityPlan(Contract):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=4000)
    selection: Selection
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    tasks: list[CapabilityTask] = Field(min_length=1, max_length=32)
    runtime: RuntimeContract
    scenarios: list[AcceptanceScenario] = Field(min_length=1, max_length=128)
    prerequisites: list[ExternalPrerequisite] = Field(default_factory=list, max_length=32)
    obligations: list[BusinessObligation] = Field(default_factory=list, max_length=128)
    # A proposal, never a model verdict. The operator must explicitly review
    # whether these atomic checks exhaust each exact original source unit.
    complete_source_ids: list[Identifier] = Field(default_factory=list, max_length=256)

    @model_validator(mode="after")
    def dependency_contract(self):
        tasks = {t.id: t for t in self.tasks}
        scenarios = {s.id: s for s in self.scenarios}
        if len(tasks) != len(self.tasks) or len(scenarios) != len(self.scenarios):
            raise ValueError("节点和验收场景ID必须唯一")
        if len({p.id for p in self.prerequisites}) != len(self.prerequisites):
            raise ValueError("外部前提ID必须唯一")
        if len({o.id for o in self.obligations}) != len(self.obligations) or len(
            set(self.complete_source_ids)
        ) != len(self.complete_source_ids):
            raise ValueError("业务义务及完整来源声明不能重复")
        if self.obligations and self.selection.database != "sqlite":
            raise ValueError("声明式物理义务目前仅支持SQLite；原生PostgreSQL须使用登记的独立oracle")
        for obligation in self.obligations:
            scenario = scenarios.get(obligation.scenario_id)
            if scenario is None or obligation.source_id not in scenario.requirements:
                raise ValueError("业务义务必须绑定同一来源的明确场景")
            if obligation.physical.table not in self.runtime.database_tables:
                raise ValueError("业务义务物理表必须属于已批准数据库清单")
            if scenario.evidence != "runtime" or not scenario.after_restart:
                raise ValueError("业务义务需要真实初始和重启场景，替身不能关闭义务")
            bound_variables = {"nonce"} | {
                name
                for value in [
                    *obligation.physical.key.values(),
                    *obligation.physical.values.values(),
                ]
                if isinstance(value, str)
                for name in re.findall(r"\$\{([a-z][a-z0-9_-]*)\}", value)
            }
            if any(bound_variables & step.captures.keys() for step in scenario.after_restart):
                raise ValueError("重启场景不能重绑物理义务的记录键或期望值变量")
            nonces = {
                value
                for value in obligation.physical.values.values()
                if isinstance(value, str) and "${nonce}" in value
            }
            if not nonces or not all(
                any(
                    step.method != "GET"
                    and 200 <= step.status < 300
                    and isinstance(step.body, dict)
                    and value in step.body.values()
                    and value in step.equals.values()
                    for step in scenario.steps
                )
                and any(
                    step.method == "GET"
                    and 200 <= step.status < 300
                    and value in step.equals.values()
                    for step in scenario.steps
                )
                and any(
                    step.method == "GET" and value in step.equals.values()
                    for step in scenario.after_restart
                )
                for value in nonces
            ):
                raise ValueError("业务义务必须独立读回同次随机业务值，不能用固定响应或无关写入")
        if not set(self.complete_source_ids) <= {o.source_id for o in self.obligations}:
            raise ValueError("完整来源声明必须有明确原子业务义务")
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
    originals = {source["id"]: source for source in sources}
    for obligation in plan.obligations:
        if obligation.source_id not in originals or (
            obligation.source_sha256 != originals[obligation.source_id]["sha256"]
        ):
            errors.append("原子业务义务没有绑定准确原始来源：" + obligation.id)
    if set(plan.complete_source_ids) - expected:
        errors.append("完整来源声明引用了不存在的原文")
    services = {p.id for p in plan.prerequisites}
    if any(s.external_service and s.external_service not in services for s in plan.scenarios):
        errors.append("外部替身引用未声明服务")
    return errors
