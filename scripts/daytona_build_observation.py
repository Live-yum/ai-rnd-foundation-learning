"""Bounded optional facts from this build's output, never admission evidence."""

import json
import re

PACKAGES = {
    "@nestjs/core",
    "@swc/core",
    "esbuild",
    "sharp",
    "msw",
    "nx",
    "core-js",
    "sqlite3",
    "@parcel/watcher",
    "protobufjs",
    "@scarf/scarf",
    "unrs-resolver",
    "cpu-features",
    "core-js-pure",
    "other",
}


def version(value):
    return (
        value
        if type(value) is str and re.fullmatch(r"\d{1,5}\.\d{1,5}\.\d{1,5}", value)
        else "unknown"
    )


def script_fact(value):
    if not isinstance(value, dict):
        return None
    identifier = value.get("id")
    script = value.get("script")
    package = value.get("package")
    if not (
        type(identifier) is str
        and re.fullmatch(r"[a-f0-9]{64}", identifier)
        and type(script) is str
        and script in {"preinstall", "install", "postinstall"}
    ):
        return None
    return {
        "id": identifier,
        "script": script,
        "package": package if type(package) is str and package in PACKAGES else "other",
        "version": version(value.get("version")),
    }


def observation(log):
    result = {
        "schema": 1,
        "coverage": "manifest_scripts_only",
        "log_excerpt": True,
        "session_limit_reached": False,
        "bases": {},
        "sessions": {},
        "events": [],
    }
    # run_command already supplies only the bounded head/tail of its own output.
    if not isinstance(log, str):
        return result
    for line in log[:64064].splitlines():
        match = re.search(
            r"\[(builder|daytona) [^\]]{1,32}\] FROM (?:docker\.io/)?library/node:24-slim@(sha256:[a-f0-9]{64})(?:\s|$)",
            line,
        )
        if match:
            result["bases"][match[1]] = match[2]
        if len(line) > 16000 or "RND_BUILD_OBSERVATION " not in line:
            continue
        try:
            data = json.loads(line.split("RND_BUILD_OBSERVATION ", 1)[1])
        except ValueError, RecursionError:
            continue
        if not isinstance(data, dict):
            continue
        session = data.get("session")
        if type(session) is not str or not re.fullmatch(r"[a-f0-9]{16}", session):
            continue
        if session not in result["sessions"]:
            if len(result["sessions"]) == 4:
                result["session_limit_reached"] = True
                continue
            result["sessions"][session] = {"tools": None, "pending": None}
        current = result["sessions"][session]
        event = data.get("event")
        if event == "tools":
            current["tools"] = {key: version(data.get(key)) for key in ("node", "yarn", "corepack")}
        elif event == "pending":
            pending = {}
            for key in ("started", "completed", "active_count"):
                value = data.get(key)
                pending[key] = value if type(value) is int and 0 <= value <= 256 else None
            pending["overflow"] = (
                data.get("overflow") if type(data.get("overflow")) is bool else None
            )
            pending["scripts"] = []
            items = data.get("scripts")
            for item in items[:32] if isinstance(items, list) else []:
                safe = script_fact(item)
                elapsed = item.get("elapsed_seconds") if isinstance(item, dict) else None
                if safe and type(elapsed) is int and 0 <= elapsed <= 2400:
                    pending["scripts"].append(
                        {**safe, "state": "awaiting_script_exit", "elapsed_seconds": elapsed}
                    )
            current["pending"] = pending
            pending["scripts_truncated"] = pending["active_count"] is not None and pending[
                "active_count"
            ] > len(pending["scripts"])
        elif event in ("start", "end") and (safe := script_fact(data)):
            safe["session"] = session
            safe["event"] = event
            if event == "end":
                safe["state"] = (
                    data.get("state") if data.get("state") in ("returned", "threw") else "unknown"
                )
                code = data.get("exit_code")
                safe["exit_code"] = code if type(code) is int and 0 <= code <= 255 else None
            result["events"] = (result["events"] + [safe])[-64:]
    return result


def retain(directory, log):
    """Diagnostics never replace a build result or authorize an image."""
    try:
        safe = observation(log)
        text = json.dumps(safe, sort_keys=True)
        (directory / "api-build-observation.json").write_text(text + "\n", encoding="utf-8")
        print("Local Daytona API build observation: " + text, flush=True)
    except OSError, ValueError, TypeError:
        pass
