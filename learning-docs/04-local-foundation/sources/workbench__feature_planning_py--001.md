# workbench/feature_planning.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.catalog`、`workbench.domain`、`workbench.module_imports`、`workbench.template_adapters`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `RoutedFeature`（L19–L36）：继承`Contract`。声明的数据项为`id`、`title`、`requirements`、`route`、`capability`、`depends_on`、`entity`、`module_id`、`blocker`；类型约束/数据库列参数以完整定义为准。
- `RoutedFeature.route_shape`（L31–L36）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L32按`(self.route == "module") != (self.module_id is not None)`分支；L33抛异常，停止当前正常路径；L34按`(self.route == "blocked") != bool(self.blocker)`分支；L35抛异常，停止当前正常路径。 调用`ValueError`、`bool`、`model_validator`。 返回路径：L36的`self`。
- `PlannedModule`（L39–L59）：继承`CapabilityTask`。声明的数据项为`adapter`、`extension`、`page_patterns`、`interfaces`、`dependency_requests`、`migrations`、`permission_changes`、`import_spec`；类型约束/数据库列参数以完整定义为准。
- `PlannedModule.exact_module_configuration`（L52–L55）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L53按`(self.extension == "batch-import-v1") != (self.import_spec is not None)`分支；L54抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。 返回路径：L55的`self`。
- `PlannedModule.requires_explicit_review`（L58–L59）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`bool`。 返回路径：L59的`bool(self.dependency_requests or self.migrations or self.permission_changes)`。
- `FeatureOutline`（L62–L100）：继承`Contract`。声明的数据项为`version`、`summary`、`selection`、`source_digest`、`features`、`modules`、`questions`；类型约束/数据库列参数以完整定义为准。
- `FeatureOutline.dependencies`（L72–L100）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L74按`len(keys) != len(self.features)`分支；L75抛异常，停止当前正常路径；L76按`any(not set(feature.depends_on) <= keys for feature in self.features)`分支；L77抛异常，停止当前正常路径；L79在`len(done) < len(keys)`成立时循环；L83按`not ready`分支；L84抛异常，停止当前正常路径；L87按`len(module_ids) != len(self.modules)`分支。后续分支沿下方源码相同行号继续阅读。 调用`len`、`ValueError`、`any`、`set`、`done.update`、`finished.update`、`model_validator`。 返回路径：L100的`self`。
- `route_errors`（L103–L135）：接收`outline`、`sources`、`selected`、`source_digest`。 控制顺序：L106按`outline.selection.model_dump() != Selection.model_validate(selected).model_dump()`分支；L108按`outline.source_digest != source_digest`分支；L112按`covered != expected`分支；L117遍历`outline.features`；L118按`feature.route == "native" and feature.capability not in native`分支；L120按`feature.route == "declarative" and feature.capability not in business`分支；L122按`feature.route == "module"`分支；L124按`not set(feature.requirements) <= set(module.requirements)`分支。后续分支沿下方源码相同行号继续阅读。 调用`get_adapter(selected["template"]).capabilities`、`get_adapter`、`outline.selection.model_dump`、`Selection.model_validate(selected).model_dump`、`Selection.model_validate`、`errors.append`、`set`、`errors.extend`、`module_path_errors`。 返回路径：L135的`errors`。
- `module_path_errors`（L138–L181）：接收`module`。 源码说明：An approved filename never grants access to trusted product control files.。 控制顺序：L144遍历`module.files`；L160按`module.adapter == "fastapiadmin"`分支；L170按`module.adapter == "yudao-vben"`分支；L179按`blocked`分支。 调用`get_adapter(module.adapter).ui_contract`、`get_adapter`、`ui.get`、`PurePosixPath`、`path.startswith`、`name.startswith`、`any`、`p.endswith`、`errors.append`。 返回路径：L181的`errors`。
- `baseline_errors`（L184–L214）：接收`outline`、`baseline`。 控制顺序：L185按`baseline is None`分支；L193按`baseline.unsupported`分支；L195按`any(feature.route == "declarative" for feature in outline.features) and baseline.busi…`分支；L201遍历`outline.modules`；L202按`module.import_spec and module.import_spec.entity not in entities`分支；L204按`module.import_spec and baseline.business is None`分支；L206按`any( feature.entity and feature.entity not in entities for feature in outline.feature…`分支；L212按`outline.selection.template != "python-basic" and baseline.data_scope != "shared"`分支。 调用`any`、`Plan.model_validate`、`errors.append`。 返回路径：L186的`["原生和声明式路由需要单独评审基础业务契约"] if any(feature.route in {"native", "declarative"} for feature in …`；L214的`errors`。
- `planning_payload`（L217–L231）：接收`scope`。 调用`Selection.model_validate`、`selection.model_dump`、`selection.capabilities`、`digest`。 返回路径：L219的`{ "source_digest": scope["source_digest"], "source_units": scope["sources"], "selection": …`。

