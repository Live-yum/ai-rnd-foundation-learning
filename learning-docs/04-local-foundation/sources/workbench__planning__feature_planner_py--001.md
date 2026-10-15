# workbench/planning/feature_planner.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business.modules.imports`、`workbench.core.contracts`、`workbench.planning.contracts`、`workbench.settings`、`workbench.templates.adapters`、`workbench.templates.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `RoutedFeature`（L24–L56）：继承`Contract`。声明的数据项为`id`、`title`、`requirements`、`route`、`capability`、`depends_on`、`entity`、`module_id`、`blocker`；类型约束/数据库列参数以完整定义为准。
- `RoutedFeature.route_shape`（L51–L56）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L52按`(self.route == "module") != (self.module_id is not None)`分支；L53抛异常，停止当前正常路径；L54按`(self.route == "blocked") != bool(self.blocker)`分支；L55抛异常，停止当前正常路径。 调用`ValueError`、`bool`、`model_validator`。 返回路径：L56的`self`。
- `PlannedModule`（L59–L79）：继承`CapabilityTask`。声明的数据项为`adapter`、`extension`、`page_patterns`、`interfaces`、`dependency_requests`、`migrations`、`permission_changes`、`import_spec`；类型约束/数据库列参数以完整定义为准。
- `PlannedModule.exact_module_configuration`（L72–L75）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L73按`(self.extension == "batch-import-v1") != (self.import_spec is not None)`分支；L74抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L75的`self`。
- `PlannedModule.requires_explicit_review`（L78–L79）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`bool`。 返回路径：L79的`bool(self.dependency_requests or self.migrations or self.permission_changes)`。
- `PlannedModuleV2`（L82–L89）：继承`PlannedModule, CapabilityTaskV2`。声明的数据项为`version`；类型约束/数据库列参数以完整定义为准。
- `PlannedModuleV2.executor_matches_extension`（L86–L89）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L87按`self.extension != "approved-source-module" and self.executor != "bounded_edit"`分支；L88抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L89的`self`。
- `FeatureOutline`（L92–L132）：继承`Contract`。声明的数据项为`version`、`summary`、`selection`、`source_digest`、`features`、`modules`、`questions`；类型约束/数据库列参数以完整定义为准。
- `FeatureOutline.dependencies`（L102–L132）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L103按`any(module.version != self.version for module in self.modules)`分支；L104抛异常，停止当前正常路径；L106按`len(keys) != len(self.features)`分支；L107抛异常，停止当前正常路径；L108按`any(not set(feature.depends_on) <= keys for feature in self.features)`分支；L109抛异常，停止当前正常路径；L111在`len(done) < len(keys)`成立时循环；L115按`not ready`分支。后续分支沿下方源码相同行号继续阅读。 调用`any`、`ValueError`、`len`、`set`、`done.update`、`finished.update`、`model_validator`。 返回路径：L132的`self`。
- `FeatureDesign`（L135–L144）：继承`Contract`。声明的数据项为`outline`、`baseline`、`implementation`；类型约束/数据库列参数以完整定义为准。
- `FeatureDesign.version_consistency`（L141–L144）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L142按`self.implementation and self.implementation.version != self.outline.version`分支；L143抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L144的`self`。
- `import_files`（L147–L154）：接收`plan`。 返回路径：L148的`[ "backend/app/plugin/module_business/" + name for name in ("controller.py", "import.json"…`。
- `feature_design_errors`（L157–L186）：接收`design`、`scope`、`selected`。 控制顺序：L163遍历`outline.modules`；L164按`module.extension == "batch-import-v1" and set(module.files) != set( import_files(desi…`分支；L168按`module.extension == "batch-import-v1" and not all( (ROOT / "templates/modules/fastapi…`分支；L173按`module.dependency_requests or module.migrations`分支；L175按`bool(outline.modules) != (design.implementation is not None)`分支；L177按`design.implementation`分支；L179按`set(tasks) != {module.id for module in outline.modules}`分支；L181遍历`outline.modules`。后续分支沿下方源码相同行号继续阅读。 调用`route_errors`、`errors.extend`、`baseline_errors`、`set`、`import_files`、`errors.append`、`all`、`(ROOT / "templates/modules/fastapiadmin" / name).is_file`、`bool`等。 返回路径：L186的`list(dict.fromkeys(errors))`。
- `route_errors`（L189–L221）：接收`outline`、`sources`、`selected`、`source_digest`。 控制顺序：L192按`outline.selection.model_dump() != Selection.model_validate(selected).model_dump()`分支；L194按`outline.source_digest != source_digest`分支；L198按`covered != expected`分支；L203遍历`outline.features`；L204按`feature.route == "native" and feature.capability not in native`分支；L206按`feature.route == "declarative" and feature.capability not in business`分支；L208按`feature.route == "module"`分支；L210按`not set(feature.requirements) <= set(module.requirements)`分支。后续分支沿下方源码相同行号继续阅读。 调用`get_adapter(selected["template"]).capabilities`、`get_adapter`、`outline.selection.model_dump`、`Selection.model_validate(selected).model_dump`、`Selection.model_validate`、`errors.append`、`set`、`errors.extend`、`module_path_errors`。 返回路径：L221的`errors`。
- `module_path_errors`（L224–L231）：接收`module`。 源码说明：An approved filename never grants access to trusted product control files.。 调用`get_adapter`、`adapter.allows_module_path`。 返回路径：L227的`[ f"{module.id}的路径不属于适配包允许的业务扩展点：{path}" for path in module.files if not adapter.allows_mo…`。
- `baseline_errors`（L234–L264）：接收`outline`、`baseline`。 控制顺序：L235按`baseline is None`分支；L243按`baseline.unsupported`分支；L245按`any(feature.route == "declarative" for feature in outline.features) and baseline.busi…`分支；L251遍历`outline.modules`；L252按`module.import_spec and module.import_spec.entity not in entities`分支；L254按`module.import_spec and baseline.business is None`分支；L256按`any( feature.entity and feature.entity not in entities for feature in outline.feature…`分支；L262按`outline.selection.template != "python-basic" and baseline.data_scope != "shared"`分支。 调用`any`、`Plan.model_validate`、`errors.append`。 返回路径：L236的`["原生和声明式路由需要单独评审基础业务契约"] if any(feature.route in {"native", "declarative"} for feature in …`；L264的`errors`。
- `planning_payload`（L267–L293）：接收`scope`。 调用`Selection.model_validate`、`selection.capabilities`、`RoutedFeature.model_json_schema`、`selection.model_dump`、`digest`。 返回路径：L271的`{ "source_digest": scope["source_digest"], "source_units": scope["sources"], "selection": …`。

