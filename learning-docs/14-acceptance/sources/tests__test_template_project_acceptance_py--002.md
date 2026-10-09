# tests/test_template_project_acceptance.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_template_project_acceptance_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_template_projects`、`scripts.template_acceptance_cases`、`scripts.template_acceptance_runtime`、`workbench.business_capabilities`、`workbench.domain`、`workbench.generator`、`workbench.llm`、`workbench.model_protocol`、`workbench.requirement_coverage`、`workbench.requirement_sources`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_complete_offline_terminal_receipts_never_export_workflow_error_text.FailedWorker`（L873–L894）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_complete_offline_terminal_receipts_never_export_workflow_error_text.FailedWorker.__init__`（L876–L877）：接收`settings`、`store`、`gateway`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_complete_offline_terminal_receipts_never_export_workflow_error_text.FailedWorker.__enter__`（L879–L880）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L880的`self`。
- `test_complete_offline_terminal_receipts_never_export_workflow_error_text.FailedWorker.__exit__`（L882–L883）：接收`*args`。 返回路径：L883的`False`。
- `test_complete_offline_terminal_receipts_never_export_workflow_error_text.FailedWorker.tick`（L885–L894）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L887按`job is None`分支；L889按`failure_kind == "workflow"`分支。 调用`self.store.claim`、`self.store.finish`、`internal_errors.append`、`self.store.get_run`。 返回路径：L888的`False`；L894的`True`。
- `test_complete_offline_terminal_receipts_never_export_workflow_error_text.reject_offline_candidate`（L901–L912）：接收`case`、`*args`。 源码说明：Exercise the real oracle, without generating or accepting a product.。 控制顺序：L907按`case.identity == "reading-shelf"`分支。 调用`fixture_plan`、`next`、`range`、`require_contract`、`plan.model_dump`。 返回路径：L912的`require_contract(case, plan.model_dump())`。
- `test_transport_bounds_actual_requests_before_dispatch`（L960–L992）：接收`tmp_path`、`case`。 控制顺序：L975按`case == "destination"`分支；L977按`case == "model"`分支；L979按`case == "token_budget"`分支；L981按`case == "call_budget"`分支；L983按`case == "authorization"`分支；L991断言`not calls`。 调用`BoundedTransport`、`configured_settings`、`transport.inner.close`、`httpx.MockTransport`、`calls.append`、`httpx.Response`、`pytest.raises`、`transport.handle_request`、`httpx.Request`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `success_receipts`（L995–L1016）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Fabricated metadata for negative aggregate tests only; never written as evidence.。 调用`list`、`suite_cases`。 返回路径：L997的`[ { "case": case.identity, "source_digest": case.source_digest, "passed": True, "ready": T…`。
- `test_all_three_must_pass_with_real_calls_and_complete_evidence`（L1033–L1054）：接收`reason`。 控制顺序：L1035断言`aggregate(suite_cases(), results)`；L1036按`reason == "missing"`分支；L1038按`reason == "duplicate"`分支；L1040按`reason == "failure"`分支；L1042按`reason == "wrong_source"`分支；L1044按`reason == "no_browser"`分支；L1046按`reason == "missing_check"`分支；L1048按`reason == "no_model_plan"`分支。后续分支沿下方源码相同行号继续阅读。 调用`success_receipts`、`aggregate`、`suite_cases`、`results.pop`、`copy.deepcopy`、`results[2]["scenario"]["checks"].pop`、`results[2].update`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_uses_rnd_key_without_automatic_cost_trigger`（L1057–L1071）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1062断言`set(events) == {"workflow_dispatch", "pull_request"}`；L1063断言`events["pull_request"]["types"] == ["labeled"]`；L1065断言`job["environment"] == "rnd"`；L1066断言`"run-live-acceptance" in job["if"]`；L1067断言`"head.repo.full_name == github.repository" in job["if"]`；L1069断言`len(secret_steps) == 1`；L1070断言`secret_steps[0]["env"]["API_KEY"] == "${{ secrets.API_KEY }}"`；L1071断言`secret_steps[0]["run"] == "uv run python -m scripts.ci_template_projects"`。 调用`Path(__file__).resolve`、`Path`、`(root / ".github/workflows/template-project-acceptance.yml").read…`、`yaml.safe_load`、`workflow.get`、`set`、`json.dumps`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_template_project_acceptance.py`；**本文件共有 2 段**。本段覆盖源文件 L873–L1071。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7964`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_template_project_acceptance.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "be614b45afac9b2e46e6620dc58747bda4fdc3d4b2338a31e00cefcb49079513"} -->
````python
# tests/test_template_project_acceptance.py
    class FailedWorker:
        """Inject a terminal failure into the real Store; no model or browser runs."""

        def __init__(self, settings, store, gateway):
            self.store = store

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def tick(self):
            job = self.store.claim()
            if job is None:
                return False
            if failure_kind == "workflow":
                self.store.finish(job, "BLOCKED", error=error)
            else:
                self.store.finish(job, "READY", result={})
            internal_errors.append(self.store.get_run(job["run_id"])["error"])
            return True

    reports = tmp_path / "reports"
    monkeypatch.setattr(suite, "Runtime", FailedWorker)
    monkeypatch.setattr(suite, "REPORTS", reports)
    if failure_kind == "contract":

        def reject_offline_candidate(case, *args):
            """Exercise the real oracle, without generating or accepting a product."""
            plan = fixture_plan(case)
            plan.title, plan.acceptance = error, [error]
            field = plan.entities[0].fields[0]
            field.label = error
            if case.identity == "reading-shelf":
                category = next(item for item in plan.entities[0].fields if item.name == "category")
                category.choices = [f"{error} {index} {'x' * 100}" for index in range(50)]
            else:
                field.max_length += 1
            return require_contract(case, plan.model_dump())

        monkeypatch.setattr(suite, "verify_delivery", reject_offline_candidate)
    report = suite.run_suite(settings, tmp_path, {"offline_guard": True})
    assert internal_errors == [error if failure_kind == "workflow" else None] * 3
    assert report["passed"] is False and report["real_model"] is False
    assert report["actual_model_calls"] == 0 and len(report["cases"]) == 3
    for receipt in report["cases"]:
        assert receipt["passed"] is False
        if failure_kind == "workflow":
            assert receipt["workflow_status"] == "BLOCKED"
            assert receipt["failure"]["workflow_error"] == {
                "code": "workflow_not_ready",
                "status": "BLOCKED",
                "sha256": hashlib.sha256(error.encode()).hexdigest(),
                "characters": len(error),
            }
        else:
            assert receipt["workflow_status"] == "READY"
            assert receipt["failure"]["code"] == "contract_mismatch"
            difference = receipt["failure"]["contract_difference"]
            assert len(json.dumps(difference).encode()) < 500
            if receipt["case"] == "reading-shelf":
                assert receipt["failure"]["path"] == "books.category.choices"
                assert difference["attribute"] == "choices"
                assert difference["expected"]["items"] == 3
                assert difference["actual"]["items"] == 50
                assert set(difference["actual"]) == {"type", "items", "sha256"}
            else:
                assert difference["attribute"] == "max_length"
                assert difference["actual"] == difference["expected"] + 1
    output = capsys.readouterr().out
    emitted = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    assert emitted == report["cases"]
    for text in [
        output,
        json.dumps(report),
        *(path.read_text() for path in reports.glob("*.json")),
    ]:
        assert all(
            canary not in text
            for canary in ("private_fact_namespace", "private-excerpt-canary", "unit-only-key")
        )


@pytest.mark.parametrize(
    "case", ["destination", "model", "token_budget", "call_budget", "authorization", "stream"]
)
def test_transport_bounds_actual_requests_before_dispatch(tmp_path, case):
    transport = BoundedTransport(configured_settings(tmp_path))
    transport.inner.close()
    calls = []
    transport.inner = httpx.MockTransport(
        lambda request: calls.append(request) or httpx.Response(200, json={})
    )
    transport.run_id, transport.stage = "unit-only", "plan"
    body = {
        "model": "unit-only-model",
        "response_format": {"type": "json_object"},
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
        "stream": False,
    }
    url, auth = "https://model.invalid/v1/chat/completions", "Bearer unit-only-key"
    if case == "destination":
        url = "https://outside.invalid/v1/chat/completions"
    elif case == "model":
        body["model"] = "different-model"
    elif case == "token_budget":
        body["max_completion_tokens"] += 1
    elif case == "call_budget":
        transport.calls["unit-only"] = MAX_MODEL_CALLS
    elif case == "authorization":
        auth = "wrong"
    else:
        body["stream"] = True
    with pytest.raises(OutputFailure):
        transport.handle_request(
            httpx.Request("POST", url, headers={"Authorization": auth}, json=body)
        )
    assert not calls
    transport.shutdown()


def success_receipts():
    """Fabricated metadata for negative aggregate tests only; never written as evidence."""
    return [
        {
            "case": case.identity,
            "source_digest": case.source_digest,
            "passed": True,
            "ready": True,
            "contract_preserved": True,
            "model_calls": 2,
            "provider_http_calls": 2,
            "completed_model_stages": ["requirement", "plan"],
            "cleanroom": {"passed": True, "real_browser": True},
            "scenario": {
                "passed": True,
                "restart": True,
                "checks": list(case.expected_checks),
                "browser": {"passed": True, "real_browser": True},
            },
        }
        for case in suite_cases()
    ]


@pytest.mark.parametrize(
    "reason",
    [
        "missing",
        "duplicate",
        "failure",
        "wrong_source",
        "no_browser",
        "missing_check",
        "no_model_plan",
        "fake_call_count",
        "over_budget",
    ],
)
def test_all_three_must_pass_with_real_calls_and_complete_evidence(reason):
    results = success_receipts()
    assert aggregate(suite_cases(), results)
    if reason == "missing":
        results.pop()
    elif reason == "duplicate":
        results[2] = copy.deepcopy(results[1])
    elif reason == "failure":
        results[2]["passed"] = False
    elif reason == "wrong_source":
        results[2]["source_digest"] = "f" * 64
    elif reason == "no_browser":
        results[2]["scenario"]["browser"]["real_browser"] = False
    elif reason == "missing_check":
        results[2]["scenario"]["checks"].pop()
    elif reason == "no_model_plan":
        results[2]["completed_model_stages"] = ["requirement"]
    elif reason == "fake_call_count":
        results[2]["provider_http_calls"] = 0
    else:
        results[2].update(model_calls=MAX_MODEL_CALLS + 1, provider_http_calls=MAX_MODEL_CALLS + 1)
    assert not aggregate(suite_cases(), results)


def test_workflow_uses_rnd_key_without_automatic_cost_trigger():
    root = Path(__file__).resolve().parents[1]
    raw = (root / ".github/workflows/template-project-acceptance.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(raw)
    events = workflow.get("on", workflow.get(True))
    assert set(events) == {"workflow_dispatch", "pull_request"}
    assert events["pull_request"]["types"] == ["labeled"]
    job = workflow["jobs"]["all-three-projects"]
    assert job["environment"] == "rnd"
    assert "run-live-acceptance" in job["if"]
    assert "head.repo.full_name == github.repository" in job["if"]
    secret_steps = [step for step in job["steps"] if "secrets." in json.dumps(step)]
    assert len(secret_steps) == 1
    assert secret_steps[0]["env"]["API_KEY"] == "${{ secrets.API_KEY }}"
    assert secret_steps[0]["run"] == "uv run python -m scripts.ci_template_projects"
````
