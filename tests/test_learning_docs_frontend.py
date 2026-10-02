"""Lossless Vue source/asset teaching and genuinely rebuilt clean-room assets."""

import base64
import hashlib
import json

import pytest

from scripts import build_handbook as legacy
from scripts import build_learning_docs as builder
from scripts import ci_learning_docs as acceptance
from scripts.rebuild_from_handbook import extract
from scripts.rebuild_learning_docs import check_fences, fences


def write_files(root, files):
    for name, data in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def test_vue_authored_source_and_generated_assets_are_both_losslessly_collected(
    tmp_path, monkeypatch
):
    files = {
        "ui/src/App.vue": "<template>中文</template>\n".encode(),
        "ui/package-lock.json": b'{"lockfileVersion":3}\n',
        "workbench/web/index.html": b'<script src="/ui/app.js"></script>',
        "workbench/web/app.js": "(()=>{const s='中文';})();".encode(),
        "workbench/web/style.css": b"body{margin:0}\n",
    }
    write_files(tmp_path, files)
    write_files(tmp_path, {"ui/node_modules/not-owned/index.js": b"not source"})
    monkeypatch.setattr(legacy, "ROOT", tmp_path)
    monkeypatch.setattr(legacy, "GROUPS", [("control plane", ["ui", "workbench"])])
    monkeypatch.setattr(legacy, "GUIDES", [])
    rows = dict(next(legacy.sources())[1])
    assert rows.keys() == files.keys()
    for name, data in files.items():
        assert rows[name] == (data if name.startswith("workbench/web/") else data.decode())
    restored = extract(legacy.render())
    assert {
        name: value.encode() if isinstance(value, str) else value
        for name, value in restored.items()
    } == files


@pytest.mark.parametrize(
    "name", ["workbench/web/app.js", "workbench/web/style.css", "workbench/web/index.html"]
)
def test_generated_assets_use_labeled_folded_base64_without_losing_bytes(name):
    data = b"generated runtime snapshot\x00\xff\n"
    pages, row = builder.source_pages(name, data, 8)
    assert len(pages) == 1
    document = next(iter(pages.values()))
    assert "/sources/assets/" in row["parts"][0]
    assert "<details>" in document and "无需手写" in document
    assert "构建快照" in document and "真实操作截图" not in document
    assert row["sha256"] == hashlib.sha256(data).hexdigest()
    assert check_fences(document) == 1
    _, language, path, payload = next(fences(document))
    assert (language, path) == ("base64", name)
    assert base64.b64decode(payload.replace("\n", ""), validate=True) == data


@pytest.mark.parametrize(
    "name,stage",
    [
        ("ui/src/App.vue", 8),
        ("ui/src/api.ts", 8),
        ("ui/tests/stream.test.ts", 8),
        ("ui/package-lock.json", 8),
        ("workbench/model_settings.py", 1),
        ("workbench/clarification.py", 2),
        ("workbench/streaming.py", 3),
        ("tests/test_streaming_backend.py", 8),
        ("tests/test_model_settings.py", 8),
        ("tests/test_clarification_choices.py", 8),
    ],
)
def test_vue_and_streaming_stage_allocation_preserves_import_order(name, stage):
    assert builder.stage_for(name) == stage


def test_cleanroom_frontend_installs_tests_builds_and_compares_without_git(tmp_path):
    expected = {"workbench/web/app.js": b"built from restored source", "ui/src/main.ts": b"source"}
    write_files(tmp_path, expected)
    commands = []

    def run(argv):
        commands.append(argv)

    assert acceptance.rebuild_frontend(tmp_path, expected, "npm", run) == 1
    assert commands == [
        ["npm", "ci", "--prefix", "ui", "--no-audit", "--no-fund"],
        ["npm", "test", "--prefix", "ui"],
        ["npm", "run", "build", "--prefix", "ui"],
    ]
    assert not (tmp_path / ".git").exists()


