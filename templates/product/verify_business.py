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
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path

import httpx


def check(condition, message):
    if not condition:
        raise ValueError(message)


def workflow_transition_paths(workflow, permitted=None):
    """Find finite routes to each named transition without changing approved states."""
    transitions = [
        transition
        for transition in workflow["transitions"]
        if permitted is None or permitted(transition)
    ]
    paths = {workflow["initial"]: []}
    pending = deque(paths)
    while pending:
        state = pending.popleft()
        for transition in transitions:
            target = transition["to_state"]
            if state in transition["from_states"] and target not in paths:
                paths[target] = [*paths[state], transition]
                pending.append(target)
    result = {}
    for transition in transitions:
        prefixes = [paths[state] for state in transition["from_states"] if state in paths]
        if not prefixes:
            check(
                permitted is not None, "Declared workflow transition has no reachable source state"
            )
            continue
        result[transition["name"]] = [*min(prefixes, key=len), transition]
    return result


def workflow_assignee_candidates(actors, grants, entity, preferred):
    eligible = {
        actor["id"]
        for actor in actors.values()
        if "read" in grants.get((actor["role"], entity), {}).get("actions", [])
        and grants[actor["role"], entity]["scope"] in {"all", "assigned"}
    }
    return [
        identity
        for identity in dict.fromkeys([preferred, *(a["id"] for a in actors.values()), None])
        if identity is None or identity in eligible
    ]


def cover_workflow_branches(
    workflow, base_row, create_branch, actor_for, apply_transition, existing_rows=()
):
    """Keep the original base path, then exercise remaining branches through callbacks."""
    paths = workflow_transition_paths(workflow)
    status = workflow["status_field"]
    covered, visited = set(), set()
    branches = [base_row, *(row for row in existing_rows if row is not base_row)]

    def advance(row, transition):
        check(row[status] in transition["from_states"], "Workflow route missed its source state")
        actor = actor_for(row, transition)
        check(actor is not None, "Reachable workflow branch has no permitted transition actor")
        apply_transition(row, transition, actor)
        covered.add(transition["name"])

    while base_row[status] not in visited:
        visited.add(base_row[status])
        transition = next(
            (
                item
                for item in workflow["transitions"]
                if base_row[status] in item["from_states"] and actor_for(base_row, item) is not None
            ),
            None,
        )
        if transition is None:
            break
        advance(base_row, transition)
    for transition in workflow["transitions"]:
        if transition["name"] in covered:
            continue
        for row in branches:
            path = workflow_transition_paths(
                {**workflow, "initial": row[status]},
                lambda step: actor_for(row, step) is not None,
            ).get(transition["name"])
            if path:
                break
        else:
            row, path = create_branch(transition)
            branches.append(row)
        for step in path:
            advance(row, step)
    check(covered == set(paths), "Declared workflow transition was not exercised")


