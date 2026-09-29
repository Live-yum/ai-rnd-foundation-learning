"""Real pinned tools + explicit model fixture. No provider credentials and no cloud requests."""

import asyncio
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

from workbench.aider_tools import Edits, repo_map
from workbench.domain import Plan, Requirement
from workbench.filesystem import atomic_text, write_json
from workbench.knowledge import build_index
from workbench.retrieval import search
from workbench.runtime import Runtime
from workbench.settings import ROOT, Settings
from workbench.store import Store
from workbench.tools import clean_env
from workbench.vendor import prepare

REPORTS = ROOT / "reports/toolchain"


def acceptance_plan():
    return Plan.model_validate(
        {
            "title": "实际工具验收",
            "data_scope": "per_user",
            "acceptance": ["CRUD", "priority不能为负"],
            "entities": [
                {
                    "name": "task",
                    "description": "任务",
                    "fields": [
                        {"name": "title", "kind": "text", "max_length": 80},
                        {"name": "priority", "kind": "integer"},
                    ],
                }
            ],
            "custom_rules": [
                {
                    "entity": "task",
                    "description": "priority >= 0",
                    "accept_examples": [{"title": "ok", "priority": 1}],
                    "reject_examples": [{"title": "bad", "priority": -1}],
                }
            ],
        }
    )


class ProtocolFixture:
    """Only model responses are fixtures. Aider, Git, processes, SQL and HTTP run for real."""

    def __init__(self):
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append(key)
        if schema is Requirement:
            return Requirement(
                summary="个人任务，priority不能为负",
                users=["个人"],
                data_scope="per_user",
                features=["CRUD", "priority非负"],
                acceptance=["CRUD", "priority不能为负"],
            )
        if schema is Plan:
            assert (
                payload["template_source_context"]["product"]["map"]["engine"]
                == "aider-0.86.2-repomap"
            )
            return acceptance_plan()
        if schema is Edits:
            first = key.startswith("coding:0:")
            # First rule is deliberately semantically wrong, forcing the real repair edge.
            return Edits.model_validate(
                {
                    "before_sha256": payload["context"]["files"]["custom_rules.py"]["sha256"],
                    "edits": [
                        {
                            "search": "    return None\n" if first else "        return None\n",
                            "replace": "    if entity == 'task' and data['priority'] < 0:\n        return None\n    return None\n"
                            if first
                            else "        raise ValueError('priority must be nonnegative')\n",
                        }
                    ],
                    "explanation": "explicit CI fixture, deliberately wrong first then repaired",
                }
            )
        raise AssertionError(schema)


def workflow(settings):
    store = Store(settings)
    store.migrate()
    gateway = ProtocolFixture()
    try:
        project = store.create_project("Aider真实流程", uuid.uuid4().hex)
        run_id = store.create_run(
            project["id"],
            {"requirement": "个人任务priority>=0", "template": "python-basic"},
            uuid.uuid4().hex,
        )["run_id"]
        with Runtime(settings, store, gateway) as worker:
            for _ in range(8):
                assert worker.tick(), "workflow unexpectedly had no work"
                run = store.get_run(run_id)
                if run["status"] == "READY":
                    break
                assert run["status"].startswith("WAITING_"), run
                store.submit(
                    run_id,
                    {"gate_id": run["pending"]["gate_id"], "action": "approve", "approved": True},
                    uuid.uuid4().hex,
                )
            assert run["status"] == "READY", run
        assert "coding:0:aider" in gateway.calls and "coding:1:aider" in gateway.calls
        assert "coding:2:aider" not in gateway.calls
        evidence = {
            "models": "explicit-protocol-fixture",
            "aider": "real-0.86.2-offline",
            "calls": gateway.calls,
            "status": run["status"],
            "cleanroom": run["result"]["cleanroom"],
        }
        for attempt in (0, 1):
            receipt = json.loads(
                (settings.data_dir / "runs" / run_id / f"aider-{attempt}.json").read_text(
                    encoding="utf-8"
                )
            )
            assert (
                receipt["before_commit"] != receipt["after_commit"]
                and receipt["model_calls_by_aider"] == 0
            )
            evidence[f"edit_{attempt}"] = receipt
        write_json(REPORTS / "aider-workflow.json", evidence)
    finally:
        store.engine.dispose()


