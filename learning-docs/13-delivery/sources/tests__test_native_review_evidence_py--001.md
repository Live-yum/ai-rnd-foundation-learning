# tests/test_native_review_evidence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.native_delivery`、`workbench.native_evidence`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `synthetic_observations`（L21–L178）：接收`plan`。 源码说明：Explicit unit-only data, not a substitute for the HTTP probe producer.。 控制顺序：L50遍历`actors`；L53遍历`plan.business.metrics`；L55按`not grant or "read_metrics" not in grant.actions`分支；L59按`metric.kind == "count"`分支；L61按`metric.kind == "average_duration"`分支；L77按`not allowed`分支；L79遍历`plan.business.resources`；L80遍历`("update", "delete")`。后续分支沿下方源码相同行号继续阅读。 调用`digest`、`plan.model_dump`、`actor.removeprefix`、`grants.get`、`result["metrics"].append`、`deepcopy`、`result["metric_denials"].append`、`result["audit"].append`、`int`等。 返回路径：L178的`result`。
- `test_nonbusiness_native_plan_keeps_existing_managed_verification`（L181–L188）：接收`tmp_path`。 控制顺序：L184断言`result["passed"] is True`；L186断言`"original_installation" not in projected`；L187断言`"fresh_database_installation" not in projected`；L188断言`projected["source_digest"] == result["source_digest"]`。 调用`verified_fixture`、`managed_verify`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `detailed_fixture`（L192–L216）：接收`tmp_path`。 控制顺序：L212遍历`(report["business_browser"], report["portable_restored"]["browser…`。 调用`legacy_business_fixture`、`Plan.model_validate_json`、`spec_path.read_text`、`report["portable_restored"].update`、`synthetic_observations`、`deepcopy`、`browser["pages"].extend`、`login_shell_observation`。 返回路径：L216的`report, plan`。
- `test_model_projection_preserves_executed_detail_and_all_bindings`（L219–L231）：接收`detailed_fixture`。 控制顺序：L223断言`result["source_digest"] == digest(files)`；L224断言`result["spec_digest"] == digest(plan.model_dump())`；L225断言`result["acceptance_sha256"] == "a" * 64`；L226断言`result["reproduction_files"] == files`；L227断言`result["original_installation"]["http"]["reminders"]`；L228断言`result["fresh_database_installation"]["http"]["metrics"]`；L229断言`result["original_installation"]["browser"]["checks"]`；L230断言`result["deployment"]["fresh_database"] is True`。后续分支沿下方源码相同行号继续阅读。 调用`native_review_evidence`、`digest`、`plan.model_dump`、`len`、`json.dumps(result).encode`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_required_executed_collection_fails_closed`（L247–L258）：接收`detailed_fixture`、`collection`、`installation`。 调用`pytest.raises`、`native_review_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_and_forged_observations_are_rejected`（L276–L300）：接收`detailed_fixture`、`change`。 控制顺序：L279按`change == "old_boolean_only"`分支；L281按`change == "wrong_plan"`分支；L283按`change == "duplicate"`分支；L285按`change == "partial"`分支；L287按`change == "coerced_boolean"`分支；L289按`change == "unknown_subject"`分支；L291按`change == "wrong_role"`分支；L293按`change == "wrong_scope"`分支。后续分支沿下方源码相同行号继续阅读。 调用`report["business_contract"].pop`、`proof["reminders"].append`、`deepcopy`、`proof["field_queries"].pop`、`pytest.raises`、`native_review_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secrets_never_enter_projection_or_errors`（L304–L324）：接收`detailed_fixture`、`location`。 控制顺序：L307按`location == "top"`分支；L309按`location == "business"`分支；L311按`location == "browser"`分支；L313按`location == "proof"`分支；L320断言`secret not in str(error)`；L321断言`location in {"proof", "deployment"}`；L323断言`secret not in json.dumps(result)`；L324断言`location in {"top", "business", "browser"}`。 调用`native_review_evidence`、`str`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrecognized_browser_check_is_not_forwarded_as_proof`（L327–L332）：接收`detailed_fixture`。 控制顺序：L332断言`"secret" not in str(error.value)`。 调用`report["business_browser"]["checks"].append`、`pytest.raises`、`native_review_evidence`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_values_must_be_bounded_real_numbers`（L336–L341）：接收`detailed_fixture`、`value`。 调用`pytest.raises`、`validate_execution_evidence`、`pytest.mark.parametrize`、`float`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_excessive_collection_cannot_expand_model_context`（L344–L349）：接收`detailed_fixture`。 调用`pytest.raises`、`native_review_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_managed_verify_forwards_bound_evidence_without_model_call`（L352–L359）：接收`tmp_path`。 控制顺序：L356断言`native["source_digest"] == result["source_digest"]`；L357断言`native["acceptance_sha256"] == result["evidence_sha256"]`；L358断言`native["spec_digest"] == receipt["spec_digest"]`；L359断言`"original_installation" not in native`。 调用`verified_fixture`、`managed_verify`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_realistic_customer_review_payload_has_room_for_all_evidence`（L362–L398）：接收`detailed_fixture`。 控制顺序：L369遍历`(report["business_contract"], report["portable_restored"]["busine…`；L371遍历`list(proof["field_queries"])`；L372按`query["role"] in {"employee", "service"}`分支；L390断言`total < 95_000`；L392断言`proof["field_query_case_columns"] == [ "case", "expected_count", "observed_count", "r…`；L398断言`proof["field_queries"][0]["cases"][0] == ["positive", 1, 1, True]`。 调用`list`、`deepcopy`、`proof["field_queries"].append`、`native_review_evidence`、`(ROOT / "examples/requirements/customer-service-contract.md").rea…`、`plan.model_dump`、`len`、`json.dumps`、`ModelReview.model_json_schema`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_alternate_query_requires_a_distinct_exact_result_set`（L401–L410）：接收`detailed_fixture`。 调用`query["cases"][1].update`、`validate_execution_evidence`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_multiple_searchable_fields_do_not_invent_a_second_q_operand`（L413–L429）：接收`detailed_fixture`。 控制顺序：L416遍历`next(e for e in plan.entities if e.name == "tasks").fields`；L420遍历`proof["field_queries"]`；L421按`query["entity"] == "tasks"`分支；L425遍历`proof["field_queries"]`；L426按`query["entity"] == "customers"`分支。 调用`plan.model_copy`、`next`、`synthetic_observations`、`validate_execution_evidence`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_review_receives_full_bound_projection_with_mock_only`（L432–L455）：接收`detailed_fixture`、`settings`。 控制顺序：L455断言`observed == [projection]`。 调用`native_review_evidence`、`Workflow(settings, None, MockReviewer()).model_review`、`Workflow`、`MockReviewer`、`plan.model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_review_receives_full_bound_projection_with_mock_only.MockReviewer`（L441–L444）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_model_review_receives_full_bound_projection_with_mock_only.MockReviewer.complete`（L442–L444）：接收`run`、`key`、`instruction`、`payload`、`schema`。 调用`observed.append`、`ModelReview`。 返回路径：L444的`ModelReview(summary="Synthetic transport test only")`。
- `test_oversized_acceptance_is_rejected_before_hashing`（L458–L465）：接收`tmp_path`、`monkeypatch`。 调用`verified_fixture`、`monkeypatch.setattr`、`report.stat`、`pytest.fail`、`pytest.raises`、`managed_verify`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `login_shell_observation`（L468–L479）：接收`actor`。 源码说明：Unit fixture matching the executed Fastapi browser producer's shell shape.。 返回路径：L470的`{ "role": actor, "route": "/module_rnd/customers", "rendered": True, "native_shell_visible…`。
- `test_fastapi_login_shells_are_distinct_from_entity_form_observations`（L482–L506）：接收`detailed_fixture`。 控制顺序：L485遍历`(report["business_browser"], report["portable_restored"]["browser…`；L491遍历`("original_installation", "fresh_database_installation")`；L493断言`{page["entity"] for page in browser["pages"]} == {e.name for e in plan.entities}`；L494断言`browser["login_shells"] == [ { "actor": actor, "rendered": True, "native_shell_visibl…`；L504断言`"route" not in json.dumps(browser)`；L505断言`"#5D87FF" not in json.dumps(browser)`；L506断言`report == original`。 调用`browser["pages"].extend`、`login_shell_observation`、`browser["checks"].extend`、`deepcopy`、`native_review_evidence`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shell_acceptance_cannot_hide_invalid_or_missing_page_proof`（L528–L566）：接收`detailed_fixture`、`installation`、`change`。 控制顺序：L538按`change == "unknown_actor"`分支；L540按`change == "unknown_shape"`分支；L542按`change == "missing_login"`分支；L544按`change == "failed_login"`分支；L546按`change == "coerced_login"`分支；L548按`change == "unapproved_route"`分支；L550按`change == "wrong_family"`分支；L552按`change == "missing_theme"`分支。后续分支沿下方源码相同行号继续阅读。 调用`next`、`page.get`、`shell.pop`、`browser["checks"].remove`、`browser["pages"].append`、`deepcopy`、`browser["pages"][0].pop`、`browser["pages"].pop`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_fastapi_login_check_requires_its_typed_shell_observation`（L571–L589）：接收`detailed_fixture`、`installation`、`missing`。 控制顺序：L580按`missing == "extra_check"`分支。 调用`browser["checks"].append`、`page.get`、`pytest.raises`、`native_review_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_lower_level_projection_does_not_invent_unclaimed_logins`（L592–L608）：接收`detailed_fixture`。 控制顺序：L594遍历`(report["business_browser"], report["portable_restored"]["browser…`；L602断言`projected["original_installation"]["browser"]["login_shells"] == []`；L603断言`projected["fresh_database_installation"]["browser"]["login_shells"] == []`。 调用`check.endswith`、`native_review_evidence`、`pytest.raises`、`require_business_browser`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_relation_column_projection_is_lossless_and_hashes_complete_proof`（L611–L628）：接收`detailed_fixture`。 控制顺序：L618断言`compact["execution_sha256"] == digest(raw)`；L619断言`compact["version"] == raw["version"] == 1`；L620断言`compact["projection_version"] == 2`；L621遍历`( ("relation_writes", RelationWrite, "relation_write_columns"), (…`；L625断言`compact[key] == list(schema.model_fields)`；L627断言`expanded == raw[collection]`；L628断言`raw == original`。 调用`deepcopy`、`execution_summary`、`digest`、`list`、`dict`、`zip`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_relation_observation_is_rejected_before_compaction`（L632–L636）：接收`detailed_fixture`、`collection`。 调用`pytest.raises`、`native_review_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_approved_fastapi_plan_protocol_projection_fits_unchanged_budget`（L639–L717）：接收`detailed_fixture`。 源码说明：Protocol mocks exercise producer cardinality, not native runtime acceptance.。 控制顺序：L652断言`hashlib.sha256(raw).hexdigest() == ( "023ed6b43f20de90ef3b68033263212204314c2df0be080…`；L658遍历`proof.items()`；L659按`isinstance(value, list) and key != "reminders"`分支；L669遍历`oracle.actors.items()`；L671断言`len(proof["relation_writes"]) == 64`；L672断言`len(proof["field_queries"]) == 49`；L673断言`validate_execution_evidence(proof, plan) == proof`；L676遍历`(report["business_contract"], report["portable_restored"]["busine…`。后续分支沿下方源码相同行号继续阅读。 调用`path.read_bytes`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`Plan.model_validate_json`、`plan.model_dump`、`synthetic_observations`、`proof.items`、`isinstance`、`protocol`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_review_evidence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L717。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`30224`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_review_evidence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6ce2e501fc68bae46b9c124f350282366ae8ba51c60e025195b32912e3ff860a"} -->
````python
# tests/test_native_review_evidence.py
"""Synthetic fixtures test proof validation; these are NOT native runtime receipts."""

import json
from copy import deepcopy

import pytest
from test_native_business_evidence import evidence as legacy_business_fixture
from test_native_managed import verified_fixture

from workbench.domain import Plan, digest
from workbench.generator import PrerequisiteError
from workbench.native_delivery import managed_verify
from workbench.native_evidence import (
    MAX_EVIDENCE_BYTES,
    native_review_evidence,
    validate_execution_evidence,
)
from workbench.settings import ROOT


def synthetic_observations(plan):
    """Explicit unit-only data, not a substitute for the HTTP probe producer."""
    actors = ("manager", "employee", "other_employee", "service", "other_service")
    grants = {(p.role, p.entity): p for p in plan.business.permissions}
    result = {
        "version": 1,
        "spec_digest": digest(plan.model_dump()),
        "reminders": [
            {
                "entity": n.entity,
                "event": n.event,
                "transition": n.transition,
                "recipient": n.recipient,
                "expected_count": 1,
                "observed_count": 1,
                "idempotent": True,
                "read_persisted": True,
                "foreign_read_denied": True,
                "outsider_count": 0,
            }
            for n in plan.business.notifications
        ],
        "metrics": [],
        "metric_denials": [],
        "audit": [],
        "related_acl": [],
        "relation_writes": [],
        "field_queries": [],
    }
    for actor in actors:
        role = actor.removeprefix("other_")
        allowed = False
        for metric in plan.business.metrics:
            grant = grants.get((role, metric.entity))
            if not grant or "read_metrics" not in grant.actions:
                continue
            allowed = True
            value = {"value": None, "samples": None, "buckets": []}
            if metric.kind == "count":
                value["value"] = 2
            elif metric.kind == "average_duration":
                value["samples"] = 0
            else:
                value["buckets"] = [{"key_sha256": "1" * 64, "count": 2}]
            result["metrics"].append(
                {
                    "name": metric.name,
                    "role": role,
                    "actor": actor,
                    "scope": grant.scope,
                    "kind": metric.kind,
                    "visible_count": 2,
                    "expected": value,
                    "observed": deepcopy(value),
                }
            )
        if not allowed:
            result["metric_denials"].append({"role": role, "actor": actor, "observed_count": 0})
    for resource in plan.business.resources:
        for mutation in ("update", "delete"):
            result["audit"].append(
                {
                    "entity": resource.entity,
                    "mutation": mutation,
                    "transport": "http",
                    "denied": True,
                    "before_count": 3,
                    "after_count": 3,
                    "unchanged": True,
                    "before_sha256": "2" * 64,
                    "after_sha256": "2" * 64,
                }
            )
    for relation in plan.business.relations:
        if relation.target_entity != "$users":
            for actor in actors:
                role = actor.removeprefix("other_")
                parent_grant = grants.get((role, relation.target_entity))
                child_grant = grants.get((role, relation.entity))
                can_read = parent_grant and "read" in parent_grant.actions
                for case in ("visible_parent", "foreign_parent"):
                    if case == "visible_parent" and not can_read:
                        continue
                    if case == "foreign_parent" and can_read and parent_grant.scope == "all":
                        continue
                    count = int(
                        case == "visible_parent"
                        and child_grant is not None
                        and "read" in child_grant.actions
                    )
                    result["related_acl"].append(
                        {
                            "parent_entity": relation.target_entity,
                            "child_entity": relation.entity,
                            "field": relation.field,
                            "role": role,
                            "actor": actor,
                            "case": case,
                            "expected_count": count,
                            "observed_count": count,
                            "record_set_equal": True,
                            "parent_denied": case == "foreign_parent",
                        }
                    )
        for case in ("visible_target", "missing_target"):
            result["relation_writes"].append(
                {
                    "entity": relation.entity,
                    "field": relation.field,
                    "target_entity": relation.target_entity,
                    "role": "manager",
                    "actor": "manager",
                    "action": "assign" if relation.target_entity == "$users" else "create",
                    "case": case,
                    "denied": case == "missing_target",
                    "unchanged": case == "missing_target",
                    "expected_count": 1,
                    "observed_count": 1,
                }
            )
    for entity in plan.entities:
        for field in entity.fields:
            for enabled, kind in (
                (field.searchable, "search"),
                (field.filterable, "exact"),
                (field.date_range, "date_range"),
            ):
                if not enabled:
                    continue
                for role in ("manager", "employee", "service"):
                    grant = grants.get((role, entity.name))
                    if not grant or "read" not in grant.actions:
                        continue
                    result["field_queries"].append(
                        {
                            "entity": entity.name,
                            "field": field.name,
                            "kind": kind,
                            "role": role,
                            "actor": role,
                            "cases": [
                                {
                                    "case": case,
                                    "expected_count": count,
                                    "observed_count": count,
                                    "expected_sha256": digest([count]),
                                    "observed_sha256": digest([count]),
                                    "record_set_equal": True,
                                }
                                for case, count in (
                                    ("positive", 1),
                                    ("negative", 0),
                                    ("combination", 1),
                                )
                            ],
                        }
                    )
    return result


def test_nonbusiness_native_plan_keeps_existing_managed_verification(tmp_path):
    destination, receipt, _ = verified_fixture(tmp_path)
    result = managed_verify(destination, receipt)
    assert result["passed"] is True
    projected = result["native_acceptance"]
    assert "original_installation" not in projected
    assert "fresh_database_installation" not in projected
    assert projected["source_digest"] == result["source_digest"]


@pytest.fixture
def detailed_fixture(tmp_path):
    report, receipt, spec_path = legacy_business_fixture(tmp_path)
    plan = Plan.model_validate_json(spec_path.read_text(encoding="utf-8"))
    report["template"] = receipt["template"]
    report["portable_restored"].update(
        {
            "passed": True,
            "fresh_database": True,
            "frontend_started": True,
            "installed_from_lock": True,
            "standalone_launcher": True,
            "archive_round_trip": True,
            "source_database_reused": False,
            "original_platform_imported": False,
            "model_required": False,
        }
    )
    proof = synthetic_observations(plan)
    report["business_contract"]["execution_evidence"] = proof
    report["portable_restored"]["business"]["execution_evidence"] = deepcopy(proof)
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["pages"].extend(
            login_shell_observation(actor) for actor in ("manager", "employee", "service")
        )
    return report, plan


def test_model_projection_preserves_executed_detail_and_all_bindings(detailed_fixture):
    report, plan = detailed_fixture
    files = {"start.py": "c" * 64, "deployment/workbench/business_probe.py": "b" * 64}
    result = native_review_evidence(report, plan, files, "a" * 64)
    assert result["source_digest"] == digest(files)
    assert result["spec_digest"] == digest(plan.model_dump())
    assert result["acceptance_sha256"] == "a" * 64
    assert result["reproduction_files"] == files
    assert result["original_installation"]["http"]["reminders"]
    assert result["fresh_database_installation"]["http"]["metrics"]
    assert result["original_installation"]["browser"]["checks"]
    assert result["deployment"]["fresh_database"] is True
    assert len(json.dumps(result).encode()) < MAX_EVIDENCE_BYTES


@pytest.mark.parametrize(
    "collection",
    [
        "reminders",
        "metrics",
        "metric_denials",
        "audit",
        "related_acl",
        "relation_writes",
        "field_queries",
    ],
)
@pytest.mark.parametrize("installation", ["original", "fresh"])
def test_every_required_executed_collection_fails_closed(
    detailed_fixture, collection, installation
):
    report, plan = detailed_fixture
    source = (
        report["business_contract"]
        if installation == "original"
        else report["portable_restored"]["business"]
    )
    source["execution_evidence"][collection] = []
    with pytest.raises(PrerequisiteError, match="执行证据"):
        native_review_evidence(report, plan, {}, "a" * 64)


@pytest.mark.parametrize(
    "change",
    [
        "old_boolean_only",
        "wrong_plan",
        "duplicate",
        "partial",
        "coerced_boolean",
        "unknown_subject",
        "wrong_role",
        "wrong_scope",
        "wrong_count",
        "changed_audit",
    ],
)
def test_partial_and_forged_observations_are_rejected(detailed_fixture, change):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    if change == "old_boolean_only":
        report["business_contract"].pop("execution_evidence")
    elif change == "wrong_plan":
        proof["spec_digest"] = "b" * 64
    elif change == "duplicate":
        proof["reminders"].append(deepcopy(proof["reminders"][0]))
    elif change == "partial":
        proof["field_queries"].pop()
    elif change == "coerced_boolean":
        proof["audit"][0]["denied"] = 1
    elif change == "unknown_subject":
        proof["reminders"][0]["entity"] = "unapproved"
    elif change == "wrong_role":
        proof["metrics"][0]["role"] = "employee"
    elif change == "wrong_scope":
        proof["metrics"][0]["scope"] = "own"
    elif change == "wrong_count":
        proof["field_queries"][0]["cases"][0]["observed_count"] = 99
    elif change == "changed_audit":
        proof["audit"][0]["after_sha256"] = "3" * 64
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


@pytest.mark.parametrize("location", ["top", "business", "browser", "proof", "deployment"])
def test_secrets_never_enter_projection_or_errors(detailed_fixture, location):
    report, plan = detailed_fixture
    secret = "Bearer sk-test-private-value postgresql://private:password@database.invalid/db"
    if location == "top":
        report["provider_response"] = {"environment": secret}
    elif location == "business":
        report["business_contract"]["browser_actors"] = {"password": secret}
    elif location == "browser":
        report["business_browser"]["pages"][0]["native_theme_tokens"] = {"token": secret}
    elif location == "proof":
        report["business_contract"]["execution_evidence"]["raw_http"] = secret
    else:
        report["portable_restored"]["archive_round_trip"] = secret
    try:
        result = native_review_evidence(report, plan, {}, "a" * 64)
    except PrerequisiteError as error:
        assert secret not in str(error)
        assert location in {"proof", "deployment"}
    else:
        assert secret not in json.dumps(result)
        assert location in {"top", "business", "browser"}


def test_unrecognized_browser_check_is_not_forwarded_as_proof(detailed_fixture):
    report, plan = detailed_fixture
    report["business_browser"]["checks"].append("password=secret")
    with pytest.raises(PrerequisiteError) as error:
        native_review_evidence(report, plan, {}, "a" * 64)
    assert "secret" not in str(error.value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "1", -1, 10**20])
def test_metric_values_must_be_bounded_real_numbers(detailed_fixture, value):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    proof["metrics"][0]["observed"]["value"] = value
    with pytest.raises(ValueError):
        validate_execution_evidence(proof, plan)


def test_excessive_collection_cannot_expand_model_context(detailed_fixture):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    proof["reminders"] = proof["reminders"] * 100
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


def test_managed_verify_forwards_bound_evidence_without_model_call(tmp_path):
    product, receipt, _ = verified_fixture(tmp_path)
    result = managed_verify(product, receipt)
    native = result["native_acceptance"]
    assert native["source_digest"] == result["source_digest"]
    assert native["acceptance_sha256"] == result["evidence_sha256"]
    assert native["spec_digest"] == receipt["spec_digest"]
    assert "original_installation" not in native  # Non-business fixture has no invented probes.


def test_realistic_customer_review_payload_has_room_for_all_evidence(detailed_fixture):
    from workbench.domain import ModelReview
    from workbench.flow import REVIEW

    report, plan = detailed_fixture
    # Exercise peer observations as well as role-level checks. This remains a
    # synthetic budget fixture, never an acceptance artifact.
    for business in (report["business_contract"], report["portable_restored"]["business"]):
        proof = business["execution_evidence"]
        for query in list(proof["field_queries"]):
            if query["role"] in {"employee", "service"}:
                peer = deepcopy(query)
                peer["actor"] = "other_" + query["role"]
                proof["field_queries"].append(peer)
    review = native_review_evidence(report, plan, {}, "a" * 64)
    payload = {
        "requirement": (ROOT / "examples/requirements/customer-service-contract.md").read_text(
            encoding="utf-8"
        ),
        "plan": plan.model_dump(),
        "independent_evidence": {"passed": True, "native_acceptance": review},
        "previous_review": {"uncovered_requirements": ["bounded previous finding"] * 7},
    }
    total = (
        len(json.dumps(payload, ensure_ascii=False))
        + len(REVIEW)
        + len(json.dumps(ModelReview.model_json_schema(), ensure_ascii=False))
    )
    assert total < 95_000  # Keep space for the gateway's system/repair scaffolding.
    proof = review["original_installation"]["http"]
    assert proof["field_query_case_columns"] == [
        "case",
        "expected_count",
        "observed_count",
        "record_set_equal",
    ]
    assert proof["field_queries"][0]["cases"][0] == ["positive", 1, 1, True]


def test_alternate_query_requires_a_distinct_exact_result_set(detailed_fixture):
    report, plan = detailed_fixture
    proof = report["business_contract"]["execution_evidence"]
    query = proof["field_queries"][0]
    query["cases"][1].update(case="alternate", expected_count=1, observed_count=1)
    validate_execution_evidence(proof, plan)
    query["cases"][1]["expected_sha256"] = query["cases"][0]["expected_sha256"]
    query["cases"][1]["observed_sha256"] = query["cases"][0]["observed_sha256"]
    with pytest.raises(ValueError):
        validate_execution_evidence(proof, plan)


def test_multiple_searchable_fields_do_not_invent_a_second_q_operand(detailed_fixture):
    _, plan = detailed_fixture
    plan = plan.model_copy(deep=True)
    for field in next(e for e in plan.entities if e.name == "tasks").fields:
        field.filterable = False
        field.date_range = False
    proof = synthetic_observations(plan)
    for query in proof["field_queries"]:
        if query["entity"] == "tasks":
            query["cases"] = [case for case in query["cases"] if case["case"] != "combination"]
    validate_execution_evidence(proof, plan)
    # Independent q + category criteria still require a real combined query.
    for query in proof["field_queries"]:
        if query["entity"] == "customers":
            query["cases"] = [case for case in query["cases"] if case["case"] != "combination"]
    with pytest.raises(ValueError):
        validate_execution_evidence(proof, plan)


def test_model_review_receives_full_bound_projection_with_mock_only(detailed_fixture, settings):
    from workbench.domain import ModelReview
    from workbench.flow import Workflow

    report, plan = detailed_fixture
    projection = native_review_evidence(report, plan, {}, "a" * 64)
    settings.model_review = True
    observed = []

    class MockReviewer:
        def complete(self, run, key, instruction, payload, schema):
            observed.append(payload["independent_evidence"]["native_acceptance"])
            return ModelReview(summary="Synthetic transport test only")

    Workflow(settings, None, MockReviewer()).model_review(
        {
            "run_id": "mock-review",
            "attempt": 0,
            "plan": plan.model_dump(),
            "requirement": {},
            "verification": {"passed": True, "native_acceptance": projection},
        }
    )
    assert observed == [projection]


def test_oversized_acceptance_is_rejected_before_hashing(tmp_path, monkeypatch):
    import workbench.native_delivery as delivery

    product, receipt, report = verified_fixture(tmp_path)
    monkeypatch.setattr(delivery, "MAX_ACCEPTANCE_BYTES", report.stat().st_size - 1)
    monkeypatch.setattr(delivery, "sha", lambda *_: pytest.fail("Oversized report was read"))
    with pytest.raises(PrerequisiteError, match="大小"):
        managed_verify(product, receipt)


def login_shell_observation(actor="manager"):
    """Unit fixture matching the executed Fastapi browser producer's shell shape."""
    return {
        "role": actor,
        "route": "/module_rnd/customers",
        "rendered": True,
        "native_shell_visible": True,
        "native_component_family": "Fa/Element Plus",
        "native_theme_tokens": {"--el-color-primary": "#5D87FF", "--el-font-size-base": "14px"},
        "real_login": True,
        "native_menu_received": True,
    }


def test_fastapi_login_shells_are_distinct_from_entity_form_observations(detailed_fixture):
    report, plan = detailed_fixture
    actors = ("manager", "employee", "other_employee", "service", "other_service")
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["pages"] = [page for page in browser["pages"] if "entity" in page]
        browser["pages"].extend(login_shell_observation(actor) for actor in actors)
        browser["checks"].extend(f"{actor}:real_native_login_menu_shell" for actor in actors)
    original = deepcopy(report)
    projection = native_review_evidence(report, plan, {}, "a" * 64)
    for installation in ("original_installation", "fresh_database_installation"):
        browser = projection[installation]["browser"]
        assert {page["entity"] for page in browser["pages"]} == {e.name for e in plan.entities}
        assert browser["login_shells"] == [
            {
                "actor": actor,
                "rendered": True,
                "native_shell_visible": True,
                "real_login": True,
                "native_menu_received": True,
            }
            for actor in actors
        ]
        assert "route" not in json.dumps(browser)
        assert "#5D87FF" not in json.dumps(browser)
    assert report == original


@pytest.mark.parametrize("installation", ["original", "fresh"])
@pytest.mark.parametrize(
    "change",
    [
        "unknown_actor",
        "unknown_shape",
        "missing_login",
        "failed_login",
        "coerced_login",
        "unapproved_route",
        "wrong_family",
        "missing_theme",
        "missing_check",
        "duplicate_actor",
        "entity_disguised_as_shell",
        "missing_entity",
        "failed_entity",
    ],
)
def test_shell_acceptance_cannot_hide_invalid_or_missing_page_proof(
    detailed_fixture, installation, change
):
    report, plan = detailed_fixture
    browser = (
        report["business_browser"]
        if installation == "original"
        else report["portable_restored"]["browser"]
    )
    shell = next(page for page in browser["pages"] if page.get("role") == "manager")
    if change == "unknown_actor":
        shell["role"] = "secret-private-role"
    elif change == "unknown_shape":
        shell["arbitrary_page"] = "secret-private-value"
    elif change == "missing_login":
        shell.pop("real_login")
    elif change == "failed_login":
        shell["real_login"] = False
    elif change == "coerced_login":
        shell["real_login"] = 1
    elif change == "unapproved_route":
        shell["route"] = "/secret-private-route"
    elif change == "wrong_family":
        shell["native_component_family"] = "generic"
    elif change == "missing_theme":
        shell["native_theme_tokens"] = {}
    elif change == "missing_check":
        browser["checks"].remove("manager:real_native_login_menu_shell")
    elif change == "duplicate_actor":
        browser["pages"].append(deepcopy(shell))
    elif change == "entity_disguised_as_shell":
        browser["pages"][0].pop("entity")
    elif change == "missing_entity":
        browser["pages"].pop(0)
    elif change == "failed_entity":
        browser["pages"][0]["real_list_request"] = False
    with pytest.raises(PrerequisiteError) as error:
        native_review_evidence(report, plan, {}, "a" * 64)
    assert "secret-private" not in str(error.value)


@pytest.mark.parametrize("installation", ["original", "fresh"])
@pytest.mark.parametrize("missing", ["manager", "employee", "service", "all", "extra_check"])
def test_every_fastapi_login_check_requires_its_typed_shell_observation(
    detailed_fixture, installation, missing
):
    report, plan = detailed_fixture
    browser = (
        report["business_browser"]
        if installation == "original"
        else report["portable_restored"]["browser"]
    )
    if missing == "extra_check":
        browser["checks"].append("other_service:real_native_login_menu_shell")
    else:
        browser["pages"] = [
            page
            for page in browser["pages"]
            if "entity" in page or missing != "all" and page.get("role") != missing
        ]
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


def test_lower_level_projection_does_not_invent_unclaimed_logins(detailed_fixture):
    report, plan = detailed_fixture
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["checks"] = [
            check
            for check in browser["checks"]
            if not check.endswith(":real_native_login_menu_shell")
        ]
        browser["pages"] = [page for page in browser["pages"] if "entity" in page]
    projected = native_review_evidence(report, plan, {}, "a" * 64)
    assert projected["original_installation"]["browser"]["login_shells"] == []
    assert projected["fresh_database_installation"]["browser"]["login_shells"] == []
    # Production's preceding business gate still requires genuine login checks.
    from workbench.business_browser import require_business_browser

    with pytest.raises(ValueError, match="real role login"):
        require_business_browser(report["business_browser"], plan, "fastapiadmin")


def test_relation_column_projection_is_lossless_and_hashes_complete_proof(detailed_fixture):
    from workbench.native_evidence import RelatedACL, RelationWrite, execution_summary

    report, plan = detailed_fixture
    raw = report["business_contract"]["execution_evidence"]
    original = deepcopy(raw)
    compact = execution_summary(raw, plan)
    assert compact["execution_sha256"] == digest(raw)
    assert compact["version"] == raw["version"] == 1
    assert compact["projection_version"] == 2
    for collection, schema, key in (
        ("relation_writes", RelationWrite, "relation_write_columns"),
        ("related_acl", RelatedACL, "related_acl_columns"),
    ):
        assert compact[key] == list(schema.model_fields)
        expanded = [dict(zip(compact[key], row, strict=True)) for row in compact[collection]]
        assert expanded == raw[collection]
    assert raw == original


@pytest.mark.parametrize("collection", ["relation_writes", "related_acl"])
def test_invalid_relation_observation_is_rejected_before_compaction(detailed_fixture, collection):
    report, plan = detailed_fixture
    report["business_contract"]["execution_evidence"][collection][0]["observed_count"] += 1
    with pytest.raises(PrerequisiteError):
        native_review_evidence(report, plan, {}, "a" * 64)


def test_exact_approved_fastapi_plan_protocol_projection_fits_unchanged_budget(detailed_fixture):
    """Protocol mocks exercise producer cardinality, not native runtime acceptance."""
    import hashlib

    from test_native_business_probes import protocol

    from workbench.business_probe import verify_scoped_metrics
    from workbench.domain import ModelReview
    from workbench.flow import REVIEW
    from workbench.native_business_probe import verify_native_execution

    path = ROOT / "tests/fixtures/customer_approved_replays/fastapi-0e8.json"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "023ed6b43f20de90ef3b68033263212204314c2df0be08095fd6f9ec9e56dcb4"
    )
    plan = Plan.model_validate_json(raw)
    before = plan.model_dump()
    proof = synthetic_observations(plan)
    for key, value in proof.items():
        if isinstance(value, list) and key != "reminders":
            proof[key] = []
    with protocol("fastapiadmin", plan=plan) as (oracle, _, _, _):
        verify_native_execution(
            plan,
            oracle.manager,
            {actor: value for actor, value in oracle.actors.items() if actor != "manager"},
            oracle.records,
            proof,
        )
        for actor, (_, client) in oracle.actors.items():
            verify_scoped_metrics(client, plan, actor.removeprefix("other_"), actor, proof)
    assert len(proof["relation_writes"]) == 64
    assert len(proof["field_queries"]) == 49
    assert validate_execution_evidence(proof, plan) == proof
    report, _ = detailed_fixture
    report["spec_digest"] = digest(plan.model_dump())
    for business in (report["business_contract"], report["portable_restored"]["business"]):
        business["execution_evidence"] = deepcopy(proof)
    actors = ("manager", "employee", "other_employee", "service", "other_service")
    for browser in (report["business_browser"], report["portable_restored"]["browser"]):
        browser["spec_digest"] = report["spec_digest"]
        browser["pages"] = [page for page in browser["pages"] if "entity" in page]
        browser["pages"].extend(login_shell_observation(actor) for actor in actors)
        browser["checks"].extend(f"{actor}:real_native_login_menu_shell" for actor in actors)
    files = {"start.py": "b" * 64, "deployment/workbench/business_probe.py": "c" * 64}
    projected = native_review_evidence(report, plan, files, "a" * 64)
    assert projected["version"] == 2
    assert MAX_EVIDENCE_BYTES == 64_000
    assert len(json.dumps(projected, separators=(",", ":")).encode()) < MAX_EVIDENCE_BYTES
    assert projected["source_digest"] == digest(files)
    assert projected["acceptance_sha256"] == "a" * 64
    for installation in ("original_installation", "fresh_database_installation"):
        assert projected[installation]["http"]["execution_sha256"] == digest(proof)
    uncompressed = deepcopy(projected)
    for installation in ("original_installation", "fresh_database_installation"):
        http = uncompressed[installation]["http"]
        for collection, key in (
            ("relation_writes", "relation_write_columns"),
            ("related_acl", "related_acl_columns"),
        ):
            columns = http.pop(key)
            http[collection] = [dict(zip(columns, row, strict=True)) for row in http[collection]]
    assert len(json.dumps(uncompressed, separators=(",", ":")).encode()) > MAX_EVIDENCE_BYTES
    payload = {
        "requirement": (ROOT / "examples/requirements/customer-service-contract.md").read_text(
            encoding="utf-8"
        ),
        "plan": plan.model_dump(),
        "independent_evidence": {"passed": True, "native_acceptance": projected},
        "previous_review": {"uncovered_requirements": ["bounded previous finding"] * 7},
    }
    size = (
        len(json.dumps(payload, ensure_ascii=False))
        + len(REVIEW)
        + len(json.dumps(ModelReview.model_json_schema(), ensure_ascii=False))
    )
    assert size < 95_000
    assert plan.model_dump() == before
````
