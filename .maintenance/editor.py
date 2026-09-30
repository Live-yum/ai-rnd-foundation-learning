# Exact, reviewable UTF-8 source operations against verified commit c3d3c612.
PATCHES = {
    'scripts/ci_aider_workflow.py': ('f29219aee3c7ada297badbad9fb637656a3fa4e042d4871e53cd38791df2adea', [
        (32, 32, r'''            assert payload["code_context"]["contexts"][0]["retrieval"]["mode"].startswith("ast+continue-fts5")
'''),
        (76, 76, r'''            retrieval_engine="continue",
'''),
        (122, 122, r'''                "actual_continue_index": True,
'''),
    ]),
    'scripts/ci_daytona_local.py': ('c667e7ad040568b769ae46d9d9202c4dbc6bf795dbd8af2339b04c75bfa8e3a1', [
        (0, 1, r'''"""Real smart-news workflow through all local tools and Daytona, fixture LLM only."""
'''),
        (6, 7, r'''from scripts.news_fixture import NewsFixture, ORIGINAL_REQUEST, LIMITATIONS
'''),
        (8, 10, r'''from workbench.runtime import Runtime
from workbench.sandbox import validate_configuration
'''),
        (11, 11, r'''from workbench.store import Store
'''),
        (14, 38, r'''    report = {"passed": False, "model_transport": "explicit-fixture", "model_api_calls": 0}
    with tempfile.TemporaryDirectory(prefix="rnd-daytona-workflow-") as temp:
        settings = Settings(
            data_dir=Path(temp),
            install_products=True,
            tool_timeout=600,
            repo_map_provider="aider",
            retrieval_engine="continue",
            _env_file=ROOT / ".data/daytona-local/workbench.env",
        )
        validate_configuration(settings, "python-basic", {"database": "sqlite"})
        if settings.sandbox_provider != "daytona":
            raise ValueError("Acceptance requires explicit local Daytona configuration")
        store = Store(settings)
        fixture = NewsFixture()
        run_id = None
'''),
        (39, 41, r'''            store.migrate()
            project = store.create_project("泰拉瑞亚游戏小助手", "project")
            run_id = store.create_run(project["id"], {
                "template": "python-basic",
                "selection": {"template": "python-basic", "frontend": "simple-admin", "database": "sqlite"},
                "requirement": ORIGINAL_REQUEST,
            }, "run")["run_id"]
            with Runtime(settings, store, fixture) as worker:
                assert worker.tick()
                run = store.get_run(run_id)
                assert run["status"] == "WAITING_CLARIFICATION", run
                assert run["pending"]["data"]["requirement"]["unsupported"] == LIMITATIONS
                store.set_automation(run_id, True, "authorize-once")
                assert worker.tick()
                run = store.get_run(run_id)
                assert run["status"] == "READY", run
                snapshot = worker.graph.get_state({"configurable": {"thread_id": run_id}})
                assert snapshot.values["sandbox"]["enabled"] is True
            assert run["auto_mode"] and not run["pending"] and not run["error"]
            result = run["result"]
            assert result["isolated_dependencies"] is True
            assert result["cleanroom"]["passed"] is True and result["cleanroom"]["restart"] is True
            assert (settings.data_dir / "runs" / run_id / "delivery.zip").is_file()
            assert fixture.calls == ["requirement:1", "recommend:2", "plan:2"], fixture.calls
            assert [row["content"] for row in store.messages(run_id)] == [ORIGINAL_REQUEST]
            report.update(
                passed=True, status="READY", initial_status="WAITING_CLARIFICATION",
                smart_authorizations=1, subsequent_manual_actions=0,
                explicit_facts_preserved=True, reported_boundary_list_regression=True,
                actual_continue_index=True, actual_aider_repo_map=True,
                isolated_dependencies=True, independent_zip=True,
                cleanroom=result["cleanroom"], model_fixture_calls=fixture.calls,
            )
'''),
        (42, 48, r'''            if run_id:
                run = store.get_run(run_id)
                report["last_status"] = run["status"]
                report["error"] = settings.redact(run["error"] or "")
                root = settings.data_dir / "runs" / run_id
                for name in ("daytona-verification.json", "tool-failure.json"):
                    path = root / name
                    if path.is_file():
                        report[name] = json.loads(settings.redact(path.read_text(encoding="utf-8")))
            write_json(ROOT / "reports/daytona-local.json", report)
            store.engine.dispose()
    print(json.dumps({"passed": report["passed"], "status": report["last_status"]}))
'''),
    ]),
    'scripts/ci_guided_browser.py': ('a5d960165496d52cb676907a31d33e9dcdc92bb535d014e13f720facaf9130a3', [
        (15, 15, r'''from scripts.news_fixture import (ORIGINAL_REQUEST, assert_approved, assert_resolution, news_requirement, news_spec)
'''),
        (19, 67, r''''''),
        (89, 100, r'''                if payload.get("autonomous"):
                    assert_resolution(payload)
                value = news_requirement(payload.get("autonomous", False))
'''),
        (101, 101, r'''                assert_approved(payload)
'''),
        (138, 138, r'''            retrieval_engine="continue",
'''),
        (155, 155, r'''            "requirement": ORIGINAL_REQUEST,
'''),
        (262, 262, r'''                    "reported_boundary_list_regression": True,
                    "explicit_facts_preserved": True,
'''),
    ]),
    'scripts/ci_handbook.py': ('52077c22e364bc782a997d1d435c42065162551b1b5359270bc28a3abf280f59', [
        (5, 5, r'''import shutil
'''),
        (59, 59, r'''        # Build the optional real Continue component from the textbook's restored files,
        # not from the original project's generated bundle or installed node_modules.
        npm = shutil.which("npm")
        if not npm:
            raise RuntimeError("Complete handbook acceptance requires Node 22/npm; see the Node environment step")
        run([npm, "ci", "--prefix", "tools/node", "--no-audit", "--no-fund"], destination, env)
        run([npm, "run", "build", "--prefix", "tools/node"], destination, env)
        env["RND_REQUIRE_NODE_TESTS"] = "1"
'''),
        (84, 84, r'''            "continue_component_rebuilt_from_handbook": True,
'''),
    ]),
    'scripts/ci_toolchain.py': ('7f51e0b1ffb02de51d146a19fd018291bf7203daab39c16be3cb84285caf2afe', [
        (9, 10, r'''from workbench.aider_tool import EditBlocks, apply_blocks, executable, repo_map
'''),
        (15, 16, r'''from workbench.tools import ToolFailure, run_command
'''),
        (27, 28, r'''        env={**os.environ, "PYTHONUTF8": "1", "RETRIEVAL_ENGINE": "continue"},
'''),
        (43, 43, r'''    ready = run_command([executable(Settings(_env_file=None)), str(ROOT / "tools/aider/offline_runner.py"), "--check-local-deps"], ROOT, 60)
    assert json.loads(ready["log"])["packaged_encodings_verified"] is True
'''),
        (47, 48, r'''        settings = Settings(data_dir=root / "state", retrieval_engine="continue", _env_file=None)
'''),
        (55, 56, r'''        java = query(backend, bindex, "RestController", settings=settings)
'''),
        (57, 58, r'''            frontend, findex, "useVbenForm", file_suffix=".vue", path_prefix="apps/web-antd/", settings=settings
'''),
        (96, 96, r'''            "continue_upstream_index": json.loads((findex / "continue-index.json").read_text(encoding="utf-8")),
'''),
    ]),
    'scripts/guided_browser.cjs': ('10af0fdebec6d356b5aa629d9c1b870f3e024a18306273ac25f79d457d351fb3', [
        (28, 33, r'''      await page.locator("#requirement").fill(cfg.requirement);
'''),
        (112, 112, r'''      await filter({ q: "矿石" }, 1);
'''),
        (113, 113, r'''      await filter({ q: "泰拉瑞亚", filter_category: "攻略", from_published_on: "2026-03-09", to_published_on: "2026-03-09" }, 1);
'''),
        (141, 141, r'''            combined_search_category_date_filter: true,
'''),
    ]),
    'scripts/news_fixture.py': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''"""Explicit deterministic model fixtures for CI, never production fallback models.

The first response deliberately reproduces the reported erroneous template-boundary
list. The next response can resolve it only after receiving stored scope and
recommendation feedback. Real processes, databases and tools remain unmocked.
"""

LIMITATIONS = [
    "自动从外部网站采集或抓取游戏资讯不受当前模板支持。",
    "面向无需登录的公众开放浏览不受当前模板支持。",
]
QUESTION = "需要个人资讯管理页面，还是无需登录的公众网站？如无特别说明，按个人管理页面规划。"
ORIGINAL_REQUEST = "泰拉瑞瑞亚游戏资讯"


def news_spec():
    return {
        "title": "游戏资讯助手",
        "data_scope": "per_user",
        "entities": [
            {
                "name": "news",
                "description": "游戏资讯",
                "fields": [
                    {
                        "name": "title",
                        "kind": "text",
                        "required": True,
                        "min_length": 1,
                        "max_length": 250,
                        "searchable": True,
                    },
                    {
                        "name": "body",
                        "kind": "text",
                        "required": True,
                        "min_length": 1,
                        "max_length": 3000,
                        "searchable": True,
                    },
                    {
                        "name": "published_on",
                        "kind": "date",
                        "required": True,
                        "filterable": True,
                        "date_range": True,
                    },
                    {
                        "name": "category",
                        "kind": "enum",
                        "required": False,
                        "choices": ["资讯", "攻略", "大神"],
                        "filterable": True,
                    },
                ],
            }
        ],
        "acceptance": ["标题正文搜索", "分类筛选", "真实日期及含边界日期区间", "逐用户隔离"],
        "custom_rules": [],
        "unsupported": [],
    }



def news_requirement(autonomous=False):
    return {
        "summary": "泰拉瑞瑞亚游戏资讯的登录后个人管理页面",
        "users": ["登录后管理自己资讯的用户"],
        "data_scope": "per_user",
        "features": ["标题与正文必填", "发布日期是真实日期", "分类可选", "资讯增删改查", "标题正文搜索", "分类与含边界日期区间组合筛选"],
        "acceptance": news_spec()["acceptance"],
        "questions": [] if autonomous else [QUESTION],
        "unsupported": [] if autonomous else LIMITATIONS,
        "limitations": LIMITATIONS if autonomous else [],
        "recommendations": ["未要求采集或公众浏览，采用登录后个人手动录入管理；标题250字，正文3000字，日期区间含边界"],
        "assumptions": ["用户没有明确要求采集或匿名公开网站"],
        "facts": {"标题长度上限": "250字符", "正文长度上限": "3000字符", "分类是否必填": "否", "日期区间": "包含起始日和结束日"},
    }


def assert_resolution(payload):
    assert payload["autonomous"] is True
    assert payload["original_request"]
    assert payload["resolution_feedback"]["unsupported"] == LIMITATIONS
    assert payload["resolution_feedback"]["questions"] == [QUESTION]
    assert payload["current_requirement"]["facts"] == news_requirement()["facts"]


def assert_approved(payload):
    approved = payload["approved_requirement"]
    assert approved["unsupported"] == [] and approved["questions"] == []
    assert approved["limitations"] == LIMITATIONS
    assert approved["facts"] == news_requirement()["facts"]


class NewsFixture:
    def __init__(self):
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        from workbench.domain import Plan, Requirement

        self.calls.append(key)
        if schema is Requirement:
            if payload["autonomous"]:
                assert_resolution(payload)
            return Requirement.model_validate(news_requirement(payload["autonomous"]))
        if schema is Plan:
            assert_approved(payload)
            context = payload["code_context"]["contexts"][0]
            assert context["repo_map"]["provider"] == "aider-cli-repo-map"
            assert context["repo_map"]["network"] == "disabled"
            assert context["retrieval"]["mode"].startswith("ast+continue-fts5")
            return Plan.model_validate(news_spec())
        raise AssertionError("Deterministic news CRUD needs no coding model: " + key)
'''),
    ]),
    'tools/aider/offline_runner.py': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', [
        (0, 0, r'''"""Python 3.12 entry for real Aider, with packaged token data and no network.

This guards the registered Repo Map/apply CLI modes. It is not a sandbox for
arbitrary Python supplied by a model. Installation is a separate uv operation.
"""

import hashlib
import json
import os
import socket
import sys
from importlib.metadata import distribution, version
from pathlib import Path

ENCODINGS = {
    "9b5ad71b2ce5302211f9c61530b329a4922fc6a4": "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7",
    "fb374d419588a4632f3f557e76b4b70aebbca790": "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d",
}


def packaged_encodings():
    cache = Path(distribution("litellm").locate_file("litellm/litellm_core_utils/tokenizers"))
    for name, expected in ENCODINGS.items():
        path = cache / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("Aider packaged tokenizer integrity failure; reinstall tools/aider with uv sync --locked")
    return cache


def install_offline_guard():
    def audit(event, args):
        if event.startswith(("socket.getaddrinfo", "socket.gethostby", "socket.getnameinfo")):
            raise PermissionError("Aider local tool network access is disabled")
        if event in {"socket.connect", "socket.sendto", "socket.bind"}:
            if args[0].family in {socket.AF_INET, socket.AF_INET6}:
                raise PermissionError("Aider local tool network access is disabled")
    sys.addaudithook(audit)


def main():
    if sys.version_info[:2] != (3, 12) or version("aider-chat") != "0.86.2":
        raise RuntimeError("Use the pinned Python 3.12 tools/aider environment")
    cache = packaged_encodings()
    os.environ.update(
        CUSTOM_TIKTOKEN_CACHE_DIR=str(cache),
        TIKTOKEN_CACHE_DIR=str(cache),
        LITELLM_LOCAL_MODEL_COST_MAP="True",
        AIDER_ANALYTICS="false",
        DO_NOT_TRACK="1",
    )
    install_offline_guard()
    if sys.argv[1:] == ["--check-local-deps"]:
        import tiktoken
        for name in ("cl100k_base", "o200k_base"):
            assert tiktoken.get_encoding(name).encode("本机编码检查")
        print(json.dumps({"aider": "0.86.2", "python": "3.12", "packaged_encodings_verified": True, "network": "disabled"}))
        return 0
    # Aider accepts a local metadata file. Use the locked package's own data,
    # instead of its otherwise automatic model-price URL lookup.
    metadata = Path(distribution("litellm").locate_file("litellm/model_prices_and_context_window_backup.json"))
    if hashlib.sha256(metadata.read_bytes()).hexdigest() != "e8da995ddcffc05a8dcbe4a8504326a6e352ba9e38151e147cbb5b4b694c937d":
        raise RuntimeError("Aider packaged model metadata integrity failure")
    sys.argv.extend(["--model-metadata-file", str(metadata)])
    from aider.main import main as aider_main
    return aider_main()


if __name__ == "__main__":
    raise SystemExit(main())
'''),
    ]),
    'workbench/aider_tool.py': ('7d06dcc750ba96cb438c162b5394269b7a59cacad43d36363d297c43a5b22192', [
        (45, 46, r'''    interpreter = candidate.parent / ("python.exe" if os.name == "nt" else "python")
    if not interpreter.is_file():
        raise ValueError("Aider路径旁没有对应Python解释器；请使用tools/aider的独立uv环境")
    return str(interpreter)
'''),
        (87, 88, r'''    version = run_command([executable(settings), str(ROOT / "tools/aider/offline_runner.py"), "--version"], work, timeout=30, extra_env=env)[
'''),
        (95, 95, r'''            str(ROOT / "tools/aider/offline_runner.py"),
'''),
        (192, 192, r'''            network="disabled",
'''),
        (263, 263, r'''        "network": "disabled",
'''),
    ]),
}