def verify_query_matrix(spec, actors, rows, samples, create_roles, request, allowed):
    """Exact query expectations come from owned API writes, never query responses."""
    business = spec["business"]
    grants = {(p["role"], p["entity"]): p for p in business["permissions"]}
    resources = {r["entity"]: r for r in business["resources"]}
    workflows = {w["entity"]: w for w in business["workflows"]}
    relations = {(r["entity"], r["field"]): r for r in business["relations"]}
    cases, evidence = [], []

    def wire(value):
        return str(value).lower() if type(value) is bool else str(value)

    def keyword(value):
        text = str(value or "")
        # A proper substring distinguishes keyword search from full-value
        # equality. One-character domains have no shorter nonempty query.
        term = text[1:-1] if len(text) > 2 else text[:1]
        return term[:200].upper()

    for definition in spec["entities"]:
        entity, fields = definition["name"], definition["fields"]
        searchable = [f for f in fields if f["searchable"]]
        filterable = [f for f in fields if f["filterable"]]
        if not searchable and not filterable:
            continue
        workflow = workflows.get(entity)
        protected = {resources[entity].get("assignee_field")}
        if workflow:
            protected.add(workflow["status_field"])
            protected.update(t.get("set_timestamp") for t in workflow["transitions"])
        due_fields = {
            n["due_field"]
            for n in business["notifications"]
            if n["entity"] == entity and n["event"] == "due"
        }
        controls = {}
        for role, actor in actors.items():
            if not allowed(role, entity, "read"):
                continue
            scope = grants[role, entity]["scope"]
            if scope == "own" and not allowed(role, entity, "create"):
                # An approved own/read-only role can legitimately have no owned
                # records. Do not manufacture extra create or ownership rights.
                continue
            creator = actor if scope == "own" else actors[create_roles[entity]]
            for side in (0, 1):
                sample = dict(samples[entity])
                for field_index, field in enumerate(fields):
                    name, kind = field["name"], field["kind"]
                    if name in protected or (entity, name) in relations:
                        continue
                    if name in due_fields:
                        sample[name] = f"2099-01-0{side + 1}T00:00:00Z"
                    elif field["searchable"] or field["filterable"]:
                        if kind == "text":
                            marker = (
                                "q"
                                + str(side)
                                + hashlib.sha256(f"{entity}/{name}".encode()).hexdigest()[:8]
                            )
                            if field["max_length"] < len(marker):
                                # Truncating the same q0 prefix would correlate
                                # short fields and lose independent field proof.
                                marker = chr(0x4E00 + field_index * 2 + side)
                            sample[name] = marker.ljust(max(1, field.get("min_length", 0)), "z")[
                                : field["max_length"]
                            ]
                            if field.get("pattern") is not None:
                                sample[name] = field["example"]
                        elif kind == "enum":
                            sample[name] = field["choices"][min(side, len(field["choices"]) - 1)]
                        elif kind == "integer":
                            from fields import integer_bounds

                            low, high = integer_bounds(field)
                            sample[name] = max(low, min(41 + side, high))
                        elif kind == "boolean":
                            sample[name] = bool(side)
                        elif kind == "date":
                            sample[name] = f"2026-02-0{side + 1}"
                        elif kind == "datetime":
                            sample[name] = f"2026-02-0{side + 1}T00:00:00Z"
                row = request("POST", "/api/" + entity, creator, status=201, json=sample)
                rows[entity].append(row)
                if scope == "assigned":
                    assigner = next(
                        (
                            a
                            for a in actors.values()
                            if allowed(a["role"], entity, "assign", row, a["id"])
                        ),
                        None,
                    )
                    check(assigner is not None, "Query controls need an approved assignment actor")
                    row.update(
                        request(
                            "POST",
                            f"/api/{entity}/{row['id']}/assign",
                            assigner,
                            json={"user_id": actor["id"]},
                        )
                    )
                if (
                    side
                    and workflow
                    and any(f["name"] == workflow["status_field"] for f in searchable + filterable)
                ):
                    transition = next(
                        (
                            t
                            for t in workflow["transitions"]
                            if row[workflow["status_field"]] in t["from_states"]
                        ),
                        None,
                    )
                    if transition:
                        handler = next(
                            (
                                a
                                for a in actors.values()
                                if a["role"] in transition["roles"]
                                and allowed(a["role"], entity, "transition", row, a["id"])
                            ),
                            None,
                        )
                        if handler:
                            row.update(
                                request(
                                    "POST",
                                    f"/api/{entity}/{row['id']}/transition",
                                    handler,
                                    json={"transition": transition["name"]},
                                )
                            )
                controls[role, side] = row
        check(len(rows[entity]) <= 100, "Query control rows exceed explicit 100-record bound")

        def matches(row, params):
            q = params.get("q", "").strip().casefold()
            if q and not any(q in str(row.get(f["name"]) or "").casefold() for f in searchable):
                return False
            return all(
                wire(row.get(f["name"])) == value
                for key, value in params.items()
                if key.startswith("filter_")
                for f in filterable
                if key == "filter_" + f["name"]
            )

        first = next(iter(controls.values()), rows[entity][0])
        other = next((row for (role, side), row in controls.items() if side), first)
        for role, actor in actors.items():
            if not allowed(role, entity, "read"):
                continue
            scope = grants[role, entity]["scope"]
            visible = [r for r in rows[entity] if allowed(role, entity, "read", r, actor["id"])]
            positive = controls.get((role, 0), first)
            alternate = controls.get((role, 1), other)
            matrix = [(f, "keyword", None) for f in searchable] + [
                (f, "exact_filter", None) for f in filterable
            ]
            matrix += (
                [(f, "combined", searchable[0]["name"]) for f in filterable] if searchable else []
            )
            for field, kind, keyword_field in matrix:
                name = field["name"]
                if kind == "keyword":
                    term = keyword(positive.get(name))
                    check(bool(term), f"Query keyword control is empty: {entity}.{name}")
                    pair = [
                        ("match", {"q": term}),
                        (
                            "miss",
                            {
                                "q": "qnever"
                                + hashlib.sha256(f"{entity}/{name}".encode()).hexdigest()[:12]
                            },
                        ),
                    ]
                else:
                    value, alternative = positive.get(name), alternate.get(name)
                    if value == alternative:
                        if field["kind"] == "enum":
                            alternative = next((v for v in field["choices"] if v != value), value)
                        elif field["kind"] == "text":
                            alternative = "query-value-not-present"
                        elif field["kind"] == "boolean":
                            alternative = not value
                        elif field["kind"] == "integer":
                            alternative = int(value or 0) + 1
                    check(
                        value is not None and alternative is not None,
                        f"Query filter control is empty: {entity}.{name}",
                    )
                    anchor = {"q": keyword(positive.get(keyword_field))} if keyword_field else {}
                    pair = [
                        ("match", {**anchor, "filter_" + name: wire(value)}),
                        ("other", {**anchor, "filter_" + name: wire(alternative)}),
                    ]
                counts, excluded, foreign, isolated = [], 0, 0, 0
                for variant, params in pair:
                    expected = {r["id"] for r in visible if matches(r, params)}
                    all_matches = {r["id"] for r in rows[entity] if matches(r, params)}
                    isolated_count = (
                        sum(
                            r["id"] in expected
                            and params["q"].casefold() in str(r.get(name) or "").casefold()
                            and not any(
                                params["q"].casefold() in str(r.get(f["name"]) or "").casefold()
                                for f in searchable
                                if f["name"] != name
                            )
                            for r in visible
                        )
                        if kind == "keyword" and variant == "match"
                        else 0
                    )
                    actual = request(
                        "GET", "/api/" + entity, actor, params={**params, "limit": 100}
                    )
                    check(
                        isinstance(actual, list)
                        and {r["id"] for r in actual} == expected
                        and len(actual) == len(expected),
                        f"Query matrix differs for {role}/{entity}/{name}/{kind}/{variant}",
                    )
                    cases.append(
                        {
                            "role": role,
                            "entity": entity,
                            "field": name,
                            "kind": kind,
                            "variant": variant,
                            "keyword_field": keyword_field,
                            "params": params,
                            "expected_ids": sorted(expected),
                            "total_count": len(visible),
                            "foreign_count": len(all_matches - expected),
                            "isolated_count": isolated_count,
                        }
                    )
                    counts.append(len(expected))
                    excluded += len(visible) - len(expected)
                    foreign += len(all_matches - expected)
                    isolated += isolated_count
                evidence.append(
                    {
                        "role": role,
                        "entity": entity,
                        "field": name,
                        "kind": kind,
                        "keyword_field": keyword_field,
                        "scope": scope,
                        "cases": 2,
                        "positive_matches": counts[0],
                        "other_matches": counts[1],
                        "excluded_records": excluded,
                        "foreign_matches": foreign,
                        "isolated_matches": isolated,
                        "exact_results": True,
                        "role_scope": True,
                    }
                )
        for field in searchable:
            check(
                any(
                    p["entity"] == entity
                    and p["field"] == field["name"]
                    and p["kind"] == "keyword"
                    and p["isolated_matches"] > 0
                    for p in evidence
                ),
                f"Keyword field lacks an isolated positive control: {entity}.{field['name']}",
            )
        for field in filterable:
            check(
                any(
                    p["entity"] == entity
                    and p["field"] == field["name"]
                    and p["kind"] == "exact_filter"
                    and p["positive_matches"] > 0
                    for p in evidence
                ),
                f"Filter lacks a positive control: {entity}.{field['name']}",
            )
    return cases, evidence


