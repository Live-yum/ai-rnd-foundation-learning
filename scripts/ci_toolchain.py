"""Real Aider CLI + real MCP stdio + real bundled Java/Vue sources, no model key."""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from workbench.aider_tool import EditBlocks, apply_blocks, repo_map
from workbench.context_mcp import export_continue
from workbench.filesystem import sha, write_json
from workbench.knowledge import build_index
from workbench.retrieval import query
from workbench.settings import ROOT, Settings
from workbench.vendor import prepare


async def mcp_roundtrip(source, index):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "workbench.cli", "tools", "context-server", str(source), str(index)],
        cwd=str(ROOT),
        env={**os.environ, "PYTHONUTF8": "1"},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            names = {tool.name for tool in (await session.list_tools()).tools}
            assert names == {"search_code", "repository_map"}
            result = await session.call_tool("search_code", {"question": "RestController"})
            assert not result.isError
            assert ".java" in str(result.content)
            return {"protocol": "real-stdio", "tools": sorted(names), "query_passed": True}


def main():
    with tempfile.TemporaryDirectory(prefix="rnd-tools-ci-") as temporary:
        root = Path(temporary)
        settings = Settings(data_dir=root / "state", _env_file=None)
        rows = prepare(settings, "yudao-vben")
        backend = Path(next(row["path"] for row in rows if row["slot"] == "backend"))
        frontend = Path(next(row["path"] for row in rows if row["slot"] == "frontend"))
        bindex, findex = root / "backend-index", root / "frontend-index"
        build_index(backend, bindex)
        build_index(frontend, findex)
        java = query(backend, bindex, "RestController")
        vue = query(frontend, findex, "useVbenForm")
        assert java["matches"] and vue["matches"]
        assert any(hit["path"].endswith(".vue") for hit in vue["matches"])
        export_continue(root, backend, bindex)
        protocol = asyncio.run(mcp_roundtrip(backend, bindex))
        source = root / "aider-source"
        source.mkdir()
        (source / "sample.py").write_text(
            "class Article:\n    def get_title(self):\n        return 'hello'\n", encoding="utf-8"
        )
        amap = root / "aider-index"
        build_index(source, amap)
        mapped = repo_map(source, amap, settings)
        assert "Article" in mapped["text"], mapped
        product = root / "product"
        product.mkdir()
        rule = product / "custom_rules.py"
        rule.write_text("def validate(entity, data):\n    return None\n", encoding="utf-8")
        value = EditBlocks(
            before_sha256=sha(rule),
            explanation="explicit CI edit, not an LLM",
            blocks="custom_rules.py\n<<<<<<< SEARCH\n    return None\n=======\n"
            "    if data.get('priority', 0) < 0:\n        raise ValueError('nonnegative')\n"
            "    return None\n>>>>>>> REPLACE\n",
        )
        edited = apply_blocks(product, value, settings)
        assert "nonnegative" in rule.read_text(encoding="utf-8")
        assert edited["before_commit"] != edited["after_commit"]
        evidence = {
            "passed": True,
            "native_java_hits": len(java["matches"]),
            "native_vben_hits": len(vue["matches"]),
            "continue_mcp": protocol,
            "aider_cli_map": True,
            "aider_cli_edit": True,
            "git_commits": True,
            "model_calls": 0,
            "daytona_live": False,
            "daytona_note": "SDK contract tested separately; no account provisioned",
        }
        write_json(ROOT / "reports/toolchain.json", evidence)
        print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
