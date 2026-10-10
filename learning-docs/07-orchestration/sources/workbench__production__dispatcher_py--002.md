# workbench/production/dispatcher.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__production__dispatcher_py--001.md)

**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_editing`、`workbench.capability_obligations`、`workbench.capability_policy`、`workbench.capability_readiness`、`workbench.capability_verification`、`workbench.catalog`、`workbench.domain`、`workbench.errors`、`workbench.feature_planning`、`workbench.filesystem`、`workbench.generator`、`workbench.template_adapters`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ExtensionWorkflow.extension_scope`（L900–L910）：接收`state`。 控制顺序：L908按`result["decision"] == "reject"`分支。 调用`self.checked_extension`、`self.extension_scope_data`、`write_json`、`self.gate`。 返回路径：L910的`result`。
- `ExtensionWorkflow.extension_package`（L912–L997）：接收`state`。 控制顺序：L930按`scope["requires_explicit_review"]`分支；L938遍历`files(product)`；L940按`"RND-DELIVERY.json" in listing`分支；L941抛异常，停止当前正常路径；L947按`{ name: value for name, value in clean_listing.items() if name != "RND-DELIVERY.json"…`分支；L950抛异常，停止当前正常路径；L970按`plan.selection.template == "python-basic"`分支。 调用`self.checked_extension`、`Path`、`manifest`、`require_evidence`、`digest`、`plan.model_dump`、`plan.selection.model_dump`、`self.extension_scope_data`、`self.store.explicit_approval`等。 返回路径：L975的`{ "delivery": { "package": archive.name, "sha256": sha(archive), "files": clean_listing, "…`。
- `ExtensionWorkflow.extension_delivery`（L999–L1015）：接收`state`。 控制顺序：L1008按`sha(archive) != result["sha256"]`分支；L1009抛异常，停止当前正常路径。 调用`self.gate`、`result.items`、`sha`、`PrerequisiteError`。 返回路径：L1015的`decision`。

</details>

**创建路径：** `workbench/production/dispatcher.py`；**本文件共有 2 段**。本段覆盖源文件 L900–L1015。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5249`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/production/dispatcher.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "d41ce7694bf305f842a99306db80c7471ea36649afae3d75c54ee32601dbd7e6"} -->
````python
# workbench/production/dispatcher.py
    def extension_scope(self, state):
        design = self.checked_extension(state)
        data = self.extension_scope_data(state, design)
        write_json(
            self.settings.data_dir / "runs" / state["run_id"] / "extension-coverage.json",
            data["coverage"],
        )
        result = self.gate(state, "extension_scope", data, ["approve", "reject"])
        if result["decision"] == "reject":
            result["status"] = "REJECTED"
        return result

    def extension_package(self, state):
        from workbench.capability_sandbox import verify_capabilities

        design = self.checked_extension(state)
        plan = design.implementation
        product = Path(state["extension_product"])
        listing = manifest(product)
        require_evidence(
            state["extension_proof"],
            source_digest=digest(listing),
            plan_digest=digest(plan.model_dump()),
            scenarios=plan.scenarios,
            selection=plan.selection.model_dump(),
            database_tables=plan.runtime.database_tables,
            aggregate=True,
        )
        scope = self.extension_scope_data(state, design)
        coverage = scope["coverage"]
        if scope["requires_explicit_review"]:
            self.store.explicit_approval(
                state["run_id"], "extension_scope", scope, version=state["round"]
            )
        root = self.settings.data_dir / "runs" / state["run_id"]
        temporary = root / "extension-delivery.zip.tmp"
        archive = root / "extension-delivery.zip"
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as handle:
            for name, path in files(product):
                handle.write(path, name)
            if "RND-DELIVERY.json" in listing:
                raise PrerequisiteError("候选不能提供控制端交付声明")
            handle.writestr("RND-DELIVERY.json", json.dumps(scope, ensure_ascii=False, indent=2))
        with tempfile.TemporaryDirectory(prefix="extension-cleanroom-", dir=root) as directory:
            clean = Path(directory) / "product"
            unpack(temporary, clean, template=plan.selection.template)
            clean_listing = manifest(clean)
            if {
                name: value for name, value in clean_listing.items() if name != "RND-DELIVERY.json"
            } != listing:
                raise PrerequisiteError("模块交付ZIP与已验收源码不一致")
            proof = verify_capabilities(
                clean,
                plan,
                plan.scenarios,
                self.settings,
                aggregate=True,
                selection=plan.selection.model_dump(),
                trusted_oracle=state["extension_policy"]["trusted_oracle"],
            )
            require_evidence(
                proof,
                source_digest=digest(clean_listing),
                plan_digest=digest(plan.model_dump()),
                scenarios=plan.scenarios,
                selection=plan.selection.model_dump(),
                database_tables=plan.runtime.database_tables,
                aggregate=True,
            )
            self.extension_coverage(state, design, proof)
            if plan.selection.template == "python-basic":
                from workbench.capability_consumer import require_consumer_evidence

                require_consumer_evidence(clean, plan, proof)
        temporary.replace(archive)
        return {
            "delivery": {
                "package": archive.name,
                "sha256": sha(archive),
                "files": clean_listing,
                "spec_digest": digest(design.model_dump()),
                "cleanroom": proof,
                "validation_level": "runtime",
                "coverage_level": coverage["coverage_level"],
                "delivery_kind": scope["delivery_kind"],
                "consumer_startup": proof.get("consumer", {}),
                "existing_schema_migration": "unverified",
                "full_request_complete": coverage.get("full_request_complete"),
                "coverage": coverage,
                "model_review": scope["model_review"],
                "review_conflicts": scope["review_conflicts"],
                "source_units": state["extension_scope"]["sources"],
                "acceptance_policy": state["extension_policy"],
                "acceptance_contract_digest": digest(plan.model_dump()),
                "production_ready": False,
            },
            "plan": design.baseline.model_dump(),
        }

    def extension_delivery(self, state):
        result = state["delivery"]
        decision = self.gate(
            state,
            "extension_delivery",
            {key: value for key, value in result.items() if key != "files"},
            ["approve", "reject"],
        )
        archive = self.settings.data_dir / "runs" / state["run_id"] / result["package"]
        if sha(archive) != result["sha256"]:
            raise PrerequisiteError("模块交付包在审批期间改变")
        decision["status"] = (
            ("SOURCE_READY" if result["delivery_kind"] == "partial" else "READY")
            if decision["decision"] == "approve"
            else "REJECTED"
        )
        return decision
````