def verify_field_constraints(client, actor, entity, fields, sample, row, protected, can_update):
    """Reject concrete invalid requests through the generated server, not metadata alone."""
    headers = {"Authorization": "Bearer " + actor["token"]}
    route = "/api/" + entity
    before = client.get(route, headers=headers, params={"limit": 100}).json()
    evidence = []
    for field in fields:
        name, kind = field["name"], field["kind"]
        proof = {"entity": entity, "field": name, "kind": kind, "required": field["required"]}
        if name in protected:
            response = client.post(route, headers=headers, json={**sample, name: "forged"})
            check(response.status_code == 422, f"Protected create field accepted: {entity}.{name}")
            proof["protected_create_rejected"] = True
            if can_update:
                response = client.put(
                    route + "/" + row["id"], headers=headers, json={name: "forged"}
                )
                check(
                    response.status_code == 422, f"Protected update field accepted: {entity}.{name}"
                )
                proof["protected_update_rejected"] = True
            evidence.append(proof)
            continue
        invalid = []
        if kind == "integer":
            from fields import integer_bounds

            low, high = integer_bounds(field)
            invalid.extend(
                (("below_minimum_rejected", low - 1), ("above_maximum_rejected", high + 1))
            )
            proof.update(minimum=low, maximum=high)
        if field["required"]:
            missing = {key: value for key, value in sample.items() if key != name}
            response = client.post(route, headers=headers, json=missing)
            check(response.status_code == 422, f"Missing required field accepted: {entity}.{name}")
            proof["missing_required_rejected"] = True
            invalid.append(("null_rejected", None))
            if kind in {"text", "enum"}:
                invalid.append(("blank_rejected", ""))
        if kind == "text":
            invalid.append(("over_max_length_rejected", "x" * (field["max_length"] + 1)))
            proof["max_length"] = field["max_length"]
            if field.get("min_length", 0) > 0:
                invalid.append(("under_min_length_rejected", "x" * (field["min_length"] - 1)))
                proof["min_length"] = field["min_length"]
        if kind == "enum":
            invalid_choice = next(
                char * max(1, field.get("min_length", 0))
                for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                if char * max(1, field.get("min_length", 0)) not in field["choices"]
            )
            invalid.append(("invalid_enum_rejected", invalid_choice))
            proof["declared_choices"] = len(field["choices"])
        if kind == "datetime":
            invalid.append(("invalid_timestamp_rejected", "not-a-timestamp"))
        for check_name, value in invalid:
            response = client.post(route, headers=headers, json={**sample, name: value})
            check(response.status_code == 422, f"{check_name} failed for {entity}.{name}")
            proof[check_name] = True
            if can_update:
                response = client.put(route + "/" + row["id"], headers=headers, json={name: value})
                check(
                    response.status_code == 422, f"Update {check_name} failed for {entity}.{name}"
                )
        if invalid and can_update:
            proof["invalid_updates_rejected"] = len(invalid)
        evidence.append(proof)
    after = client.get(route, headers=headers, params={"limit": 100}).json()
    check(before == after, "Rejected field input changed stored records")
    return evidence


