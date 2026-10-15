# workbench/_compat/aliases.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：旧导入名的惰性兼容注册。** 维护精确旧名到功能目录的映射；只有请求旧模块时才加载唯一实现，并共享模块对象及monkeypatch。注册本身不加载未来教材阶段。

**对应关系：** workbench包入口 → _compat注册 → 按需导入功能目录实现。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `workbench/_compat/aliases.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L101。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6983`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/_compat/aliases.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c4c9dbf9327ba83287de12459dcfdc3fbd8a879ba994bb31ca08880c070d8338"} -->
````python
# workbench/_compat/aliases.py
"""Explicit legacy import names; targets are imported only when requested."""

ALIASES = {
    "workbench.aider_tool": "workbench.coding.aider",
    "workbench.api": "workbench.interfaces.http",
    "workbench.business_browser": "workbench.business.browser",
    "workbench.business_capabilities": "workbench.business.capabilities",
    "workbench.business_contracts": "workbench.business.contracts",
    "workbench.business_fastapi": "workbench.business.fastapi",
    "workbench.business_native": "workbench.business.native",
    "workbench.business_probe": "workbench.business.probe",
    "workbench.business_python": "workbench.business.python",
    "workbench.business_schema_receipt": "workbench.business.schema_receipt",
    "workbench.business_yudao": "workbench.business.yudao",
    "workbench.capability_browser_isolation": "workbench.infrastructure.sandbox.browser.isolation",
    "workbench.capability_browser_policy": "workbench.infrastructure.sandbox.browser.policy",
    "workbench.capability_consumer": "workbench.extensions.consumer",
    "workbench.capability_contest_oracle": "workbench.extensions.contest_oracle",
    "workbench.capability_contracts": "workbench.planning.contracts",
    "workbench.capability_dependencies": "workbench.infrastructure.sandbox.dependencies",
    "workbench.capability_diagnostics": "workbench.infrastructure.sandbox.diagnostics",
    "workbench.capability_editing": "workbench.coding.candidates",
    "workbench.capability_execution": "workbench.infrastructure.sandbox.execution",
    "workbench.capability_isolation": "workbench.infrastructure.sandbox.isolation",
    "workbench.capability_native_runtime": "workbench.infrastructure.sandbox.native_runtime",
    "workbench.capability_obligations": "workbench.extensions.obligations",
    "workbench.capability_policy": "workbench.extensions.policy",
    "workbench.capability_readiness": "workbench.extensions.readiness",
    "workbench.capability_services": "workbench.extensions.services",
    "workbench.capability_stack": "workbench.extensions.stack",
    "workbench.capability_startup_paths": "workbench.infrastructure.sandbox.startup_paths",
    "workbench.capability_verification": "workbench.acceptance.capability_verification",
    "workbench.catalog": "workbench.templates.catalog",
    "workbench.clarification": "workbench.requirements.clarification",
    "workbench.context_mcp": "workbench.knowledge_services.mcp",
    "workbench.continue_index": "workbench.knowledge_services.continue_index",
    "workbench.conversation": "workbench.requirements.conversation",
    "workbench.daytona_diagnostics": "workbench.infrastructure.sandbox.daytona.diagnostics",
    "workbench.daytona_profiles": "workbench.infrastructure.sandbox.daytona.profiles",
    "workbench.daytona_sessions": "workbench.infrastructure.sandbox.daytona.sessions",
    "workbench.domain": "workbench.core.contracts",
    "workbench.entity_requirements": "workbench.requirements.entities",
    "workbench.feature_planning": "workbench.planning.feature_planner",
    "workbench.flow": "workbench.production.graph",
    "workbench.generator": "workbench.generation.python_basic",
    "workbench.knowledge": "workbench.knowledge_services.index",
    "workbench.llm": "workbench.infrastructure.llm.gateway",
    "workbench.model_connection": "workbench.models.connection",
    "workbench.model_diagnostics": "workbench.models.diagnostics",
    "workbench.model_discovery": "workbench.models.discovery",
    "workbench.model_protocol": "workbench.models.protocol",
    "workbench.model_settings": "workbench.models.settings",
    "workbench.module_imports": "workbench.business.modules.imports",
    "workbench.native": "workbench.generation.native.service",
    "workbench.native_acceptance": "workbench.acceptance.native_acceptance",
    "workbench.native_business_checks": "workbench.acceptance.native_business_checks",
    "workbench.native_business_probe": "workbench.acceptance.native_business_probe",
    "workbench.native_checks": "workbench.acceptance.native_checks",
    "workbench.native_coding": "workbench.generation.native.coding",
    "workbench.native_compatibility": "workbench.generation.native.compatibility",
    "workbench.native_delivery": "workbench.delivery.native",
    "workbench.native_environment": "workbench.infrastructure.native.environment",
    "workbench.native_evidence": "workbench.acceptance.native_evidence",
    "workbench.native_frontend": "workbench.generation.native.frontend",
    "workbench.native_lab": "workbench.acceptance.native_lab",
    "workbench.native_modules": "workbench.generation.native.modules",
    "workbench.native_plan_normalization": "workbench.generation.native.plan_normalization",
    "workbench.native_ports": "workbench.infrastructure.native.ports",
    "workbench.native_recovery": "workbench.delivery.recovery",
    "workbench.native_resources": "workbench.infrastructure.native.resources",
    "workbench.native_schema": "workbench.generation.native.schema",
    "workbench.native_style": "workbench.generation.native.style",
    "workbench.native_vben": "workbench.generation.native.vben",
    "workbench.orchestration": "workbench.production.dispatcher",
    "workbench.owned_lifecycle": "workbench.infrastructure.processes.owned_lifecycle",
    "workbench.portable": "workbench.delivery.portable",
    "workbench.portable_checks": "workbench.acceptance.portable_checks",
    "workbench.postgres_lab": "workbench.acceptance.postgres_lab",
    "workbench.product_sql": "workbench.generation.product_sql",
    "workbench.recommendation": "workbench.planning.recommendation",
    "workbench.requirement_canonical": "workbench.requirements.canonical",
    "workbench.requirement_coverage": "workbench.requirements.coverage",
    "workbench.requirement_intent": "workbench.requirements.intent",
    "workbench.requirement_sources": "workbench.requirements.source_ledger",
    "workbench.retrieval": "workbench.knowledge_services.retrieval",
    "workbench.rules": "workbench.planning.rules",
    "workbench.runtime": "workbench.production.worker",
    "workbench.sandbox": "workbench.infrastructure.sandbox.daytona.verification",
    "workbench.scaffolding": "workbench.templates.scaffolding",
    "workbench.store": "workbench.infrastructure.persistence.store",
    "workbench.streaming": "workbench.interfaces.streaming",
    "workbench.symbols": "workbench.knowledge_services.symbols",
    "workbench.template_adapters": "workbench.templates.adapters",
    "workbench.template_standards": "workbench.templates.standards",
    "workbench.toolchain": "workbench.interfaces.toolchain",
    "workbench.tools": "workbench.infrastructure.processes.tools",
    "workbench.vendor": "workbench.templates.vendor",
    "workbench.verification": "workbench.acceptance.verification",
    "workbench.yudao_navigation": "workbench.generation.native.yudao_navigation",
    "workbench.yudao_navigation_checks": "workbench.acceptance.yudao_navigation",
}
````
