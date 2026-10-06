"""One executable template contract for selection, discovery and delivery planning.

Static support is not a configuration check or an acceptance receipt. Custom
source is a candidate until the selected stack and independent checks prove it.
"""

import json
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256

from workbench.settings import ROOT


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
        if self.template == "python-basic":
            return {
                "family": "simple-admin / semantic HTML",
                "source_root": "templates/frontends/simple-admin",
                "request": "same-origin fetch with Bearer authentication",
                "api_prefix": "/api",
                "components": ["native HTML form", "table", "dialog"],
                "api_only_available": True,
                "verification": "workbench.verification.require_browser_evidence",
            }
        from workbench.native_style import PROFILES, native_page_contracts

        profile = PROFILES[self.template]
        pages = native_page_contracts(self.template, ["record"], business=True)
        return {
            "family": profile["family"],
            "source_root": "frontend/web" if self.template == "fastapiadmin" else "apps/web-antd",
            "request": "request from @utils"
            if self.template == "fastapiadmin"
            else "requestClient from #/api/request",
            "api_prefix": "/api/v1" if self.template == "fastapiadmin" else "/admin-api",
            "response_envelope": "ApiResponse data"
            if self.template == "fastapiadmin"
            else "code=0, data, msg",
            "components": sorted({name for names, _ in pages.values() for name in names}),
            "imports": sorted({name for _, imports in pages.values() for name in imports}),
            "protected_paths": list(profile["protected"]),
            "preserve_native_shell": True,
            "api_only_available": False,
            "verification": "workbench.native_style.verify_native_style",
        }

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