def verify_audit_immutability(client, actor, entity, row, actor_ids):
    headers = {"Authorization": "Bearer " + actor["token"]}
    route = f"/api/{entity}/{row['id']}/history"
    response = client.get(route, headers=headers)
    check(response.status_code == 200, "Audit history unavailable")
    original = response.json()
    check(bool(original), "Audit history is empty")
    for entry in original:
        check(
            {"before", "after"} <= entry.keys()
            and all(
                entry[key] is None or isinstance(entry[key], dict) for key in ("before", "after")
            ),
            "Audit snapshots unavailable",
        )
        check(
            entry.get("id") and entry.get("action") and entry.get("actor_id") in actor_ids,
            "Audit action/actor missing",
        )
        check(bool(entry.get("created_at")), "Audit timestamp missing")
        check(
            datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00")).tzinfo is not None,
            "Audit timestamp is not timezone-aware",
        )
    forged = {
        "action": "forged",
        "actor_id": "forged",
        "created_at": "2000-01-01T00:00:00Z",
        "before": {},
        "after": {},
    }
    attempts = 0
    for path in (route, route + "/" + original[0]["id"]):
        for method in ("PUT", "PATCH", "DELETE"):
            denied = client.request(method, path, headers=headers, json=forged)
            check(denied.status_code in {403, 404, 405}, "Audit mutation/deletion route accepted")
            check(
                client.get(route, headers=headers).json() == original,
                "Audit changed after rejected mutation",
            )
            attempts += 1
    return original, {
        "entity": entity,
        "entries_checked": len(original),
        "action_actor_timestamp": True,
        "mutation_delete_attempts_rejected": attempts,
        "surface": "http_history_collection_and_entry",
        "unchanged_after_attempts": True,
    }


