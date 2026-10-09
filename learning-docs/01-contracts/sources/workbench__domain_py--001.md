# workbench/domain.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：模型、网页、数据库之间的数据合同。** Pydantic模型定义哪些字段可以进入系统；校验在业务处理前发生。FieldSpec约束字段类型，Entity组合字段，Plan组合实体与规则；digest把规范化JSON变成稳定指纹，审批只对该指纹有效。

**对应关系：** api/llm解析 → Requirement/Plan → knowledge/generator/verification；test_contracts。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 以批准为例：网页传入的是ResumeInput，不是任意字典。action=approve必须携带严格布尔true，字符串true不能当批准；gate_id随后还要与数据库当前关口相符。Plan的字段、关系和业务合同先完成交叉校验，再允许生成器接收，所以模型写出一段JSON并不是绕过边界的办法。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `digest`（L31–L33）：接收`data`。 调用`json.dumps`、`hashlib.sha256(raw.encode()).hexdigest`、`hashlib.sha256`、`raw.encode`。 返回路径：L33的`hashlib.sha256(raw.encode()).hexdigest()`。
- `Contract`（L36–L37）：继承`BaseModel`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ProjectInput`（L40–L41）：继承`Contract`。声明的数据项为`title`；类型约束/数据库列参数以完整定义为准。
- `RunInput`（L44–L61）：继承`Contract`。声明的数据项为`requirement`、`template`、`selection`、`intelligent`、`allow_custom_extensions`；类型约束/数据库列参数以完整定义为准。
- `RunInput.validate_selection`（L52–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L56按`chosen.template != self.template`分支；L57抛异常，停止当前正常路径；L59按`not self.requirement.strip()`分支；L60抛异常，停止当前正常路径。 调用`Selection.model_validate`、`ValueError`、`chosen.model_dump`、`self.requirement.strip`、`model_validator`。 返回路径：L61的`self`。
- `BatchItem`（L64–L65）：继承`RunInput`。声明的数据项为`title`；类型约束/数据库列参数以完整定义为准。
- `BatchInput`（L68–L71）：继承`Contract`。声明的数据项为`items`；类型约束/数据库列参数以完整定义为准。
- `ClarificationAnswer`（L74–L87）：继承`Contract`。声明的数据项为`question_id`、`option_ids`、`text`；类型约束/数据库列参数以完整定义为准。
- `ClarificationAnswer.unique_options`（L84–L87）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L85按`len(self.option_ids) != len(set(self.option_ids))`分支；L86抛异常，停止当前正常路径。 调用`len`、`set`、`ValueError`、`model_validator`。 返回路径：L87的`self`。
- `ResumeInput`（L90–L136）：继承`Contract`。声明的数据项为`gate_id`、`action`、`version`、`digest`、`answers`、`text`、`approved`；类型约束/数据库列参数以完整定义为准。
- `ResumeInput.action_matches`（L100–L136）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L101按`self.answers and self.action != "answer"`分支；L102抛异常，停止当前正常路径；L103按`len({answer.question_id for answer in self.answers}) != len(self.answers)`分支；L104抛异常，停止当前正常路径；L105按`self.action in {"answer", "revise"} and not self.text.strip() and not self.answers`分支；L106抛异常，停止当前正常路径；L107按`self.action in {"answer", "revise"}`分支；L110按`command_word(self.text) in { "批准", "approve", "拒绝", "reject", "智能推荐", "推荐", "smart", …`分支。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`len`、`self.text.strip`、`command_word`、`model_validator`。 返回路径：L136的`self`。
- `RequirementChange`（L139–L154）：继承`Contract`。声明的数据项为`section`、`key`、`replacement`、`source_quote`；类型约束/数据库列参数以完整定义为准。
- `FieldRequirement`（L157–L187）：继承`Contract`。声明的数据项为`field`、`entity`、`kind`、`required`、`min_length`、`max_length`、`searchable`、`filterable`、`date_range`、`choices`、`minimum`、`maximum`、`exclusive_minimum`、`exclusive_maximum`、`pattern`；类型约束/数据库列参数以完整定义为准。
- `EntityRequirement`（L190–L205）：继承`Contract`。声明的数据项为`entity`、`fields`、`additional_fields`；类型约束/数据库列参数以完整定义为准。
- `EntityRequirement.unique_fields`（L202–L205）：接收`value`。 控制顺序：L203按`len(set(value)) != len(value)`分支；L204抛异常，停止当前正常路径。 调用`len`、`set`、`ValueError`、`field_validator`。 返回路径：L205的`value`。
- `ClarificationOption`（L208–L211）：继承`Contract`。声明的数据项为`id`、`label`、`description`；类型约束/数据库列参数以完整定义为准。
- `ClarificationQuestion`（L214–L234）：继承`Contract`。声明的数据项为`id`、`prompt`、`kind`、`options`、`required`、`allow_other`；类型约束/数据库列参数以完整定义为准。
- `ClarificationQuestion.valid_options`（L225–L234）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L226按`self.kind == "text" and self.options`分支；L227抛异常，停止当前正常路径；L228按`self.kind != "text" and len(self.options) < 2`分支；L229抛异常，停止当前正常路径；L230按`len({option.id for option in self.options}) != len(self.options)`分支；L231抛异常，停止当前正常路径；L232按`len({option.label for option in self.options}) != len(self.options)`分支；L233抛异常，停止当前正常路径。 调用`ValueError`、`len`、`model_validator`。 返回路径：L234的`self`。
- `Requirement`（L237–L311）：继承`Contract`。声明的数据项为`summary`、`users`、`data_scope`、`features`、`acceptance`、`questions`、`question_items`、`assumptions`、`unsupported`、`limitations`、`recommendations`、`facts`、`field_requirements`、`entity_requirements`、`additional_entities`、`changes`；类型约束/数据库列参数以完整定义为准。
- `Requirement.gate_dump`（L264–L280）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.model_dump`、`getattr`、`set`。 返回路径：L267的`self.model_dump( exclude={ name for name in ( "limitations", "field_requirements", "entity…`。
- `Requirement.question_presentation`（L283–L292）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L284按`len({item.id for item in self.question_items}) != len(self.question_items)`分支；L285抛异常，停止当前正常路径；L286按`len({item.prompt for item in self.question_items}) != len(self.question_items)`分支；L287抛异常，停止当前正常路径；L288按`self.question_items and {item.prompt for item in self.question_items} != set( self.qu…`分支；L291抛异常，停止当前正常路径。 调用`len`、`ValueError`、`set`、`model_validator`。 返回路径：L292的`self`。
- `Requirement.unique_entity_requirements`（L296–L299）：接收`value`。 控制顺序：L297按`len({item.entity for item in value}) != len(value)`分支；L298抛异常，停止当前正常路径。 调用`len`、`ValueError`、`field_validator`。 返回路径：L299的`value`。
- `Requirement.ready`（L302–L311）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`bool`。 返回路径：L303的`bool( self.summary and self.users and self.features and self.acceptance and self.data_scop…`。
- `FieldSpec`（L314–L435）：继承`Contract`。声明的数据项为`name`、`label`、`choice_labels`、`kind`、`required`、`max_length`、`min_length`、`minimum`、`maximum`、`exclusive_minimum`、`exclusive_maximum`、`pattern`、`example`、`choices`、`searchable`、`filterable`、`date_range`；类型约束/数据库列参数以完整定义为准。
- `FieldSpec.field_options`（L361–L378）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L362按`self.min_length > self.max_length`分支；L363抛异常，停止当前正常路径；L364按`self.kind == "enum" and ( not self.choices or len(set(self.choices)) != len(self.choi…`分支；L367抛异常，停止当前正常路径；L368按`self.kind != "enum" and self.choices`分支；L369抛异常，停止当前正常路径；L370按`self.choice_labels and ( self.kind != "enum" or not set(self.choice_labels) <= set(se…`分支；L373抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`len`、`set`、`model_validator`。 返回路径：L378的`self`。
- `FieldSpec.enum_domain`（L381–L388）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L382按`self.kind == "enum" and any( not max(1 if self.required else 0, self.min_length) <= l…`分支；L387抛异常，停止当前正常路径。 调用`any`、`max`、`len`、`value.strip`、`ValueError`、`model_validator`。 返回路径：L388的`self`。
- `FieldSpec.scalar_constraints`（L391–L428）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L393按`any(value is not None for value in bounds)`分支；L394按`self.kind != "integer"`分支；L395抛异常，停止当前正常路径；L406按`low > high`分支；L407抛异常，停止当前正常路径；L408按`self.pattern is not None`分支；L409按`self.kind != "text"`分支；L410抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`any`、`ValueError`、`max`、`min`、`TypeAdapter`、`Field`、`validator.validate_python`、`self.example.strip`、`len`等。 返回路径：L428的`self`。
- `FieldSpec.reserved`（L432–L435）：接收`value`。 控制顺序：L433按`keyword.iskeyword(value) or value in {"id", "owner_id", "created_at", "updated_at"}`分支；L434抛异常，停止当前正常路径。 调用`keyword.iskeyword`、`ValueError`、`field_validator`。 返回路径：L435的`value`。
- `Entity`（L438–L447）：继承`Contract`。声明的数据项为`name`、`description`、`fields`；类型约束/数据库列参数以完整定义为准。
- `Entity.unique_fields`（L444–L447）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L445按`len({f.name for f in self.fields}) != len(self.fields)`分支；L446抛异常，停止当前正常路径。 调用`len`、`ValueError`、`model_validator`。 返回路径：L447的`self`。
- `CustomRule`（L450–L454）：继承`Contract`。声明的数据项为`description`、`entity`、`accept_examples`、`reject_examples`；类型约束/数据库列参数以完整定义为准。
- `Plan`（L457–L513）：继承`Contract`。声明的数据项为`title`、`data_scope`、`entities`、`acceptance`、`custom_rules`、`business`、`unsupported`；类型约束/数据库列参数以完整定义为准。
- `Plan.unique_entities`（L467–L513）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L469按`len(names) != len(self.entities) or ( names & {"users", "tokens", "alembic_version"} …`分支；L473抛异常，停止当前正常路径；L474按`any(rule.entity not in names for rule in self.custom_rules)`分支；L475抛异常，停止当前正常路径；L476遍历`self.custom_rules`；L478遍历`rule.accept_examples + rule.reject_examples`；L479按`set(sample) - {f.name for f in entity.fields}`分支；L480抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`len`、`any`、`n.startswith`、`ValueError`、`next`、`set`、`sample.get`、`type`、`date.fromisoformat`等。 返回路径：L513的`self`。
- `Patch`（L516–L519）：继承`Contract`。声明的数据项为`path`、`before_sha256`、`content`；类型约束/数据库列参数以完整定义为准。
- `Patches`（L522–L524）：继承`Contract`。声明的数据项为`explanation`、`patches`；类型约束/数据库列参数以完整定义为准。
- `safe_component`（L527–L530）：接收`value`。 控制顺序：L528按`not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", value)`分支；L529抛异常，停止当前正常路径。 调用`re.fullmatch`、`ValueError`。 返回路径：L530的`value`。
- `ModelReview`（L533–L536）：继承`Contract`。声明的数据项为`summary`、`observations`、`uncovered_requirements`；类型约束/数据库列参数以完整定义为准。
- `AutomationInput`（L541–L549）：继承`Contract`。声明的数据项为`enabled`、`accepted`；类型约束/数据库列参数以完整定义为准。
- `AutomationInput.consent`（L546–L549）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L547按`self.enabled and not self.accepted`分支；L548抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L549的`self`。

</details>

**创建路径：** `workbench/domain.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L549。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`22283`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/domain.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8f06fa5206ba2c21b98684d05db1119d8c5b1b85bde00d48198341ea350bd7c2"} -->
````python
# workbench/domain.py
"""Typed external contracts. Raw user input cannot choose roles, commands or approval state."""

import hashlib
import json
import keyword
import re
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StrictBool,
    StrictInt,
    StringConstraints,
    TypeAdapter,
    field_validator,
    model_validator,
)
from pydantic_core import SchemaError

from workbench.business_contracts import BusinessSpec

Text = Annotated[str, Field(min_length=1, max_length=20000)]
UserText = Annotated[str, StringConstraints(strip_whitespace=False)]
Name = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")]


def digest(data: object) -> str:
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProjectInput(Contract):
    title: Annotated[str, Field(min_length=1, max_length=200)]


class RunInput(Contract):
    requirement: Annotated[UserText, Field(min_length=1, max_length=20000)]
    template: Literal["python-basic", "fastapiadmin", "yudao-vben"] = "python-basic"
    selection: dict | None = None
    intelligent: StrictBool = False
    allow_custom_extensions: StrictBool = False

    @model_validator(mode="after")
    def validate_selection(self):
        from workbench.catalog import Selection

        chosen = Selection.model_validate(self.selection or {"template": self.template})
        if chosen.template != self.template:
            raise ValueError("选择与模板标识不一致")
        self.selection = chosen.model_dump()
        if not self.requirement.strip():
            raise ValueError("需求不能为空")
        return self


class BatchItem(RunInput):
    title: Annotated[str, Field(min_length=1, max_length=200)]


class BatchInput(Contract):
    """A bounded set of ordinary runs; every item keeps its own approval policy."""

    items: list[BatchItem] = Field(min_length=1, max_length=10)


class ClarificationAnswer(Contract):
    """Explicit selections refer only to the current, reviewed question version."""

    question_id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")]
    option_ids: list[Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")]] = Field(
        default_factory=list, max_length=20
    )
    text: UserText = Field(default="", max_length=10000)

    @model_validator(mode="after")
    def unique_options(self):
        if len(self.option_ids) != len(set(self.option_ids)):
            raise ValueError("同一个选项不能重复提交")
        return self


class ResumeInput(Contract):
    gate_id: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    action: Literal["answer", "approve", "reject", "revise", "recommend", "retry_node"]
    version: int | None = Field(default=None, ge=1)
    digest: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    answers: list[ClarificationAnswer] = Field(default_factory=list, max_length=6)
    text: UserText = Field(default="", max_length=20000)
    approved: StrictBool | None = None

    @model_validator(mode="after")
    def action_matches(self):
        if self.answers and self.action != "answer":
            raise ValueError("选项回答只能用于当前澄清问题")
        if len({answer.question_id for answer in self.answers}) != len(self.answers):
            raise ValueError("同一个问题不能重复提交")
        if self.action in {"answer", "revise"} and not self.text.strip() and not self.answers:
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
                "手动",
                "manual",
                "重试",
                "retry",
                "退出",
                "quit",
                "exit",
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


class RequirementChange(Contract):
    """A proposed correction; the workflow checks the quote against fresh user input."""

    section: Literal[
        "facts",
        "features",
        "acceptance",
        "users",
        "data_scope",
        "field_requirements",
        "entity_requirements",
        "additional_entities",
    ]
    key: str
    replacement: JsonValue = None
    source_quote: Text


class FieldRequirement(Contract):
    """Executable obligations, independent from a planner's implementation choices."""

    field: Name
    entity: Name | None = None
    kind: Literal["text", "integer", "boolean", "date", "datetime", "enum"] | None = None
    required: bool | None = None
    min_length: int | None = Field(default=None, ge=0, le=20000)
    max_length: int | None = Field(default=None, ge=1, le=20000)
    searchable: bool | None = None
    filterable: bool | None = None
    date_range: bool | None = Field(
        default=None,
        description="Only kind=date supports this; datetime must use false. Do not invent date ranges when none were requested.",
    )
    choices: list[str] | None = None
    minimum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    maximum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    exclusive_minimum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    exclusive_maximum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    pattern: str | None = Field(
        default=None, min_length=1, max_length=500, exclude_if=lambda value: value is None
    )


class EntityRequirement(Contract):
    """An explicit field inventory; ordinary inventories remain extensible."""

    entity: Name
    fields: list[Name] = Field(min_length=1, max_length=128)
    additional_fields: StrictBool = Field(
        default=True,
        description="False only when the user explicitly says this entity's field list is exhaustive or forbids additional fields. An ordinary list is open by default.",
    )

    @field_validator("fields")
    @classmethod
    def unique_fields(cls, value):
        if len(set(value)) != len(value):
            raise ValueError("字段清单不能包含重复名称")
        return value


class ClarificationOption(Contract):
    id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")]
    label: Annotated[str, Field(min_length=1, max_length=1000)]
    description: str = Field(default="", max_length=1000)


class ClarificationQuestion(Contract):
    """Optional presentation of a real blocking question, with an open-text escape."""

    id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")]
    prompt: Text
    kind: Literal["single", "multiple", "text"]
    options: list[ClarificationOption] = Field(default_factory=list, max_length=20)
    required: StrictBool = True
    allow_other: StrictBool = True

    @model_validator(mode="after")
    def valid_options(self):
        if self.kind == "text" and self.options:
            raise ValueError("文本问题不能包含选择项")
        if self.kind != "text" and len(self.options) < 2:
            raise ValueError("选择问题至少包含两个不同选项")
        if len({option.id for option in self.options}) != len(self.options):
            raise ValueError("同一个问题的选项标识不能重复")
        if len({option.label for option in self.options}) != len(self.options):
            raise ValueError("同一个问题的选项文字不能重复")
        return self


class Requirement(Contract):
    summary: str = Field(max_length=4000)
    users: list[Text] = Field(max_length=20)
    data_scope: Literal["per_user", "shared", "unknown"]
    features: list[Text] = Field(max_length=40)
    acceptance: list[Text]
    questions: list[Text] = Field(default_factory=list, max_length=6)
    question_items: list[ClarificationQuestion] = Field(default_factory=list, max_length=6)
    assumptions: list[Text] = Field(default_factory=list)
    unsupported: list[Text] = Field(
        default_factory=list,
        description="用户明确要求且仍需实现、但模板无法实现的阻塞项；不是模板全部限制的清单",
    )
    limitations: list[Text] = Field(
        default_factory=list,
        description="本次未要求或已明确排除的模板能力边界；仅说明，不阻塞交付",
    )
    recommendations: list[Text] = Field(default_factory=list)
    facts: dict[str, JsonValue] = Field(default_factory=dict)
    field_requirements: list[FieldRequirement] = Field(default_factory=list, max_length=128)
    entity_requirements: list[EntityRequirement] = Field(default_factory=list, max_length=40)
    additional_entities: StrictBool = Field(
        default=True,
        description="False only when the user explicitly restricts the complete entity inventory to entity_requirements. Ordinary projects stay open.",
    )
    changes: list[RequirementChange] = Field(default_factory=list, max_length=128)

    def gate_dump(self) -> dict:
        # Resuming a pre-upgrade interrupt reruns its node. Do not change the
        # digest of a legacy gate just by adding an empty optional schema field.
        return self.model_dump(
            exclude={
                name
                for name in (
                    "limitations",
                    "field_requirements",
                    "entity_requirements",
                    "changes",
                    "question_items",
                )
                if not getattr(self, name)
            }
            | ({"additional_entities"} if self.additional_entities else set())
        )

    @model_validator(mode="after")
    def question_presentation(self):
        if len({item.id for item in self.question_items}) != len(self.question_items):
            raise ValueError("问题标识不能重复")
        if len({item.prompt for item in self.question_items}) != len(self.question_items):
            raise ValueError("问题文字不能重复")
        if self.question_items and {item.prompt for item in self.question_items} != set(
            self.questions
        ):
            raise ValueError("结构化问题必须逐字完整对应 questions 中的全部真实阻塞问题")
        return self

    @field_validator("entity_requirements")
    @classmethod
    def unique_entity_requirements(cls, value):
        if len({item.entity for item in value}) != len(value):
            raise ValueError("同一实体不能重复声明字段清单")
        return value

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
    label: str = Field(
        default="",
        max_length=100,
        description="Human-readable field label; use the user's interface language without changing the stable name.",
    )
    choice_labels: dict[str, Annotated[str, Field(min_length=1, max_length=100)]] = Field(
        default_factory=dict,
        description="Optional enum stored value to human-readable label. Keys must occur in choices.",
    )
    kind: Literal["text", "integer", "boolean", "date", "datetime", "enum"]
    required: bool = True
    max_length: int = Field(default=200, ge=1, le=20000)
    min_length: int = Field(default=0, ge=0, le=20000)
    minimum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    maximum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    exclusive_minimum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    exclusive_maximum: StrictInt | None = Field(
        default=None, ge=-(2**31), le=2**31 - 1, exclude_if=lambda value: value is None
    )
    pattern: str | None = Field(
        default=None, min_length=1, max_length=500, exclude_if=lambda value: value is None
    )
    example: str | None = Field(
        default=None,
        max_length=20000,
        exclude_if=lambda value: value is None,
        description="A valid text example is required for pattern constraints; independent API/browser checks use it.",
    )
    choices: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(
        default_factory=list, max_length=50
    )
    searchable: bool = False
    filterable: bool = False
    date_range: bool = Field(
        default=False,
        description="Only kind=date supports inclusive date ranges; kind=datetime must set false.",
    )

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
        if self.choice_labels and (
            self.kind != "enum" or not set(self.choice_labels) <= set(self.choices)
        ):
            raise ValueError("choice_labels只能映射已声明的enum选项")
        if self.searchable and self.kind not in {"text", "enum"}:
            raise ValueError("关键词搜索只能使用文本/枚举字段")
        if self.date_range and self.kind != "date":
            raise ValueError("日期范围只支持 date 类型")
        return self

    @model_validator(mode="after")
    def enum_domain(self):
        if self.kind == "enum" and any(
            not max(1 if self.required else 0, self.min_length) <= len(value) <= self.max_length
            or value != value.strip()
            for value in self.choices
        ):
            raise ValueError("全部枚举选项必须满足长度约束且不能含首尾空白")
        return self

    @model_validator(mode="after")
    def scalar_constraints(self):
        bounds = (self.minimum, self.maximum, self.exclusive_minimum, self.exclusive_maximum)
        if any(value is not None for value in bounds):
            if self.kind != "integer":
                raise ValueError("数值边界仅适用于 integer 字段")
            low = max(
                -(2**31),
                self.minimum if self.minimum is not None else -(2**31),
                self.exclusive_minimum + 1 if self.exclusive_minimum is not None else -(2**31),
            )
            high = min(
                2**31 - 1,
                self.maximum if self.maximum is not None else 2**31 - 1,
                self.exclusive_maximum - 1 if self.exclusive_maximum is not None else 2**31 - 1,
            )
            if low > high:
                raise ValueError("整数约束没有可接受的值")
        if self.pattern is not None:
            if self.kind != "text":
                raise ValueError("pattern 仅适用于 text 字段")
            if self.searchable or self.filterable:
                raise ValueError("pattern 与查询组合尚缺可隔离的独立正例，当前不能同时声明")
            try:
                validator = TypeAdapter(Annotated[str, Field(pattern=self.pattern)])
            except SchemaError as exc:
                raise ValueError("pattern 正则表达式无效") from exc
            if self.example is None:
                raise ValueError("pattern 必须提供符合格式的 example，供独立验收使用")
            validator.validate_python(self.example)
        if self.example is not None and (
            self.kind != "text"
            or self.example != self.example.strip()
            or not max(1 if self.required else 0, self.min_length)
            <= len(self.example)
            <= self.max_length
        ):
            raise ValueError("example 必须满足文本字段完整约束")
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
    business: BusinessSpec | None = Field(default=None, exclude_if=lambda value: value is None)
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
                        "datetime": str,
                        "enum": str,
                    }[field.kind]
                    if type(value) is not expected:
                        raise ValueError("规则示例字段类型错误")
                    if field.kind == "date":
                        date.fromisoformat(value)
                    if field.kind == "datetime":
                        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        if parsed.tzinfo is None:
                            raise ValueError("datetime 必须包含时区")
                    if field.kind == "enum" and value not in field.choices:
                        raise ValueError("规则示例不在枚举选项内")
                    if field.kind in {"text", "enum"} and len(value) > field.max_length:
                        raise ValueError("规则示例文本过长")
        if self.business is not None:
            if self.custom_rules:
                raise ValueError(
                    "Business contracts cannot also use standalone custom_rules; express supported behavior in the business contract"
                )
            self.business.validate_plan(self)
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
    # Observations are advisory; uncovered approved requirements block delivery.
    # No model verdict can override a failed executable test.


class AutomationInput(Contract):
    enabled: StrictBool
    accepted: StrictBool

    @model_validator(mode="after")
    def consent(self):
        if self.enabled and not self.accepted:
            raise ValueError("启用智能推荐需要明确接受其后续自动决定语义")
        return self
````
