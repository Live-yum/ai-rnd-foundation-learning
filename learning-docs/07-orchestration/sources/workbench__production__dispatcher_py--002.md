# workbench/production/dispatcher.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__production__dispatcher_py--001.md)

**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.acceptance.capability_verification`、`workbench.coding.candidates`、`workbench.core.contracts`、`workbench.errors`、`workbench.extensions.obligations`、`workbench.extensions.policy`、`workbench.extensions.readiness`、`workbench.filesystem`、`workbench.generation.python_basic`、`workbench.planning.contracts`、`workbench.planning.feature_planner`、`workbench.templates.adapters`、`workbench.templates.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ExtensionWorkflow.extension_after_aggregate`（L892–L904）：接收`state`。 控制顺序：L893按`state.get("extension_aggregate_passed")`分支；L896按`any( getattr(task, "executor", None) == "mini_swe" for task in design.implementation.…`分支；L899抛异常，停止当前正常路径；L900按`state.get("extension_integration_attempt", 0) < self.settings.max_repair_attempts`分支；L902抛异常，停止当前正常路径。 调用`state.get`、`self.checked_extension`、`any`、`getattr`、`UnsupportedScope`。 返回路径：L894的`"extension_review"`；L901的`"extension_integration_repair"`。
- `ExtensionWorkflow.extension_integration_repair`（L906–L925）：接收`state`。 控制顺序：L915按`manifest(baseline) != state["extension_baseline"]`分支；L916抛异常，停止当前正常路径。 调用`self.checked_extension`、`digest`、`design.model_dump`、`manifest`、`PrerequisiteError`、`state.get`、`str`。 返回路径：L917的`{ "extension_integration_attempt": state.get("extension_integration_attempt", 0) + 1, "ext…`。
- `ExtensionWorkflow.extension_review`（L927–L952）：接收`state`。 控制顺序：L929按`not self.settings.review_enabled`分支。 调用`self.checked_extension`、`self.gateway.complete`、`digest`、`design.model_dump`、`review.model_dump`、`write_json`。 返回路径：L930的`{ "model_review": { "enabled": False, "note": "Independent execution remains mandatory", }…`；L952的`{"model_review": result}`。
- `ExtensionWorkflow.extension_scope_data`（L954–L1004）：接收`state`、`design`。 控制顺序：L958按`conflicts`分支。 调用`self.extension_coverage`、`state.get`、`list`、`review.get`、`dict`、`coverage.get`、`sorted`、`bool`、`digest`等。 返回路径：L984的`{ "delivery_kind": "partial" if partial else "reviewed-contract", "full_request_complete":…`。
- `ExtensionWorkflow.extension_scope`（L1006–L1016）：接收`state`。 控制顺序：L1014按`result["decision"] == "reject"`分支。 调用`self.checked_extension`、`self.extension_scope_data`、`write_json`、`self.gate`。 返回路径：L1016的`result`。
- `ExtensionWorkflow.extension_package`（L1018–L1189）：接收`state`。 控制顺序：L1022按`state.get("native_generation", {}).get("execution") == "source-candidate"`分支；L1034按`native_receipt.get("spec_digest") != state["native_generation"].get("spec_digest")`分支；L1035抛异常，停止当前正常路径；L1098按`scope_name in handle.namelist()`分支；L1099抛异常，停止当前正常路径；L1122按`scope["requires_explicit_review"]`分支；L1130遍历`files(product)`；L1132按`"RND-DELIVERY.json" in listing`分支。后续分支沿下方源码相同行号继续阅读。 调用`self.checked_extension`、`Path`、`state.get("native_generation", {}).get`、`state.get`、`verify_native`、`json.loads`、`(product.parent / "native-generation.json").read_text`、`native_receipt.get`、`state["native_generation"].get`等。 返回路径：L1107的`{"delivery": result, "plan": design.baseline.model_dump()}`；L1167的`{ "delivery": { "package": archive.name, "sha256": sha(archive), "files": clean_listing, "…`。
- `ExtensionWorkflow.extension_delivery`（L1191–L1211）：接收`state`。 控制顺序：L1200按`sha(archive) != result["sha256"]`分支；L1201抛异常，停止当前正常路径。 调用`self.gate`、`result.items`、`sha`、`PrerequisiteError`。 返回路径：L1211的`decision`。

</details>

**创建路径：** `workbench/production/dispatcher.py`；**本文件共有 2 段**。本段覆盖源文件 L892–L1211。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14985`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/production/dispatcher.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "692be4ca453bd626a5b18067c496b3bd1992d0c0f09c415ac4edc55b60bc88f0"} -->
````python
# workbench/production/dispatcher.py
    def extension_after_aggregate(self, state):
        if state.get("extension_aggregate_passed"):
            return "extension_review"
        design = self.checked_extension(state)
        if any(
            getattr(task, "executor", None) == "mini_swe" for task in design.implementation.tasks
        ):
            raise UnsupportedScope("最终独立汇总验收否决；不重启mini-SWE预算")
        if state.get("extension_integration_attempt", 0) < self.settings.max_repair_attempts:
            return "extension_integration_repair"
        raise UnsupportedScope(
            "模块集成修复预算已用尽；候选及全部范围保留：" + state.get("extension_error", "")
        )

    def extension_integration_repair(self, state):
        design = self.checked_extension(state)
        baseline = (
            self.settings.data_dir
            / "runs"
            / state["run_id"]
            / "extension-baselines"
            / digest(design.model_dump())
        )
        if manifest(baseline) != state["extension_baseline"]:
            raise PrerequisiteError("集成修复基线与已批准生成回执不一致")
        return {
            "extension_integration_attempt": state.get("extension_integration_attempt", 0) + 1,
            "extension_completed": [],
            "extension_attempt": 0,
            "extension_product": str(baseline),
            "extension_candidate": "",
            "extension_candidate_passed": False,
            "extension_aggregate_passed": False,
        }

    def extension_review(self, state):
        design = self.checked_extension(state)
        if not self.settings.review_enabled:
            return {
                "model_review": {
                    "enabled": False,
                    "note": "Independent execution remains mandatory",
                }
            }
        review = self.gateway.complete(
            state["run_id"],
            "review:extension:"
            + digest({"design": design.model_dump(), "proof": state["extension_proof"]}),
            "独立审阅全部原始需求、模块实现契约与独立验收证据。列出未覆盖需求；不能以摘要或模型自称替代测试。",
            {
                "sources": state["extension_scope"]["sources"],
                "design": design.model_dump(),
                "independent_evidence": state["extension_proof"],
            },
            ModelReview,
        )
        result = {"enabled": True, **review.model_dump()}
        write_json(
            self.settings.data_dir / "runs" / state["run_id"] / "extension-review.json", result
        )
        return {"model_review": result}

    def extension_scope_data(self, state, design):
        coverage = self.extension_coverage(state, design, state["extension_proof"])
        review = state.get("model_review", {"enabled": False})
        conflicts = list(review.get("uncovered_requirements", []))
        if conflicts:
            # Model findings cannot close a source, or be silently discarded
            # when another source is already open. Free-text findings do not
            # reliably identify one source, so conservatively dispute every
            # completeness claim while preserving passed atomic observations.
            rows = [
                {**row, "status": "review_conflict"}
                if row["semantic"] == "original.full_source"
                else dict(row)
                for row in coverage["obligations"]
            ]
            coverage = {
                **coverage,
                "pre_review_complete_source_ids": coverage.get("complete_source_ids", []),
                "complete_source_ids": [],
                "remaining_source_ids": sorted({row["source_id"] for row in rows}),
                "remaining_obligations": [
                    row["goal_id"] for row in rows if row["status"] != "verified"
                ],
                "obligations": rows,
                "full_request_complete": False,
                "requires_source_rereview": True,
            }
        partial = coverage.get("full_request_complete") is not True or bool(
            design.implementation.prerequisites
        )
        return {
            "delivery_kind": "partial" if partial else "reviewed-contract",
            "full_request_complete": not partial,
            "coverage": coverage,
            "model_review": review,
            "review_conflicts": conflicts,
            "source_units": state["extension_scope"]["sources"],
            "plan_digest": digest(design.implementation.model_dump()),
            "evidence_digest": digest(state["extension_proof"]),
            "source_inventory_digest": digest(manifest(Path(state["extension_product"]))),
            "unverified_prerequisites": [
                p.model_dump() for p in design.implementation.prerequisites
            ],
            "readiness": readiness_report(
                design, manifest(Path(state["extension_product"])), state["extension_proof"]
            ),
            "requires_explicit_review": partial,
            "notice": "部分成果不关闭未完成来源、外部服务或迁移义务；批准只允许下载当前明确范围。"
            if partial
            else "仅证明明确人工审阅的原子合同，不保证任意自然语言的语义完整性。",
        }

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
        design = self.checked_extension(state)
        plan = design.implementation
        product = Path(state["extension_product"])
        if state.get("native_generation", {}).get("execution") == "source-candidate":
            # A preserved baseline is not a completed module and is never promoted
            # into the verified task ledger or passed to the runtime sandbox.
            from workbench.delivery.source_candidate import refresh_candidate
            from workbench.generation.native.service import package_native, verify_native

            # Verify the last controller-bound tree before refreshing metadata;
            # otherwise a modified candidate could be silently re-authorized here.
            verify_native(product)
            native_receipt = json.loads(
                (product.parent / "native-generation.json").read_text(encoding="utf-8")
            )
            if native_receipt.get("spec_digest") != state["native_generation"].get("spec_digest"):
                raise PrerequisiteError("候选源码规格与批准状态不一致")
            pending_tasks = [
                "Implement module task: " + task.id
                for task in plan.tasks
                if task.id not in state.get("extension_drafted", [])
            ]
            refresh_candidate(
                product,
                native_receipt,
                pending_steps=list(
                    dict.fromkeys(
                        [
                            *[
                                step
                                for step in native_receipt.get("pending_steps", [])
                                if not step.startswith("Implement module task: ")
                            ],
                            *pending_tasks,
                            "Run isolated module and aggregate acceptance",
                            *([state["extension_error"]] if state.get("extension_error") else []),
                        ]
                    )
                ),
                generation_status="partial"
                if pending_tasks
                else native_receipt["generation_status"],
            )
            report = verify_native(product)
            result = package_native(product, report)
            root = self.settings.data_dir / "runs" / state["run_id"]
            archive = root / "extension-source.zip"
            shutil.copyfile(product.parent / result["package"], archive)
            result.update(
                package=archive.name,
                sha256=sha(archive),
                generation_status=(
                    "partial"
                    if result.get("generation_status") == "partial"
                    or any(task.id not in state.get("extension_drafted", []) for task in plan.tasks)
                    else "complete"
                ),
                verification_status=report.get("verification_status", "unverified"),
                generation_error=state.get("extension_error", ""),
                drafted_tasks=state.get("extension_drafted", []),
                acceptance_passed=False,
                runtime_verified=False,
                production_ready=False,
                full_request_complete=False,
                delivery_kind="source-candidate",
                source_units=state["extension_scope"]["sources"],
                acceptance_contract_digest=digest(plan.model_dump()),
            )
            scope_name = "RND-SOURCE-SCOPE.json"
            scope_data = json.dumps(
                {
                    key: value
                    for key, value in result.items()
                    if key not in {"files", "sha256", "package"}
                },
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8")
            with zipfile.ZipFile(archive, "a", zipfile.ZIP_DEFLATED) as handle:
                if scope_name in handle.namelist():
                    raise PrerequisiteError("候选不能提供控制端源码范围声明")
                handle.writestr(scope_name, scope_data)
            result["files"] = {
                **result["files"],
                scope_name: hashlib.sha256(scope_data).hexdigest(),
            }
            result["sha256"] = sha(archive)
            write_json(root / "delivery.json", result)
            return {"delivery": result, "plan": design.baseline.model_dump()}
        from workbench.acceptance.capability_sandbox import verify_capabilities

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
                from workbench.extensions.consumer import require_consumer_evidence

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
            (
                "SOURCE_READY"
                if result["delivery_kind"] in {"partial", "source-candidate"}
                else "READY"
            )
            if decision["decision"] == "approve"
            else "REJECTED"
        )
        return decision
````