class NotificationEvidence:
    """Expected reminders come from successful actions and the approved contract."""

    def __init__(self, business):
        self.rules = business["notifications"]
        self.resources = {r["entity"]: r for r in business["resources"]}
        self.workflows = {w["entity"]: w for w in business["workflows"]}
        self.expected = Counter()
        self.covered = set()
        self.due_seen = set()

    def recipient(self, rule, row):
        field = (
            "created_by"
            if rule["recipient"] == "creator"
            else self.resources[rule["entity"]]["assignee_field"]
        )
        return row.get(field)

    def event(self, entity, row, event, transition=None):
        recipients = set()
        for index, rule in enumerate(self.rules):
            if rule["entity"] != entity or rule["event"] != event:
                continue
            if event == "transitioned" and rule["transition"] != transition:
                continue
            recipient = self.recipient(rule, row)
            if recipient:
                self.covered.add(index)
                recipients.add(recipient)
        self.expected.update((recipient, entity, row["id"], event) for recipient in recipients)

    def due(self, rows, actor, allowed):
        now = datetime.now(timezone.utc)
        for index, rule in enumerate(self.rules):
            if rule["event"] != "due":
                continue
            entity, field = rule["entity"], rule["due_field"]
            for row in rows[entity]:
                value = row.get(field)
                if (
                    not value
                    or row.get("archived_at")
                    or self.recipient(rule, row) != actor["id"]
                    or not allowed(actor["role"], entity, "read", row, actor["id"])
                    or datetime.fromisoformat(value.replace("Z", "+00:00")) > now
                ):
                    continue
                workflow = self.workflows.get(entity)
                if workflow and row[workflow["status_field"]] not in {
                    state for t in workflow["transitions"] for state in t["from_states"]
                }:
                    continue
                self.covered.add(index)
                key = (actor["id"], entity, row["id"], field, value)
                if key not in self.due_seen:
                    self.due_seen.add(key)
                    self.expected[actor["id"], entity, row["id"], "due"] += 1

    def inbox(self, actor, notices, event=None):
        check(
            len({n["id"] for n in notices}) == len(notices),
            "Duplicate notification identifiers",
        )
        check(
            all(n["recipient_id"] == actor["id"] for n in notices),
            "Notification recipient leak",
        )
        actual = Counter(
            (n["recipient_id"], n["entity"], n["record_id"], n["event"])
            for n in notices
            if event is None or n["event"] == event
        )
        expected = Counter(
            {
                k: v
                for k, v in self.expected.items()
                if k[0] == actor["id"] and (event is None or k[3] == event)
            }
        )
        check(actual == expected, "Missing, duplicated or unexpected declared notifications")
        check(all(n["created_at"] for n in notices), "Notification timestamp missing")

    def complete(self):
        check(
            self.covered == set(range(len(self.rules))),
            "Declared notification rule was not exercised by the approved workflow",
        )


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
    notification_evidence = NotificationEvidence(business)
    persisted_notifications = {}
    persisted_audit = {}
    evidence = {
        "version": 1,
        "field_validation": [],
        "related_views": [],
        "relation_labels": [],
        "datetime_policy": [],
        "due_notifications": [],
        "audit_immutability": [],
        "query_matrix": [],
    }
    related_expectations, relation_labels = [], []
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
