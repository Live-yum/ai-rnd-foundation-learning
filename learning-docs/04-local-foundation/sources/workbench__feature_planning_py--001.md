# workbench/feature_planning.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.catalog`、`workbench.domain`、`workbench.module_imports`、`workbench.settings`、`workbench.template_adapters`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `RoutedFeature`（L19–L51）：继承`Contract`。声明的数据项为`id`、`title`、`requirements`、`route`、`capability`、`depends_on`、`entity`、`module_id`、`blocker`；类型约束/数据库列参数以完整定义为准。
- `RoutedFeature.route_shape`（L46–L51）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L47按`(self.route == "module") != (self.module_id is not None)`分支；L48抛异常，停止当前正常路径；L49按`(self.route == "blocked") != bool(self.blocker)`分支；L50抛异常，停止当前正常路径。 调用`ValueError`、`bool`、`model_validator`。 返回路径：L51的`self`。
- `PlannedModule`（L54–L74）：继承`CapabilityTask`。声明的数据项为`adapter`、`extension`、`page_patterns`、`interfaces`、`dependency_requests`、`migrations`、`permission_changes`、`import_spec`；类型约束/数据库列参数以完整定义为准。
- `PlannedModule.exact_module_configuration`（L67–L70）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L68按`(self.extension == "batch-import-v1") != (self.import_spec is not None)`分支；L69抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L70的`self`。
- `PlannedModule.requires_explicit_review`（L73–L74）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`bool`。 返回路径：L74的`bool(self.dependency_requests or self.migrations or self.permission_changes)`。
- `FeatureOutline`（L77–L115）：继承`Contract`。声明的数据项为`version`、`summary`、`selection`、`source_digest`、`features`、`modules`、`questions`；类型约束/数据库列参数以完整定义为准。
- `FeatureOutline.dependencies`（L87–L115）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L89按`len(keys) != len(self.features)`分支；L90抛异常，停止当前正常路径；L91按`any(not set(feature.depends_on) <= keys for feature in self.features)`分支；L92抛异常，停止当前正常路径；L94在`len(done) < len(keys)`成立时循环；L98按`not ready`分支；L99抛异常，停止当前正常路径；L102按`len(module_ids) != len(self.modules)`分支。后续分支沿下方源码相同行号继续阅读。 调用`len`、`ValueError`、`any`、`set`、`done.update`、`finished.update`、`model_validator`。 返回路径：L115的`self`。
- `FeatureDesign`（L118–L121）：继承`Contract`。声明的数据项为`outline`、`baseline`、`implementation`；类型约束/数据库列参数以完整定义为准。
- `import_files`（L124–L131）：接收`plan`。 返回路径：L125的`[ "backend/app/plugin/module_business/" + name for name in ("controller.py", "import.json"…`。
- `feature_design_errors`（L134–L163）：接收`design`、`scope`、`selected`。 控制顺序：L140遍历`outline.modules`；L141按`module.extension == "batch-import-v1" and set(module.files) != set( import_files(desi…`分支；L145按`module.extension == "batch-import-v1" and not all( (ROOT / "templates/modules/fastapi…`分支；L150按`module.dependency_requests or module.migrations`分支；L152按`bool(outline.modules) != (design.implementation is not None)`分支；L154按`design.implementation`分支；L156按`set(tasks) != {module.id for module in outline.modules}`分支；L158遍历`outline.modules`。后续分支沿下方源码相同行号继续阅读。 调用`route_errors`、`errors.extend`、`baseline_errors`、`set`、`import_files`、`errors.append`、`all`、`(ROOT / "templates/modules/fastapiadmin" / name).is_file`、`bool`等。 返回路径：L163的`list(dict.fromkeys(errors))`。
- `route_errors`（L166–L198）：接收`outline`、`sources`、`selected`、`source_digest`。 控制顺序：L169按`outline.selection.model_dump() != Selection.model_validate(selected).model_dump()`分支；L171按`outline.source_digest != source_digest`分支；L175按`covered != expected`分支；L180遍历`outline.features`；L181按`feature.route == "native" and feature.capability not in native`分支；L183按`feature.route == "declarative" and feature.capability not in business`分支；L185按`feature.route == "module"`分支；L187按`not set(feature.requirements) <= set(module.requirements)`分支。后续分支沿下方源码相同行号继续阅读。 调用`get_adapter(selected["template"]).capabilities`、`get_adapter`、`outline.selection.model_dump`、`Selection.model_validate(selected).model_dump`、`Selection.model_validate`、`errors.append`、`set`、`errors.extend`、`module_path_errors`。 返回路径：L198的`errors`。
- `module_path_errors`（L201–L208）：接收`module`。 源码说明：An approved filename never grants access to trusted product control files.。 调用`get_adapter`、`adapter.allows_module_path`。 返回路径：L204的`[ f"{module.id}的路径不属于适配包允许的业务扩展点：{path}" for path in module.files if not adapter.allows_mo…`。
- `baseline_errors`（L211–L241）：接收`outline`、`baseline`。 控制顺序：L212按`baseline is None`分支；L220按`baseline.unsupported`分支；L222按`any(feature.route == "declarative" for feature in outline.features) and baseline.busi…`分支；L228遍历`outline.modules`；L229按`module.import_spec and module.import_spec.entity not in entities`分支；L231按`module.import_spec and baseline.business is None`分支；L233按`any( feature.entity and feature.entity not in entities for feature in outline.feature…`分支；L239按`outline.selection.template != "python-basic" and baseline.data_scope != "shared"`分支。 调用`any`、`Plan.model_validate`、`errors.append`。 返回路径：L213的`["原生和声明式路由需要单独评审基础业务契约"] if any(feature.route in {"native", "declarative"} for feature in …`；L241的`errors`。
- `planning_payload`（L244–L270）：接收`scope`。 调用`Selection.model_validate`、`selection.capabilities`、`RoutedFeature.model_json_schema`、`selection.model_dump`、`digest`。 返回路径：L248的`{ "source_digest": scope["source_digest"], "source_units": scope["sources"], "selection": …`。

</details>

**创建路径：** `workbench/feature_planning.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L270。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12995`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/feature_planning.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d3d225346437c389ec76b41be8cc4f5b670fb4038545468507cc3508ca023851"} -->
````python
# workbench/feature_planning.py
"""Per-feature routing over the selected adapter, separate from graph orchestration.

Coverage references support review; they never constitute implementation proof.
Only executable adapter capabilities can select a deterministic route.
"""

from typing import Literal

from pydantic import Field, model_validator

from workbench.capability_contracts import CapabilityPlan, CapabilityTask, Identifier
from workbench.catalog import Selection
from workbench.domain import ClarificationQuestion, Contract, Plan, digest
from workbench.module_imports import ImportModuleSpec
from workbench.settings import ROOT
from workbench.template_adapters import get_adapter


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


class FeatureOutline(Contract):
    version: Literal[1] = 1
    summary: str = Field(min_length=1, max_length=4000)
    selection: Selection
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    features: list[RoutedFeature] = Field(min_length=1, max_length=64)
    modules: list[PlannedModule] = Field(default_factory=list, max_length=32)
    questions: list[ClarificationQuestion] = Field(default_factory=list, max_length=6)

    @model_validator(mode="after")
    def dependencies(self):
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
                include=set(CapabilityTask.model_fields)
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