async def mcp_protocol(source, index):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "workbench.continue_mcp", "--source", str(source), "--index", str(index)],
        env=clean_env(),
        cwd=str(ROOT),
    )
    async with asyncio.timeout(90):
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                catalog = await client.list_tools()
                assert {tool.name for tool in catalog.tools} == {"search_code", "read_source"}
                assert all(tool.annotations.readOnlyHint for tool in catalog.tools)
                found = await client.call_tool("search_code", {"query": "useArticleForm"})
                assert not found.isError, found
                result = json.loads(found.content[0].text)
                hit = result["results"][0]
                read = await client.call_tool(
                    "read_source",
                    {
                        "path": hit["path"],
                        "line": hit["line"],
                        "end_line": hit["end_line"],
                        "expected_sha256": hit["sha256"],
                    },
                )
                assert not read.isError
                denied = await client.call_tool(
                    "read_source",
                    {"path": "../.env", "line": 1, "end_line": 1, "expected_sha256": hit["sha256"]},
                )
                assert denied.isError
    write_json(
        REPORTS / "continue-mcp.json",
        {
            "mcp_stdio": "real-client-server-passed",
            "read_only": True,
            "continue_ide_ui_tested": False,
            "engine": "platform-index-via-supported-Continue-MCP",
        },
    )


def native_indexes(settings):
    evidence = []
    for template in ("fastapiadmin", "yudao-vben"):
        for row in prepare(settings, template):
            root = Path(row["path"])
            index = settings.data_dir / "knowledge" / template / row["slot"] / row["sha"]
            data = json.loads((index / "index.json").read_text(encoding="utf-8"))
            record = {
                "slot": row["slot"],
                "revision": row["sha"],
                "source_digest": row["source_digest"],
                "symbol_files": sum(bool(e["symbols"]) for e in data["files"].values()),
                "parse_diagnostics": sum(
                    bool(e.get("parse_error")) for e in data["files"].values()
                ),
            }
            assert record["symbol_files"] > 0
            if row["slot"] == "backend":
                assert search(root, index, "CodegenController")["results"]
                mapping = repo_map(root, settings)
                assert mapping["text"] and ".java" in mapping["text"]
                write_json(REPORTS / "aider-yudao-map.json", mapping)
            if row["slot"] == "frontend":
                result = search(root, index, "useVbenForm")
                assert result["results"], "Vben Hook search had no source-backed match"
                write_json(REPORTS / "vben-retrieval.json", result)
            evidence.append(record)
    write_json(REPORTS / "bundled-ast.json", evidence)


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rnd-toolchain-ci-") as directory:
        root = Path(directory)
        settings = Settings(
            data_dir=root / "state",
            tool_timeout=900,
            coding_engine="aider",
            repo_map_engine="aider",
            _env_file=None,
        )
        workflow(settings)
        source, index = root / "mcp-source", root / "mcp-index"
        atomic_text(source / "hook.ts", "export function useArticleForm() { return true; }\n")
        build_index(source, index)
        asyncio.run(mcp_protocol(source, index))
        if os.name != "nt":
            native_indexes(settings)
        # Genuine installed SDK schema/signature check, explicitly NOT a cloud acceptance.
        import inspect

        from daytona import Daytona, DaytonaConfig

        from workbench.daytona_tools import sandbox_params

        params = sandbox_params(
            settings.model_copy(update={"daytona_snapshot": "operator-snapshot"}), "ci-no-cloud"
        )
        assert params.network_block_all and params.ttl_minutes == 15 and params.public is False
        assert "wait" in inspect.signature(Daytona.delete).parameters
        config = DaytonaConfig(
            api_key="not-a-real-key", api_url="https://example.invalid/api", otel_enabled=False
        )
        assert config.api_url == "https://example.invalid/api"
        write_json(
            REPORTS / "daytona-coverage.json",
            {
                "sdk_schema": "passed",
                "cloud_executed": False,
                "reason": "No user authorization, endpoint, snapshot or secret supplied",
            },
        )
    print(
        "Real Aider workflow/repair/clean-room, AST and MCP checks passed; Daytona cloud NOT executed"
    )


if __name__ == "__main__":
    main()