</details>

**创建路径：** `workbench/planning/feature_planner.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L293。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13849`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/planning/feature_planner.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "95367242fa03e17990c73882bc795ae865dce7140946973ce8e9b611b334e447"} -->
````python
# workbench/planning/feature_planner.py
"""Per-feature routing over the selected adapter, separate from graph orchestration.

Coverage references support review; they never constitute implementation proof.
Only executable adapter capabilities can select a deterministic route.
"""

from typing import Literal

from pydantic import Field, model_validator

from workbench.business.modules.imports import ImportModuleSpec
from workbench.core.contracts import ClarificationQuestion, Contract, Plan, digest
from workbench.planning.contracts import (
    CapabilityPlan,
    CapabilityTask,
    CapabilityTaskV2,
    Identifier,
)
from workbench.settings import ROOT
from workbench.templates.adapters import get_adapter
from workbench.templates.catalog import Selection


class RoutedFeature(Contract):
    id: Identifier = Field(
        description="稳定的功能技术标识：以小写英文字母开头，仅含小写英文、数字、下划线或连字符，最多64字符；中文名称写入title。",
        examples=["registration-submit"],
    )
    title: str = Field(min_length=1, max_length=300)
    requirements: list[Identifier] = Field(
        min_length=1,
        max_length=256,
        description="逐字引用本轮source_units中的来源ID，不能自行编造、翻译或改写。",
    )
    route: Literal["native", "declarative", "module", "blocked"]
    capability: str = Field(
        min_length=1,
        max_length=100,
        description="单个能力技术键。native/declarative须逐字选择当前adapter对应features中的一项，不能填写业务说明或拼接多个能力；业务含义写入title，阻塞原因写入blocker。",
    )
    depends_on: list[Identifier] = Field(
        default_factory=list,
        max_length=32,
        description="只引用本轮outline.features中的准确id；修改id时同步修正引用，不能形成循环。",
    )
    entity: str | None = None
    module_id: Identifier | None = None
    blocker: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def route_shape(self):
        if (self.route == "module") != (self.module_id is not None):
            raise ValueError("仅受控模块路由引用准确module_id")
        if (self.route == "blocked") != bool(self.blocker):
            raise ValueError("阻塞路由须明确缺少的环境或授权，其他路由不能隐藏阻塞")
        return self


