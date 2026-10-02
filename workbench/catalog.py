"""Executable, deterministic template capabilities. The LLM cannot invent support flags."""

from pydantic import BaseModel, ConfigDict, model_validator

PAIRS = {
    "python-basic": {
        "backend": "fastapi",
        "frontends": ["simple-admin", "api-only"],
        "databases": ["sqlite", "postgresql"],
        "name": "FastAPI + 轻量管理页面",
        "scope": "per_user",
        "features": [
            "typed-crud",
            "authentication",
            "user-isolation",
            "keyword-search",
            "exact-filter",
            "date-range",
            "enum",
            "field-length",
            "single-record-rules",
        ],
        "field_kinds": ["text", "integer", "boolean", "date", "enum"],
        "not_supported": [
            "web-scraping",
            "external-payments",
            "cross-entity-transactions",
            "business-rbac",
            "public-anonymous-site",
        ],
    },
    "fastapiadmin": {
        "backend": "fastapiadmin",
        "frontends": ["fastapiadmin-vue"],
        "databases": ["postgresql"],
        "name": "FastapiAdmin 原生后端 + Vue 管理端",
        "scope": "shared",
        "features": ["native-crud", "native-rbac", "menu-integration", "native-record-rules"],
        "field_kinds": ["text", "integer", "boolean"],
        "not_supported": [
            "per-user-isolation",
            "arbitrary-code-execution",
            "cross-entity-transactions",
        ],
    },
    "yudao-vben": {
        "backend": "yudao-java",
        "frontends": ["vben-antd"],
        "databases": ["postgresql"],
        "name": "芋道 Java 后端 + Vben5 Ant Design",
        "scope": "shared",
        "features": ["native-crud", "native-rbac", "menu-integration", "native-record-rules"],
        "field_kinds": ["text", "integer", "boolean"],
        "not_supported": [
            "per-user-isolation",
            "arbitrary-code-execution",
            "cross-entity-transactions",
        ],
    },
}


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = "python-basic"
    backend: str = ""
    frontend: str = ""
    database: str = ""

    @model_validator(mode="after")
    def supported(self):
        if self.template not in PAIRS:
            raise ValueError("未知模板")
        spec = PAIRS[self.template]
        self.backend = self.backend or spec["backend"]
        self.frontend = self.frontend or spec["frontends"][0]
        self.database = self.database or spec["databases"][0]
        if (
            self.backend != spec["backend"]
            or self.frontend not in spec["frontends"]
            or self.database not in spec["databases"]
        ):
            raise ValueError("前后端与数据库组合不兼容；从模板目录中选择已验证的组合")
        return self

    def capabilities(self):
        from workbench.business_capabilities import BUSINESS

        return {
            **PAIRS[self.template],
            **self.model_dump(),
            "date_range_inclusive": True,
            "scopes": [
                PAIRS[self.template]["scope"],
                *(["shared"] if self.template == "python-basic" else []),
            ],
            "business_contract": BUSINESS,
            "not_supported": [
                item
                for item in PAIRS[self.template]["not_supported"]
                if item not in {"business-rbac", "cross-entity-transactions"}
            ],
            "defaults": {
                "title_max_length": 250,
                "body_max_length": 3000,
                "date_format": "YYYY-MM-DD",
                "category_required": False,
            },
        }


def options_for_run(run):
    return Selection.model_validate(run.get("options") or {"template": run["template"]})


def selections():
    return [Selection(template=template).capabilities() for template in PAIRS]