</details>

**创建路径：** `workbench/feature_planning.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L231。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10682`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/feature_planning.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0c3c5221a588e1a231a65f41a26c37b22109db8778079188358c297596d99cce"} -->
````python
# workbench/feature_planning.py
"""Per-feature routing over the selected adapter, separate from graph orchestration.

Coverage references support review; they never constitute implementation proof.
Only executable adapter capabilities can select a deterministic route.
"""

from pathlib import PurePosixPath
from typing import Literal

from pydantic import Field, model_validator

from workbench.capability_contracts import CapabilityTask, Identifier
from workbench.catalog import Selection
from workbench.domain import ClarificationQuestion, Contract, Plan, digest
from workbench.module_imports import ImportModuleSpec
from workbench.template_adapters import get_adapter


class RoutedFeature(Contract):
    id: Identifier
    title: str = Field(min_length=1, max_length=300)
    requirements: list[Identifier] = Field(min_length=1, max_length=256)
    route: Literal["native", "declarative", "module", "blocked"]
    capability: str = Field(min_length=1, max_length=100)
    depends_on: list[Identifier] = Field(default_factory=list, max_length=32)
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
    errors = []
    ui = get_adapter(module.adapter).ui_contract()
    prefix = "frontend/web/" if module.adapter == "fastapiadmin" else "frontend-product/"
    protected = [prefix + path for path in ui.get("protected_paths", [])]
    for path in module.files:
        name = PurePosixPath(path).name
        blocked = (
            path.startswith(("deployment/", ".", "backend/app/core/", "backend/app/config/"))
            or name
            in {
                "uv.lock",
                "pnpm-lock.yaml",
                "package-lock.json",
                "pyproject.toml",
                "package.json",
                "pom.xml",
            }
            or name.startswith(("verify", "RND-"))
            or any(path == p or (p.endswith("/") and path.startswith(p)) for p in protected)
        )
        if module.adapter == "fastapiadmin":
            blocked |= not path.startswith(
                (
                    "backend/app/plugin/",
                    "backend/tests/",
                    "frontend/web/src/views/",
                    "frontend/web/src/components/",
                    "frontend/web/src/api/",
                )
            )
        if module.adapter == "yudao-vben":
            blocked |= not path.startswith(
                (
                    "backend/yudao-module-infra/src/main/java/",
                    "backend/yudao-module-infra/src/test/java/",
                    "frontend-product/apps/web-antd/src/views/",
                    "frontend-product/apps/web-antd/src/api/",
                )
            )
        if blocked:
            errors.append(f"{module.id}的路径不属于适配包允许的业务扩展点：{path}")
    return errors


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
    return {
        "source_digest": scope["source_digest"],
        "source_units": scope["sources"],
        "selection": selection.model_dump(),
        "adapter": selection.capabilities(),
        "rules": {
            "routes": ["native", "declarative", "module", "blocked"],
            "route_is_not_verification": True,
            "native_stack_and_ui_must_remain": True,
            "baseline_contract_is_separate": True,
            "scope_review_digest": digest(scope["sources"]),
        },
    }
````