class PlannedModule(CapabilityTask):
    adapter: Literal["python-basic", "fastapiadmin", "yudao-vben"]
    extension: Literal["batch-import-v1", "approved-source-module"]
    page_patterns: list[Literal["list", "form", "detail", "wizard"]] = Field(
        default_factory=list, max_length=4
    )
    interfaces: list[str] = Field(min_length=1, max_length=20)
    dependency_requests: list[str] = Field(default_factory=list, max_length=8)
    migrations: list[str] = Field(default_factory=list, max_length=8)
    permission_changes: list[str] = Field(default_factory=list, max_length=8)
    import_spec: ImportModuleSpec | None = None

    @model_validator(mode="after")
    def exact_module_configuration(self):
        if (self.extension == "batch-import-v1") != (self.import_spec is not None):
            raise ValueError("批量导入模块必须有准确实体、重复策略和行数配置；其他模块不能混用")
        return self

    @property
    def requires_explicit_review(self):
        return bool(self.dependency_requests or self.migrations or self.permission_changes)


class PlannedModuleV2(PlannedModule, CapabilityTaskV2):
    version: Literal[2] = 2

    @model_validator(mode="after")
    def executor_matches_extension(self):
        if self.extension != "approved-source-module" and self.executor != "bounded_edit":
            raise ValueError("确定性模块安装器不能切换到Agent")
        return self


class FeatureOutline(Contract):
    version: Literal[1, 2] = 1
    summary: str = Field(min_length=1, max_length=4000)
    selection: Selection
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    features: list[RoutedFeature] = Field(min_length=1, max_length=64)
    modules: list[PlannedModuleV2 | PlannedModule] = Field(default_factory=list, max_length=32)
    questions: list[ClarificationQuestion] = Field(default_factory=list, max_length=6)

    @model_validator(mode="after")
    def dependencies(self):
        if any(module.version != self.version for module in self.modules):
            raise ValueError("功能计划与模块合同版本必须一致")
        keys = {feature.id for feature in self.features}
        if len(keys) != len(self.features):
            raise ValueError("功能ID不能重复")
        if any(not set(feature.depends_on) <= keys for feature in self.features):
            raise ValueError("功能依赖必须引用本轮明确功能")
        done = set()
        while len(done) < len(keys):
            ready = {
                feature.id for feature in self.features if set(feature.depends_on) <= done
            } - done
            if not ready:
                raise ValueError("功能依赖不能形成循环")
            done.update(ready)
        module_ids = {module.id for module in self.modules}
        if len(module_ids) != len(self.modules):
            raise ValueError("模块ID不能重复")
        referenced = {feature.module_id for feature in self.features if feature.route == "module"}
        if referenced != module_ids:
            raise ValueError("每个模块必须逐个关联所保留的功能，不能有遗漏或孤立模块")
        finished = set()
        while len(finished) < len(module_ids):
            ready = {
                module.id for module in self.modules if set(module.depends_on) <= finished
            } - finished
            if not ready:
                raise ValueError("模块依赖必须引用本计划模块且不能形成循环")
            finished.update(ready)
        return self


class FeatureDesign(Contract):
    outline: FeatureOutline
    baseline: Plan
    implementation: CapabilityPlan | None = None

    @model_validator(mode="after")
    def version_consistency(self):
        if self.implementation and self.implementation.version != self.outline.version:
            raise ValueError("功能设计与执行计划版本不一致")
        return self


def import_files(plan):
    return [
        "backend/app/plugin/module_business/" + name
        for name in ("controller.py", "import.json", "import_runtime.py", "import_routes.py")
    ] + [
        "frontend/web/src/components/business/ImportWizard.vue",
        *(f"frontend/web/src/views/module_rnd/{e.name}/index.vue" for e in plan.entities),
    ]


def feature_design_errors(design, scope, selected):
    outline = design.outline
    errors = route_errors(outline, scope["sources"], selected, scope["source_digest"])
    errors.extend(baseline_errors(outline, design.baseline))
    errors.extend(feature.blocker for feature in outline.features if feature.route == "blocked")
    errors.extend(question.prompt for question in outline.questions)
    for module in outline.modules:
        if module.extension == "batch-import-v1" and set(module.files) != set(
            import_files(design.baseline)
        ):
            errors.append("批导模块必须准确审阅确定性安装器修改的全部业务文件")
        if module.extension == "batch-import-v1" and not all(
            (ROOT / "templates/modules/fastapiadmin" / name).is_file()
            for name in ("import_runtime.py", "import_routes.py", "ImportWizard.vue")
        ):
            errors.append("batch-import-v1缺少实际运行时与页面模板，当前不能生成或验收")
        if module.dependency_requests or module.migrations:
            errors.append("当前混合流程不支持新增依赖或既有数据迁移")
    if bool(outline.modules) != (design.implementation is not None):
        errors.append("模块必须有独立CapabilityPlan验收；基础功能不能伪造源码任务")
    if design.implementation:
        tasks = {task.id: task for task in design.implementation.tasks}
        if set(tasks) != {module.id for module in outline.modules}:
            errors.append("验收任务必须与分派模块逐个对应")
        for module in outline.modules:
            if module.id in tasks and tasks[module.id].model_dump() != module.model_dump(
                include=set(type(tasks[module.id]).model_fields)
            ):
                errors.append("模块任务与批准功能分派的文件、场景及契约不一致")
    return list(dict.fromkeys(errors))


