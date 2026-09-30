"""Independent HTTP/browser business verification against a new owned database."""

import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import zlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx


def check(condition, message):
    if not condition:
        raise ValueError(message)


SCREENSHOT_VIEWS = {"list", "form", "relations", "workflow", "reminders", "dashboard"}
SCREENSHOT_LIMIT = 48
SCREENSHOT_FILE_BYTES = 5 * 1024 * 1024
SCREENSHOT_TOTAL_BYTES = 40 * 1024 * 1024


def validate_png(payload):
    check(payload.startswith(b"\x89PNG\r\n\x1a\n"), "Screenshot must be PNG")
    offset, header, compressed, ended = 8, None, [], False
    safe_chunks = {
        b"IHDR",
        b"PLTE",
        b"IDAT",
        b"IEND",
        b"sRGB",
        b"gAMA",
        b"cHRM",
        b"iCCP",
        b"pHYs",
        b"sBIT",
        b"bKGD",
        b"tRNS",
    }
    while offset < len(payload):
        check(offset + 12 <= len(payload), "Truncated PNG")
        length = struct.unpack(">I", payload[offset : offset + 4])[0]
        kind = payload[offset + 4 : offset + 8]
        end = offset + 12 + length
        check(end <= len(payload) and kind in safe_chunks, "Invalid PNG chunk")
        data = payload[offset + 8 : offset + 8 + length]
        checksum = struct.unpack(">I", payload[end - 4 : end])[0]
        check(zlib.crc32(kind + data) & 0xFFFFFFFF == checksum, "Invalid PNG checksum")
        if header is None:
            check(kind == b"IHDR" and length == 13, "Invalid PNG header")
            header = struct.unpack(">IIBBBBB", data)
        elif kind == b"IHDR":
            raise ValueError("Duplicate PNG header")
        if kind == b"IDAT":
            compressed.append(data)
        if kind == b"IEND":
            check(length == 0 and end == len(payload), "PNG has trailing data")
            ended = True
        offset = end
    check(header is not None and ended and compressed, "Incomplete PNG")
    width, height, depth, color, compression, filtering, interlace = header
    check(
        0 < width * height <= 16 * 1024 * 1024 and compression == filtering == interlace == 0,
        "Unsupported or excessive PNG dimensions",
    )
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    check(channels is not None and depth in {1, 2, 4, 8, 16}, "Unsupported PNG pixels")
    row_bytes = (width * channels * depth + 7) // 8 + 1
    expected = row_bytes * height
    check(expected <= 64 * 1024 * 1024, "PNG decompression limit exceeded")
    decoder = zlib.decompressobj()
    try:
        pixels = decoder.decompress(b"".join(compressed), expected + 1)
    except zlib.error:
        raise ValueError("Invalid PNG compressed data") from None
    check(
        decoder.eof and not decoder.unused_data and len(pixels) == expected,
        "Invalid PNG image data",
    )
    check(
        all(pixels[index] <= 4 for index in range(0, len(pixels), row_bytes)), "Invalid PNG filter"
    )


def validate_screenshots(directory, entries):
    """Only bounded, named PNGs from the owned synthetic-product directory escape."""
    check(
        isinstance(entries, list) and len(entries) <= SCREENSHOT_LIMIT,
        "Invalid screenshot manifest",
    )
    if directory is None:
        check(not entries, "Screenshots were not requested")
        return []
    check(bool(entries), "Requested screenshots were not captured")
    root = Path(directory).resolve()
    seen, result, total = set(), [], 0
    for entry in entries:
        check(
            isinstance(entry, dict) and set(entry) == {"file", "role", "entity", "view"},
            "Invalid screenshot entry",
        )
        name, role, entity, view = (entry.get(key) for key in ("file", "role", "entity", "view"))
        check(
            isinstance(role, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", role),
            "Invalid screenshot role",
        )
        check(
            entity is None
            or isinstance(entity, str)
            and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", entity),
            "Invalid screenshot entity",
        )
        check(isinstance(view, str) and view in SCREENSHOT_VIEWS, "Invalid screenshot view")
        expected = f"{role}--{entity or 'overview'}--{view}.png"
        check(name == expected and name not in seen, "Invalid or duplicate screenshot filename")
        path = root / name
        check(
            not path.is_symlink() and path.is_file() and path.resolve().parent == root,
            "Screenshot file escaped owned directory",
        )
        size = path.stat().st_size
        check(0 < size <= SCREENSHOT_FILE_BYTES, "Screenshot exceeds file limit")
        total += size
        check(total <= SCREENSHOT_TOTAL_BYTES, "Screenshots exceed total limit")
        payload = path.read_bytes()
        validate_png(payload)
        seen.add(name)
        result.append({**entry, "bytes": size, "sha256": hashlib.sha256(payload).hexdigest()})
    check(
        {path.name for path in root.iterdir()} == seen,
        "Unlisted screenshot artifacts are forbidden",
    )
    return result


def verify_business(product, python, stop, browser_error, screenshot_dir=None):
    product = Path(product).resolve()
    screenshot_target = None
    if screenshot_dir is not None:
        target = Path(screenshot_dir).absolute()
        check(
            not target.is_symlink()
            and not (hasattr(target, "is_junction") and target.is_junction()),
            "Screenshot directory cannot be a link",
        )
        check(
            not target.resolve().is_relative_to(product),
            "Screenshot evidence must be outside immutable product source",
        )
        target.mkdir(parents=True, exist_ok=True, mode=0o700)
        check(not any(target.iterdir()), "Screenshot output directory must be empty")
        screenshot_target = target.resolve()
    spec = json.loads((product / "approved-spec.json").read_text(encoding="utf-8"))
    selection = json.loads((product / "selection.json").read_text(encoding="utf-8"))
    business = spec["business"]
    digest = hashlib.sha256(
        json.dumps(spec, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    grants = {(g["role"], g["entity"]): g for g in business["permissions"]}
    resources = {r["entity"]: r for r in business["resources"]}
    workflows = {w["entity"]: w for w in business["workflows"]}
    fields = {e["name"]: e["fields"] for e in spec["entities"]}
    checks = []
    password = secrets.token_urlsafe(24)

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
                return response.json() if response.content else None

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
                            sample[name] = 1
                        elif kind == "date":
                            sample[name] = "2026-01-01"
                        elif kind == "datetime":
                            sample[name] = "2020-01-01T00:00:00Z"
                        else:
                            sample[name] = (
                                "Verify " + name + " x" * max(1, field.get("min_length", 0))
                            )[: field["max_length"]]
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
                                rows[entity].append(response.json())
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
            checks.extend(["business-relations", "business-protected-fields"])
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
            checks.extend(["business-row-permissions", "business-notifications"])
            for entity, row in base.items():
                workflow = workflows.get(entity)
                visited = set()
                while workflow and row[workflow["status_field"]] not in visited:
                    state = row[workflow["status_field"]]
                    visited.add(state)
                    choices = [
                        (t, a)
                        for t in workflow["transitions"]
                        for a in actors.values()
                        if state in t["from_states"]
                        and a["role"] in t["roles"]
                        and allowed(a["role"], entity, "transition", row, a["id"])
                    ]
                    if not choices:
                        break
                    transition, actor = choices[0]
                    changed = request(
                        "POST",
                        f"/api/{entity}/{row['id']}/transition",
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
                    row.update(changed)
                    request(
                        "POST",
                        f"/api/{entity}/{row['id']}/transition",
                        actor,
                        status=409,
                        json={"transition": transition["name"]},
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
        },
        "browser": browser,
    }
