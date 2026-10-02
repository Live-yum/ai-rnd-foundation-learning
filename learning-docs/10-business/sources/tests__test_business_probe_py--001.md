# tests/test_business_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_public_registration_is_anonymous_and_requires_native_default_role`（L11–L78）：接收`monkeypatch`、`violation`。 控制顺序：L59按`violation`分支；L67断言`all(client.is_closed for client in clients)`；L75断言`identifier == "8"`；L77断言`registered == [True]`；L78断言`len(logins) == (0 if violation == "registration_denied" else 1)`。 调用`monkeypatch.setattr`、`pytest.raises`、`probe.register_fastapi_actor`、`all`、`actor.close`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_public_registration_is_anonymous_and_requires_native_default_role.handler`（L15–L46）：接收`request`。 控制顺序：L16按`request.url.path == "/system/user/register"`分支；L17断言`"authorization" not in request.headers`；L21断言`body["is_superuser"] is True and body["role_ids"] == [1]`；L23按`violation == "registration_denied"`分支；L26按`request.url.path == "/business/configuration"`分支；L27断言`request.headers["Authorization"] == "Bearer synthetic-test-token"`；L37断言`request.url.path == "/system/user/current/info"`；L44按`violation == "menu_scope"`分支。 调用`json.loads`、`registered.append`、`httpx.Response`、`data["menus"].append`。 返回路径：L24的`httpx.Response(409, json={"code": 409})`；L46的`httpx.Response(200, json={"code": 200, "data": data})`。
- `test_public_registration_is_anonymous_and_requires_native_default_role.factory`（L48–L51）：接收`**kwargs`。 调用`original_client`、`httpx.MockTransport`、`clients.append`。 返回路径：L51的`client`。
- `test_public_registration_is_anonymous_and_requires_native_default_role.login`（L53–L55）：接收`*args`。 调用`logins.append`。 返回路径：L55的`"synthetic-test-token"`。
- `test_yudao_registration_requires_native_anonymous_default_membership`（L85–L130）：接收`monkeypatch`、`violation`。 控制顺序：L121按`violation`分支；L128断言`identifier == "8"`；L130断言`all(client.is_closed for client in clients)`。 调用`monkeypatch.setattr`、`pytest.raises`、`probe.register_yudao_actor`、`actor.close`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_registration_requires_native_anonymous_default_membership.handler`（L91–L112）：接收`request`。 控制顺序：L92按`request.url.path == "/admin-api/system/auth/register"`分支；L93断言`"authorization" not in request.headers`；L94断言`request.headers["tenant-id"] == "1"`；L96断言`body["roleIds"] == [1] and body["roles"] == ["super_admin"]`；L97按`violation == "registration_denied"`分支；L100按`request.url.path.endswith("/me")`分支；L106断言`request.url.path == "/admin-api/system/auth/get-permission-info"`。 调用`json.loads`、`httpx.Response`、`request.url.path.endswith`。 返回路径：L98的`httpx.Response(200, json={"code": 403})`；L112的`httpx.Response(200, json={"code": 0, "data": data})`。
- `test_yudao_registration_requires_native_anonymous_default_membership.factory`（L114–L117）：接收`**kwargs`。 调用`original_client`、`httpx.MockTransport`、`clients.append`。 返回路径：L117的`client`。
- `reminder_case`（L133–L194）：接收`template`、`violation`。 调用`Plan.model_validate`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Client`。 返回路径：L194的`plan, recipients, outsider, emit`。
- `reminder_case.Client`（L145–L168）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `reminder_case.Client.__init__`（L146–L147）：接收`role`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `reminder_case.Client.inbox`（L149–L150）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L150的`[row for recipient, row in store if recipient is self]`。
- `reminder_case.Client.read_notice`（L152–L168）：接收`identifier`。 控制顺序：L156按`not matches and violation != "wrong_recipient"`分支；L160按`matches and violation != "unread"`分支。 调用`matches[0].update`、`httpx.Response`、`httpx.Request`。 返回路径：L164的`httpx.Response( 200, json={"code": code, "data": True}, request=httpx.Request("POST", "htt…`。
- `reminder_case.emit`（L173–L192）：接收`entity`、`identifier`、`event`、`transition`。 控制顺序：L175遍历`expected`；L176按`violation in {"missing_due", "missing"} and ( event == "due" or violation == "missing…`分支；L180遍历`range( 2 if violation == "duplicated_due" and event == "due" or v…`。 调用`probe.reminder_recipients`、`range`、`str`、`len`、`row.update`、`store.append`。 返回路径：L192的`"action result"`。
- `test_assignment_due_idempotency_and_read_recipient_are_required`（L202–L216）：接收`template`、`violation`、`recipient`。 控制顺序：L204遍历`plan.business.notifications`；L205按`notice.event in {"assigned", "due"}`分支；L208遍历`[("requests", "2"), ("tasks", "3")]`；L210遍历`["assigned", "due"]`；L212按`violation`分支。 调用`reminder_case`、`records.append`、`emit`、`pytest.raises`、`probe.verify_reminders`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_note_or_transition_requires_its_own_persisted_routed_reminder`（L228–L246）：接收`template`、`event`、`transition`、`recipient`、`violation`。 控制顺序：L232遍历`plan.business.notifications`；L233按`(notice.entity, notice.event, notice.transition) == ("requests", event, transition)`分支；L242按`violation`分支；L246断言`probe.verify_event_reminders(*args) == "action result"`。 调用`reminder_case`、`emit`、`pytest.raises`、`probe.verify_event_reminders`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_note_or_transition_requires_its_own_persisted_routed_reminder.action`（L238–L239）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`emit`。 返回路径：L239的`emit("requests", "2", event, transition)`。
- `test_handling_history_uses_required_service_grant_and_exact_employee_permissions`（L254–L338）：接收`template`、`employee_grant`、`violation`。 控制顺序：L270按`not employee_grant`分支；L326按`violation`分支；L335断言`{role for role, _ in calls} == {"manager", "service", "employee", "outsider"}`；L337遍历`clients`。 调用`Plan.model_validate`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`permission.actions.remove`、`client`、`pytest.raises`、`probe.verify_handling_history`、`actor.close`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_handling_history_uses_required_service_grant_and_exact_employee_permissions.client`（L276–L320）：接收`role`。 调用`object.__new__`、`httpx.Client`、`httpx.MockTransport`、`clients.append`。 返回路径：L320的`actor`。
- `test_handling_history_uses_required_service_grant_and_exact_employee_permissions.client.handler`（L277–L311）：接收`request`。 控制顺序：L284断言`request.url.path == expected`；L285按`not fastapi`分支；L286断言`request.url.params["entity"] == "requests" and request.url.params["id"] == "2"`；L289按`role == "manager"`分支；L290断言`request.url.params["audit"] == "true"`；L292按`role == "employee" and not employee_grant and violation == "employee_history"`分支；L294按`role == "outsider" and violation == "outsider_history"`分支；L296按`not permitted`分支。后续分支沿下方源码相同行号继续阅读。 调用`calls.append`、`httpx.Response`、`{ "service": "service_history", "manager": "manager_audit", "empl…`、`str`、`range`。 返回路径：L297的`httpx.Response(403 if fastapi else 200, json={"code": 403})`；L305的`httpx.Response( 200, json={ "code": 200 if fastapi else 0, "data": [{"id": str(i)} for i i…`。

</details>

**创建路径：** `tests/test_business_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L338。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13292`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5c122e09b0d2fbaf9c485b519e70cf5f021f1986adad9c51629b196d428ed0db"} -->
````python
# tests/test_business_probe.py
import httpx
import pytest

from workbench import business_probe as probe


@pytest.mark.parametrize(
    "violation",
    [None, "role", "identity", "global_admin", "menus", "menu_scope", "registration_denied"],
)
def test_public_registration_is_anonymous_and_requires_native_default_role(monkeypatch, violation):
    original_client = httpx.Client
    clients, registered, logins = [], [], []

    def handler(request):
        if request.url.path == "/system/user/register":
            assert "authorization" not in request.headers
            import json

            body = json.loads(request.content)
            assert body["is_superuser"] is True and body["role_ids"] == [1]
            registered.append(True)
            if violation == "registration_denied":
                return httpx.Response(409, json={"code": 409})
            data = {"id": 8}
        elif request.url.path == "/business/configuration":
            assert request.headers["Authorization"] == "Bearer synthetic-test-token"
            data = {
                "actor": {
                    "id": "9" if violation == "identity" else "8",
                    "role": "manager" if violation == "role" else "employee",
                },
                "can_manage_roles": False,
                "permissions": [{"entity": "customers", "actions": ["read"]}],
            }
        else:
            assert request.url.path == "/system/user/current/info"
            data = {
                "is_superuser": violation == "global_admin",
                "menus": []
                if violation == "menus"
                else [{"id": 10, "component_path": "module_rnd/customers/index"}],
            }
            if violation == "menu_scope":
                data["menus"].append({"id": 11, "component_path": "module_rnd/tasks/index"})
        return httpx.Response(200, json={"code": 200, "data": data})

    def factory(**kwargs):
        client = original_client(**kwargs, transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    def login(*args):
        logins.append(args)
        return "synthetic-test-token"

    monkeypatch.setattr(probe.httpx, "Client", factory)
    monkeypatch.setattr(probe, "login", login)
    if violation:
        with pytest.raises(AssertionError):
            probe.register_fastapi_actor(
                "http://127.0.0.1",
                "syntheticuser",
                "SyntheticPass123!",
                [{"entity": "customers"}, {"entity": "tasks"}],
            )
        assert all(client.is_closed for client in clients)
    else:
        identifier, actor = probe.register_fastapi_actor(
            "http://127.0.0.1",
            "syntheticuser",
            "SyntheticPass123!",
            [{"entity": "customers"}, {"entity": "tasks"}],
        )
        assert identifier == "8"
        actor.close()
    assert registered == [True]
    assert len(logins) == (0 if violation == "registration_denied" else 1)


@pytest.mark.parametrize(
    "violation",
    [None, "role", "identity", "global_admin", "permissions", "menus", "registration_denied"],
)
def test_yudao_registration_requires_native_anonymous_default_membership(monkeypatch, violation):
    import json

    original_client = httpx.Client
    clients = []

    def handler(request):
        if request.url.path == "/admin-api/system/auth/register":
            assert "authorization" not in request.headers
            assert request.headers["tenant-id"] == "1"
            body = json.loads(request.content)
            assert body["roleIds"] == [1] and body["roles"] == ["super_admin"]
            if violation == "registration_denied":
                return httpx.Response(200, json={"code": 403})
            data = {"userId": 8}
        elif request.url.path.endswith("/me"):
            data = {
                "id": "9" if violation == "identity" else "8",
                "roles": ["manager" if violation == "role" else "employee"],
            }
        else:
            assert request.url.path == "/admin-api/system/auth/get-permission-info"
            data = {
                "roles": ["super_admin"] if violation == "global_admin" else ["rnd_employee"],
                "permissions": ["*:*:*"] if violation == "permissions" else ["infra:rnd:query"],
                "menus": [] if violation == "menus" else [{"id": 20}],
            }
        return httpx.Response(200, json={"code": 0, "data": data})

    def factory(**kwargs):
        client = original_client(**kwargs, transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    monkeypatch.setattr(probe.httpx, "Client", factory)
    monkeypatch.setattr(probe, "login", lambda *args: "synthetic-test-token")
    if violation:
        with pytest.raises(AssertionError):
            probe.register_yudao_actor("http://127.0.0.1", "syntheticuser", "Synthetic123!", [])
    else:
        identifier, actor = probe.register_yudao_actor(
            "http://127.0.0.1", "syntheticuser", "Synthetic123!", []
        )
        assert identifier == "8"
        actor.close()
    assert all(client.is_closed for client in clients)


def reminder_case(template, violation=None):
    import json

    from workbench.domain import Plan
    from workbench.settings import ROOT

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    fastapi = template == "fastapiadmin"
    store = []

    class Client:
        def __init__(self, role):
            self.role = role

        def inbox(self):
            return [row for recipient, row in store if recipient is self]

        def read_notice(self, identifier):
            matches = [
                row for recipient, row in store if row["id"] == identifier and recipient is self
            ]
            if not matches and violation != "wrong_recipient":
                code = 403
            else:
                code = 200 if fastapi else 0
                if matches and violation != "unread":
                    matches[0].update(
                        {"read": True} if fastapi else {"read_at": "2026-09-30T00:00:00Z"}
                    )
            return httpx.Response(
                200,
                json={"code": code, "data": True},
                request=httpx.Request("POST", "http://127.0.0.1/read"),
            )

    creator, assignee, outsider = [Client(role) for role in ["creator", "assignee", "outsider"]]
    recipients = {"creator": creator, "assignee": assignee}

    def emit(entity, identifier, event, transition=None):
        expected = probe.reminder_recipients(plan, entity, event, recipients, transition)
        for recipient in expected:
            if violation in {"missing_due", "missing"} and (
                event == "due" or violation == "missing"
            ):
                continue
            for _ in range(
                2
                if violation == "duplicated_due" and event == "due" or violation == "duplicated"
                else 1
            ):
                row = {"id": str(len(store) + 1), "entity": entity, "record_id": identifier}
                row.update(
                    {"event": event, "read": False}
                    if fastapi
                    else {"message": f"{entity} #{identifier} {event}", "read_at": None}
                )
                store.append((outsider if violation == "misrouted" else recipient, row))
        return "action result"

    return plan, recipients, outsider, emit


@pytest.mark.parametrize(
    "violation", [None, "missing_due", "duplicated_due", "unread", "wrong_recipient", "misrouted"]
)
@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("recipient", ["creator", "assignee"])
def test_assignment_due_idempotency_and_read_recipient_are_required(template, violation, recipient):
    plan, recipients, outsider, emit = reminder_case(template, violation)
    for notice in plan.business.notifications:
        if notice.event in {"assigned", "due"}:
            notice.recipient = recipient
    records = []
    for entity, identifier in [("requests", "2"), ("tasks", "3")]:
        records.append((entity, identifier, recipients["creator"], recipients["assignee"]))
        for event in ["assigned", "due"]:
            emit(entity, identifier, event)
    if violation:
        with pytest.raises(AssertionError):
            probe.verify_reminders(plan, records, [outsider])
    else:
        probe.verify_reminders(plan, records, [outsider])


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize(
    "event,transition",
    [("note_added", None), ("transitioned", "start"), ("transitioned", "resolve")],
)
@pytest.mark.parametrize("recipient", ["creator", "assignee"])
@pytest.mark.parametrize(
    "violation", [None, "missing", "duplicated", "misrouted", "unread", "wrong_recipient"]
)
def test_each_note_or_transition_requires_its_own_persisted_routed_reminder(
    template, event, transition, recipient, violation
):
    plan, recipients, outsider, emit = reminder_case(template, violation)
    for notice in plan.business.notifications:
        if (notice.entity, notice.event, notice.transition) == ("requests", event, transition):
            notice.recipient = recipient
    # Pre-existing notifications cannot stand in for a missing current event.
    emit("requests", "2", event, transition)

    def action():
        return emit("requests", "2", event, transition)

    args = (plan, "requests", "2", event, recipients, [outsider], action, transition)
    if violation:
        with pytest.raises(AssertionError):
            probe.verify_event_reminders(*args)
    else:
        assert probe.verify_event_reminders(*args) == "action result"


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("employee_grant", [False, True])
@pytest.mark.parametrize(
    "violation", [None, "service_history", "manager_audit", "employee_history", "outsider_history"]
)
def test_handling_history_uses_required_service_grant_and_exact_employee_permissions(
    template, employee_grant, violation
):
    import json

    from workbench.domain import Plan
    from workbench.settings import ROOT

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    permission = next(
        grant
        for grant in plan.business.permissions
        if grant.role == "employee" and grant.entity == "requests"
    )
    if not employee_grant:
        permission.actions.remove("read_history")
    fastapi = template == "fastapiadmin"
    calls = []
    clients = []

    def client(role):
        def handler(request):
            calls.append((role, request.url))
            expected = (
                "/business/requests/2/history"
                if fastapi
                else "/admin-api/infra/rnd-business/history"
            )
            assert request.url.path == expected
            if not fastapi:
                assert (
                    request.url.params["entity"] == "requests" and request.url.params["id"] == "2"
                )
            if role == "manager":
                assert request.url.params["audit"] == "true"
            permitted = role in {"manager", "service"} or role == "employee" and employee_grant
            if role == "employee" and not employee_grant and violation == "employee_history":
                permitted = True
            if role == "outsider" and violation == "outsider_history":
                permitted = True
            if not permitted:
                return httpx.Response(403 if fastapi else 200, json={"code": 403})
            count = 4
            if violation == {
                "service": "service_history",
                "manager": "manager_audit",
                "employee": "employee_history",
            }.get(role):
                count = 3
            return httpx.Response(
                200,
                json={
                    "code": 200 if fastapi else 0,
                    "data": [{"id": str(i)} for i in range(count)],
                },
            )

        actor = object.__new__(probe.BusinessClient)
        actor.fastapi = fastapi
        actor.prefix = "/business" if fastapi else "/admin-api/infra/rnd-business"
        actor.http = httpx.Client(
            base_url="http://127.0.0.1", transport=httpx.MockTransport(handler)
        )
        clients.append(actor)
        return actor

    manager, service, employee, outsider = [
        client(role) for role in ["manager", "service", "employee", "outsider"]
    ]
    try:
        if violation:
            with pytest.raises(AssertionError):
                probe.verify_handling_history(
                    plan, manager, service, employee, outsider, "requests", "2"
                )
        else:
            probe.verify_handling_history(
                plan, manager, service, employee, outsider, "requests", "2"
            )
            assert {role for role, _ in calls} == {"manager", "service", "employee", "outsider"}
    finally:
        for actor in clients:
            actor.close()
````