def route_errors(outline, sources, selected, source_digest):
    adapter = get_adapter(selected["template"]).capabilities()
    errors = []
    if outline.selection.model_dump() != Selection.model_validate(selected).model_dump():
        errors.append("功能分派改变了已选语言、框架、前端或数据库")
    if outline.source_digest != source_digest:
        errors.append("功能分派未绑定当前原始需求版本")
    expected = {source["id"] for source in sources}
    covered = {ref for feature in outline.features for ref in feature.requirements}
    if covered != expected:
        errors.append("全部原始来源必须保留在明确功能中，不能只给总体摘要")
    native = set(adapter["capability_layers"]["native_generator"]["features"])
    business = set(adapter["capability_layers"]["declarative_business"]["features"])
    modules = {module.id: module for module in outline.modules}
    for feature in outline.features:
        if feature.route == "native" and feature.capability not in native:
            errors.append(f"{feature.id}不是当前确定性生成器能力")
        if feature.route == "declarative" and feature.capability not in business:
            errors.append(f"{feature.id}不是当前声明式业务能力")
        if feature.route == "module":
            module = modules[feature.module_id]
            if not set(feature.requirements) <= set(module.requirements):
                errors.append(f"{feature.id}未由对应模块覆盖全部来源")
    for module in outline.modules:
        if module.adapter != outline.selection.template:
            errors.append(f"{module.id}更换了模板适配包")
        if not set(module.requirements) <= expected:
            errors.append(f"{module.id}引用了不存在的来源")
        if module.extension == "batch-import-v1" and module.adapter != "fastapiadmin":
            errors.append("批导适配器尚未在该原生栈实现，保留为待实现模块，不能冒充已接入")
        if module.extension == "approved-source-module":
            errors.extend(module_path_errors(module))
    return errors


def module_path_errors(module):
    """An approved filename never grants access to trusted product control files."""
    adapter = get_adapter(module.adapter)
    return [
        f"{module.id}的路径不属于适配包允许的业务扩展点：{path}"
        for path in module.files
        if not adapter.allows_module_path(path)
    ]


def baseline_errors(outline, baseline):
    if baseline is None:
        return (
            ["原生和声明式路由需要单独评审基础业务契约"]
            if any(feature.route in {"native", "declarative"} for feature in outline.features)
            else []
        )
    baseline = Plan.model_validate(baseline)
    errors = []
    if baseline.unsupported:
        errors.append("基础契约不能丢弃已分派到模块或外部前提的功能")
    if (
        any(feature.route == "declarative" for feature in outline.features)
        and baseline.business is None
    ):
        errors.append("声明式功能必须有实际Plan.business契约")
    entities = {entity.name for entity in baseline.entities}
    for module in outline.modules:
        if module.import_spec and module.import_spec.entity not in entities:
            errors.append(f"{module.id}的批导实体未在基础模型中定义")
        if module.import_spec and baseline.business is None:
            errors.append("原生批导需要明确角色和动作的基础business契约")
    if any(
        feature.entity and feature.entity not in entities
        for feature in outline.features
        if feature.route in {"native", "declarative"}
    ):
        errors.append("基础功能引用的实体不在批准的基础模型中")
    if outline.selection.template != "python-basic" and baseline.data_scope != "shared":
        errors.append("原生模板保留shared模式，使用明确own/assigned/all行权限")
    return errors


def planning_payload(scope):
    selection = Selection.model_validate(scope["selection"])
    adapter = selection.capabilities()
    fields = RoutedFeature.model_json_schema()["properties"]
    return {
        "source_digest": scope["source_digest"],
        "source_units": scope["sources"],
        "selection": selection.model_dump(),
        "adapter": adapter,
        "rules": {
            "routes": ["native", "declarative", "module", "blocked"],
            "route_is_not_verification": True,
            "native_stack_and_ui_must_remain": True,
            "baseline_contract_is_separate": True,
            "scope_review_digest": digest(scope["sources"]),
            "feature_id": {
                "pattern": fields["id"]["pattern"],
                "examples": fields["id"]["examples"],
                "description": fields["id"]["description"],
            },
            "capability_choices": {
                "native": adapter["capability_layers"]["native_generator"]["features"],
                "declarative": adapter["capability_layers"]["declarative_business"]["features"],
            },
            "capability_description": fields["capability"]["description"],
        },
    }
````
