# templates/product/verify_business.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](templates__product__verify_business_py--001.md)

**作用：独立基础产品的组成文件。** 独立客服HTTP/浏览器验收器：新建自有数据库和三角色合成账号，验证关系、指派、流程、记录、提醒、统计、拒绝路径及重启；截图仅限有界命名PNG，不导出密码或运行数据库。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `verify_business.allowed`（L781–L788）：接收`role`、`entity`、`action`、`row`、`identity`。 控制顺序：L783按`action not in grant.get("actions", [])`分支；L785按`row is None or grant["scope"] == "all"`分支。 调用`grants.get`、`grant.get`、`row.get`。 返回路径：L784的`False`；L786的`True`；L788的`row.get(key) == identity`。
- `verify_business.start`（L829–L870）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L859遍历`range(150)`；L861按`client.get("/health").status_code == 200`分支；L865按`process.poll() is not None`分支；L870抛异常，停止当前正常路径。 调用`socket.socket`、`listener.bind`、`listener.getsockname`、`subprocess.Popen`、`str`、`httpx.Client`、`range`、`client.get`、`process.poll`等。 返回路径：L862的`process, client`。
- `verify_business.request`（L880–L918）：接收`method`、`path`、`actor`、`status`、`**kw`。 控制顺序：L888按`method == "GET" and path == "/business/notifications"`分支；L890按`method == "POST" and status in {200, 201} and path.startswith("/api/")`分支；L894按`len(parts) == 2`分支；L897按`len(parts) == 4`分支；L903按`event`分支；L912按`event`分支；L915遍历`actors.values()`。 调用`client.request`、`check`、`response.json`、`notification_evidence.due`、`path.startswith`、`path.strip("/").split`、`path.strip`、`len`、`notification_evidence.event`等。 返回路径：L918的`result`。
- `verify_business.actor_for`（L1233–L1242）：接收`candidate`、`transition`。 调用`next`、`actors.values`、`allowed`。 返回路径：L1234的`next( ( actor for actor in actors.values() if actor["role"] in transition["roles"] and all…`。
- `verify_business.create_branch`（L1244–L1313）：接收`transition`。 控制顺序：L1252遍历`actors.values()`；L1253按`not ( allowed(creator["role"], entity, "create") and allowed(creator["role"], entity,…`分支；L1258遍历`recipients`；L1262按`assignee and recipient`分支；L1263按`not any( allowed(a["role"], entity, "assign", access, a["id"]) for a in actors.values…`分支；L1272按`path`分支；L1275按`selection`分支；L1289按`assignee and recipient`分支。后续分支沿下方源码相同行号继续阅读。 调用`resources[entity].get`、`workflow_assignee_candidates`、`row.get`、`actors.values`、`allowed`、`any`、`workflow_transition_paths( workflow, lambda step: actor_for(acces…`、`workflow_transition_paths`、`actor_for`等。 返回路径：L1313的`created, path`。
- `verify_business.apply_transition`（L1315–L1338）：接收`candidate`、`transition`、`actor`。 控制顺序：L1326按`transition.get("set_timestamp")`分支。 调用`request`、`check`、`transition.get`、`candidate.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify_business.selected`（L1449–L1465）：接收`row`。 控制顺序：L1450遍历`metric["filters"]`；L1452按`op == "eq" and actual != want or op == "ne" and actual == want or op == "in" and actu…`分支；L1461按`op in {"gte", "lte"} and ( actual is None or (actual < want if op == "gte" else actua…`分支。 调用`row.get`。 返回路径：L1460的`False`；L1464的`False`；L1465的`True`。

</details>

