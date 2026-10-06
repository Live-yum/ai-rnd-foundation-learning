# tests/test_capability_obligations.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`workbench.capability_contracts`、`workbench.capability_obligations`、`workbench.capability_policy`、`workbench.capability_verification`、`workbench.catalog`、`workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `proposed`（L35–L62）：接收`text`。 调用`scope_sources`、`digest`、`make_plan`、`Selection().model_dump`、`Selection`、`plan.model_dump`、`CapabilityPlan.model_validate`、`scope_policy`、`plan.selection.model_dump`。 返回路径：L62的`plan, scope, scope_policy(scope, plan.selection.model_dump())`。
- `proof_for`（L65–L78）：接收`plan`。 调用`obligation_identity`。 返回路径：L66的`{ "obligation_checks": [ { "id": o.id, "contract_sha256": obligation_identity(o), "phase":…`。
- `test_unrelated_crud_source_ids_never_complete_original_request`（L89–L111）：接收`requirement_text`。 控制顺序：L104断言`coverage_errors(plan, sources) == []`；L105断言`contract_errors(plan) == []`；L108断言`result["full_request_complete"] is False`；L109断言`result["complete_source_ids"] == []`；L110断言`{row["source_id"] for row in result["obligations"]} == {s["id"] for s in sources}`；L111断言`all(row["status"] == "remaining" for row in result["obligations"])`。 调用`scope_sources`、`digest`、`make_plan`、`Selection().model_dump`、`Selection`、`coverage_errors`、`contract_errors`、`scope_policy`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_atomic_source_binding_and_exhaustive_claim_require_exact_review`（L114–L135）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L116断言`coverage_errors(plan, scope["sources"]) == []`；L118遍历`( {}, {"actor": "delegated-ai"}, {"actor": "local-operator", "con…`；L127断言`closed["full_request_complete"]`；L128断言`closed["remaining_obligations"] == []`；L129断言`closed["remaining_source_ids"] == []`；L135断言`coverage_errors(plan, scope["sources"])`。 调用`proposed`、`coverage_errors`、`business_coverage`、`pytest.raises`、`reviewed_coverage`、`proof_for`、`digest`、`review_contract`、`plan.model_copy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_cannot_replace_controller_nonce_before_write_or_after_restart`（L139–L159）：接收`phase`。 控制顺序：L159断言`variables == {"nonce": "controller-random"}`。 调用`proposed`、`plan.model_dump`、`raw["scenarios"][0][phase].insert`、`pytest.raises`、`CapabilityPlan.model_validate`、`CaptureBudget`、`budget.store`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_physical_receipts_cannot_be_missing_duplicated_stale_or_restart_inconsistent`（L163–L177）：接收`mutation`。 控制顺序：L166按`mutation == "missing"`分支；L168按`mutation == "duplicate"`分支；L170按`mutation == "stale"`分支；L172按`mutation == "changed-values"`分支。 调用`proposed`、`proof_for`、`proof["obligation_checks"].pop`、`proof["obligation_checks"].append`、`deepcopy`、`pytest.raises`、`require_obligation_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_hardcoded_responses_unrelated_writes_and_duplicate_rows_do_not_close_obligation`（L189–L191）：接收`rows`。 调用`pytest.raises`、`assert_physical_rows`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_trusted_sqlite_probe_observes_real_rows_without_importing_app`（L195–L269）：接收`tmp_path`、`monkeypatch`。 控制顺序：L252断言`len(calls) == 2`；L253断言`stopped == [True]`。 调用`proposed`、`database.parent.mkdir`、`sqlite3.connect`、`connection.execute`、`private.mkdir`、`SimpleNamespace`、`monkeypatch.setattr`、`stopped.append`、`run_obligation_checks`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_trusted_sqlite_probe_observes_real_rows_without_importing_app.upload`（L206–L208）：接收`data`、`path`、`timeout`。 控制顺序：L207断言`type(data) is bytes and len(data) <= 65536`。 调用`type`、`len`、`(private / Path(path).name).write_bytes`、`Path`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_trusted_sqlite_probe_observes_real_rows_without_importing_app.trusted_exec`（L212–L240）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L213按`argv[:3] == ["/usr/bin/rm", "-f", "--"]`分支；L216断言`argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]`；L217断言`timeout <= 15`；L221按`len(argv) > 6`分支；L222断言`"ApplicationPause" in argv[4]`；L223断言`0 < float(argv[-2]) <= 12`。 调用`(private / Path(argv[3]).name).unlink`、`Path`、`SimpleNamespace`、`len`、`float`、`probe.replace( "pathlib.Path('/tmp/rnd-capability/product')", f"p…`、`probe.replace`、`str`、`os.getuid`等。 返回路径：L215的`SimpleNamespace(exit_code=0)`；L240的`SimpleNamespace(exit_code=result.returncode, result=result.stdout)`。
- `test_sqlite_missing_or_computed_columns_cannot_masquerade_as_physical_values`（L276–L302）：接收`tmp_path`、`shape`。 控制顺序：L279按`shape == "view"`分支；L283按`shape.endswith("generated")`分支；L299按`shape == "missing-columns"`分支；L302断言`result.returncode != 0`。 调用`sqlite3.connect`、`connection.execute`、`shape.endswith`、`shape.startswith`、`local_sqlite_probe`、`pytest.mark.parametrize`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `local_sqlite_probe`（L305–L327）：接收`root`、`database`、`assertion`、`probe`。 控制顺序：L326断言`list(private.iterdir()) == []`。 调用`private.mkdir`、`request.write_text`、`json.dumps`、`str`、`probe.replace("pathlib.Path('/tmp/rnd-capability/product')", f"pa…`、`probe.replace`、`os.getuid`、`subprocess.run`、`request.unlink`等。 返回路径：L327的`result`。
- `test_root_sqlite_never_follows_candidate_links_or_special_files`（L332–L363）：接收`tmp_path`、`shape`。 控制顺序：L340按`shape == "database"`分支；L342按`shape == "hardlink"`分支；L344按`shape == "fifo"`分支；L345按`not hasattr(os, "mkfifo")`分支；L348按`shape == "directory"`分支；L360断言`result.returncode != 0`；L361断言`"secret" not in result.stdout`；L363断言`connection.execute("SELECT title FROM entries").fetchone() == ("secret",)`。 调用`inside.mkdir`、`sqlite3.connect`、`connection.execute`、`database.symlink_to`、`os.link`、`hasattr`、`pytest.skip`、`os.mkfifo`、`inside.rmdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_rename_after_open_cannot_redirect_root_sqlite`（L368–L404）：接收`tmp_path`、`swapped`。 控制顺序：L374遍历`((database, "retained"), (outside / "owned.db", "secret"))`；L402断言`result.returncode == 0`；L403断言`json.loads(result.stdout) == [{"title": "retained"}]`；L404断言`"secret" not in result.stdout`。 调用`inside.mkdir`、`outside.mkdir`、`sqlite3.connect`、`connection.execute`、`str`、`SQLITE_PROBE.replace`、`local_sqlite_probe`、`json.loads`、`pytest.mark.skipif`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_sqlite_snapshot_includes_committed_uncheckpointed_wal`（L408–L426）：接收`tmp_path`。 控制顺序：L417断言`database.with_name(database.name + "-wal").stat().st_size > 0`；L423断言`result.returncode == 0`；L424断言`json.loads(result.stdout) == [{"title": "retained-random"}]`。 调用`sqlite3.connect`、`connection.execute`、`connection.commit`、`database.with_name(database.name + "-wal").stat`、`database.with_name`、`local_sqlite_probe`、`json.loads`、`connection.close`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonempty_rollback_journal_is_rejected_without_recovery`（L430–L446）：接收`tmp_path`。 控制顺序：L444断言`result.returncode != 0`；L445断言`not result.stdout`；L446断言`journal.read_bytes() == b"\0" * 512`。 调用`sqlite3.connect`、`connection.execute`、`database.with_name`、`journal.write_bytes`、`local_sqlite_probe`、`journal.read_bytes`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_replayed_response_cannot_replace_an_obligations_saved_physical_selector`（L449–L454）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`proposed`、`plan.model_dump`、`pytest.raises`、`CapabilityPlan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_restart_order_rejects_reconstruction_before_any_challenge_replay`（L459–L625）：接收`tmp_path`、`monkeypatch`、`replay`。 源码说明：Run the production restart block with a reset-on-start/rebuild-on-request app. Aliases and encoded bearer tokens deliberately retransmit the challenge without a literal ${nonce} in the request. Reject。 控制顺序：L473按`replay in {"post-nonce", "alias"}`分支；L482按`replay == "get-nonce"`分支；L487按`replay in {"post-nonce", "alias"}`分支；L615按`replay == "retained"`分支；L618断言`events == ["start-health", "physical", "replay"]`；L622断言`events == ["start-health", "physical"]`；L623断言`receipt["checks"] == []`；L624断言`receipt["obligation_checks"] == initial`。后续分支沿下方源码相同行号继续阅读。 调用`proposed`、`plan.model_dump`、`step.update`、`raw["scenarios"][0]["after_restart"].append`、`CapabilityPlan.model_validate`、`base64.urlsafe_b64encode(json.dumps(stored).encode()).decode`、`base64.urlsafe_b64encode`、`json.dumps(stored).encode`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_restart_order_rejects_reconstruction_before_any_challenge_replay.trusted_exec`（L518–L527）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L519按`argv[:3] == ["/usr/bin/rm", "-f", "--"]`分支；L522断言`argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]`；L523断言`argv[4] == SQLITE_PROBE or "ApplicationPause" in argv[4]`。 调用`uploads.pop`、`SimpleNamespace`、`events.append`、`json.loads`、`local_sqlite_probe`。 返回路径：L521的`SimpleNamespace(exit_code=0)`；L527的`SimpleNamespace(exit_code=result.returncode, result=result.stdout)`。
- `test_actual_restart_order_rejects_reconstruction_before_any_challenge_replay.candidate`（L529–L547）：接收`request`。 控制顺序：L531按`replay in {"post-nonce", "alias"}`分支；L533按`replay == "get-nonce"`分支；L538按`replay != "retained" and recovered is not None`分支。 调用`events.append`、`json.loads`、`dict`、`base64.urlsafe_b64decode`、`sqlite3.connect`、`connection.execute`、`int`、`connection.execute("SELECT title FROM entries WHERE id=7").fetcho…`、`httpx.Response`等。 返回路径：L543的`httpx.Response( 200, stream=httpx.ByteStream(json.dumps({"title": found[0]}).encode()), he…`。
- `test_actual_restart_order_rejects_reconstruction_before_any_challenge_replay.start`（L549–L556）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L551按`replay != "retained"`分支。 调用`events.append`、`sqlite3.connect`、`connection.execute`、`httpx.Client`、`httpx.MockTransport`、`clients.append`。 返回路径：L556的`client, "unused", "unused"`。
- `test_atomic_contract_rejects_weak_or_unrelated_evidence_shapes`（L640–L658）：接收`mutation`。 控制顺序：L643按`mutation == "no-nonce"`分支；L645按`mutation == "unknown-scenario"`分支；L647按`mutation == "unknown-table"`分支；L649按`mutation == "fixture"`分支；L651按`mutation == "boolean-storage"`分支；L653按`mutation == "unsupported-postgres"`分支。 调用`proposed`、`plan.model_dump`、`raw["scenarios"][0].update`、`Selection(template="fastapiadmin").model_dump`、`Selection`、`pytest.raises`、`CapabilityPlan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_store_requires_operator_approval_for_exact_run_stage_and_data`（L661–L687）：接收`settings`、`store`。 控制顺序：L676断言`store.explicit_approval(run, "extension_design", data, version=1)["gate_id"] == gate[…`；L682遍历`[ ("extension_scope", data), ("extension_design", {**data, "sourc…`。 调用`store.create_project`、`store.create_run`、`store.gate`、`pytest.raises`、`store.explicit_approval`、`store.tx`、`session.add`、`Approval`、`session.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_expected_values_never_enter_submitted_command_or_environment`（L691–L729）：接收`monkeypatch`、`phase`。 控制顺序：L728断言`result[0]["passed"] is True`；L729断言`len(submissions) == 2 and files == {}`。 调用`proposed`、`SimpleNamespace`、`monkeypatch.setattr`、`run_obligation_checks`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_expected_values_never_enter_submitted_command_or_environment.upload`（L701–L705）：接收`data`、`path`、`timeout`。 控制顺序：L702断言`isinstance(data, bytes) and len(data) <= 65536`；L703断言`path.startswith(CONTROL + "/private/obligation-")`；L704断言`nonce not in path and key not in path`。 调用`isinstance`、`len`、`path.startswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_expected_values_never_enter_submitted_command_or_environment.execute`（L707–L719）：接收`command`、`env`、`timeout`。 控制顺序：L709断言`nonce not in command and key not in command`；L710断言`nonce not in json.dumps(env) and key not in json.dumps(env)`；L712按`"/usr/bin/rm" in argv`分支；L717断言`request["assertion"]["key"] == {"id": key}`；L718断言`nonce in request["assertion"]["values"]["title"]`。 调用`submissions.append`、`json.dumps`、`shlex.split`、`files.pop`、`SimpleNamespace`、`next`、`json.loads`。 返回路径：L714的`SimpleNamespace(exit_code=0, result="")`；L719的`SimpleNamespace(exit_code=0, result=json.dumps([request["assertion"]["values"]]))`。
- `test_private_request_cleanup_is_required_even_after_transport_failure`（L733–L768）：接收`monkeypatch`、`failure`。 控制顺序：L768断言`bool(files) is (failure == "cleanup")`。 调用`proposed`、`SimpleNamespace`、`pytest.raises`、`run_obligation_checks`、`bool`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_request_cleanup_is_required_even_after_transport_failure.upload`（L739–L742）：接收`data`、`path`、`**kwargs`。 控制顺序：L741按`failure == "upload"`分支；L742抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_private_request_cleanup_is_required_even_after_transport_failure.execute`（L744–L753）：接收`command`、`**kwargs`。 控制顺序：L746按`"/usr/bin/rm" in argv`分支；L747按`failure == "cleanup"`分支；L751按`failure == "probe"`分支；L752抛异常，停止当前正常路径。 调用`shlex.split`、`SimpleNamespace`、`files.pop`、`RuntimeError`、`json.dumps`。 返回路径：L748的`SimpleNamespace(exit_code=1)`；L750的`SimpleNamespace(exit_code=0)`；L753的`SimpleNamespace(exit_code=0, result=json.dumps([{"title": "持久化资料-random"}]))`。
- `test_private_request_rejects_unsafe_sources_before_observation`（L776–L819）：接收`tmp_path`、`mutation`。 控制顺序：L791按`mutation == "public-directory"`分支；L793按`mutation in {"symlink", "hardlink"}`分支；L797按`mutation == "symlink"`分支；L801按`mutation == "writable-file"`分支；L803按`mutation == "oversized"`分支；L815断言`result.returncode != 0`；L816断言`not result.stdout`；L817断言`"unopened.db" not in result.stderr`。 调用`private.mkdir`、`json.dumps`、`request.write_text`、`private.chmod`、`outside.write_text`、`request.unlink`、`request.symlink_to`、`os.link`、`request.chmod`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_obligations.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L819。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`33377`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_obligations.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b670ad29a3a3c18d90f88ff6be300f982577d3f478a3264a5a6706e3d86fd194"} -->
````python
# tests/test_capability_obligations.py
"""Authored counterexamples, not live model/native acceptance attestations."""

import ast
import base64
import json
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from scripts.capability_fixture import make_plan
from workbench.capability_contracts import CapabilityPlan, coverage_errors, scope_sources
from workbench.capability_obligations import (
    SQLITE_PROBE,
    assert_physical_rows,
    obligation_identity,
    require_obligation_evidence,
    review_contract,
    reviewed_coverage,
    run_obligation_checks,
)
from workbench.capability_policy import business_coverage, contract_errors, scope_policy
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection
from workbench.domain import digest


def proposed(text="用户创建并持久化自己的资料。"):
    sources = scope_sources([text])
    scope = {"messages": [text], "source_digest": digest([text]), "sources": sources}
    plan = make_plan(
        {
            "source_units": sources,
            "source_digest": scope["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    raw = plan.model_dump()
    raw["obligations"] = [
        {
            "id": "saved-record",
            "source_id": sources[0]["id"],
            "source_sha256": sources[0]["sha256"],
            "assertion": "资料标题写入并跨进程重启保留",
            "scenario_id": "private_records",
            "physical": {
                "table": "entries",
                "key": {"id": "${entry}"},
                "values": {"title": "持久化资料-${nonce}"},
            },
        }
    ]
    raw["complete_source_ids"] = [sources[0]["id"]]
    plan = CapabilityPlan.model_validate(raw)
    return plan, scope, scope_policy(scope, plan.selection.model_dump())


def proof_for(plan):
    return {
        "obligation_checks": [
            {
                "id": o.id,
                "contract_sha256": obligation_identity(o),
                "phase": phase,
                "passed": True,
                "observation_sha256": "a" * 64,
            }
            for o in plan.obligations
            for phase in ("initial", "restart")
        ]
    }


@pytest.mark.parametrize(
    "requirement_text",
    [
        "库存不能超卖且过期订单自动释放占用。",
        "预约改期应保留原记录并通知客户。",
        "仓库批次过期时禁止出库；并发预订不得重复占用。",
    ],
)
def test_unrelated_crud_source_ids_never_complete_original_request(requirement_text):
    sources = scope_sources([requirement_text])
    scope = {
        "messages": [requirement_text],
        "source_digest": digest([requirement_text]),
        "sources": sources,
    }
    plan = make_plan(
        {
            "source_units": sources,
            "source_digest": scope["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    # Reproduces the old false-positive structural minimum deliberately.
    assert coverage_errors(plan, sources) == []
    assert contract_errors(plan) == []
    policy = scope_policy(scope, plan.selection.model_dump())
    result = business_coverage(policy, {"passed": True, "full_request_complete": True})
    assert result["full_request_complete"] is False
    assert result["complete_source_ids"] == []
    assert {row["source_id"] for row in result["obligations"]} == {s["id"] for s in sources}
    assert all(row["status"] == "remaining" for row in result["obligations"])


def test_atomic_source_binding_and_exhaustive_claim_require_exact_review():
    plan, scope, policy = proposed()
    assert coverage_errors(plan, scope["sources"]) == []
    base = business_coverage(policy, {})
    for approval in (
        {},
        {"actor": "delegated-ai"},
        {"actor": "local-operator", "contract_digest": "b" * 64},
    ):
        with pytest.raises(CheckFailure, match="人工审阅"):
            reviewed_coverage(plan, policy, proof_for(plan), approval, base)
    approval = {"actor": "local-operator", "contract_digest": digest(review_contract(plan, policy))}
    closed = reviewed_coverage(plan, policy, proof_for(plan), approval, base)
    assert closed["full_request_complete"]
    assert closed["remaining_obligations"] == []
    assert closed["remaining_source_ids"] == []
    stale = plan.model_copy(deep=True)
    stale.obligations[0].assertion = "a changed business assertion"
    with pytest.raises(CheckFailure):
        reviewed_coverage(stale, policy, proof_for(stale), approval, base)
    plan.obligations[0].source_sha256 = "0" * 64
    assert coverage_errors(plan, scope["sources"])


@pytest.mark.parametrize("phase", ["steps", "after_restart"])
def test_candidate_cannot_replace_controller_nonce_before_write_or_after_restart(phase):
    from workbench.capability_verification import CaptureBudget

    plan, _, _ = proposed()
    raw = plan.model_dump()
    raw["scenarios"][0][phase].insert(
        0,
        {
            "method": "GET",
            "path": "/constant",
            "status": 200,
            "captures": {"nonce": "$.fixed"},
        },
    )
    with pytest.raises(ValueError, match="nonce"):
        CapabilityPlan.model_validate(raw)
    variables = {"nonce": "controller-random"}
    budget = CaptureBudget({"scenario": variables})
    with pytest.raises(CheckFailure, match="随机挑战"):
        budget.store(variables, "nonce", "app-controlled-constant")
    assert variables == {"nonce": "controller-random"}


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "stale", "changed-values", "failed"])
def test_physical_receipts_cannot_be_missing_duplicated_stale_or_restart_inconsistent(mutation):
    plan, _, _ = proposed()
    proof = proof_for(plan)
    if mutation == "missing":
        proof["obligation_checks"].pop()
    elif mutation == "duplicate":
        proof["obligation_checks"].append(deepcopy(proof["obligation_checks"][0]))
    elif mutation == "stale":
        proof["obligation_checks"][0]["contract_sha256"] = "c" * 64
    elif mutation == "changed-values":
        proof["obligation_checks"][1]["observation_sha256"] = "c" * 64
    else:
        proof["obligation_checks"][0]["passed"] = False
    with pytest.raises(CheckFailure):
        require_obligation_evidence(plan, proof, aggregate=True)


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [{"title": "constant"}],
        [{"unrelated": "value"}],
        [{"title": "random"}, {"title": "random"}],
    ],
)
def test_hardcoded_responses_unrelated_writes_and_duplicate_rows_do_not_close_obligation(rows):
    with pytest.raises(CheckFailure, match="物理值"):
        assert_physical_rows(rows, {"values": {"title": "random"}})


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_fixed_trusted_sqlite_probe_observes_real_rows_without_importing_app(tmp_path, monkeypatch):
    plan, _, _ = proposed()
    database = tmp_path / plan.runtime.database_path
    database.parent.mkdir(parents=True)
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER, title TEXT)")
        connection.execute("INSERT INTO entries VALUES(?,?)", (7, "持久化资料-run-random"))
    calls = []
    private = tmp_path / "controller-private"
    private.mkdir(mode=0o700)

    def upload(data, path, *, timeout):
        assert type(data) is bytes and len(data) <= 65536
        (private / Path(path).name).write_bytes(data)

    sandbox = SimpleNamespace(fs=SimpleNamespace(upload_file=upload))

    def trusted_exec(sandbox, argv, timeout):
        if argv[:3] == ["/usr/bin/rm", "-f", "--"]:
            (private / Path(argv[3]).name).unlink(missing_ok=True)
            return SimpleNamespace(exit_code=0)
        assert argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]
        assert timeout <= 15
        # The supervisor has separate real-process tests. This transport fixture
        # runs only its fixed reader, never UID-wide signals on the test host.
        probe = argv[4] if len(argv) == 6 else argv[-1]
        if len(argv) > 6:
            assert "ApplicationPause" in argv[4]
            assert 0 < float(argv[-2]) <= 12
        code = (
            probe.replace(
                "pathlib.Path('/tmp/rnd-capability/product')", f"pathlib.Path({str(tmp_path)!r})"
            )
            .replace(
                "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
            )
            .replace("control_uid=0", f"control_uid={os.getuid()}")
        )
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", code, str(private / Path(argv[5]).name)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        calls.append(argv)
        return SimpleNamespace(exit_code=result.returncode, result=result.stdout)

    monkeypatch.setattr("workbench.capability_obligations.control_exec", trusted_exec)
    stopped = []
    monkeypatch.setattr(
        "workbench.capability_sandbox.restart_application_identity",
        lambda *args: stopped.append(True),
    )
    saved = {"private_records": {"entry": 7, "nonce": "run-random"}}
    first = run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase="initial")
    second = run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase="restart")
    require_obligation_evidence(plan, {"obligation_checks": first + second}, aggregate=True)
    assert len(calls) == 2
    assert stopped == [True], "Only the initial probe may destroy the application generation"
    with sqlite3.connect(database) as connection:
        connection.execute("INSERT INTO entries VALUES(?,?)", (8, "持久化资料-run-random"))
    rebound = run_obligation_checks(
        sandbox,
        plan,
        plan.scenarios,
        {"private_records": {"entry": 8, "nonce": "run-random"}},
        30,
        phase="restart",
    )
    with pytest.raises(CheckFailure, match="已改变"):
        require_obligation_evidence(plan, {"obligation_checks": first + rebound}, aggregate=True)
    with sqlite3.connect(database) as connection:
        connection.execute("UPDATE entries SET title='wrong-but-row-count-is-unchanged'")
    with pytest.raises(CheckFailure, match="物理值"):
        run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase="restart")


@pytest.mark.parametrize(
    "shape", ["missing-columns", "virtual-generated", "stored-generated", "view"]
)
@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_sqlite_missing_or_computed_columns_cannot_masquerade_as_physical_values(tmp_path, shape):
    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        if shape == "view":
            connection.execute(
                "CREATE VIEW entries AS SELECT 'random-value' AS title, 'missing_status' AS missing_status"
            )
        elif shape.endswith("generated"):
            mode = "STORED" if shape.startswith("stored") else "VIRTUAL"
            connection.execute(
                "CREATE TABLE entries(title TEXT, missing_status TEXT GENERATED ALWAYS AS ('missing_status') "
                + mode
                + ")"
            )
            connection.execute("INSERT INTO entries(title) VALUES('random-value')")
        else:
            connection.execute("CREATE TABLE entries(title TEXT)")
            connection.execute("INSERT INTO entries VALUES('random-value')")
    assertion = {
        "table": "entries",
        "key": {"title": "random-value"},
        "values": {"title": "random-value", "missing_status": "missing_status"},
    }
    if shape == "missing-columns":
        assertion["key"] = {"nonexistent_key": "nonexistent_key"}
    result = local_sqlite_probe(tmp_path, database.name, assertion)
    assert result.returncode != 0, result.stdout


def local_sqlite_probe(root, database, assertion, *, probe=SQLITE_PROBE):
    private = root / "controller-private"
    private.mkdir(mode=0o700, exist_ok=True)
    request = private / ("obligation-" + "a" * 32 + ".json")
    request.write_text(json.dumps({"database_path": str(database), "assertion": assertion}))
    code = (
        probe.replace("pathlib.Path('/tmp/rnd-capability/product')", f"pathlib.Path({str(root)!r})")
        .replace(
            "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
        )
        .replace("control_uid=0", f"control_uid={os.getuid()}")
    )
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", code, str(request)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    finally:
        request.unlink(missing_ok=True)
    assert list(private.iterdir()) == [], "Private observations must be removed even on failure"
    return result


@pytest.mark.parametrize("shape", ["database", "directory", "wal", "journal", "hardlink", "fifo"])
@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_root_sqlite_never_follows_candidate_links_or_special_files(tmp_path, shape):
    inside = tmp_path / "data"
    inside.mkdir()
    database = inside / "owned.db"
    outside = tmp_path / "private.db"
    with sqlite3.connect(outside) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(7,'secret')")
    if shape == "database":
        database.symlink_to(outside)
    elif shape == "hardlink":
        os.link(outside, database)
    elif shape == "fifo":
        if not hasattr(os, "mkfifo"):
            pytest.skip("POSIX FIFO fixture")
        os.mkfifo(database)
    elif shape == "directory":
        inside.rmdir()
        inside.symlink_to(tmp_path, target_is_directory=True)
        database = inside / "private.db"
    else:
        database.write_bytes(outside.read_bytes())
        database.with_name(database.name + "-" + shape).symlink_to(outside)
    result = local_sqlite_probe(
        tmp_path,
        database.relative_to(tmp_path),
        {"table": "entries", "key": {"id": 7}, "values": {"title": "secret"}},
    )
    assert result.returncode != 0
    assert "secret" not in result.stdout
    with sqlite3.connect(outside) as connection:
        assert connection.execute("SELECT title FROM entries").fetchone() == ("secret",)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
@pytest.mark.parametrize("swapped", ["database", "directory"])
def test_candidate_rename_after_open_cannot_redirect_root_sqlite(tmp_path, swapped):
    inside = tmp_path / "data"
    inside.mkdir()
    database = inside / "owned.db"
    outside = tmp_path / "outside"
    outside.mkdir()
    for path, value in ((database, "retained"), (outside / "owned.db", "secret")):
        with sqlite3.connect(path) as connection:
            connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
            connection.execute("INSERT INTO entries VALUES(7,?)", (value,))
    entry = database if swapped == "database" else inside
    target = outside / "owned.db" if swapped == "database" else outside
    # Deterministically swap the candidate pathname immediately after its
    # descriptor was opened, before fstat/copy/SQLite. The root reader must keep
    # the pinned original object, never reopen through the replacement link.
    injection = f"""
original_open=os.open
def raced_open(path,flags,*args,**kwargs):
 fd=original_open(path,flags,*args,**kwargs)
 if path=={entry.name!r}:
  os.rename({str(entry)!r},{str(entry) + ".old"!r})
  os.symlink({str(target)!r},{str(entry)!r})
 return fd
os.open=raced_open
"""
    probe = SQLITE_PROBE.replace(
        "request=payload['assertion']", "request=payload['assertion']" + injection
    )
    result = local_sqlite_probe(
        tmp_path,
        "data/owned.db",
        {"table": "entries", "key": {"id": 7}, "values": {"title": "retained"}},
        probe=probe,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [{"title": "retained"}]
    assert "secret" not in result.stdout


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_private_sqlite_snapshot_includes_committed_uncheckpointed_wal(tmp_path):
    database = tmp_path / "owned.db"
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA wal_autocheckpoint=0")
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(7,'retained-random')")
        connection.commit()
        assert database.with_name(database.name + "-wal").stat().st_size > 0
        result = local_sqlite_probe(
            tmp_path,
            database.name,
            {"table": "entries", "key": {"id": 7}, "values": {"title": "retained-random"}},
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == [{"title": "retained-random"}]
    finally:
        connection.close()


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_nonempty_rollback_journal_is_rejected_without_recovery(tmp_path):
    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(7,'retained-random')")
    journal = database.with_name(database.name + "-journal")
    # Even a zeroed PERSIST journal, not just a recognized hot journal, fails
    # closed. The reader never needs to interpret candidate super-journal data.
    journal.write_bytes(b"\0" * 512)
    result = local_sqlite_probe(
        tmp_path,
        database.name,
        {"table": "entries", "key": {"id": 7}, "values": {"title": "retained-random"}},
    )
    assert result.returncode != 0
    assert not result.stdout
    assert journal.read_bytes() == b"\0" * 512


def test_replayed_response_cannot_replace_an_obligations_saved_physical_selector():
    plan, _, _ = proposed()
    raw = plan.model_dump()
    raw["scenarios"][0]["after_restart"][0]["captures"] = {"entry": "$.id"}
    with pytest.raises(ValueError):
        CapabilityPlan.model_validate(raw)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
@pytest.mark.parametrize("replay", ["post-nonce", "get-nonce", "alias", "token", "retained"])
def test_actual_restart_order_rejects_reconstruction_before_any_challenge_replay(
    tmp_path, monkeypatch, replay
):
    """Run the production restart block with a reset-on-start/rebuild-on-request app.

    Aliases and encoded bearer tokens deliberately retransmit the challenge
    without a literal ${nonce} in the request. Rejecting POST or that spelling
    alone would not fix this counterexample.
    """
    from workbench.capability_verification import run_scenarios

    plan, _, _ = proposed()
    raw = plan.model_dump()
    step = {"status": 200, "equals": {"$.title": "持久化资料-${nonce}"}}
    if replay in {"post-nonce", "alias"}:
        step.update(
            method="POST",
            path="/rebuild",
            body={
                "id": "${entry}",
                "title": "${alias}" if replay == "alias" else "持久化资料-${nonce}",
            },
        )
    elif replay == "get-nonce":
        step.update(method="GET", path="/rebuild?id=${entry}&title=持久化资料-${nonce}")
    else:
        step.update(method="GET", path="/entries/${entry}", headers={"Authorization": "${owner}"})
    raw["scenarios"][0]["after_restart"] = [step]
    if replay in {"post-nonce", "alias"}:
        raw["scenarios"][0]["after_restart"].append(
            {
                "method": "GET",
                "path": "/entries/${entry}",
                "status": 200,
                "equals": {"$.title": "持久化资料-${nonce}"},
            }
        )
    plan = CapabilityPlan.model_validate(raw)
    scenarios = plan.scenarios[:1]
    title = "持久化资料-run-random"
    stored = {"id": 7, "title": title}
    saved = {
        "private_records": {
            "nonce": "run-random",
            "entry": 7,
            "alias": title,
            "owner": base64.urlsafe_b64encode(json.dumps(stored).encode()).decode(),
        }
    }
    database = tmp_path / plan.runtime.database_path
    database.parent.mkdir()
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(?,?)", (7, title))
    events, clients, uploads = [], [], {}
    sandbox = SimpleNamespace(
        fs=SimpleNamespace(upload_file=lambda data, path, **kwargs: uploads.__setitem__(path, data))
    )

    def trusted_exec(sandbox, argv, timeout):
        if argv[:3] == ["/usr/bin/rm", "-f", "--"]:
            uploads.pop(argv[3], None)
            return SimpleNamespace(exit_code=0)
        assert argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]
        assert argv[4] == SQLITE_PROBE or "ApplicationPause" in argv[4]
        events.append("physical")
        payload = json.loads(uploads[argv[5]])
        result = local_sqlite_probe(tmp_path, payload["database_path"], payload["assertion"])
        return SimpleNamespace(exit_code=result.returncode, result=result.stdout)

    def candidate(request):
        events.append("replay")
        if replay in {"post-nonce", "alias"}:
            recovered = json.loads(request.content) if request.method == "POST" else None
        elif replay == "get-nonce":
            recovered = dict(request.url.params)
        else:
            recovered = json.loads(base64.urlsafe_b64decode(request.headers["Authorization"]))
        with sqlite3.connect(database) as connection:
            if replay != "retained" and recovered is not None:
                connection.execute(
                    "INSERT INTO entries VALUES(?,?)", (int(recovered["id"]), recovered["title"])
                )
            found = connection.execute("SELECT title FROM entries WHERE id=7").fetchone()
        return httpx.Response(
            200,
            stream=httpx.ByteStream(json.dumps({"title": found[0]}).encode()),
            headers={"Content-Type": "application/json"},
        )

    def start():
        events.append("start-health")
        if replay != "retained":
            with sqlite3.connect(database) as connection:
                connection.execute("DELETE FROM entries")
        client = httpx.Client(transport=httpx.MockTransport(candidate), base_url="http://fixture")
        clients.append(client)
        return client, "unused", "unused"

    monkeypatch.setattr("workbench.capability_obligations.control_exec", trusted_exec)
    monkeypatch.setattr(
        "workbench.capability_sandbox.restart_application_identity", lambda *a: None
    )
    initial = run_obligation_checks(sandbox, plan, scenarios, saved, 30, phase="initial")
    # The old request-before-witness ordering really does accept this same app.
    http, _, _ = start()
    with closing(http):
        run_scenarios(http, scenarios, saved=saved, after_restart=True)
        reconstructed = run_obligation_checks(sandbox, plan, scenarios, saved, 30, phase="restart")
    require_obligation_evidence(
        plan, {"obligation_checks": initial + reconstructed}, aggregate=True
    )

    tree = ast.parse((Path(__file__).parents[1] / "workbench/capability_sandbox.py").read_text())
    block = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "aggregate"
        and any(
            isinstance(child, ast.Assign) and ast.unparse(child.targets[0]) == "(http, _, _)"
            for child in node.body
        )
    )
    first = next(
        i
        for i, child in enumerate(block.body)
        if isinstance(child, ast.Assign) and ast.unparse(child.targets[0]) == "(http, _, _)"
    )
    last = next(
        i
        for i, child in enumerate(block.body)
        if isinstance(child, ast.Assign)
        and ast.unparse(child.targets[0]) == "receipt['database']['after_restart']"
    )
    receipt = {"checks": [], "obligation_checks": initial[:], "database": {}}
    scope = {
        "start": start,
        "closing": closing,
        "plan": plan,
        "scenarios": scenarios,
        "saved": saved,
        "sandbox": sandbox,
        "settings": SimpleNamespace(tool_timeout=30),
        "native": False,
        "trusted_oracle": None,
        "run_obligation_checks": run_obligation_checks,
        "run_scenarios": run_scenarios,
        "receipt": receipt,
        "counts": {"entries": 1},
        "database_counts": lambda *a: {"entries": 1},
        "CheckFailure": CheckFailure,
    }
    compiled = compile(ast.Module(block.body[first : last + 1], []), "actual-restart-order", "exec")
    events.clear()
    if replay == "retained":
        exec(compiled, scope)
        require_obligation_evidence(plan, receipt, aggregate=True)
        assert events == ["start-health", "physical", "replay"]
    else:
        with pytest.raises(CheckFailure, match="物理值"):
            exec(compiled, scope)
        assert events == ["start-health", "physical"]
        assert receipt["checks"] == []
        assert receipt["obligation_checks"] == initial
    assert all(client.is_closed for client in clients)


@pytest.mark.parametrize(
    "mutation",
    [
        "no-nonce",
        "unknown-scenario",
        "unknown-table",
        "fixture",
        "no-restart",
        "boolean-storage",
        "unsupported-postgres",
    ],
)
def test_atomic_contract_rejects_weak_or_unrelated_evidence_shapes(mutation):
    plan, _, _ = proposed()
    raw = plan.model_dump()
    if mutation == "no-nonce":
        raw["obligations"][0]["physical"]["values"] = {"title": "hardcoded"}
    elif mutation == "unknown-scenario":
        raw["obligations"][0]["scenario_id"] = "other"
    elif mutation == "unknown-table":
        raw["obligations"][0]["physical"]["table"] = "unrelated"
    elif mutation == "fixture":
        raw["scenarios"][0].update(evidence="external_fixture", external_service="email")
    elif mutation == "boolean-storage":
        raw["obligations"][0]["physical"]["key"] = {"id": True}
    elif mutation == "unsupported-postgres":
        raw["selection"] = Selection(template="fastapiadmin").model_dump()
    else:
        raw["scenarios"][0]["after_restart"] = []
    with pytest.raises(ValueError):
        CapabilityPlan.model_validate(raw)


def test_store_requires_operator_approval_for_exact_run_stage_and_data(settings, store):
    from workbench.store import Approval, Conflict

    project = store.create_project("review fixture", "review-project")
    run = store.create_run(project["id"], {"requirement": "authored"}, "review-run")["run_id"]
    data = {"source_digest": "a" * 64, "requires_explicit_review": True}
    gate = store.gate(run, "extension_design", 1, data, ["approve"])
    with pytest.raises(Conflict):
        store.explicit_approval(run, "extension_design", data, version=1)
    with store.tx() as session:
        session.add(Approval(gate_id=gate["gate_id"], decision=True, actor="delegated-ai"))
    with pytest.raises(Conflict):
        store.explicit_approval(run, "extension_design", data, version=1)
    with store.tx() as session:
        session.get(Approval, gate["gate_id"]).actor = "local-operator"
    assert (
        store.explicit_approval(run, "extension_design", data, version=1)["gate_id"]
        == gate["gate_id"]
    )
    with pytest.raises(Conflict):
        store.explicit_approval(run, "extension_design", data, version=2)
    for stage, revised in [
        ("extension_scope", data),
        ("extension_design", {**data, "source_digest": "b" * 64}),
    ]:
        with pytest.raises(Conflict):
            store.explicit_approval(run, stage, revised, version=1)


@pytest.mark.parametrize("phase", ["initial", "restart"])
def test_private_expected_values_never_enter_submitted_command_or_environment(monkeypatch, phase):
    import shlex

    from workbench.capability_isolation import CONTROL

    plan, _, _ = proposed()
    nonce, key = "secret-nonce-that-must-not-be-in-proc", "secret-physical-key"
    saved = {"private_records": {"nonce": nonce, "entry": key}}
    files, submissions = {}, []

    def upload(data, path, *, timeout):
        assert isinstance(data, bytes) and len(data) <= 65536
        assert path.startswith(CONTROL + "/private/obligation-")
        assert nonce not in path and key not in path
        files[path] = data

    def execute(command, *, env, timeout):
        submissions.append((command, env))
        assert nonce not in command and key not in command
        assert nonce not in json.dumps(env) and key not in json.dumps(env)
        argv = shlex.split(command)
        if "/usr/bin/rm" in argv:
            files.pop(argv[-1])
            return SimpleNamespace(exit_code=0, result="")
        request_path = next(value for value in argv if value in files)
        request = json.loads(files[request_path])
        assert request["assertion"]["key"] == {"id": key}
        assert nonce in request["assertion"]["values"]["title"]
        return SimpleNamespace(exit_code=0, result=json.dumps([request["assertion"]["values"]]))

    sandbox = SimpleNamespace(
        fs=SimpleNamespace(upload_file=upload), process=SimpleNamespace(exec=execute)
    )
    monkeypatch.setattr(
        "workbench.capability_sandbox.restart_application_identity", lambda *a: None
    )
    result = run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase=phase)
    assert result[0]["passed"] is True
    assert len(submissions) == 2 and files == {}


@pytest.mark.parametrize("failure", ["upload", "probe", "cleanup"])
def test_private_request_cleanup_is_required_even_after_transport_failure(monkeypatch, failure):
    import shlex

    plan, _, _ = proposed()
    files = {}

    def upload(data, path, **kwargs):
        files[path] = data
        if failure == "upload":
            raise RuntimeError("injected interrupted upload")

    def execute(command, **kwargs):
        argv = shlex.split(command)
        if "/usr/bin/rm" in argv:
            if failure == "cleanup":
                return SimpleNamespace(exit_code=1)
            files.pop(argv[-1], None)
            return SimpleNamespace(exit_code=0)
        if failure == "probe":
            raise RuntimeError("injected probe interruption")
        return SimpleNamespace(exit_code=0, result=json.dumps([{"title": "持久化资料-random"}]))

    sandbox = SimpleNamespace(
        fs=SimpleNamespace(upload_file=upload), process=SimpleNamespace(exec=execute)
    )
    expected = CheckFailure if failure == "cleanup" else RuntimeError
    with pytest.raises(expected):
        run_obligation_checks(
            sandbox,
            plan,
            plan.scenarios,
            {"private_records": {"entry": 7, "nonce": "random"}},
            30,
            phase="restart",
        )
    assert bool(files) is (failure == "cleanup")


@pytest.mark.skipif(sys.platform != "linux", reason="Linux root-private request validation")
@pytest.mark.parametrize(
    "mutation",
    ["public-directory", "symlink", "hardlink", "writable-file", "oversized", "wrong-owner"],
)
def test_private_request_rejects_unsafe_sources_before_observation(tmp_path, mutation):
    private = tmp_path / "controller-private"
    private.mkdir(mode=0o700)
    request = private / ("obligation-" + "b" * 32 + ".json")
    payload = json.dumps(
        {
            "database_path": "unopened.db",
            "assertion": {
                "table": "entries",
                "key": {"id": 7},
                "values": {"title": "private-challenge"},
            },
        }
    )
    request.write_text(payload)
    if mutation == "public-directory":
        private.chmod(0o755)
    elif mutation in {"symlink", "hardlink"}:
        outside = tmp_path / "outside.json"
        outside.write_text(payload)
        request.unlink()
        if mutation == "symlink":
            request.symlink_to(outside)
        else:
            os.link(outside, request)
    elif mutation == "writable-file":
        request.chmod(0o666)
    elif mutation == "oversized":
        request.write_bytes(b" " * 65537)
    uid = os.getuid() + (mutation == "wrong-owner")
    code = SQLITE_PROBE.replace(
        "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
    ).replace("control_uid=0", f"control_uid={uid}")
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code, str(request)],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode != 0
    assert not result.stdout
    assert "unopened.db" not in result.stderr, (
        "Reject the private source before touching the product"
    )
````
