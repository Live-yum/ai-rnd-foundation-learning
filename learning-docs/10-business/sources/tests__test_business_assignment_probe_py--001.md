# tests/test_business_assignment_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `assignment_case`（L20–L205）：接收`template`、`read_scope`、`assign_scope`、`violation`、`denial_response`。 控制顺序：L26按`read_scope`分支；L32按`assign_scope`分支；L183遍历`identities`；L200断言`plan.model_dump() == original`；L204遍历`clients.values()`。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`plan.business.permissions.append`、`type(plan.business.permissions[0])`、`type`、`next`、`grant.actions.append`、`plan.model_dump`、`probe.BusinessClient`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `assignment_case.permission`（L63–L66）：接收`role`、`entity`。 调用`next`。 返回路径：L64的`next( (p for p in plan.business.permissions if p.role == role and p.entity == entity), Non…`。
- `assignment_case.permitted`（L68–L77）：接收`grant`、`user`、`record`。 控制顺序：L69按`grant is None`分支。 返回路径：L70的`False`；L71的`grant.scope == "all" or grant.scope == "own" and record["created_by"] == user or grant.sco…`。
- `assignment_case.answer`（L79–L82）：接收`data`、`code`。 控制顺序：L80按`code`分支。 调用`httpx.Response`。 返回路径：L81的`httpx.Response(code if fastapi else 200, json={"code": code})`；L82的`httpx.Response(200, json={"code": 200 if fastapi else 0, "data": data})`。
- `assignment_case.handler`（L84–L180）：接收`request`。 控制顺序：L90按`request.method == "GET" and path.endswith(("/inbox", "/notifications"))`分支；L94按`request.method == "GET" and path.endswith("/history")`分支；L95断言`role == "manager" and request.url.params["audit"] == "true"`；L99按`request.method == "GET"`分支；L103按`path.endswith(("/list", "/page"))`分支；L104按`not readable`分支；L106按`violation == "peer_list_leak" and label == "other_employee" and entity == "tasks"`分支；L113断言`path.endswith(("/get", "/related"))`。后续分支沿下方源码相同行号继续阅读。 调用`request.headers["Authorization"].removeprefix`、`json.loads`、`calls.append`、`deepcopy`、`path.endswith`、`answer`、`next`、`request.url.params.get`、`body.get`等。 返回路径：L91的`answer(notices[label])`；L96的`answer(histories[entity])`；L105的`answer(code=403)`。
- `by_case`（L208–L209）：接收`proof`。 返回路径：L209的`{(item["entity"], item["case"]): item for item in proof["checks"]}`。
- `test_canonical_plan_exercises_target_and_actor_denials_without_invented_grants`（L213–L225）：接收`template`。 控制顺序：L217断言`proof["spec_digest"] == digest(args[0].model_dump())`；L218断言`checks["requests", "own_only_assignee_denied"]["status"] == "exercised"`；L219断言`checks["tasks", "no_read_assignee_denied"]["status"] == "exercised"`；L220遍历`records`；L221断言`checks[entity, "unauthorized_actor_denied"]["status"] == "exercised"`；L222断言`checks[entity, "foreign_row_denied"]["status"] == "absent"`；L223断言`checks[entity, "read_only_recipient_accepted"]["status"] == "absent"`；L224断言`sum(method == "POST" for _, method, _, _ in calls) == 4`。后续分支沿下方源码相同行号继续阅读。 调用`assignment_case`、`probe.verify_assignment_boundaries`、`by_case`、`digest`、`args[0].model_dump`、`sum`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_read_only_recipient_is_assignable_without_acquiring_mutation_power`（L230–L251）：接收`template`、`scope`。 控制顺序：L236断言`positive["status"] == "exercised" and positive["assignee_scope"] == scope`；L237断言`positive["persisted_and_recipient_readable"]`；L238断言`positive["original_assignee_restored"] and records["tasks"]["assignee_id"] == "23"`；L239遍历`("assign", "update", "transition")`；L240断言`checks["tasks", f"read_only_recipient_{action}_denied"]["status"] == "exercised"`；L241断言`positive["peer_isolation"]["status"] == ( "exercised" if scope == "assigned" else "ab…`；L244按`scope == "assigned"`分支；L245断言`positive["peer_isolation"]["record_endpoint"] == ( "related" if template == "fastapia…`。后续分支沿下方源码相同行号继续阅读。 调用`assignment_case`、`by_case`、`probe.verify_assignment_boundaries`、`any`、`path.endswith`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_foreign_row_denial_is_exercised_only_with_an_existing_restricted_assign_grant`（L256–L263）：接收`template`、`role`、`scope`。 控制顺序：L261断言`checks["requests", "foreign_row_denied"]["status"] == "exercised"`；L262断言`checks["requests", "foreign_row_denied"]["actor_role"] == role`；L263断言`any(label == "other_" + role and method == "POST" for label, method, _, _ in calls)`。 调用`assignment_case`、`by_case`、`probe.verify_assignment_boundaries`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_faults_cannot_be_reported_as_assignment_boundary_proof`（L279–L282）：接收`template`、`violation`。 调用`assignment_case`、`pytest.raises`、`probe.verify_assignment_boundaries`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_positive_assignment_requires_persistence_least_privilege_isolation_and_restoration`（L296–L301）：接收`template`、`violation`。 调用`assignment_case`、`pytest.raises`、`probe.verify_assignment_boundaries`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_restricted_assign_cannot_escape_its_row_scope`（L305–L310）：接收`template`。 调用`assignment_case`、`pytest.raises`、`probe.verify_assignment_boundaries`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_denial_server_error_diagnostics_remain_safe_and_fail_closed`（L314–L333）：接收`template`。 控制顺序：L330断言`"own_only_assignee_denied" in message and "entity=requests" in message`；L331断言`f"http_status={status}, response_code=500" in message`；L332断言`len(message) < 240`；L333断言`all(part not in message for part in ["secret", "系统异常", "X-Debug-Token", "Bearer"])`。 调用`httpx.Response`、`assignment_case`、`pytest.raises`、`probe.verify_assignment_boundaries`、`str`、`len`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_denial_diagnostics_do_not_echo_noninteger_or_unbounded_codes`（L341–L349）：接收`template`、`code`。 控制顺序：L347断言`"http_status=200, response_code=None" in message`；L348断言`"secret" not in message`；L349断言`len(message) < 240`。 调用`httpx.Response`、`assignment_case`、`pytest.raises`、`probe.verify_assignment_boundaries`、`str`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_denial_diagnostics_handle_malformed_or_nonobject_bodies`（L354–L362）：接收`template`、`body`。 控制顺序：L360断言`"http_status=200, response_code=None" in message`；L361断言`"secret" not in message and "html" not in message`；L362断言`len(message) < 240`。 调用`httpx.Response`、`assignment_case`、`pytest.raises`、`probe.verify_assignment_boundaries`、`str`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_assignment_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L362。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15663`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_assignment_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ad7565b0a8c4418d39fd5d9e08d60e268da9a1528b0f7ee18c1e7e68d282e564"} -->
````python
# tests/test_business_assignment_probe.py
"""MockTransport unit tests for native probes; these are not live native evidence.

Plan variations exist only in these isolated tests. The production HTTP probe
must never substitute or mutate the approved Plan to obtain a positive branch.
"""

import json
from contextlib import contextmanager
from copy import deepcopy

import httpx
import pytest

from workbench import business_probe as probe
from workbench.domain import Plan, digest
from workbench.settings import ROOT


@contextmanager
def assignment_case(
    template, read_scope=None, assign_scope=None, violation=None, denial_response=None
):
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    if read_scope:
        plan.business.permissions.append(
            type(plan.business.permissions[0])(
                role="employee", entity="tasks", actions=["read"], scope=read_scope
            )
        )
    if assign_scope:
        role, scope = assign_scope
        grant = next(
            item
            for item in plan.business.permissions
            if item.entity == "requests" and item.role == role
        )
        grant.actions.append("assign")
        grant.scope = scope
    original = plan.model_dump()
    fastapi = template == "fastapiadmin"
    prefix = "/business" if fastapi else "/admin-api/infra/rnd-business"
    targets = [
        {"entity": name, "api": f"/admin-api/infra/{name}", "list": f"/admin-api/infra/{name}/page"}
        for name in ("requests", "tasks")
    ]
    identities = {
        "manager": ("20", "manager"),
        "employee": ("21", "employee"),
        "other_employee": ("22", "employee"),
        "service": ("23", "service"),
        "other_service": ("24", "service"),
    }
    records = {
        "requests": {"id": "11", "title": "Request", "created_by": "21", "assignee_id": "23"},
        "tasks": {"id": "12", "title": "Task", "created_by": "20", "assignee_id": "23"},
    }
    histories = {name: [{"id": "1", "event": "created"}] for name in records}
    notices = {label: [] for label in identities}
    calls = []

    def permission(role, entity):
        return next(
            (p for p in plan.business.permissions if p.role == role and p.entity == entity), None
        )

    def permitted(grant, user, record):
        if grant is None:
            return False
        return (
            grant.scope == "all"
            or grant.scope == "own"
            and record["created_by"] == user
            or grant.scope == "assigned"
            and record["assignee_id"] == user
        )

    def answer(data=None, code=None):
        if code:
            return httpx.Response(code if fastapi else 200, json={"code": code})
        return httpx.Response(200, json={"code": 200 if fastapi else 0, "data": data})

    def handler(request):
        label = request.headers["Authorization"].removeprefix("Bearer ")
        user, role = identities[label]
        path = request.url.path
        body = json.loads(request.content) if request.content else {}
        calls.append((label, request.method, path, deepcopy(body)))
        if request.method == "GET" and path.endswith(("/inbox", "/notifications")):
            return answer(notices[label])
        entity = next((name for name in records if f"/{name}/" in path), None)
        entity = entity or request.url.params.get("entity") or body.get("entity")
        if request.method == "GET" and path.endswith("/history"):
            assert role == "manager" and request.url.params["audit"] == "true"
            return answer(histories[entity])
        record = records[entity]
        grant = permission(role, entity)
        if request.method == "GET":
            readable = grant is not None and "read" in grant.actions
            scoped = permitted(grant, user, record)
            row = {probe.wire_name(template, key): value for key, value in record.items()}
            if path.endswith(("/list", "/page")):
                if not readable:
                    return answer(code=403)
                if (
                    violation == "peer_list_leak"
                    and label == "other_employee"
                    and entity == "tasks"
                ):
                    scoped = True
                return answer({"items" if fastapi else "list": [row] if scoped else []})
            assert path.endswith(("/get", "/related"))
            if violation == "peer_detail_leak" and label == "other_employee":
                scoped = True
            return answer(row) if readable and scoped else answer(code=404 if fastapi else 403)
        action = path.rsplit("/", 1)[-1] if fastapi else body.get("action", "update")
        if action == "update" and not fastapi:
            assert request.method == "PUT" and set(body) == {"id", "title"}
        elif not fastapi:
            assert request.method == "POST" and path == prefix + "/action"
            expected = {
                "entity",
                "id",
                "action",
                "assigneeId" if action == "assign" else "transition",
            }
            assert set(body) == expected, (
                "Native action body must reach the intended permission gate"
            )
        else:
            assert request.method == "POST"
            assert path == f"{prefix}/{entity}/{record['id']}/{action}"
            assert set(body) == {
                "assignee" if action == "assign" else action if action == "transition" else "title"
            }
        recipient = body.get("assignee" if fastapi else "assigneeId")
        error = None
        if grant is None or action not in grant.actions:
            if violation not in {"unauthorized_actor", "readonly_mutation"}:
                error = 403
        elif not permitted(grant, user, record) and violation != "foreign_row":
            error = 404 if fastapi else 403
        if error is None and action == "assign":
            recipient_role = next(r for i, r in identities.values() if i == recipient)
            recipient_grant = permission(recipient_role, entity)
            eligible = (
                recipient_grant is not None
                and "read" in recipient_grant.actions
                and recipient_grant.scope in {"assigned", "all"}
            )
            if not eligible and violation != "ineligible_assignee":
                error = 422 if fastapi else 400
        if error is not None:
            if denial_response is not None:
                return denial_response
            if violation == "server_error":
                return answer(code=500)
            if violation == "unrelated_denial":
                return answer(code=401)
            if violation == "denial_row_write":
                record["title"] += " changed"
            if violation == "denial_audit_write":
                histories[entity].append({"id": "rogue", "event": "assigned"})
            if violation == "denial_notice_write":
                notices["manager"].append(
                    {"id": "rogue", "entity": entity, "record_id": record["id"]}
                )
            return answer(code=error)
        if action == "assign":
            if (
                violation == "restore_failure"
                and record["assignee_id"] == "21"
                and recipient == "23"
            ):
                return answer(code=400)
            if not (violation == "positive_not_persisted" and recipient == "21"):
                record["assignee_id"] = recipient
        histories[entity].append({"id": str(len(histories[entity]) + 1), "event": action})
        return answer({probe.wire_name(template, key): value for key, value in record.items()})

    clients = {}
    for label in identities:
        client = probe.BusinessClient(template, "http://127.0.0.1", label, targets)
        client.http.close()
        client.http = httpx.Client(
            base_url="http://127.0.0.1",
            headers={"Authorization": "Bearer " + label},
            transport=httpx.MockTransport(handler),
        )
        clients[label] = client
    actors = {
        label: (identities[label][0], client)
        for label, client in clients.items()
        if label != "manager"
    }
    args = (plan, clients["manager"], actors, {name: row["id"] for name, row in records.items()})
    try:
        yield args, records, calls
        assert plan.model_dump() == original, (
            "Even isolated probe execution must preserve its input Plan"
        )
    finally:
        for client in clients.values():
            client.close()


def by_case(proof):
    return {(item["entity"], item["case"]): item for item in proof["checks"]}


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_canonical_plan_exercises_target_and_actor_denials_without_invented_grants(template):
    with assignment_case(template) as (args, records, calls):
        proof = probe.verify_assignment_boundaries(*args)
        checks = by_case(proof)
        assert proof["spec_digest"] == digest(args[0].model_dump())
        assert checks["requests", "own_only_assignee_denied"]["status"] == "exercised"
        assert checks["tasks", "no_read_assignee_denied"]["status"] == "exercised"
        for entity in records:
            assert checks[entity, "unauthorized_actor_denied"]["status"] == "exercised"
            assert checks[entity, "foreign_row_denied"]["status"] == "absent"
            assert checks[entity, "read_only_recipient_accepted"]["status"] == "absent"
        assert sum(method == "POST" for _, method, _, _ in calls) == 4
        assert len(proof["checks"]) == 10


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("scope", ["assigned", "all"])
def test_approved_read_only_recipient_is_assignable_without_acquiring_mutation_power(
    template, scope
):
    with assignment_case(template, read_scope=scope) as (args, records, calls):
        checks = by_case(probe.verify_assignment_boundaries(*args))
        positive = checks["tasks", "read_only_recipient_accepted"]
        assert positive["status"] == "exercised" and positive["assignee_scope"] == scope
        assert positive["persisted_and_recipient_readable"]
        assert positive["original_assignee_restored"] and records["tasks"]["assignee_id"] == "23"
        for action in ("assign", "update", "transition"):
            assert checks["tasks", f"read_only_recipient_{action}_denied"]["status"] == "exercised"
        assert positive["peer_isolation"]["status"] == (
            "exercised" if scope == "assigned" else "absent"
        )
        if scope == "assigned":
            assert positive["peer_isolation"]["record_endpoint"] == (
                "related" if template == "fastapiadmin" else "get"
            )
        if template == "yudao-vben":
            assert any(
                method == "PUT" and path.endswith("/tasks/update") for _, method, path, _ in calls
            )


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("role,scope", [("employee", "own"), ("service", "assigned")])
def test_foreign_row_denial_is_exercised_only_with_an_existing_restricted_assign_grant(
    template, role, scope
):
    with assignment_case(template, assign_scope=(role, scope)) as (args, _, calls):
        checks = by_case(probe.verify_assignment_boundaries(*args))
        assert checks["requests", "foreign_row_denied"]["status"] == "exercised"
        assert checks["requests", "foreign_row_denied"]["actor_role"] == role
        assert any(label == "other_" + role and method == "POST" for label, method, _, _ in calls)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "violation",
    [
        "ineligible_assignee",
        "unauthorized_actor",
        "server_error",
        "unrelated_denial",
        "denial_row_write",
        "denial_audit_write",
        "denial_notice_write",
    ],
)
def test_http_faults_cannot_be_reported_as_assignment_boundary_proof(template, violation):
    with assignment_case(template, violation=violation) as (args, _, _):
        with pytest.raises(AssertionError):
            probe.verify_assignment_boundaries(*args)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "violation",
    [
        "positive_not_persisted",
        "readonly_mutation",
        "peer_list_leak",
        "peer_detail_leak",
        "restore_failure",
    ],
)
def test_positive_assignment_requires_persistence_least_privilege_isolation_and_restoration(
    template, violation
):
    with assignment_case(template, read_scope="assigned", violation=violation) as (args, _, _):
        with pytest.raises(AssertionError):
            probe.verify_assignment_boundaries(*args)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_approved_restricted_assign_cannot_escape_its_row_scope(template):
    with assignment_case(
        template, assign_scope=("service", "assigned"), violation="foreign_row"
    ) as (args, _, _):
        with pytest.raises(AssertionError, match="foreign_row_denied"):
            probe.verify_assignment_boundaries(*args)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_native_denial_server_error_diagnostics_remain_safe_and_fail_closed(template):
    status = 500 if template == "fastapiadmin" else 200
    response = httpx.Response(
        status,
        headers={"X-Debug-Token": "header-secret"},
        json={
            "code": 500,
            "msg": "系统异常 body-secret",
            "detail": "exception-secret",
            "data": {"token": "data-secret"},
        },
    )
    with assignment_case(template, denial_response=response) as (args, _, _):
        with pytest.raises(AssertionError) as error:
            probe.verify_assignment_boundaries(*args)
    message = str(error.value)
    assert "own_only_assignee_denied" in message and "entity=requests" in message
    assert f"http_status={status}, response_code=500" in message
    assert len(message) < 240
    assert all(part not in message for part in ["secret", "系统异常", "X-Debug-Token", "Bearer"])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "code",
    [True, False, "400", "token-secret", 400.0, None, [400], {"token": "secret"}, 10**500],
)
def test_native_denial_diagnostics_do_not_echo_noninteger_or_unbounded_codes(template, code):
    response = httpx.Response(200, json={"code": code, "msg": "message-secret"})
    with assignment_case(template, denial_response=response) as (args, _, _):
        with pytest.raises(AssertionError) as error:
            probe.verify_assignment_boundaries(*args)
    message = str(error.value)
    assert "http_status=200, response_code=None" in message
    assert "secret" not in message
    assert len(message) < 240


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("body", [b"<html>body-secret</html>", b"[400]", b"null", b'"secret"'])
def test_native_denial_diagnostics_handle_malformed_or_nonobject_bodies(template, body):
    response = httpx.Response(200, content=body)
    with assignment_case(template, denial_response=response) as (args, _, _):
        with pytest.raises(AssertionError) as error:
            probe.verify_assignment_boundaries(*args)
    message = str(error.value)
    assert "http_status=200, response_code=None" in message
    assert "secret" not in message and "html" not in message
    assert len(message) < 240
````