**创建路径：** `templates/product/verify_business.py`；**本文件共有 2 段**。本段覆盖源文件 L781–L1913。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`54884`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/verify_business.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "83ebbe6a5c08121706f06e1731285d4e7329df32703148cceb3f29e135023659"} -->
````python
# templates/product/verify_business.py
    def allowed(role, entity, action, row=None, identity=None):
        grant = grants.get((role, entity), {})
        if action not in grant.get("actions", []):
            return False
        if row is None or grant["scope"] == "all":
            return True
        key = "created_by" if grant["scope"] == "own" else resources[entity]["assignee_field"]
        return row.get(key) == identity

    with tempfile.TemporaryDirectory(prefix="business-verify-") as temporary:
        directory = Path(temporary)
        env = {
            k: v
            for k, v in os.environ.items()
            if k.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP"}
        }
        env.update(
            PRODUCT_DATA_DIR=str(directory / "database"),
            HOME=str(directory),
            USERPROFILE=str(directory),
            PYTHONUTF8="1",
            PYTHONIOENCODING="utf-8",
            PYTHONDONTWRITEBYTECODE="1",
        )
        if selection["database"] == "postgresql":
            target = os.environ.get("VERIFY_DATABASE_URL")
            check(
                bool(target), "Business PostgreSQL requires an owned isolated verification database"
            )
            env["PRODUCT_DATABASE_URL"] = target
        migration = subprocess.run(
            [python, "manage.py", "init"], cwd=product, env=env, capture_output=True, timeout=90
        )
        check(migration.returncode == 0, "Business migration failed")
        bootstrap = "import sys,json,getpass; data=json.load(sys.stdin); getpass.getpass=lambda _:data['password']; import manage; manage.bootstrap_admin(data['username'])"
        result = subprocess.run(
            [python, "-c", bootstrap],
            input=json.dumps({"username": "verify-admin", "password": password}),
            text=True,
            encoding="utf-8",
            cwd=product,
            env=env,
            capture_output=True,
            timeout=30,
        )
        check(result.returncode == 0, "Business bootstrap failed")
        checks.extend(["migration", "business-bootstrap"])

        def start():
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            options = (
                {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                if os.name == "nt"
                else {"start_new_session": True}
            )
            process = subprocess.Popen(
                [
                    python,
                    "-m",
                    "uvicorn",
                    "app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--log-level",
                    "critical",
                ],
                cwd=product,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **options,
            )
            client = httpx.Client(base_url=f"http://127.0.0.1:{port}", trust_env=False, timeout=20)
            for _ in range(150):
                try:
                    if client.get("/health").status_code == 200:
                        return process, client
                except httpx.HTTPError:
                    pass
                if process.poll() is not None:
                    break
                time.sleep(0.1)
            stop(process)
            client.close()
            raise ValueError("Business HTTP startup failed")

        process, client = start()
        actors = {}
        rows = {name: [] for name in fields}
        base = {}
        samples = {}
        create_roles = {}
        try:

            def request(method, path, actor=None, status=200, **kw):
                headers = {"Authorization": "Bearer " + actor["token"]} if actor else {}
                response = client.request(method, path, headers=headers, **kw)
                check(
                    response.status_code == status,
                    f"Business check failed: {method} {path} expected {status}, got {response.status_code}",
                )
                result = response.json() if response.content else None
                if method == "GET" and path == "/business/notifications":
                    notification_evidence.due(rows, actor, allowed)
                if method == "POST" and status in {200, 201} and path.startswith("/api/"):
                    parts = path.strip("/").split("/")
                    entity = parts[1]
                    event = None
                    if len(parts) == 2:
                        event = "created"
                        notification_evidence.event(entity, result, event)
                    elif len(parts) == 4:
                        event = {
                            "assign": "assigned",
                            "transition": "transitioned",
                            "notes": "note_added",
                        }.get(parts[3])
                        if event:
                            row = (
                                next(r for r in rows[entity] if r["id"] == parts[2])
                                if event == "note_added"
                                else result
                            )
                            notification_evidence.event(
                                entity, row, event, kw.get("json", {}).get("transition")
                            )
                    if event:
                        # Check each action before a later transition can mask an omitted
                        # reminder with an extra reminder of the same canonical event.
                        for recipient in actors.values():
                            notices = request("GET", "/business/notifications", recipient)
                            notification_evidence.inbox(recipient, notices, event)
                return result

            token = request(
                "POST", "/auth/login", json={"username": "verify-admin", "password": password}
            )["access_token"]
            bootstrap_actor = {
                "token": token,
                "username": "verify-admin",
                "role": business["bootstrap_role"],
            }
            bootstrap_actor.update(request("GET", "/business/me", bootstrap_actor))
            for role in business["roles"]:
                name = role["name"]
                user = request(
                    "POST",
                    "/business/users",
                    bootstrap_actor,
                    status=201,
                    json={"username": "verify-" + name, "password": password, "role": name},
                )
                token = request(
                    "POST", "/auth/login", json={"username": "verify-" + name, "password": password}
                )["access_token"]
                actors[name] = {**user, "token": token, "role": name}
            registration = client.post(
                "/auth/register", json={"username": "verify-public", "password": password}
            )
            if business["registration"]["enabled"]:
                check(registration.status_code == 201, "Public signup failed")
                public = {"token": registration.json()["access_token"]}
                check(
                    request("GET", "/business/me", public)["role"]
                    == business["registration"]["default_role"],
                    "Signup escalated role",
                )
                check(
                    client.post(
                        "/auth/register",
                        json={
                            "username": "verify-forged",
                            "password": password,
                            "role": business["bootstrap_role"],
                        },
                    ).status_code
                    == 422,
                    "Signup accepted forged role",
                )
            else:
                check(registration.status_code == 403, "Disabled public signup accepted")
            checks.append("business-role-default")
            pending = list(fields)
            while pending:
                progress = False
                for entity in list(pending):
                    relations = [
                        r
                        for r in business["relations"]
                        if r["entity"] == entity and r["target_entity"] != "$users"
                    ]
                    if any(r["target_entity"] not in base for r in relations):
                        continue
                    candidates = [
                        a
                        for a in actors.values()
                        if allowed(a["role"], entity, "create")
                        and allowed(a["role"], entity, "read")
                    ]
                    check(bool(candidates), "No permitted create/read actor for resource " + entity)
                    creator = next(
                        (a for a in candidates if a["role"] == business["bootstrap_role"]),
                        candidates[0],
                    )
                    create_roles[entity] = creator["role"]
                    protected = {
                        "id",
                        "owner_id",
                        "created_by",
                        "created_at",
                        "updated_at",
                        "archived_at",
                        resources[entity].get("assignee_field"),
                    }
                    workflow = workflows.get(entity)
                    if workflow:
                        protected.add(workflow["status_field"])
                        protected.update(t.get("set_timestamp") for t in workflow["transitions"])
                    sample = {}
                    for field in fields[entity]:
                        name, kind = field["name"], field["kind"]
                        if name in protected:
                            continue
                        relation = next(
                            (
                                r
                                for r in business["relations"]
                                if r["entity"] == entity and r["field"] == name
                            ),
                            None,
                        )
                        if relation:
                            sample[name] = (
                                creator["id"]
                                if relation["target_entity"] == "$users"
                                else base[relation["target_entity"]]["id"]
                            )
                        elif kind == "enum":
                            sample[name] = field["choices"][0]
                        elif kind == "boolean":
                            sample[name] = True
                        elif kind == "integer":
                            from fields import integer_bounds

                            low, high = integer_bounds(field)
                            sample[name] = max(low, min(1, high))
                        elif kind == "date":
                            sample[name] = "2026-01-01"
                        elif kind == "datetime":
                            sample[name] = "2020-01-01T00:00:00Z"
                        else:
                            sample[name] = (
                                "Verify " + name + " x" * max(1, field.get("min_length", 0))
                            )[: field["max_length"]]
                            if field.get("example") is not None:
                                sample[name] = field["example"]
                    rule = next(
                        (r for r in spec.get("custom_rules", []) if r["entity"] == entity), None
                    )
                    if rule:
                        sample.update(
                            {
                                k: v
                                for k, v in rule["accept_examples"][0].items()
                                if k not in protected
                            }
                        )
                    row = request("POST", "/api/" + entity, creator, status=201, json=sample)
                    check(
                        row["created_by"] == creator["id"] and row["created_at"],
                        "Immutable creator missing",
                    )
                    evidence["field_validation"].extend(
                        verify_field_constraints(
                            client,
                            creator,
                            entity,
                            fields[entity],
                            sample,
                            row,
                            protected,
                            allowed(creator["role"], entity, "update", row, creator["id"]),
                        )
                    )
                    for relation in relations:
                        invalid = {
                            **sample,
                            relation["field"]: "00000000-0000-0000-0000-000000000000",
                        }
                        denied = client.post(
                            "/api/" + entity,
                            headers={"Authorization": "Bearer " + creator["token"]},
                            json=invalid,
                        )
                        check(
                            denied.status_code in {403, 404, 422},
                            "Invalid foreign record reference accepted",
                        )
                    base[entity] = row
                    rows[entity].append(row)
                    samples[entity] = sample
                    pending.remove(entity)
                    progress = True
                    for other in actors.values():
                        if other["id"] != creator["id"] and allowed(
                            other["role"], entity, "create"
                        ):
                            response = client.post(
                                "/api/" + entity,
                                headers={"Authorization": "Bearer " + other["token"]},
                                json=sample,
                            )
                            if response.status_code == 201:
                                created = response.json()
                                rows[entity].append(created)
                                notification_evidence.event(entity, created, "created")
                            else:
                                check(
                                    response.status_code in {403, 404},
                                    "Secondary role create failed validation",
                                )
                    for key in protected - {None}:
                        if allowed(creator["role"], entity, "update", row, creator["id"]):
                            response = client.put(
                                f"/api/{entity}/{row['id']}",
                                headers={"Authorization": "Bearer " + creator["token"]},
                                json={key: "forged"},
                            )
                            check(response.status_code == 422, "Protected field mutation accepted")
                check(progress, "Required relation cycle cannot be constructed by approved APIs")
            checks.extend(
                ["business-relations", "business-protected-fields", "business-field-validation"]
            )
            for entity, row in base.items():
                assignee = resources[entity].get("assignee_field")
                if assignee:
                    targets = [
                        a
                        for a in actors.values()
                        if grants.get((a["role"], entity), {}).get("scope") in {"all", "assigned"}
                        and allowed(a["role"], entity, "read")
                        and (
                            allowed(a["role"], entity, "update")
                            or allowed(a["role"], entity, "transition")
                        )
                    ]
                    target = next(
                        (a for a in targets if grants[a["role"], entity]["scope"] == "assigned"),
                        targets[0],
                    )
                    administrator = next(
                        (
                            a
                            for a in actors.values()
                            if allowed(a["role"], entity, "assign", row, a["id"])
                        ),
                        None,
                    )
                    check(
                        administrator is not None,
                        "Assignee resource has no permitted assignment actor",
                    )
                    changed = request(
                        "POST",
                        f"/api/{entity}/{row['id']}/assign",
                        administrator,
                        json={"user_id": target["id"]},
                    )
                    row.update(changed)
            future_due_rows = []
            for entity in dict.fromkeys(
                n["entity"] for n in business["notifications"] if n["event"] == "due"
            ):
                creator = actors[create_roles[entity]]
                due_fields = {
                    n["due_field"]
                    for n in business["notifications"]
                    if n["entity"] == entity and n["event"] == "due"
                }
                future_sample = {
                    **samples[entity],
                    **{field: "2099-01-01T00:00:00Z" for field in due_fields},
                }
                future = request("POST", "/api/" + entity, creator, status=201, json=future_sample)
                rows[entity].append(future)
                assignee_field = resources[entity].get("assignee_field")
                if assignee_field and base[entity].get(assignee_field):
                    assigner = next(
                        a
                        for a in actors.values()
                        if allowed(a["role"], entity, "assign", future, a["id"])
                    )
                    future.update(
                        request(
                            "POST",
                            f"/api/{entity}/{future['id']}/assign",
                            assigner,
                            json={"user_id": base[entity][assignee_field]},
                        )
                    )
                future_due_rows.append((entity, future["id"]))
            for actor in actors.values():
                for entity, row in base.items():
                    response = client.get(
                        "/api/" + entity, headers={"Authorization": "Bearer " + actor["token"]}
                    )
                    if not allowed(actor["role"], entity, "read"):
                        check(response.status_code == 403, "Resource role denial bypassed")
                        continue
                    check(response.status_code == 200, "Permitted resource list denied")
                    expected = {
                        r["id"]
                        for r in rows[entity]
                        if allowed(actor["role"], entity, "read", r, actor["id"])
                    }
                    check(
                        {r["id"] for r in response.json()} == expected,
                        "Row-scoped list leaked or omitted records",
                    )
                    detail = client.get(
                        f"/api/{entity}/{row['id']}",
                        headers={"Authorization": "Bearer " + actor["token"]},
                    )
                    check(
                        detail.status_code == (200 if row["id"] in expected else 404),
                        "Row detail scope mismatch",
                    )
                notes = request("GET", "/business/notifications", actor)
                check(
                    all(n["recipient_id"] == actor["id"] for n in notes),
                    "Notification recipient leak",
                )
                check(
                    {n["id"] for n in notes}
                    == {n["id"] for n in request("GET", "/business/notifications", actor)},
                    "Duplicate due reminders",
                )
                for note in notes:
                    other = next((a for a in actors.values() if a["id"] != actor["id"]), None)
                    if other:
                        request(
                            "POST", f"/business/notifications/{note['id']}/read", other, status=404
                        )
            checks.append("business-row-permissions")
            for entity, row in base.items():
                workflow = workflows.get(entity)

                def actor_for(candidate, transition):
                    return next(
                        (
                            actor
                            for actor in actors.values()
                            if actor["role"] in transition["roles"]
                            and allowed(actor["role"], entity, "transition", candidate, actor["id"])
                        ),
                        None,
                    )

                def create_branch(transition):
                    assignee = resources[entity].get("assignee_field")
                    recipients = (
                        workflow_assignee_candidates(actors, grants, entity, row.get(assignee))
                        if assignee
                        else [None]
                    )
                    selection = None
                    for creator in actors.values():
                        if not (
                            allowed(creator["role"], entity, "create")
                            and allowed(creator["role"], entity, "read")
                        ):
                            continue
                        for recipient in recipients:
                            # This is an access-plan only; persisted creator, assignee and
                            # workflow state are still obtained exclusively through APIs.
                            access = {"created_by": creator["id"]}
                            if assignee and recipient:
                                if not any(
                                    allowed(a["role"], entity, "assign", access, a["id"])
                                    for a in actors.values()
                                ):
                                    continue
                                access[assignee] = recipient
                            path = workflow_transition_paths(
                                workflow, lambda step: actor_for(access, step) is not None
                            ).get(transition["name"])
                            if path:
                                selection = (creator, recipient, path)
                                break
                        if selection:
                            break
                    check(selection is not None, "Workflow branch has no permitted creation path")
                    creator, recipient, path = selection
                    created = request(
                        "POST",
                        "/api/" + entity,
                        creator,
                        status=201,
                        json=samples[entity],
                    )
                    # Notification/due expectations must see this owned record before
                    # assigning it or exercising any of its state transitions.
                    rows[entity].append(created)
                    if assignee and recipient:
                        assigner = next(
                            (
                                actor
                                for actor in actors.values()
                                if allowed(actor["role"], entity, "assign", created, actor["id"])
                            ),
                            None,
                        )
                        check(
                            assigner is not None,
                            "Workflow branch has no permitted assignment actor",
                        )
                        created.update(
                            request(
                                "POST",
                                f"/api/{entity}/{created['id']}/assign",
                                assigner,
                                json={"user_id": recipient},
                            )
                        )
                    for actor in actors.values():
                        notices = request("GET", "/business/notifications", actor)
                        notification_evidence.inbox(actor, notices)
                    return created, path

                def apply_transition(candidate, transition, actor):
                    changed = request(
                        "POST",
                        f"/api/{entity}/{candidate['id']}/transition",
                        actor,
                        json={"transition": transition["name"]},
                    )
                    check(
                        changed[workflow["status_field"]] == transition["to_state"],
                        "Wrong transition state",
                    )
                    if transition.get("set_timestamp"):
                        check(
                            changed[transition["set_timestamp"]],
                            "Server transition timestamp missing",
                        )
                    candidate.update(changed)
                    request(
                        "POST",
                        f"/api/{entity}/{candidate['id']}/transition",
                        actor,
                        status=409,
                        json={"transition": transition["name"]},
                    )

                if workflow:
                    cover_workflow_branches(
                        workflow,
                        row,
                        create_branch,
                        actor_for,
                        apply_transition,
                        [
                            candidate
                            for candidate in rows[entity]
                            if (entity, candidate["id"]) not in future_due_rows
                        ],
                    )
                actor = next(
                    (
                        a
                        for a in actors.values()
                        if allowed(a["role"], entity, "add_note", row, a["id"])
                    ),
                    None,
                )
                reader = next(
                    (
                        a
                        for a in actors.values()
                        if allowed(a["role"], entity, "read_history", row, a["id"])
                    ),
                    None,
                )
                if actor and resources[entity]["notes"]:
                    note = request(
                        "POST",
                        f"/api/{entity}/{row['id']}/notes",
                        actor,
                        status=201,
                        json={"body": "Independent business verification note"},
                    )
                    check(
                        note["actor_id"] == actor["id"] and note["created_at"],
                        "Forged or absent note actor/time",
                    )
                    if reader:
                        check(
                            any(
                                n["id"] == note["id"]
                                for n in request("GET", f"/api/{entity}/{row['id']}/notes", reader)
                            ),
                            "Note missing from history",
                        )
                if reader:
                    check(
                        bool(request("GET", f"/api/{entity}/{row['id']}/history", reader)),
                        "Immutable history missing",
                    )
            checks.extend(["business-transitions", "business-notes-history"])
            notification_evidence.complete()
            for actor in actors.values():
                notices = request("GET", "/business/notifications", actor)
                notification_evidence.inbox(actor, notices)
                repeated = request("GET", "/business/notifications", actor)
                check(notices == repeated, "Repeated inbox reads changed notification evidence")
                check(
                    not any(
                        n["event"] == "due" and (n["entity"], n["record_id"]) in future_due_rows
                        for n in notices
                    ),
                    "Future deadline generated an overdue reminder",
                )
            for rule in business["notifications"]:
                if rule["event"] != "due":
                    continue
                count = sum(
                    1
                    for recipient, entity, record, field, value in notification_evidence.due_seen
                    if entity == rule["entity"]
                    and field == rule["due_field"]
                    and recipient
                    == notification_evidence.recipient(
                        rule, next(row for row in rows[entity] if row["id"] == record)
                    )
                )
                check(count > 0, "Declared overdue reminder was not exercised")
                evidence["due_notifications"].append(
                    {
                        "entity": rule["entity"],
                        "field": rule["due_field"],
                        "recipient": rule["recipient"],
                        "past_due_events_verified": count,
                        "future_deadline_no_event": True,
                        "repeated_reads_deduplicated": True,
                    }
                )
            checks.append("business-due-reminders")
            for actor in actors.values():
                metrics = request("GET", "/business/metrics", actor)
                expected_names = {
                    m["name"]
                    for m in business["metrics"]
                    if allowed(actor["role"], m["entity"], "read_metrics")
                }
                check({m["name"] for m in metrics} == expected_names, "Metric permission leak")
                for result in metrics:
                    metric = next(m for m in business["metrics"] if m["name"] == result["name"])
                    visible = [
                        r
                        for r in rows[metric["entity"]]
                        if allowed(actor["role"], metric["entity"], "read_metrics", r, actor["id"])
                    ]

                    def selected(row):
                        for p in metric["filters"]:
                            actual, want, op = row.get(p["field"]), p["value"], p["op"]
                            if (
                                op == "eq"
                                and actual != want
                                or op == "ne"
                                and actual == want
                                or op == "in"
                                and actual not in want
                            ):
                                return False
                            if op in {"gte", "lte"} and (
                                actual is None or (actual < want if op == "gte" else actual > want)
                            ):
                                return False
                        return True

                    visible = [r for r in visible if selected(r)]
                    if metric["kind"] == "count":
                        check(result["value"] == len(visible), "Incorrect scoped count")
                    elif metric["kind"] == "average_duration":
                        durations = [
                            (
                                datetime.fromisoformat(
                                    r[metric["end_field"]].replace("Z", "+00:00")
                                )
                                - datetime.fromisoformat(
                                    r[metric["start_field"]].replace("Z", "+00:00")
                                )
                            ).total_seconds()
                            for r in visible
                            if r.get(metric["start_field"]) and r.get(metric["end_field"])
                        ]
                        durations = [v for v in durations if v >= 0]
                        check(result["samples"] == len(durations), "Wrong duration sample count")
                        check(
                            result["value"] is None
                            if not durations
                            else abs(result["value"] - sum(durations) / len(durations)) < 1e-6,
                            "Incorrect resolution duration",
                        )
                    else:
                        if metric["kind"] == "group_count":
                            expected_groups = Counter(r.get(metric["group_by"]) for r in visible)
                            actual_groups = {
                                group["key"]: group["count"] for group in result["groups"]
                            }
                        else:
                            expected_groups = Counter(
                                datetime.fromisoformat(
                                    r[metric["time_field"]].replace("Z", "+00:00")
                                )
                                .astimezone(timezone.utc)
                                .date()
                                .isoformat()
                                for r in visible
                                if r.get(metric["time_field"])
                            )
                            actual_groups = {
                                group["day"]: group["count"] for group in result["groups"]
                            }
                        check(
                            actual_groups == dict(expected_groups),
                            "Incorrect scoped grouping or day buckets",
                        )
            checks.append("business-scoped-metrics")
            query_cases, evidence["query_matrix"] = verify_query_matrix(
                spec, actors, rows, samples, create_roles, request, allowed
            )
            checks.append("business-query-matrix")
            actor_ids = {a["id"] for a in actors.values()} | {bootstrap_actor["id"]}
            for entity, row in base.items():
                auditor = next(
                    (
                        a
                        for a in actors.values()
                        if allowed(a["role"], entity, "read_audit", row, a["id"])
                    ),
                    None,
                )
                if resources[entity]["audit"]:
                    check(
                        auditor is not None,
                        "Audited resource has no permitted audit reader",
                    )
                    original, proof = verify_audit_immutability(
                        client, auditor, entity, row, actor_ids
                    )
                    persisted_audit[entity] = (auditor, row["id"], original)
                    evidence["audit_immutability"].append(proof)
                reader = next(
                    a for a in actors.values() if allowed(a["role"], entity, "read", row, a["id"])
                )
                for field in fields[entity]:
                    if field["kind"] != "datetime":
                        continue
                    name = field["name"]
                    value = row.get(name)
                    proof = {
                        "entity": entity,
                        "field": name,
                        "searchable": field["searchable"],
                        "filterable": field["filterable"],
                        "date_range": field["date_range"],
                    }
                    if value:
                        check(
                            datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None,
                            "Stored datetime lost its timezone",
                        )
                        proof["timestamp_stored"] = True
                    if not field["searchable"] and value:
                        matching = request(
                            "GET",
                            "/api/" + entity,
                            reader,
                            status=200 if any(f["searchable"] for f in fields[entity]) else 422,
                            params={"q": value, "limit": 100},
                        )
                        if isinstance(matching, list):
                            expected_ids = {
                                r["id"]
                                for r in rows[entity]
                                if allowed(reader["role"], entity, "read", r, reader["id"])
                                and any(
                                    f["searchable"]
                                    and value.lower() in str(r.get(f["name"]) or "").lower()
                                    for f in fields[entity]
                                )
                            }
                            check(
                                {r["id"] for r in matching} == expected_ids,
                                "Nonsearchable datetime participated in keyword matching",
                            )
                        proof["excluded_from_keyword_search"] = True
                    excluded = []
                    for prefix, prohibited in (
                        ("filter_", not field["filterable"]),
                        ("from_", not field["date_range"]),
                        ("to_", not field["date_range"]),
                    ):
                        if prohibited:
                            request(
                                "GET",
                                "/api/" + entity,
                                reader,
                                status=422,
                                params={prefix + name: "2020-01-01"},
                            )
                            excluded.append(prefix.rstrip("_"))
                    proof["undeclared_query_parameters_rejected"] = excluded
                    evidence["datetime_policy"].append(proof)
            for actor in actors.values():
                for entity, items in rows.items():
                    readable = [
                        row
                        for row in items
                        if allowed(actor["role"], entity, "read", row, actor["id"])
                    ]
                    for row in readable:
                        groups = []
                        for relation in business["relations"]:
                            target = relation["entity"]
                            if relation["target_entity"] != entity or not allowed(
                                actor["role"], target, "read"
                            ):
                                continue
                            visible = [
                                r
                                for r in rows[target]
                                if r.get(relation["field"]) == row["id"]
                                and allowed(actor["role"], target, "read", r, actor["id"])
                            ]
                            groups.append(
                                {
                                    "entity": target,
                                    "field": relation["field"],
                                    "record_ids": [r["id"] for r in visible],
                                    "labels": [
                                        r.get("name") or r.get("title") or r["id"] for r in visible
                                    ],
                                }
                            )
                        actual = request("GET", f"/business/related/{entity}/{row['id']}", actor)
                        expected_keys = {(g["entity"], g["field"]) for g in groups}
                        check(
                            {(g["entity"], g["field"]) for g in actual} == expected_keys
                            and len(actual) == len(groups),
                            "Related view omitted or leaked a target entity",
                        )
                        for group in groups:
                            found = next(
                                g
                                for g in actual
                                if (g["entity"], g["field"]) == (group["entity"], group["field"])
                            )
                            check(
                                {r["id"] for r in found["records"]} == set(group["record_ids"])
                                and len(found["records"]) == len(group["record_ids"]),
                                "Related view violated target row ACL",
                            )
                        related_expectations.append(
                            {
                                "role": actor["role"],
                                "entity": entity,
                                "record_id": row["id"],
                                "groups": groups,
                            }
                        )
                    if readable:
                        evidence["related_views"].append(
                            {
                                "role": actor["role"],
                                "entity": entity,
                                "source_records_checked": len(readable),
                                "target_entities": sorted(
                                    {
                                        g["entity"]
                                        for expected in related_expectations
                                        if expected["role"] == actor["role"]
                                        and expected["entity"] == entity
                                        for g in expected["groups"]
                                    }
                                ),
                                "target_row_acl": True,
                            }
                        )
                        actual_labels = request(
                            "POST",
                            "/business/labels/" + entity,
                            actor,
                            json={"record_ids": [r["id"] for r in readable]},
                        )
                        for relation in business["relations"]:
                            if relation["entity"] != entity:
                                continue
                            name, target = relation["field"], relation["target_entity"]
                            expected_labels = {}
                            checked_refs = 0
                            for row in readable:
                                identifier = row.get(name)
                                if not identifier:
                                    continue
                                if target == "$users":
                                    target_row = next(
                                        (a for a in actors.values() if a["id"] == identifier), None
                                    )
                                    label = target_row["username"] if target_row else None
                                else:
                                    target_row = next(
                                        (
                                            r
                                            for r in rows[target]
                                            if r["id"] == identifier
                                            and allowed(
                                                actor["role"], target, "read", r, actor["id"]
                                            )
                                        ),
                                        None,
                                    )
                                    label = (
                                        (
                                            target_row.get("name")
                                            or target_row.get("title")
                                            or "关联记录"
                                        )
                                        if target_row
                                        else None
                                    )
                                if label is not None:
                                    expected_labels[str(identifier)] = label
                                relation_labels.append(
                                    {
                                        "role": actor["role"],
                                        "entity": entity,
                                        "record_id": row["id"],
                                        "field": name,
                                        "target_id": identifier,
                                        "label": label,
                                        "visible": label is not None,
                                    }
                                )
                                checked_refs += 1
                            check(
                                actual_labels.get(name, {}) == expected_labels,
                                "Reference labels leaked hidden rows or exposed raw identifiers",
                            )
                            if checked_refs:
                                evidence["relation_labels"].append(
                                    {
                                        "role": actor["role"],
                                        "entity": entity,
                                        "field": name,
                                        "references_checked": checked_refs,
                                        "readable_labels_verified": True,
                                        "target_row_acl": True,
                                    }
                                )
            checks.extend(
                [
                    "business-related-views",
                    "business-readable-relation-labels",
                    "business-datetime-policy",
                    "business-audit-immutability",
                ]
            )
            browser = {"applicable": False, "reason": "api-only frontend"}
            if selection["frontend"] == "simple-admin":
                module = os.environ.get("PRODUCT_VERIFY_PLAYWRIGHT")
                if not module or not Path(module).is_dir() or not shutil.which("node"):
                    raise browser_error("Business browser requires pinned Playwright/Chromium")
                config = directory / "business-browser.json"
                output = directory / "business-browser-result.json"
                config.write_text(
                    json.dumps(
                        {
                            "url": str(client.base_url),
                            "spec": spec,
                            "spec_digest": digest,
                            "actors": [
                                {k: v for k, v in a.items() if k != "token"}
                                for a in actors.values()
                            ],
                            "password": password,
                            "samples": samples,
                            "base_records": {entity: row["id"] for entity, row in base.items()},
                            "related_expectations": related_expectations,
                            "relation_labels": relation_labels,
                            "query_cases": query_cases,
                            "query_evidence": evidence["query_matrix"],
                            "create_roles": create_roles,
                            "output": str(output),
                            "screenshot_dir": str(screenshot_target) if screenshot_target else None,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                result = subprocess.run(
                    [
                        "node",
                        str(Path(__file__).with_name("verify-business-browser.cjs")),
                        str(config),
                        module,
                    ],
                    env={**env, "PLAYWRIGHT_BROWSERS_PATH": "0"},
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=300,
                )
                check(result.returncode == 0, "Business browser failed: " + result.stderr[-1800:])
                check(output.is_file(), "Missing business browser evidence")
                browser = json.loads(output.read_text(encoding="utf-8"))
                browser["screenshots"] = validate_screenshots(
                    screenshot_target, browser.get("screenshots", [])
                )
                browser["applicable"] = True
                check(
                    browser.get("passed") and browser.get("spec_digest") == digest,
                    "Invalid business browser evidence",
                )
            # Keep unread reminders available for the real browser interaction first.
            # Browser-created records may add legitimate events beyond the HTTP ledger.
            for actor in actors.values():
                notices = request("GET", "/business/notifications", actor)
                check(
                    all(n["recipient_id"] == actor["id"] for n in notices),
                    "Notification recipient leak after browser actions",
                )
                read_times = {}
                for notice in notices:
                    outsider = next(a for a in actors.values() if a["id"] != actor["id"])
                    path = f"/business/notifications/{notice['id']}/read"
                    request("POST", path, outsider, status=404)
                    marked = request("POST", path, actor)
                    check(bool(marked["read_at"]), "Notification was not marked read")
                    read_times[notice["id"]] = marked["read_at"]
                    check(
                        request("POST", path, actor) == marked,
                        "Repeated mark-read changed the original read timestamp",
                    )
                persisted_notifications[actor["id"]] = request(
                    "GET", "/business/notifications", actor
                )
                expected_notices = {n["id"]: {**n, "read_at": read_times[n["id"]]} for n in notices}
                check(
                    {n["id"]: n for n in persisted_notifications[actor["id"]]} == expected_notices,
                    "Notification or read state was not persisted unchanged",
                )
            checks.append("business-notifications")
            for entity, row in base.items():
                actor = next(
                    (
                        a
                        for a in actors.values()
                        if allowed(a["role"], entity, "archive", row, a["id"])
                    ),
                    None,
                )
                if actor:
                    request("POST", f"/api/{entity}/{row['id']}/archive", actor)
                    if allowed(actor["role"], entity, "read", row, actor["id"]):
                        request("GET", f"/api/{entity}/{row['id']}", actor, status=404)
            checks.append("business-archive")
            for entity, (auditor, identifier, original) in list(persisted_audit.items()):
                archived = request("GET", f"/api/{entity}/{identifier}/history", auditor)
                check(
                    archived[: len(original)] == original,
                    "Archive rewrote or removed audit history",
                )
                persisted_audit[entity] = (auditor, identifier, archived)
        finally:
            client.close()
            stop(process)
        process, client = start()
        try:
            response = client.get(
                "/business/me", headers={"Authorization": "Bearer " + bootstrap_actor["token"]}
            )
            check(response.status_code == 200, "Business role/token lost after restart")
            check(
                response.json()["id"] == bootstrap_actor["id"],
                "Business actor changed after restart",
            )
            for actor in actors.values():
                notices = request("GET", "/business/notifications", actor)
                previous = {n["id"]: n for n in persisted_notifications[actor["id"]]}
                restored = {n["id"]: n for n in notices}
                check(
                    all(restored.get(key) == value for key, value in previous.items()),
                    "Notification event or read state changed after restart",
                )
            for entity, (auditor, identifier, original) in persisted_audit.items():
                check(
                    request("GET", f"/api/{entity}/{identifier}/history", auditor) == original,
                    "Audit history changed after restart",
                )
                next(item for item in evidence["audit_immutability"] if item["entity"] == entity)[
                    "archive_and_restart_preserved"
                ] = True
            for proof in evidence["due_notifications"]:
                proof["event_and_read_state_persisted_after_restart"] = True
        finally:
            client.close()
            stop(process)
    checks.append("process_restart_persistence")
    return {
        "passed": True,
        "http": True,
        "restart": True,
        "database": "real-isolated-" + selection["database"],
        "entities": len(fields),
        "checks": checks,
        "business": {
            "passed": True,
            "spec_digest": digest,
            "resources_checked": list(fields),
            "roles_checked": [r["name"] for r in business["roles"]],
            "checks": [c for c in checks if c.startswith("business-")],
            "evidence": evidence,
        },
        "browser": browser,
    }
````
