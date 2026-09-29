"""Typed external contracts. Raw user input cannot choose roles, commands or approval state."""

import hashlib
import json
import keyword
import re
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, model_validator

Text = Annotated[str, Field(min_length=1, max_length=20000)]
Name = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")]


def digest(data: object) -> str:
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProjectInput(Contract):
    title: Annotated[str, Field(min_length=1, max_length=200)]


class RunInput(Contract):
    requirement: Text
    template: Literal["python-basic", "fastapiadmin", "yudao-vben"] = "python-basic"
    selection: dict | None = None
    intelligent: StrictBool = False

    @model_validator(mode="after")
    def validate_selection(self):
        from workbench.catalog import Selection

        chosen = Selection.model_validate(self.selection or {"template": self.template})
        if chosen.template != self.template:
            raise ValueError("选择与模板标识不一致")
        self.selection = chosen.model_dump()
        return self


class ResumeInput(Contract):
    gate_id: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    action: Literal["answer", "approve", "reject", "revise", "recommend"]
    text: str = Field(default="", max_length=20000)
    approved: StrictBool | None = None

    @model_validator(mode="after")
    def action_matches(self):
        if self.action in {"answer", "revise"} and not self.text:
            raise ValueError("回答或修改意见不能为空")
        if self.action in {"answer", "revise"}:
            from workbench.conversation import command_word

            if command_word(self.text) in {
                "批准",
                "approve",
                "拒绝",
                "reject",
                "智能推荐",
                "推荐",
                "smart",
                "recommend",
            }:
                raise ValueError(
                    "这是控制指令，不是需求回答；请使用对应按钮或 CLI 命令，不消耗澄清轮数"
                )
        if self.action == "approve" and self.approved is not True:
            raise ValueError("批准必须显式提交布尔值 true")
        if self.action == "recommend" and self.approved is not True:
            raise ValueError("智能推荐须显式授权 approved=true；后续不再逐项询问")
        if self.action == "reject" and self.approved is not False:
            raise ValueError("拒绝必须显式提交布尔值 false")
        return self


class Requirement(Contract):
    summary: str = Field(max_length=4000)
    users: list[Text] = Field(max_length=20)
    data_scope: Literal["per_user", "shared", "unknown"]
    features: list[Text] = Field(max_length=40)
    acceptance: list[Text]
    questions: list[Text] = Field(default_factory=list, max_length=6)
    assumptions: list[Text] = Field(default_factory=list)
    unsupported: list[Text] = Field(default_factory=list)
    recommendations: list[Text] = Field(default_factory=list)
    facts: dict[str, str] = Field(default_factory=dict)

    @property
    def ready(self) -> bool:
        return bool(
            self.summary
            and self.users
            and self.features
            and self.acceptance
            and self.data_scope != "unknown"
            and not self.questions
            and not self.unsupported
        )


class FieldSpec(Contract):
    name: Name
    kind: Literal["text", "integer", "boolean", "date", "enum"]
    required: bool = True
    max_length: int = Field(default=200, ge=1, le=20000)
    min_length: int = Field(default=0, ge=0, le=20000)
    choices: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(
        default_factory=list, max_length=50
    )
    searchable: bool = False
    filterable: bool = False
    date_range: bool = False

    @model_validator(mode="after")
    def field_options(self):
        if self.min_length > self.max_length:
            raise ValueError("最小长度不得大于最大长度")
        if self.kind == "enum" and (
            not self.choices or len(set(self.choices)) != len(self.choices)
        ):
            raise ValueError("枚举必须有不重复的选项")
        if self.kind != "enum" and self.choices:
            raise ValueError("只有 enum 类型可以声明 choices")
        if self.searchable and self.kind not in {"text", "enum"}:
            raise ValueError("关键词搜索只能使用文本/枚举字段")
        if self.date_range and self.kind != "date":
            raise ValueError("日期范围只支持 date 类型")
        return self

    @field_validator("name")
    @classmethod
    def reserved(cls, value):
        if keyword.iskeyword(value) or value in {"id", "owner_id", "created_at", "updated_at"}:
            raise ValueError("字段名属于保留名称")
        return value


class Entity(Contract):
    name: Name
    description: str
    fields: list[FieldSpec] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def unique_fields(self):
        if len({f.name for f in self.fields}) != len(self.fields):
            raise ValueError("字段名称必须唯一")
        return self


class CustomRule(Contract):
    description: Text
    entity: Name
    accept_examples: list[dict] = Field(min_length=1, max_length=10)
    reject_examples: list[dict] = Field(min_length=1, max_length=10)


class Plan(Contract):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    data_scope: Literal["per_user", "shared"]
    entities: list[Entity] = Field(min_length=1, max_length=8)
    acceptance: list[Text] = Field(min_length=1)
    custom_rules: list[CustomRule] = Field(default_factory=list, max_length=6)
    unsupported: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_entities(self):
        names = {e.name for e in self.entities}
        if len(names) != len(self.entities) or (
            names & {"users", "tokens", "alembic_version"}
            or any(n.startswith("sqlite_") for n in names)
        ):
            raise ValueError("实体名称重复或为保留名称")
        if any(rule.entity not in names for rule in self.custom_rules):
            raise ValueError("自定义规则引用未知实体")
        for rule in self.custom_rules:
            entity = next(e for e in self.entities if e.name == rule.entity)
            for sample in rule.accept_examples + rule.reject_examples:
                if set(sample) - {f.name for f in entity.fields}:
                    raise ValueError("规则示例包含未定义字段")
                for field in entity.fields:
                    value = sample.get(field.name)
                    if value is None:
                        if field.required:
                            raise ValueError("规则示例缺少必填字段")
                        continue
                    expected = {
                        "text": str,
                        "integer": int,
                        "boolean": bool,
                        "date": str,
                        "enum": str,
                    }[field.kind]
                    if type(value) is not expected:
                        raise ValueError("规则示例字段类型错误")
                    if field.kind == "date":
                        date.fromisoformat(value)
                    if field.kind == "enum" and value not in field.choices:
                        raise ValueError("规则示例不在枚举选项内")
                    if field.kind in {"text", "enum"} and len(value) > field.max_length:
                        raise ValueError("规则示例文本过长")
        return self


class Patch(Contract):
    path: Literal["custom_rules.py"]
    before_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    content: Annotated[str, Field(min_length=1, max_length=30000)]


class Patches(Contract):
    explanation: str
    patches: list[Patch] = Field(min_length=1, max_length=1)


def safe_component(value: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", value):
        raise ValueError("无效的路径标识")
    return value


class ModelReview(Contract):
    summary: Text
    observations: list[Text] = Field(default_factory=list, max_length=20)
    uncovered_requirements: list[Text] = Field(default_factory=list, max_length=20)
    # Advisory only: never gives permission to override a failed executable test.


class AutomationInput(Contract):
    enabled: StrictBool
    accepted: StrictBool

    @model_validator(mode="after")
    def consent(self):
        if self.enabled and not self.accepted:
            raise ValueError("启用智能推荐需要明确接受其后续自动决定语义")
        return self