@pytest.mark.parametrize("damage", ["missing", "extra", "bytes", "no_snapshot"])
def test_cleanroom_frontend_rejects_incomplete_or_different_builds(tmp_path, damage):
    expected = {"workbench/web/app.js": b"snapshot"}
    write_files(tmp_path, expected)
    if damage == "missing":
        (tmp_path / "workbench/web/app.js").unlink()
    elif damage == "extra":
        write_files(tmp_path, {"workbench/web/unexpected.js": b"extra"})
    elif damage == "bytes":
        write_files(tmp_path, {"workbench/web/app.js": b"different"})
    else:
        expected = {}
    with pytest.raises(AssertionError):
        acceptance.verify_frontend_bundle(tmp_path, expected)


def test_frontend_test_failure_stops_before_build_and_byte_comparison(tmp_path):
    commands = []

    def run(argv):
        commands.append(argv)
        if "test" in argv:
            raise RuntimeError("frontend tests failed")

    with pytest.raises(RuntimeError, match="frontend tests failed"):
        acceptance.rebuild_frontend(tmp_path, {}, "npm", run)
    assert len(commands) == 2
    assert all("build" not in command for command in commands)


def test_lessons_distinguish_browser_evidence_and_current_startup_delivery_boundaries():
    stages = {stage["id"]: stage for stage in builder.read_content()}
    startup = stages["00-environment"]["body"]
    control = stages["08-control-plane"]["body"]
    final = stages["14-acceptance"]["body"]
    assert "`start` 还会要求真实模型配置" not in startup
    assert "没有供应商Key时启动操作台" in control
    assert "SOURCE_READY" in control
    assert "uv run python -m scripts.ci_guided_browser" in final
    assert "reports/learning-docs-guided-browser" in final
    assert "不能把纯函数测试当作整条页面链已通过" in final
    assert all(check_fences(stage["body"]) >= 0 for stage in stages.values())


def test_cleanroom_calls_real_browser_driver_and_copies_its_distinct_evidence(tmp_path):
    destination, reports = tmp_path / "restored", tmp_path / "evidence"
    summary = {
        "passed": True,
        "real_browser": True,
        "actual_incremental_sse": True,
        "first_delta_before_provider_complete": True,
        "unicode_split_replay_dedupe": True,
        "model_mode": "explicit-local-http-fixtures",
    }
    commands = []

    def run(argv):
        commands.append(argv)
        write_files(
            destination,
            {"reports/guided-browser/summary.json": json.dumps(summary).encode()},
        )

    assert (
        acceptance.verify_frontend_browser(destination, "student-python", run, reports) == summary
    )
    assert commands == [["student-python", "-m", "scripts.ci_guided_browser"]]
    assert json.loads((reports / "summary.json").read_text()) == summary


def test_cleanroom_preserves_browser_failure_without_accepting_an_old_success(tmp_path):
    destination = tmp_path / "restored"
    previous, reports = tmp_path / "evidence/previous", tmp_path / "evidence/current"
    write_files(previous, {"summary.json": b'{"passed":true}', "old.png": b"old image"})

    def run(argv):
        write_files(destination, {"reports/guided-browser/workbench.log": b"fixture failure"})
        raise RuntimeError("browser failed")

    with pytest.raises(RuntimeError, match="browser failed"):
        acceptance.verify_frontend_browser(destination, "student-python", run, reports)
    assert (reports / "workbench.log").read_bytes() == b"fixture failure"
    assert not (reports / "summary.json").exists()

    assert not (reports / "old.png").exists()
    assert (previous / "summary.json").read_bytes() == b'{"passed":true}'
    assert (previous / "old.png").read_bytes() == b"old image"


def test_cleanroom_browser_refuses_reusing_an_existing_evidence_directory(tmp_path):
    reports = tmp_path / "evidence"
    write_files(reports, {"summary.json": b'{"passed":true}'})
    commands = []
    with pytest.raises(FileExistsError):
        acceptance.verify_frontend_browser(tmp_path / "student", "python", commands.append, reports)
    assert commands == []
    assert (reports / "summary.json").read_bytes() == b'{"passed":true}'
