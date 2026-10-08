# tests/test_business_workflow_branches.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `forked_plan`（L17–L128）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate`。 返回路径：L39的`Plan.model_validate( { "title": "Forked review workflow", "data_scope": "shared", "accepta…`。
- `run_api_probe`（L131–L166）：接收`tmp_path`、`plan`、`omit_transition_notification`。 控制顺序：L136按`omit_transition_notification`分支；L140断言`original.count(notify) == 1`；L165断言`result.stdout.strip()`。 调用`generate_basic`、`source.read_text`、`original.count`、`source.write_text`、`original.replace`、`temporary.mkdir`、`subprocess.run`、`str`、`clean_env`等。 返回路径：L166的`result, json.loads(result.stdout.splitlines()[-1])`。
- `test_api_probe_exercises_each_branch_and_notifies_both_recipients`（L169–L176）：接收`tmp_path`。 控制顺序：L171断言`result.returncode == 0 and report["passed"] is True`；L172断言`"business-transitions" in report["checks"]`；L173断言`"business-notifications" in report["checks"]`；L174断言`"process_restart_persistence" in report["checks"]`；L175断言`report["browser"] == {"applicable": False, "reason": "api-only frontend"}`；L176断言`report["http"] and report["restart"]`。 调用`run_api_probe`、`forked_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_api_probe_rejects_an_omitted_notification_on_the_alternative_branch`（L179–L182）：接收`tmp_path`。 控制顺序：L181断言`result.returncode == 1 and report["passed"] is False`；L182断言`report["message"] == "Missing, duplicated or unexpected declared notifications"`。 调用`run_api_probe`、`forked_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_api_probe_uses_each_branchs_existing_authorized_role`（L186–L209）：接收`tmp_path`、`scope`。 控制顺序：L192按`scope == "own"`分支；L196遍历`business["permissions"]`；L202遍历`business["workflows"][0]["transitions"]`；L203按`transition["name"] == "start"`分支；L205按`transition["name"] in {"decline", "reopen"}`分支；L208断言`result.returncode == 0 and report["passed"] is True`；L209断言`"business-notifications" in report["checks"] and report["restart"]`。 调用`forked_plan().model_dump`、`forked_plan`、`business["roles"].append`、`next`、`operator["actions"].append`、`business["permissions"].append`、`run_api_probe`、`Plan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_large_source_contract_passes_independent_api_probe`（L212–L229）：接收`tmp_path`。 控制顺序：L219断言`require_contract(case, plan.model_dump())`；L221断言`result.returncode == 0 and report["passed"] is True`；L222断言`report["entities"] == 6 and report["http"] and report["restart"]`；L223断言`report["browser"] == {"applicable": False, "reason": "api-only frontend"}`；L224断言`{ "business-transitions", "business-relations", "business-scoped-metrics", "business-…`。 调用`load_case`、`fixture_plan`、`require_contract`、`plan.model_dump`、`run_api_probe`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_api_probe_skips_transition_actor_who_is_not_an_eligible_assignee`（L232–L252）：接收`tmp_path`。 控制顺序：L235遍历`["no_read", "specialist"]`；L245遍历`business["workflows"][0]["transitions"]`；L246按`transition["name"] == "start"`分支；L248按`transition["name"] in {"decline", "reopen"}`分支；L251断言`result.returncode == 0 and report["passed"] is True`；L252断言`"business-notifications" in report["checks"] and report["restart"]`。 调用`forked_plan().model_dump`、`forked_plan`、`business["roles"].append`、`business["permissions"].append`、`run_api_probe`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verifier`（L256–L261）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Path`、`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`。 返回路径：L261的`module`。
- `test_assignee_candidates_preserve_nullable_and_existing_runtime_qualifications`（L264–L282）：接收`verifier`。 控制顺序：L275断言`verifier.workflow_assignee_candidates(actors, grants, "reviews", "handler-user") == […`；L280断言`verifier.workflow_assignee_candidates( {"owner": actors["owner"]}, grants, "reviews",…`。 调用`verifier.workflow_assignee_candidates`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transition_paths_accept_any_reachable_source_and_include_cycle_edges`（L285–L291）：接收`verifier`。 控制顺序：L289断言`[step["name"] for step in paths["accept"]] == ["start", "accept"]`；L290断言`[step["name"] for step in paths["reopen"]] == ["start", "decline", "reopen"]`；L291断言`set(paths) == {"start", "accept", "decline", "reopen"}`。 调用`forked_plan().business.workflows[0].model_dump`、`forked_plan`、`verifier.workflow_transition_paths`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_branch_coverage_replays_required_prefixes_and_bounds_cycles`（L295–L327）：接收`verifier`、`cycle_first`。 控制顺序：L297按`cycle_first`分支；L315断言`{name for _, name in actions} == {"start", "accept", "decline", "reopen"}`；L316断言`rows[0] == {"id": "base", "state": "accepted"}`；L317按`cycle_first`分支；L318断言`len(actions) == 4 and len(rows) == 1`；L320断言`actions == [ ("base", "start"), ("base", "accept"), ("branch", "start"), ("branch", "…`；L327断言`rows[1] == {"id": "branch", "state": "review"}`。 调用`forked_plan().business.workflows[0].model_dump`、`forked_plan`、`verifier.cover_workflow_branches`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_branch_coverage_replays_required_prefixes_and_bounds_cycles.create_branch`（L302–L305）：接收`transition`。 调用`rows.append`、`verifier.workflow_transition_paths`。 返回路径：L305的`row, verifier.workflow_transition_paths(workflow)[transition["name"]]`。
- `test_branch_coverage_replays_required_prefixes_and_bounds_cycles.apply`（L307–L310）：接收`row`、`transition`、`actor`。 控制顺序：L308断言`row["state"] in transition["from_states"] and actor == "operator"`。 调用`actions.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unreachable_declared_transition_fails_before_any_side_effect`（L330–L340）：接收`verifier`。 调用`forked_plan().business.workflows[0].model_dump`、`forked_plan`、`pytest.raises`、`verifier.cover_workflow_branches`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unreachable_declared_transition_fails_before_any_side_effect.unexpected`（L334–L335）：接收`*args`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_branch_actor_scope_is_rechecked_for_new_records`（L344–L364）：接收`verifier`、`scope_field`。 控制顺序：L363断言`actions == [("base", "start"), ("base", "accept")]`；L364断言`rows[1] == {"id": "branch", "state": "queued", scope_field: "another-user"}`。 调用`forked_plan().business.workflows[0].model_dump`、`forked_plan`、`pytest.raises`、`verifier.cover_workflow_branches`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_branch_actor_scope_is_rechecked_for_new_records.create_branch`（L349–L352）：接收`transition`。 调用`rows.append`、`verifier.workflow_transition_paths`。 返回路径：L352的`row, verifier.workflow_transition_paths(workflow)[transition["name"]]`。
- `test_branch_actor_scope_is_rechecked_for_new_records.actor_for`（L354–L355）：接收`row`、`transition`。 返回路径：L355的`"operator" if row[scope_field] == "operator" else None`。
- `test_branch_actor_scope_is_rechecked_for_new_records.apply`（L357–L359）：接收`row`、`transition`、`actor`。 调用`actions.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_owner_record_uses_a_permitted_prefix_regardless_of_order`（L368–L397）：接收`verifier`、`reverse_prefix_order`。 控制顺序：L376按`reverse_prefix_order`分支；L397断言`actions == [("base", "a_start"), ("secondary", "b_start"), ("secondary", "b_finish")]`。 调用`transitions.reverse`、`verifier.cover_workflow_branches`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_owner_record_uses_a_permitted_prefix_regardless_of_order.actor_for`（L385–L386）：接收`row`、`transition`。 返回路径：L386的`row["created_by"] if row["created_by"] in transition["roles"] else None`。
- `test_existing_owner_record_uses_a_permitted_prefix_regardless_of_order.apply`（L388–L391）：接收`row`、`transition`、`actor`。 控制顺序：L389断言`row["state"] in transition["from_states"] and row["created_by"] == actor`。 调用`actions.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_owner_record_uses_a_permitted_prefix_regardless_of_order.unnecessary_create`（L393–L394）：接收`transition`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_workflow_branches.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L397。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16195`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_workflow_branches.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3d5dfb1694eb1fa9f30091a163212322c83cc835ed9b57b12b6db188d99fc95e"} -->
````python
# tests/test_business_workflow_branches.py
"""Real API-only probes cover alternative workflow paths without weakening notifications."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.tools import clean_env


def forked_plan():
    transitions = [
        {"name": "start", "from_states": ["queued"], "to_state": "review", "roles": ["operator"]},
        {
            "name": "accept",
            "from_states": ["review"],
            "to_state": "accepted",
            "roles": ["operator"],
        },
        {
            "name": "decline",
            "from_states": ["review"],
            "to_state": "rejected",
            "roles": ["operator"],
        },
        {
            "name": "reopen",
            "from_states": ["rejected"],
            "to_state": "review",
            "roles": ["operator"],
        },
    ]
    return Plan.model_validate(
        {
            "title": "Forked review workflow",
            "data_scope": "shared",
            "acceptance": [
                "Every declared transition and its recipient notifications are exercised"
            ],
            "entities": [
                {
                    "name": "reviews",
                    "description": "Reviews",
                    "fields": [
                        {"name": "title", "kind": "text", "max_length": 60},
                        {"name": "reviewer_id", "kind": "text", "required": False},
                        {
                            "name": "state",
                            "kind": "enum",
                            "choices": ["queued", "review", "accepted", "rejected"],
                        },
                        {"name": "due_at", "kind": "datetime", "required": False},
                    ],
                }
            ],
            "business": {
                "roles": [
                    {"name": "manager", "label": "Manager"},
                    {"name": "operator", "label": "Operator"},
                ],
                "bootstrap_role": "manager",
                "role_admin_roles": ["manager"],
                "registration": {"enabled": False, "default_role": "operator"},
                "resources": [
                    {"entity": "reviews", "assignee_field": "reviewer_id", "notes": False}
                ],
                "relations": [
                    {"entity": "reviews", "field": "reviewer_id", "target_entity": "$users"}
                ],
                "permissions": [
                    {
                        "role": "manager",
                        "entity": "reviews",
                        "scope": "all",
                        "actions": [
                            "create",
                            "read",
                            "update",
                            "archive",
                            "assign",
                            "read_history",
                            "read_audit",
                        ],
                    },
                    {
                        "role": "operator",
                        "entity": "reviews",
                        "scope": "assigned",
                        "actions": ["read", "transition", "read_history"],
                    },
                ],
                "workflows": [
                    {
                        "entity": "reviews",
                        "status_field": "state",
                        "initial": "queued",
                        "transitions": transitions,
                    }
                ],
                "notifications": [
                    {"entity": "reviews", "event": "assigned", "recipient": "assignee"},
                    {
                        "entity": "reviews",
                        "event": "due",
                        "recipient": "assignee",
                        "due_field": "due_at",
                    },
                    *[
                        {
                            "entity": "reviews",
                            "event": "transitioned",
                            "transition": transition["name"],
                            "recipient": recipient,
                        }
                        for transition in transitions
                        for recipient in ("creator", "assignee")
                    ],
                ],
                "metrics": [],
            },
        }
    )


def run_api_probe(tmp_path, plan, omit_transition_notification=False):
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    if omit_transition_notification:
        source = product / "business_runtime.py"
        original = source.read_text(encoding="utf-8")
        notify = 'notify(connection, entity, after, "transitioned", event_id, data.transition)'
        assert original.count(notify) == 1
        source.write_text(
            original.replace(notify, f'{notify} if data.transition != "decline" else None'),
            encoding="utf-8",
        )
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "verify.py",
            "--python",
            sys.executable,
            "--report",
            str(tmp_path / "verification.json"),
        ],
        cwd=product,
        env=clean_env(
            {"PATH": os.environ.get("PATH", ""), "TEMP": str(temporary), "TMP": str(temporary)}
        ),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=180,
    )
    assert result.stdout.strip(), result.stderr
    return result, json.loads(result.stdout.splitlines()[-1])


def test_api_probe_exercises_each_branch_and_notifies_both_recipients(tmp_path):
    result, report = run_api_probe(tmp_path, forked_plan())
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-transitions" in report["checks"]
    assert "business-notifications" in report["checks"]
    assert "process_restart_persistence" in report["checks"]
    assert report["browser"] == {"applicable": False, "reason": "api-only frontend"}
    assert report["http"] and report["restart"]


def test_api_probe_rejects_an_omitted_notification_on_the_alternative_branch(tmp_path):
    result, report = run_api_probe(tmp_path, forked_plan(), omit_transition_notification=True)
    assert result.returncode == 1 and report["passed"] is False, report
    assert report["message"] == "Missing, duplicated or unexpected declared notifications"


@pytest.mark.parametrize("scope", ["own", "assigned"])
def test_api_probe_uses_each_branchs_existing_authorized_role(tmp_path, scope):
    raw = forked_plan().model_dump()
    business = raw["business"]
    business["roles"].append({"name": "specialist", "label": "Specialist"})
    operator = next(grant for grant in business["permissions"] if grant["role"] == "operator")
    operator["scope"] = scope
    if scope == "own":
        operator["actions"].append("create")
        business["resources"][0]["assignee_field"] = None
        business["relations"] = []
        for grant in business["permissions"]:
            grant["actions"] = [action for action in grant["actions"] if action != "assign"]
        business["notifications"] = [
            rule for rule in business["notifications"] if rule["recipient"] == "creator"
        ]
    business["permissions"].append({**operator, "role": "specialist"})
    for transition in business["workflows"][0]["transitions"]:
        if transition["name"] == "start":
            transition["roles"] = ["operator", "specialist"]
        elif transition["name"] in {"decline", "reopen"}:
            transition["roles"] = ["specialist"]
    result, report = run_api_probe(tmp_path, Plan.model_validate(raw))
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-notifications" in report["checks"] and report["restart"]


def test_large_source_contract_passes_independent_api_probe(tmp_path):
    from test_template_project_acceptance import fixture_plan

    from scripts.template_acceptance_cases import load_case, require_contract

    case = load_case("facilities-ops")
    plan = fixture_plan(case)
    assert require_contract(case, plan.model_dump())
    result, report = run_api_probe(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert report["entities"] == 6 and report["http"] and report["restart"]
    assert report["browser"] == {"applicable": False, "reason": "api-only frontend"}
    assert {
        "business-transitions",
        "business-relations",
        "business-scoped-metrics",
        "business-notifications",
    } <= set(report["checks"])


def test_api_probe_skips_transition_actor_who_is_not_an_eligible_assignee(tmp_path):
    raw = forked_plan().model_dump()
    business = raw["business"]
    for role in ["no_read", "specialist"]:
        business["roles"].append({"name": role, "label": role})
        business["permissions"].append(
            {
                "role": role,
                "entity": "reviews",
                "scope": "assigned",
                "actions": ["transition"] if role == "no_read" else ["read", "transition"],
            }
        )
    for transition in business["workflows"][0]["transitions"]:
        if transition["name"] == "start":
            transition["roles"] = ["operator", "no_read", "specialist"]
        elif transition["name"] in {"decline", "reopen"}:
            transition["roles"] = ["no_read", "specialist"]
    result, report = run_api_probe(tmp_path, Plan.model_validate(raw))
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-notifications" in report["checks"] and report["restart"]


@pytest.fixture
def verifier():
    path = Path(__file__).parents[1] / "templates/product/verify_business.py"
    spec = importlib.util.spec_from_file_location("branch_verifier", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_assignee_candidates_preserve_nullable_and_existing_runtime_qualifications(verifier):
    actors = {
        role: {"id": role + "-user", "role": role}
        for role in ["no_read", "owner", "reader", "handler"]
    }
    grants = {
        ("no_read", "reviews"): {"actions": ["transition"], "scope": "assigned"},
        ("owner", "reviews"): {"actions": ["read", "transition"], "scope": "own"},
        ("reader", "reviews"): {"actions": ["read"], "scope": "all"},
        ("handler", "reviews"): {"actions": ["read", "transition"], "scope": "assigned"},
    }
    assert verifier.workflow_assignee_candidates(actors, grants, "reviews", "handler-user") == [
        "handler-user",
        "reader-user",
        None,
    ]
    assert verifier.workflow_assignee_candidates(
        {"owner": actors["owner"]}, grants, "reviews", "no_read-user"
    ) == [None]


def test_transition_paths_accept_any_reachable_source_and_include_cycle_edges(verifier):
    workflow = forked_plan().business.workflows[0].model_dump()
    workflow["transitions"][1]["from_states"] = ["unreachable", "review"]
    paths = verifier.workflow_transition_paths(workflow)
    assert [step["name"] for step in paths["accept"]] == ["start", "accept"]
    assert [step["name"] for step in paths["reopen"]] == ["start", "decline", "reopen"]
    assert set(paths) == {"start", "accept", "decline", "reopen"}


@pytest.mark.parametrize("cycle_first", [False, True])
def test_branch_coverage_replays_required_prefixes_and_bounds_cycles(verifier, cycle_first):
    workflow = forked_plan().business.workflows[0].model_dump()
    if cycle_first:
        workflow["transitions"] = [workflow["transitions"][i] for i in [0, 2, 3, 1]]
    rows = [{"id": "base", "state": "queued"}]
    actions = []

    def create_branch(transition):
        row = {"id": "branch", "state": "queued"}
        rows.append(row)
        return row, verifier.workflow_transition_paths(workflow)[transition["name"]]

    def apply(row, transition, actor):
        assert row["state"] in transition["from_states"] and actor == "operator"
        actions.append((row["id"], transition["name"]))
        row["state"] = transition["to_state"]

    verifier.cover_workflow_branches(
        workflow, rows[0], create_branch, lambda row, transition: "operator", apply
    )
    assert {name for _, name in actions} == {"start", "accept", "decline", "reopen"}
    assert rows[0] == {"id": "base", "state": "accepted"}
    if cycle_first:
        assert len(actions) == 4 and len(rows) == 1
    else:
        assert actions == [
            ("base", "start"),
            ("base", "accept"),
            ("branch", "start"),
            ("branch", "decline"),
            ("branch", "reopen"),
        ]
        assert rows[1] == {"id": "branch", "state": "review"}


def test_unreachable_declared_transition_fails_before_any_side_effect(verifier):
    workflow = forked_plan().business.workflows[0].model_dump()
    workflow["transitions"][2]["from_states"] = ["never_reachable"]

    def unexpected(*args):
        pytest.fail("Unreachable graph must fail before creating or changing records")

    with pytest.raises(ValueError, match="no reachable source state"):
        verifier.cover_workflow_branches(
            workflow, {"state": "queued"}, unexpected, unexpected, unexpected
        )


@pytest.mark.parametrize("scope_field", ["created_by", "reviewer_id"])
def test_branch_actor_scope_is_rechecked_for_new_records(verifier, scope_field):
    workflow = forked_plan().business.workflows[0].model_dump()
    rows = [{"id": "base", "state": "queued", scope_field: "operator"}]
    actions = []

    def create_branch(transition):
        row = {"id": "branch", "state": "queued", scope_field: "another-user"}
        rows.append(row)
        return row, verifier.workflow_transition_paths(workflow)[transition["name"]]

    def actor_for(row, transition):
        return "operator" if row[scope_field] == "operator" else None

    def apply(row, transition, actor):
        actions.append((row["id"], transition["name"]))
        row["state"] = transition["to_state"]

    with pytest.raises(ValueError, match="no permitted transition actor"):
        verifier.cover_workflow_branches(workflow, rows[0], create_branch, actor_for, apply)
    assert actions == [("base", "start"), ("base", "accept")]
    assert rows[1] == {"id": "branch", "state": "queued", scope_field: "another-user"}


@pytest.mark.parametrize("reverse_prefix_order", [False, True])
def test_existing_owner_record_uses_a_permitted_prefix_regardless_of_order(
    verifier, reverse_prefix_order
):
    transitions = [
        {"name": "a_start", "from_states": ["queued"], "to_state": "review", "roles": ["a"]},
        {"name": "b_finish", "from_states": ["review"], "to_state": "accepted", "roles": ["b"]},
        {"name": "b_start", "from_states": ["queued"], "to_state": "review", "roles": ["b"]},
    ]
    if reverse_prefix_order:
        transitions.reverse()
    workflow = {"status_field": "state", "initial": "queued", "transitions": transitions}
    rows = [
        {"id": "base", "state": "queued", "created_by": "a"},
        {"id": "secondary", "state": "queued", "created_by": "b"},
    ]
    actions = []

    def actor_for(row, transition):
        return row["created_by"] if row["created_by"] in transition["roles"] else None

    def apply(row, transition, actor):
        assert row["state"] in transition["from_states"] and row["created_by"] == actor
        actions.append((row["id"], transition["name"]))
        row["state"] = transition["to_state"]

    def unnecessary_create(transition):
        pytest.fail("An existing permitted owner record must be used before creating another")

    verifier.cover_workflow_branches(workflow, rows[0], unnecessary_create, actor_for, apply, rows)
    assert actions == [("base", "a_start"), ("secondary", "b_start"), ("secondary", "b_finish")]
````
