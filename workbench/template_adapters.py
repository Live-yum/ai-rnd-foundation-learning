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
