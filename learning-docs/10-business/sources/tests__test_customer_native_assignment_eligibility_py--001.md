# tests/test_customer_native_assignment_eligibility.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.symbols`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_assignment`（L20–L131）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Run unmodified native functions over SQLite; no native server is claimed here.。 调用`declarative_base`、`runpy.run_path`、`str`、`policy["Policy"]`、`ast.parse`、`path.read_text`、`getattr`、`exec`、`compile`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `native_assignment.Task`（L24–L31）：继承`base`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `native_assignment.User`（L33–L37）：继承`base`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `native_assignment.Role`（L39–L44）：继承`base`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `native_assignment.Membership`（L46–L49）：继承`base`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `native_assignment.event`（L68–L69）：接收`*args`。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_assignment.AsyncSession`（L109–L120）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `native_assignment.AsyncSession.scalar`（L110–L111）：接收`statement`。 调用`session.scalar`。 返回路径：L111的`session.scalar(statement)`。
- `native_assignment.AsyncSession.scalars`（L113–L114）：接收`statement`。 调用`session.scalars`。 返回路径：L114的`session.scalars(statement)`。
- `native_assignment.AsyncSession.flush`（L116–L117）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`session.flush`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_assignment.AsyncSession.commit`（L119–L120）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`session.commit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fastapi_native_assignee_needs_read_and_receiving_scope`（L136–L158）：接收`native_assignment`、`scope`、`actions`。 控制顺序：L142按`scope in {"all", "assigned"} and "read" in actions`分支；L143断言`asyncio.run(call)["assignee_id"] == 2`；L144断言`fixture.events == ["assigned"]`；L145断言`asyncio.run( fixture.runtime.record( fixture.db, {"id": "2", "role": "employee"}, "ta…`；L156断言`error.value.status_code == 422`；L157断言`fixture.session.get(fixture.Task, 1).assignee_id is None`；L158断言`fixture.events == []`。 调用`fixture.permissions[1].update`、`fixture.runtime.mutate`、`asyncio.run`、`fixture.runtime.record`、`pytest.raises`、`fixture.session.get`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fastapi_assignment_keeps_actor_acl_and_target_boundaries`（L164–L195）：接收`native_assignment`、`failure`。 控制顺序：L166按`failure == "no_action"`分支；L168按`failure == "outside_actor_scope"`分支；L170按`failure == "inactive"`分支；L185断言`error.value.status_code == { "no_action": 403, "outside_actor_scope": 404, "inactive"…`；L194断言`fixture.session.get(fixture.Task, 2).assignee_id is None`；L195断言`fixture.events == []`。 调用`fixture.session.get`、`pytest.raises`、`asyncio.run`、`fixture.runtime.mutate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_read_only_native_assignee_gains_no_mutation_actions`（L199–L214）：接收`native_assignment`、`action`。 控制顺序：L212断言`error.value.status_code == 403`；L213断言`fixture.session.get(fixture.Task, 1).assignee_id == 2`；L214断言`fixture.events == ["assigned"]`。 调用`asyncio.run`、`fixture.runtime.mutate`、`pytest.raises`、`fixture.session.get`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fastapi_selector_source_matches_read_only_eligibility`（L217–L227）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L223断言`"p.role === u.role && p.entity === tab.value" in selector`；L224断言`"['all', 'assigned'].includes(p.scope) && p.actions.includes('read')" in selector`；L225断言`"'update'" not in selector and "'transition'" not in selector`；L226断言`"v-if=\"can('assign')\"" in source`；L227断言`parse_file(path)["parse_error"] is False`。 调用`path.read_text`、`next`、`source.splitlines`、`line.startswith`、`parse_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_selector_uses_server_eligibility_without_limiting_role_admin_users`（L230–L241）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L233断言`"eligibleEntities: string[]" in source`；L234断言`"users.value.filter(user => user.eligibleEntities?.includes(props.entity))" in source`；L235断言`"return userOptions.value.filter(option => eligible.has(option.value));" in source`；L239断言`':options="assigneeOptions"' in assignment`；L240断言`'v-model:value="selectedUser" :options="userOptions"' in source`；L241断言`parse_file(path)["parse_error"] is False`。 调用`path.read_text`、`next`、`source.splitlines`、`parse_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_source_guards_target_receiving_scope_and_actor_row_acl`（L244–L273）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L250断言`"Set<String> roleSet=rolesFor(user);" in helper`；L251断言`'!p.path("entity").asText().equals(name)' in helper`；L252断言`'!roleSet.contains(p.path("role").asText())' in helper`；L253断言`'!contains(p.path("actions"),"read")) continue;' in helper`；L254断言`'if(scope.equals("all")\|\|scope.equals("assigned")) return true;' in helper`；L255断言`"return false;" in helper`；L256断言`all('"' + action + '"' not in helper for action in ["own", "update", "transition"])`；L258断言`action.index("require(name,row,action)") < action.index('if(action.equals("assign"))'…`。后续分支沿下方源码相同行号继续阅读。 调用`path.read_text`、`source.split("private boolean eligibleAssignee(", 1)[1].split`、`source.split`、`all`、`source.split("public Object action(", 1)[1].split`、`action.index`、`source.split("public Object users()", 1)[1].split`、`parse_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_yudao_ineligible_assignee_uses_pinned_native_client_error_mapping`（L276–L318）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Source contract only; real HTTP status and rollback are checked by native CI.。 控制顺序：L279断言`"import cn.iocoder.yudao.framework.common.exception.ServiceException;" in source`；L280断言`( "import static cn.iocoder.yudao.framework.common.exception.enums." "GlobalErrorCode…`；L284断言`source.count( 'new ServiceException(BAD_REQUEST.getCode(),"Assignee cannot handle thi…`；L290断言`( "private IllegalArgumentException bad(String detail) " "{ return new IllegalArgumen…`；L294断言`( "private AccessDeniedException denied() { return new AccessDeniedException(" '"Busi…`；L298断言`"catch(IllegalArgumentException ignored)" in source`；L311断言`"this.code = code;" in constructor and "this.message = message;" in constructor`；L312断言`"ErrorCode BAD_REQUEST = new ErrorCode(400," in codes`。后续分支沿下方源码相同行号继续阅读。 调用`(ROOT / "templates/business/yudao/RndBusinessService.java").read_…`、`source.count`、`ZipFile`、`archive.read(common + "exception/ServiceException.java").decode`、`archive.read`、`archive.read(common + "exception/enums/GlobalErrorCodeConstants.j…`、`archive.read(web + "GlobalExceptionHandler.java").decode`、`exception.split`、`constructor.split`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_customer_native_assignment_eligibility.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L318。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12702`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_native_assignment_eligibility.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6fdb73ae5a9ec75d8e7f1dde37c412ac5d5637e33fdcf80d3cb2375b660d2292"} -->
````python
# tests/test_customer_native_assignment_eligibility.py
"""Native assignment eligibility: executed Python ORM checks and Java/Vue source guards."""

import ast
import asyncio
import runpy
from datetime import UTC, datetime
from types import SimpleNamespace
from zipfile import ZipFile

import pytest
from fastapi import HTTPException
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import Session, declarative_base

from workbench.settings import ROOT
from workbench.symbols import parse_file


@pytest.fixture
def native_assignment():
    """Run unmodified native functions over SQLite; no native server is claimed here."""
    base = declarative_base()

    class Task(base):
        __tablename__ = "tasks"
        id = Column(Integer, primary_key=True)
        created_id = Column(Integer)
        assignee_id = Column(Integer)
        is_deleted = Column(Boolean, default=False)
        updated_id = Column(Integer)
        updated_time = Column(DateTime)

    class User(base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        is_deleted = Column(Boolean, default=False)
        status = Column(Integer, default=0)

    class Role(base):
        __tablename__ = "roles"
        id = Column(Integer, primary_key=True)
        code = Column(String)
        is_deleted = Column(Boolean, default=False)
        status = Column(Integer, default=0)

    class Membership(base):
        __tablename__ = "memberships"
        user_id = Column(Integer, primary_key=True)
        role_id = Column(Integer, primary_key=True)

    permissions = [
        {"role": "manager", "entity": "tasks", "scope": "all", "actions": ["read", "assign"]},
        {"role": "employee", "entity": "tasks", "scope": "assigned", "actions": ["read"]},
    ]
    plan = {
        "entities": [{"name": "tasks"}],
        "business": {
            "permissions": permissions,
            "roles": [{"name": role} for role in ["manager", "employee"]],
            "resources": [{"entity": "tasks", "assignee_field": "assignee_id"}],
            "workflows": [],
            "relations": [],
        },
    }
    policy = runpy.run_path(str(ROOT / "templates/business/common/policy.py"))
    events = []

    async def event(*args):
        events.append(args[4])

    namespace = {
        "SPEC": plan["business"],
        "POLICY": policy["Policy"](plan),
        "PolicyError": policy["PolicyError"],
        "MODELS": {"tasks": Task},
        "UserModel": User,
        "RoleModel": Role,
        "UserRolesModel": Membership,
        "ROLE_PREFIX": "test_",
        "HTTPException": HTTPException,
        "select": select,
        "datetime": datetime,
        "UTC": UTC,
        "serialize": lambda row, entity: {"id": row.id, "assignee_id": row.assignee_id},
        "event": event,
    }
    path = ROOT / "templates/business/fastapiadmin/runtime.py"
    names = {"fail", "identifier", "grant", "scope", "record", "mutate"}
    nodes = [
        node
        for node in ast.parse(path.read_text(encoding="utf-8")).body
        if getattr(node, "name", None) in names
    ]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    engine = create_engine("sqlite://")
    base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        session.add_all(
            [
                Task(id=1, created_id=1),
                Task(id=2, created_id=3),
                User(id=2),
                Role(id=1, code="test_employee"),
                Membership(user_id=2, role_id=1),
            ]
        )
        session.commit()

        class AsyncSession:
            async def scalar(self, statement):
                return session.scalar(statement)

            async def scalars(self, statement):
                return session.scalars(statement)

            async def flush(self):
                session.flush()

            async def commit(self):
                session.commit()

        yield SimpleNamespace(
            runtime=SimpleNamespace(**namespace),
            db=AsyncSession(),
            permissions=permissions,
            events=events,
            session=session,
            Task=Task,
            User=User,
        )
    engine.dispose()


@pytest.mark.parametrize("scope", ["all", "assigned", "own"])
@pytest.mark.parametrize("actions", [["read"], ["update", "transition"]])
def test_fastapi_native_assignee_needs_read_and_receiving_scope(native_assignment, scope, actions):
    fixture = native_assignment
    fixture.permissions[1].update(scope=scope, actions=actions)
    call = fixture.runtime.mutate(
        fixture.db, {"id": "1", "role": "manager"}, "tasks", 1, "assign", {"assignee": "2"}
    )
    if scope in {"all", "assigned"} and "read" in actions:
        assert asyncio.run(call)["assignee_id"] == 2
        assert fixture.events == ["assigned"]
        assert (
            asyncio.run(
                fixture.runtime.record(
                    fixture.db, {"id": "2", "role": "employee"}, "tasks", 1, "read"
                )
            ).assignee_id
            == 2
        )
    else:
        with pytest.raises(HTTPException) as error:
            asyncio.run(call)
        assert error.value.status_code == 422
        assert fixture.session.get(fixture.Task, 1).assignee_id is None
        assert fixture.events == []


@pytest.mark.parametrize(
    "failure", ["no_action", "outside_actor_scope", "inactive", "other_entity"]
)
def test_fastapi_assignment_keeps_actor_acl_and_target_boundaries(native_assignment, failure):
    fixture = native_assignment
    if failure == "no_action":
        fixture.permissions[0]["actions"] = ["read"]
    elif failure == "outside_actor_scope":
        fixture.permissions[0]["scope"] = "own"
    elif failure == "inactive":
        fixture.session.get(fixture.User, 2).status = 1
    else:
        fixture.permissions[1]["entity"] = "requests"
    with pytest.raises(HTTPException) as error:
        asyncio.run(
            fixture.runtime.mutate(
                fixture.db,
                {"id": "1", "role": "manager"},
                "tasks",
                2,
                "assign",
                {"assignee": "2"},
            )
        )
    assert (
        error.value.status_code
        == {
            "no_action": 403,
            "outside_actor_scope": 404,
            "inactive": 422,
            "other_entity": 422,
        }[failure]
    )
    assert fixture.session.get(fixture.Task, 2).assignee_id is None
    assert fixture.events == []


@pytest.mark.parametrize("action", ["update", "assign", "transition", "add_note", "archive"])
def test_read_only_native_assignee_gains_no_mutation_actions(native_assignment, action):
    fixture = native_assignment
    asyncio.run(
        fixture.runtime.mutate(
            fixture.db, {"id": "1", "role": "manager"}, "tasks", 1, "assign", {"assignee": "2"}
        )
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(
            fixture.runtime.mutate(
                fixture.db, {"id": "2", "role": "employee"}, "tasks", 1, action, {}
            )
        )
    assert error.value.status_code == 403
    assert fixture.session.get(fixture.Task, 1).assignee_id == 2
    assert fixture.events == ["assigned"]


def test_fastapi_selector_source_matches_read_only_eligibility():
    path = ROOT / "templates/business/fastapiadmin/index.vue"
    source = path.read_text(encoding="utf-8")
    selector = next(
        line for line in source.splitlines() if line.startswith("const eligibleUsers =")
    )
    assert "p.role === u.role && p.entity === tab.value" in selector
    assert "['all', 'assigned'].includes(p.scope) && p.actions.includes('read')" in selector
    assert "'update'" not in selector and "'transition'" not in selector
    assert "v-if=\"can('assign')\"" in source
    assert parse_file(path)["parse_error"] is False


def test_yudao_selector_uses_server_eligibility_without_limiting_role_admin_users():
    path = ROOT / "templates/business/yudao/panel.vue"
    source = path.read_text(encoding="utf-8")
    assert "eligibleEntities: string[]" in source
    assert "users.value.filter(user => user.eligibleEntities?.includes(props.entity))" in source
    assert "return userOptions.value.filter(option => eligible.has(option.value));" in source
    assignment = next(
        line for line in source.splitlines() if 'data-testid="business-assignee"' in line
    )
    assert ':options="assigneeOptions"' in assignment
    assert 'v-model:value="selectedUser" :options="userOptions"' in source
    assert parse_file(path)["parse_error"] is False


def test_yudao_source_guards_target_receiving_scope_and_actor_row_acl():
    path = ROOT / "templates/business/yudao/RndBusinessService.java"
    source = path.read_text(encoding="utf-8")
    helper = source.split("private boolean eligibleAssignee(", 1)[1].split(
        "private void require(", 1
    )[0]
    assert "Set<String> roleSet=rolesFor(user);" in helper
    assert '!p.path("entity").asText().equals(name)' in helper
    assert '!roleSet.contains(p.path("role").asText())' in helper
    assert '!contains(p.path("actions"),"read")) continue;' in helper
    assert 'if(scope.equals("all")||scope.equals("assigned")) return true;' in helper
    assert "return false;" in helper
    assert all('"' + action + '"' not in helper for action in ["own", "update", "transition"])
    action = source.split("public Object action(", 1)[1].split("public Object related(", 1)[0]
    assert action.index("require(name,row,action)") < action.index('if(action.equals("assign"))')
    assert (
        action.index("if(sidecar.activeUser(tenant(),user)==null)")
        < action.index(
            "if(!eligibleAssignee(name,user)) throw new ServiceException("
            'BAD_REQUEST.getCode(),"Assignee cannot handle this resource")'
        )
        < action.index("set(row,wire(field),user)")
        < action.index("persist(name,row)")
        < action.index("event(name,row,action,before,note)")
        < action.index("notify(name,row,notificationEvent,transition,audit)")
    )
    users = source.split("public Object users()", 1)[1].split("public void changeRole(", 1)[0]
    assert 'eligibleAssignee(name,number(user.get("id")))' in users
    assert 'user.put("eligibleEntities",eligibleEntities)' in users
    assert parse_file(path)["parse_error"] is False


def test_yudao_ineligible_assignee_uses_pinned_native_client_error_mapping():
    """Source contract only; real HTTP status and rollback are checked by native CI."""
    source = (ROOT / "templates/business/yudao/RndBusinessService.java").read_text(encoding="utf-8")
    assert "import cn.iocoder.yudao.framework.common.exception.ServiceException;" in source
    assert (
        "import static cn.iocoder.yudao.framework.common.exception.enums."
        "GlobalErrorCodeConstants.BAD_REQUEST;"
    ) in source
    assert (
        source.count(
            'new ServiceException(BAD_REQUEST.getCode(),"Assignee cannot handle this resource")'
        )
        == 1
    )
    assert (
        "private IllegalArgumentException bad(String detail) "
        "{ return new IllegalArgumentException(detail); }"
    ) in source
    assert (
        "private AccessDeniedException denied() { return new AccessDeniedException("
        '"Business permission denied"); }'
    ) in source
    assert "catch(IllegalArgumentException ignored)" in source

    common = "yudao-framework/yudao-common/src/main/java/cn/iocoder/yudao/framework/common/"
    web = (
        "yudao-framework/yudao-spring-boot-starter-web/src/main/java/"
        "cn/iocoder/yudao/framework/web/core/handler/"
    )
    with ZipFile(ROOT / "templates/vendor/yudao-backend.zip") as archive:
        exception = archive.read(common + "exception/ServiceException.java").decode()
        codes = archive.read(common + "exception/enums/GlobalErrorCodeConstants.java").decode()
        handler = archive.read(web + "GlobalExceptionHandler.java").decode()
    constructor = exception.split("public ServiceException(Integer code, String message)", 1)[1]
    constructor = constructor.split("}", 1)[0]
    assert "this.code = code;" in constructor and "this.message = message;" in constructor
    assert "ErrorCode BAD_REQUEST = new ErrorCode(400," in codes
    assert "@ExceptionHandler(value = ServiceException.class)" in handler
    mapping = handler.split(
        "public CommonResult<?> serviceExceptionHandler(ServiceException ex)", 1
    )[1]
    mapping = mapping.split("@ExceptionHandler(value = Exception.class)", 1)[0]
    assert "return CommonResult.error(ex.getCode(), ex.getMessage());" in mapping
````
