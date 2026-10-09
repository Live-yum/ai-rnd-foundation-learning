# workbench/template_adapters.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：技术栈选择与后续交付共用的模板合同。** Selection在导入catalog时就读取固定适配器，所以本模块必须在第01站与catalog一同写入。基础组合校验不启动生成器、浏览器或原生服务；源码锁、UI和运行证据在后续阶段分别核验，静态能力声明不能替代验收。

**对应关系：** catalog.Selection → get_adapter及validate_selection → 后续feature规划、所选栈生成与独立交付。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.template_standards`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `PageContract`（L18–L23）：继承`object`。声明的数据项为`path`、`components`、`imports`、`business_components`、`business_only`；类型约束/数据库列参数以完整定义为准。
- `FrontendContract`（L27–L49）：继承`object`。声明的数据项为`family`、`source_root`、`product_root`、`request`、`api_prefix`、`response_envelope`、`protected`、`pages`；类型约束/数据库列参数以完整定义为准。
- `FrontendContract.page_contracts`（L37–L49）：接收`entities`、`business`。 源码说明：Expand stack data; shared pages occur once and entity names stay stable.。 控制顺序：L41遍历`self.pages`；L42按`page.business_only and not business`分支；L45遍历`names`。 调用`tuple`、`page.path.format`、`entity.replace`、`list`。 返回路径：L49的`required`。
- `TemplateAdapter`（L53–L267）：继承`object`。声明的数据项为`template`、`name`、`backend`、`frontends`、`databases`、`scope`、`features`、`field_kinds`、`languages`、`runtimes`、`package_managers`、`generator`、`verifier`、`ui`、`extension_roots`；类型约束/数据库列参数以完整定义为准。
- `TemplateAdapter.validate_selection`（L70–L76）：接收`backend`、`frontend`、`database`。 控制顺序：L71按`backend != self.backend or frontend not in self.frontends or database not in self.dat…`分支；L76抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `TemplateAdapter.selection_spec`（L78–L89）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`list`、`self.blocked_features`、`self.coding_standard`。 返回路径：L79的`{ "backend": self.backend, "frontends": list(self.frontends), "databases": list(self.datab…`。
- `TemplateAdapter.blocked_features`（L91–L99）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L92的`[ "public-anonymous-site", "external-payments", "web-scraping", "arbitrary-code-execution"…`。
- `TemplateAdapter.source_pins`（L101–L122）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L102按`self.template == "python-basic"`分支。 调用`sha256((ROOT / path).read_bytes()).hexdigest`、`sha256`、`(ROOT / path).read_bytes`、`json.loads`、`(ROOT / "templates/vendor/manifest.json").read_text`。 返回路径：L106的`[ { "slot": "product", "origin": "platform-repository", "revision": "platform-head", "lice…`；L118的`[ {key: row[key] for key in ("slot", "url", "sha", "license", "archive_sha256")} for row i…`。
- `TemplateAdapter.ui_contract`（L124–L142）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.ui.page_contracts`、`bool`、`sorted`、`pages.values`、`list`。 返回路径：L127的`{ "family": self.ui.family, "source_root": self.ui.source_root, "product_root": self.ui.pr…`。
- `TemplateAdapter.allows_module_path`（L144–L169）：接收`path`。 源码说明：The same extension boundary is exposed to the planner and enforced on edits.。 调用`PurePosixPath`、`parsed.is_absolute`、`path.startswith`、`name.startswith`、`any`、`p.endswith`。 返回路径：L149的`not ( parsed.is_absolute() or ".." in parsed.parts or "\\" in path or path.startswith(("de…`。
- `TemplateAdapter.coding_standard`（L171–L172）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`coding_standard`。 返回路径：L172的`coding_standard(self.template)`。
- `TemplateAdapter.capabilities`（L174–L267）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`deepcopy`、`self.source_pins`、`self.selection_spec`、`list`、`sorted`、`self.ui_contract`、`self.blocked_features`。 返回路径：L180的`{ **self.selection_spec(), "id": self.template, "template": self.template, "catalog_versio…`。
- `get_adapter`（L421–L425）：接收`template`。 控制顺序：L425抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L423的`_ADAPTERS[template]`。
- `template_ids`（L428–L429）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`tuple`。 返回路径：L429的`tuple(_ADAPTERS)`。
- `template_catalog`（L432–L433）：接收`template`。 调用`get_adapter(template).capabilities`、`get_adapter`。 返回路径：L433的`get_adapter(template).capabilities()`。

</details>

**创建路径：** `workbench/template_adapters.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L433。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17235`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/template_adapters.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "84d2925b6500a5fd258059c69c3c2a478857f8cf4a177c2ae3669594e96dcc4e"} -->
````python
# workbench/template_adapters.py
"""One executable template contract for selection, discovery and delivery planning.

Static support is not a configuration check or an acceptance receipt. Custom
source is a candidate until the selected stack and independent checks prove it.
"""

import json
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePosixPath

from workbench.settings import ROOT
from workbench.template_standards import coding_standard


@dataclass(frozen=True)
class PageContract:
    path: str
    components: tuple[str, ...]
    imports: tuple[str, ...] = ()
    business_components: tuple[str, ...] = ()
    business_only: bool = False


@dataclass(frozen=True)
class FrontendContract:
    family: str
    source_root: str
    product_root: str
    request: str
    api_prefix: str
    response_envelope: str
    protected: tuple[str, ...] = ()
    pages: tuple[PageContract, ...] = ()

    def page_contracts(self, entities, business=False):
        """Expand stack data; shared pages occur once and entity names stay stable."""
        entities = tuple(entities)
        required = {}
        for page in self.pages:
            if page.business_only and not business:
                continue
            names = entities if "{" in page.path else ("",)
            for entity in names:
                path = page.path.format(entity=entity, compact_entity=entity.replace("_", ""))
                components = {*page.components, *(page.business_components if business else ())}
                required[path] = (components, list(page.imports))
        return required


@dataclass(frozen=True)
class TemplateAdapter:
    template: str
    name: str
    backend: str
    frontends: tuple[str, ...]
    databases: tuple[str, ...]
    scope: str
    features: tuple[str, ...]
    field_kinds: tuple[str, ...]
    languages: tuple[str, ...]
    runtimes: tuple[str, ...]
    package_managers: tuple[str, ...]
    generator: str
    verifier: str
    ui: FrontendContract
    extension_roots: tuple[str, ...] = ()

    def validate_selection(self, backend, frontend, database):
        if (
            backend != self.backend
            or frontend not in self.frontends
            or database not in self.databases
        ):
            raise ValueError("前后端与数据库组合不兼容；从模板目录中选择已验证的组合")

    def selection_spec(self):
        return {
            "backend": self.backend,
            "frontends": list(self.frontends),
            "databases": list(self.databases),
            "name": self.name,
            "scope": self.scope,
            "features": list(self.features),
            "field_kinds": list(self.field_kinds),
            "not_supported": self.blocked_features(),
            "coding_standard": self.coding_standard(),
        }

    def blocked_features(self):
        return [
            "public-anonymous-site",
            "external-payments",
            "web-scraping",
            "arbitrary-code-execution",
            "arbitrary-cross-entity-transactions",
            *(["standalone-per-user-template-mode"] if self.scope == "shared" else []),
        ]

    def source_pins(self):
        if self.template == "python-basic":
            # This template has no separately versioned upstream repository. Its
            # source and dependency locks belong to the executing platform commit.
            paths = ["templates/product/pyproject.toml", "templates/product/uv.lock"]
            return [
                {
                    "slot": "product",
                    "origin": "platform-repository",
                    "revision": "platform-head",
                    "license": "not-declared",
                    "lock_sha256": {
                        path: sha256((ROOT / path).read_bytes()).hexdigest() for path in paths
                    },
                }
            ]
        manifest = json.loads((ROOT / "templates/vendor/manifest.json").read_text(encoding="utf-8"))
        return [
            {key: row[key] for key in ("slot", "url", "sha", "license", "archive_sha256")}
            for row in manifest["sources"]
            if row["template"] == self.template
        ]

    def ui_contract(self):
        pages = self.ui.page_contracts(["record"], business=True)
        native = bool(self.ui.protected)
        return {
            "family": self.ui.family,
            "source_root": self.ui.source_root,
            "product_root": self.ui.product_root,
            "request": self.ui.request,
            "api_prefix": self.ui.api_prefix,
            "response_envelope": self.ui.response_envelope,
            "components": sorted({name for names, _ in pages.values() for name in names}),
            "imports": sorted({name for _, imports in pages.values() for name in imports}),
            "protected_paths": list(self.ui.protected),
            "preserve_native_shell": native,
            "api_only_available": "api-only" in self.frontends,
            "verification": "workbench.native_style.verify_native_style"
            if native
            else "workbench.verification.require_browser_evidence",
        }

    def allows_module_path(self, path):
        """The same extension boundary is exposed to the planner and enforced on edits."""
        parsed = PurePosixPath(path)
        name = parsed.name
        protected = [self.ui.product_root + "/" + value for value in self.ui.protected]
        return not (
            parsed.is_absolute()
            or ".." in parsed.parts
            or "\\" in path
            or path.startswith(("deployment/", ".", "backend/app/core/", "backend/app/config/"))
            or name
            in {
                "uv.lock",
                "pnpm-lock.yaml",
                "package-lock.json",
                "pyproject.toml",
                "package.json",
                "pom.xml",
                "AGENTS.md",
                "VIBECODING.md",
                "template-standard.json",
            }
            or name.startswith(("verify", "RND-"))
            or any(path == p or (p.endswith("/") and path.startswith(p)) for p in protected)
            or (self.extension_roots and not path.startswith(self.extension_roots))
        )

    def coding_standard(self):
        return coding_standard(self.template)

    def capabilities(self):
        from workbench.business_capabilities import BUSINESS

        business = deepcopy(BUSINESS)
        native = self.template != "python-basic"
        sources = self.source_pins()
        return {
            **self.selection_spec(),
            "id": self.template,
            "template": self.template,
            "catalog_version": 1,
            "stack": {
                "languages": list(self.languages),
                "runtimes": list(self.runtimes),
                "package_managers": list(self.package_managers),
                "sources": sources,
                "licenses": sorted({row["license"] for row in sources}),
                "database_compatibility": list(self.databases),
                "services": ["PostgreSQL 17", "Redis 7.4"] if native else [],
                "lock_policy": "use bundled dependency locks; do not select latest versions",
            },
            "ui_contract": self.ui_contract(),
            "extension_roots": list(self.extension_roots),
            "capability_layers": {
                "native_generator": {
                    "available": True,
                    "uses_upstream_generator": native,
                    "kind": "upstream-native-generator" if native else "reviewed-golden-template",
                    "entrypoint": self.generator,
                    "features": list(self.features),
                    "field_kinds": list(self.field_kinds),
                },
                "declarative_business": {
                    "available": True,
                    "requires": "approved Plan.business contract",
                    **deepcopy(business),
                },
                "custom_extension": {
                    "status": "candidate-only",
                    "available": False,
                    "preverified_features": [],
                    "reviewed_modules": [],
                    "module_blockers": {
                        "batch-import-v1": "runtime and UI templates are absent; installation is not executable"
                    },
                    "selection": "RunInput.allow_custom_extensions; approval and evidence remain required",
                    "requires": [
                        "explicit user approval of scope and source plan",
                        "implemented selected-template adapter and native UI integration",
                        "trusted isolated executor and prepared offline dependencies",
                        "independent per-node and aggregate HTTP/browser/database/restart evidence",
                    ],
                    "note": "自定义功能须先实现并逐项验收；安装SDK、创建候选或配置服务不代表能力可交付",
                },
                "blocked": {
                    "features": self.blocked_features(),
                    "scope": "built-in generator and declarative business contract",
                    "note": "模板外需求保留为待实现能力或外部前提，不得静默删减或标记通过",
                },
            },
            "verification_contract": {
                "entrypoint": self.verifier,
                "runtime_verified": False,
                "configuration_is_not_acceptance": True,
                "requires": [
                    "approved-spec digest",
                    "unchanged source manifest",
                    "real HTTP and selected frontend checks",
                    "physical database and restart persistence",
                    "independent fresh-database delivery verification",
                    *(["pinned native sources and unchanged native UI shell"] if native else []),
                ],
            },
            "date_range_inclusive": True,
            "scopes": [self.scope, *(["shared"] if self.scope == "per_user" else [])],
            "business_contract": business,
            "record_authorization": {
                "scopes": ["all", "own", "assigned"],
                "requires": "explicit Plan.business permissions per role and resource",
                "note": "shared模板仍支持本人/分配记录行权限；团队共享须明确成员关系和允许动作，不能等同单owner隔离",
            },
            "registration_modes": {
                "authenticated_business_ui": True,
                "anonymous_submission": False,
                "custom_public_portal": False,
                "note": "参赛者可使用已生成业务界面登录后提交，须声明非管理员角色和逐角色行权限；独立公众门户与匿名提交不在当前交付能力内",
            },
            "defaults": {
                "title_max_length": 250,
                "body_max_length": 3000,
                "date_format": "YYYY-MM-DD",
                "category_required": False,
            },
        }


_ADAPTERS = {
    "python-basic": TemplateAdapter(
        "python-basic",
        "FastAPI + 轻量管理页面",
        "fastapi",
        ("simple-admin", "api-only"),
        ("sqlite", "postgresql"),
        "per_user",
        (
            "typed-crud",
            "authentication",
            "user-isolation",
            "keyword-search",
            "exact-filter",
            "date-range",
            "enum",
            "field-length",
            "single-record-rules",
        ),
        ("text", "integer", "boolean", "date", "enum"),
        ("Python", "JavaScript", "HTML", "CSS"),
        ("Python 3.14",),
        ("uv",),
        "workbench.generator.generate_basic",
        "workbench.verification.verify_basic",
        FrontendContract(
            family="simple-admin / semantic HTML",
            source_root="templates/frontends/simple-admin",
            product_root="web",
            request="same-origin fetch with Bearer authentication",
            api_prefix="/api",
            response_envelope="JSON resource or FastAPI detail error",
            pages=(PageContract("index.html", ("native HTML form", "table", "dialog")),),
        ),
    ),
    "fastapiadmin": TemplateAdapter(
        "fastapiadmin",
        "FastapiAdmin 原生后端 + Vue 管理端",
        "fastapiadmin",
        ("fastapiadmin-vue",),
        ("postgresql",),
        "shared",
        ("native-crud", "native-rbac", "menu-integration", "native-record-rules"),
        ("text", "integer", "boolean"),
        ("Python", "TypeScript", "Vue"),
        ("Python 3.14 (upstream >=3.12)", "Node.js 22 (upstream >=20.19)"),
        ("uv", "pnpm 9.15.3"),
        "workbench.native.generate_native",
        "workbench.native_delivery.managed_verify",
        FrontendContract(
            family="FastapiAdmin Vue / Fa components / Element Plus",
            source_root="frontend/web",
            product_root="frontend/web",
            request="request from @utils",
            api_prefix="/api/v1",
            response_envelope="ApiResponse data",
            protected=("src/layouts/", "src/styles/", "src/main.ts"),
            pages=(
                PageContract(
                    "src/views/module_rnd/{entity}/index.vue",
                    ("FaSearchBar", "FaTable", "FaDialog", "FaForm"),
                    business_components=("ElCard", "ElTimeline", "ElTimelineItem", "ElStatistic"),
                ),
            ),
        ),
        (
            "backend/app/plugin/",
            "backend/tests/",
            "frontend/web/src/views/",
            "frontend/web/src/components/",
            "frontend/web/src/api/",
        ),
    ),
    "yudao-vben": TemplateAdapter(
        "yudao-vben",
        "芋道 Java 后端 + Vben5 Ant Design",
        "yudao-java",
        ("vben-antd",),
        ("postgresql",),
        "shared",
        ("native-crud", "native-rbac", "menu-integration", "native-record-rules"),
        ("text", "integer", "boolean"),
        ("Java", "TypeScript", "Vue"),
        ("Java 17", "Node.js 22.18+ (upstream ^22.18.0 || ^24.12.0)"),
        ("Maven", "pnpm 11.16.0"),
        "workbench.native.generate_native",
        "workbench.native_delivery.managed_verify",
        FrontendContract(
            family="Vben5 web-antd / Ant Design Vue / VXE",
            source_root="apps/web-antd",
            product_root="frontend-product",
            request="requestClient from #/api/request",
            api_prefix="/admin-api",
            response_envelope="code=0, data, msg",
            protected=(
                "apps/web-antd/src/layouts/",
                "apps/web-antd/src/main.ts",
                "apps/web-antd/src/bootstrap.ts",
                "packages/@core/ui-kit/layout-ui/",
                "packages/@core/base/design/",
                "packages/effects/layouts/",
                "packages/styles/",
            ),
            pages=(
                PageContract(
                    "apps/web-antd/src/views/infra/wb{compact_entity}/index.vue",
                    ("Page", "Grid", "TableAction"),
                    ("@vben/common-ui", "#/adapter/vxe-table", "ant-design-vue"),
                    ("RndBusinessPanel",),
                ),
                PageContract(
                    "apps/web-antd/src/views/infra/wb{compact_entity}/modules/form.vue",
                    ("Modal", "Form"),
                    ("@vben/common-ui", "#/adapter/form", "ant-design-vue"),
                ),
                PageContract(
                    "apps/web-antd/src/views/infra/rnd-business/panel.vue",
                    (
                        "Card",
                        "Table",
                        "Timeline",
                        "TimelineItem",
                        "Statistic",
                        "MetricChart",
                        "ActionModal",
                        "ActionForm",
                    ),
                    ("ant-design-vue", "@vben/common-ui", "#/adapter/form", "#/api/request"),
                    business_only=True,
                ),
                PageContract(
                    "apps/web-antd/src/views/infra/rnd-business/metric-chart.vue",
                    ("EchartsUI",),
                    ("@vben/plugins/echarts",),
                    business_only=True,
                ),
            ),
        ),
        (
            *(
                f"backend/yudao-module-infra/{module}/src/{tree}/java/"
                for module in ("yudao-module-infra-server", "yudao-module-infra-api")
                for tree in ("main", "test")
            ),
            "frontend-product/apps/web-antd/src/views/",
            "frontend-product/apps/web-antd/src/api/",
        ),
    ),
}


def get_adapter(template):
    try:
        return _ADAPTERS[template]
    except KeyError:
        raise ValueError("未知模板") from None


def template_ids():
    return tuple(_ADAPTERS)


def template_catalog(template):
    return get_adapter(template).capabilities()
````
